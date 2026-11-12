"""
Tests for Start or sit at the route seam: the FastAPI test client with FakeJev, a function model of Pydantic AI in place
of Claude, and the live Sleeper week 10 of cpc and norcal with the week kickoffs, recorded on 2026-11-12 before the game.
"""
import dataclasses
import json
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from pathlib import Path

import pytest
import test_api
from fakes import FakeJev
from fastapi.testclient import TestClient
from pydantic_ai.messages import ModelMessage
from pydantic_ai.models.function import AgentInfo, FunctionModel
from test_api import HEADERS, PASSPHRASE, _here

from cornerstone_api.app import create_app
from cornerstone_api.game_lock import ESPN_SCOREBOARD_URL, SLEEPER_GRAPHQL_URL
from league.jev_port import ChoiceQuestion, JevError, NoulQuestion
from league.provider.sleeper import load_raw

repo = test_api.repo
settings = test_api.settings
sources = test_api.sources

PERSONAL = "/clients/{slug}/personal"
BO_GIRDS = {"cpc": 6, "norcal": 7}
# The recorded live week: the Sleeper raw files of each league, trimmed to the rostered players, and the answers of the
# Sleeper GraphQL `scores` query and of the ESPN scoreboard for weeks 9 and 10.
RECORDED = Path(__file__).parent / "fixtures" / "start-sit"
# The time of the recording, Thursday of week 10, before NYG at WAS, the first kickoff of the week.
BEFORE_KICKOFF = datetime(2026, 11, 12, 12, 53, tzinfo=UTC)
# One minute after the kickoff of NYG at WAS, at 2026-11-13T01:15Z.
AFTER_THURSDAY = datetime(2026, 11, 13, 1, 16, tzinfo=UTC)
NORCAL_HEADERS = {"X-League-Passphrase": "norcal-test"}


def _recorded(name: str) -> dict:
    return json.loads((RECORDED / name).read_text())


def sleeper_scores(season: int, week: int) -> dict:
    return _recorded(f"sleeper-scores-week-{week}.json")


def espn_scoreboard(season: int, week: int) -> dict:
    return _recorded(f"espn-scoreboard-week-{week}.json")


def _down(season: int, week: int) -> dict:
    raise OSError("the scores query is down")


def _forbidden(*args, **kwargs):
    raise AssertionError("Start or sit called a source other than Sleeper, ESPN, TypeSafe, and Anthropic")


class Calls:
    """Each source that a request calls, by name, so a test reads the outbound calls of Start or sit."""

    def __init__(self):
        self.names: list[str] = []

    def wrap(self, name: str, fetch):
        def call(*args, **kwargs):
            self.names.append(name)
            return fetch(*args, **kwargs)
        return call


class Writer:
    """A stand-in for Claude: the text of `text`, word by word, and a count of its calls."""

    def __init__(self, text: str = "Start your lineup by projection."):
        self.calls = 0
        self.text = text

    async def stream(self, messages: list[ModelMessage], info: AgentInfo) -> AsyncIterator[str]:
        self.calls += 1
        for word in self.text.split():
            yield word + " "


def _checks(key: str, question: NoulQuestion, state: dict) -> float:
    return 0.95


class Edges:
    """A stand-in for the Jev read of the Swaps: the probability of each bench player over each starter, by their two
    names. A pair with no entry gets 0.5, so it keeps the starter. Each Swap question is in `asked`."""

    def __init__(self, edges: dict[tuple[str, str], float] | None = None):
        self.edges = edges or {}
        self.asked: list[ChoiceQuestion] = []

    def choose(self, key: str, question: ChoiceQuestion, state: dict) -> dict[str, float]:
        self.asked.append(question)
        bench, starter = question.options
        names = {option: question.options[option].split(",")[0] for option in (bench, starter)}
        p = self.edges.get((names[bench], names[starter]), 0.5)
        return {bench: p, starter: 1 - p}


def _sources(base, slug: str, now: datetime, calls: Calls | None = None, scores=sleeper_scores,
             scoreboard=espn_scoreboard):
    calls = calls or Calls()
    raw = load_raw(RECORDED / f"{slug}-week-10")
    return dataclasses.replace(
        base, clock=lambda: now.astimezone(base.client.tz),
        fetch_sleeper=calls.wrap("sleeper", lambda league_id: (raw, BEFORE_KICKOFF)),
        fetch_sleeper_scores=calls.wrap("sleeper scores", scores),
        fetch_espn_scoreboard=calls.wrap("espn scoreboard", scoreboard),
        fetch_nflverse=_forbidden, fetch_history_week=_forbidden, fetch_trending=_forbidden, read_chart=_forbidden,
        fetch_past=_forbidden)


def _api(settings, sources, slug: str = "cpc", now: datetime = BEFORE_KICKOFF, writer: Writer | None = None,
         jev: FakeJev | None = None, **source_changes) -> TestClient:
    """An app over cpc and norcal, each on its recorded week 10."""
    cpc = _sources(_here(sources, settings), "cpc", now, **source_changes)
    values = cpc.client.values.model_copy(
        update={"packages": [name for name in cpc.client.values.packages if name != "eggs"]})
    norcal = _sources(dataclasses.replace(cpc, client=cpc.client.model_copy(update={"slug": "norcal",
                                                                                      "values": values})),
                      "norcal", now, **source_changes)
    settings = dataclasses.replace(settings, passphrases={"cpc": PASSPHRASE,
                                                          "norcal": NORCAL_HEADERS["X-League-Passphrase"]})
    app = create_app(settings, [cpc.client, norcal.client], sources={"cpc": cpc, "norcal": norcal},
                     jev=jev or FakeJev(answer=_checks, choose=Edges().choose))
    app.state.personal_model = FunctionModel(stream_function=(writer or Writer()).stream)
    return TestClient(app)


def _chunks(response) -> list[dict]:
    lines = [line.removeprefix("data: ") for line in response.text.splitlines() if line.startswith("data: ")]
    return [json.loads(line) for line in lines if line != "[DONE]"]


def _block(api: TestClient, slug: str = "cpc", roster_id: int | None = None) -> dict:
    response = api.post(PERSONAL.format(slug=slug), json={"topic": "start_sit", "roster_id": roster_id or BO_GIRDS[slug]},
                        headers=HEADERS if slug == "cpc" else NORCAL_HEADERS)
    assert response.status_code == 200, response.text
    # A lineup with a Swap sends its block again after the checked text, with the reason of each Swap. The site shows
    # the last block.
    return [c["data"] for c in _chunks(response) if c["type"] == "data-block"][-1]


def test_the_cpc_lineup_lists_the_slots_in_the_sleeper_order_with_each_fact_of_a_row(settings, sources):
    # AT-1: QB, RB, RB, WR, WR, TE, FLEX, FLEX, DEF, each row with the player, his team, the opponent, the kickoff, and
    # the projection.
    block = _block(_api(settings, sources))
    assert block["kind"] == "lineup" and block["topic"] == "start_sit" and block["team"] == BO_GIRDS["cpc"]
    assert [row["slot"] for row in block["rows"]] == ["QB", "RB", "RB", "WR", "WR", "TE", "FLEX", "FLEX", "DEF"]
    qb = block["rows"][0]
    assert qb["player"] == "Aaron Rodgers" and qb["nfl_team"] == "PIT" and qb["opponent"] == "CIN"
    # CIN hosts PIT on Sunday night, 2026-11-16T01:20Z, in the scores query.
    assert qb["kickoff"] == 1794792000000
    assert all(row["player"] and row["nfl_team"] and row["opponent"] and row["kickoff"] and row["projection"] is not None
               for row in block["rows"])


def test_the_norcal_lineup_has_three_flex_and_no_def(settings, sources):
    # AT-2: the slots of norcal, from its own league settings.
    block = _block(_api(settings, sources), "norcal")
    assert [row["slot"] for row in block["rows"]] == ["QB", "RB", "RB", "WR", "WR", "TE", "FLEX", "FLEX", "FLEX"]


def test_a_projection_is_the_stat_line_scored_with_the_cpc_scoring(settings, sources):
    # AT-3: Trey McBride has receptions in his projected stat line, and cpc scores half PPR.
    block = _block(_api(settings, sources))
    [row] = [row for row in block["rows"] if row["player"] == "Trey McBride"]
    raw = load_raw(RECORDED / "cpc-week-10")
    scoring = raw.league.scoring_settings
    [line] = [p.stats for p in raw.projections if p.player_id == row["player_id"]]
    assert scoring["rec"] == 0.5 and line["rec"] > 0
    assert row["projection"] == pytest.approx(sum(value * scoring[key] for key, value in line.items() if key in scoring),
                                              abs=0.1)
    # Rotowire prices the same line at half PPR, so the two agree for a TE with no bonus of the league.
    assert row["projection"] == pytest.approx(line["pts_half_ppr"], abs=0.1)


def test_a_questionable_starter_shows_his_body_part_no_practice_report_and_the_pivot(settings, sources):
    # AT-7 and AT-8: Jared Goff of cpc roster 7 is Questionable (chest), Sleeper has no practice report yet, and Patrick
    # Mahomes is the QB of his bench.
    raw = load_raw(RECORDED / "cpc-week-10")
    assert raw.players["3163"]["practice_participation"] is None
    block = _block(_api(settings, sources), roster_id=7)
    [row] = [row for row in block["rows"] if row["player"] == "Jared Goff"]
    assert row["slot"] == "QB"
    assert row["risk"] == {"tag": "Q", "body_part": "Chest", "practice": "No practice report yet",
                           "pivot": "Start J. Goff if he is active. If he is ruled out, start P. Mahomes."}
    # A healthy starter has no Q tag.
    assert all(r["risk"] is None for r in block["rows"] if r["player"] != "Jared Goff"
               and raw.players.get(r["player_id"] or "", {}).get("injury_status") is None)


def test_a_pivot_line_ends_with_one_period_after_a_name_with_a_suffix(settings, sources):
    # Kyle Pitts Sr. is the Pivot of Harold Fannin Jr. on cpc roster 7.
    block = _block(_api(settings, sources), roster_id=7)
    [row] = [row for row in block["rows"] if row["player"] == "Harold Fannin Jr."]
    assert row["risk"]["pivot"] == "Start H. Fannin Jr. if he is active. If he is ruled out, start K. Pitts Sr."


def test_the_players_who_cannot_play_are_named_with_their_status_and_sit_in_no_slot(settings, sources):
    # AT-10: Lamar Jackson of Bo Girds is on IR with his thumb. Luther Burden III of norcal is on a bye with CHI.
    cpc = _block(_api(settings, sources))
    assert {"name": "L. Jackson", "status": "IR", "body_part": "Thumb"} in cpc["cannot_play"]
    assert "Lamar Jackson" not in {row["player"] for row in cpc["rows"]}
    norcal = _block(_api(settings, sources), "norcal")
    assert {"name": "L. Burden III", "status": "Bye", "body_part": "Undisclosed"} in norcal["cannot_play"]
    assert "J.K. Dobbins" not in {row["player"] for row in norcal["rows"]}


def _held(slug: str) -> list[str]:
    raw = load_raw(RECORDED / f"{slug}-week-10")
    return next(m.starters or [] for m in raw.matchups if m.roster_id == BO_GIRDS[slug])


def test_a_player_whose_game_has_started_keeps_his_sleeper_slot_and_no_bench_player_of_that_game_moves(settings,
                                                                                                       sources):
    # AT-12: after the Thursday kickoff of NYG at WAS, Isaiah Likely (NYG) and Austin Ekeler (WAS) of norcal keep the
    # slots that they hold in Sleeper, locked. Antonio Williams (WAS) stays on the bench of cpc.
    before = _block(_api(settings, sources), "norcal")
    after = _block(_api(settings, sources, now=AFTER_THURSDAY), "norcal")
    held = _held("norcal")
    for pid in ("8131", "4663"):
        [row] = [row for row in after["rows"] if row["player_id"] == pid]
        assert row["locked"] and row["slot"] == ["QB", "RB", "RB", "WR", "WR", "TE", "FLEX", "FLEX", "FLEX"][held.index(pid)]
        assert after["rows"].index(row) == held.index(pid)
    assert not any(row["locked"] for row in before["rows"])
    unlocked = [row for row in after["rows"] if not row["locked"]]
    assert all(row["nfl_team"] not in {"NYG", "WAS"} for row in unlocked)
    cpc = _block(_api(settings, sources, now=AFTER_THURSDAY))
    assert "13301" not in {row["player_id"] for row in cpc["rows"]}


def test_a_game_that_sleeper_marks_started_is_locked_before_its_kickoff_time():
    # The lock reads the live flag too, so a wrong clock never leaves a started game open. The recorded week 9 games
    # are over, with has_started true.
    from cornerstone_api.game_lock import sleeper_kickoffs
    games = sleeper_kickoffs(sleeper_scores(2026, 9))
    assert games and all(game.started for game in games)
    assert all(game.locked(datetime(2026, 9, 1, tzinfo=UTC)) for game in games)


def test_the_espn_scoreboard_gives_the_kickoffs_when_the_sleeper_query_fails(settings, sources):
    # The fallback maps the ESPN code WSH to WAS, so the lock of NYG at WAS holds through ESPN too.
    after = _block(_api(settings, sources, now=AFTER_THURSDAY, scores=_down), "norcal")
    assert {row["player_id"] for row in after["rows"] if row["locked"]} == {"8131", "4663"}
    before = _block(_api(settings, sources, scores=_down))
    assert before["rows"][0]["kickoff"] == 1794792000000


def test_no_kickoff_source_gives_an_honest_503_and_no_lineup(settings, sources):
    api = _api(settings, sources, scores=_down, scoreboard=_down)
    response = api.post(PERSONAL.format(slug="cpc"), json={"topic": "start_sit", "roster_id": BO_GIRDS["cpc"]},
                        headers=HEADERS)
    assert response.status_code == 503


def test_start_sit_calls_only_sleeper_and_the_kickoff_sources(settings, sources):
    # AT-53: every source of the live snapshot that is not Sleeper raises, so a call to one fails the test. Jev is the
    # TypeSafe port and the function model stands in for Anthropic.
    calls = Calls()
    writer = Writer()
    _block(_api(settings, sources, calls=calls, writer=writer))
    assert set(calls.names) == {"sleeper", "sleeper scores"}
    assert writer.calls == 1
    assert SLEEPER_GRAPHQL_URL.startswith("https://sleeper.com/")
    assert ESPN_SCOREBOARD_URL.startswith("https://site.api.espn.com/")


def _swaps(block: dict) -> dict[str, str]:
    """The Swaps of a lineup block: the starter that each Swap benches, by the name of the bench player who takes his
    slot."""
    return {row["player"]: row["swap"]["over"] for row in block["rows"] if row["swap"]}


def _edges(edges: dict[tuple[str, str], float]) -> FakeJev:
    return FakeJev(answer=_checks, choose=Edges(edges).choose)


@pytest.mark.parametrize(("probability", "swaps"), [(0.70, {"Konata Mumpfield": "M. Golden"}), (0.69, {})])
def test_a_bench_player_takes_the_slot_at_a_probability_of_0_70_and_not_at_0_69(settings, sources, probability, swaps):
    # AT-5: Konata Mumpfield of the bench of Bo Girds over Matthew Golden, who starts at WR by projection. Each case
    # runs in its own test, because a second tap of the same lineup reads the kept Answer of the first.
    block = _block(_api(settings, sources, jev=_edges({("Konata Mumpfield", "Matthew Golden"): probability})))
    assert _swaps(block) == swaps
    if swaps:
        [row] = [row for row in block["rows"] if row["player"] == "Konata Mumpfield"]
        assert row["slot"] == "WR" and row["position"] == "WR" and row["nfl_team"] and row["kickoff"]
        assert "Matthew Golden" not in {row["player"] for row in block["rows"]}
    else:
        assert "Matthew Golden" in {row["player"] for row in block["rows"]}


def test_the_swap_candidates_resolve_by_the_highest_probability_and_fill_each_slot_once(settings, sources):
    # AT-6, on the lineup of Bo Girds: Audric Estime and Mike Washington Jr. each beat Kyren Williams, the second RB, at
    # 0.75 and 0.85. Konata Mumpfield beats Zay Flowers at 0.8 and Matthew Golden at 0.9.
    block = _block(_api(settings, sources, jev=_edges({
        ("Audric Estime", "Kyren Williams"): 0.75, ("Mike Washington Jr.", "Kyren Williams"): 0.85,
        ("Konata Mumpfield", "Zay Flowers"): 0.8, ("Konata Mumpfield", "Matthew Golden"): 0.9})))
    # The bench player at 0.85 takes the slot. The bench player who beats two starters fills only the slot at 0.9.
    assert _swaps(block) == {"Mike Washington Jr.": "K. Williams", "Konata Mumpfield": "M. Golden"}
    assert [row["player"] for row in block["rows"] if row["slot"] in {"RB", "WR"}] == [
        "Kenneth Walker III", "Mike Washington Jr.", "Zay Flowers", "Konata Mumpfield"]


def test_one_jev_request_reads_every_pair_of_a_bench_player_and_a_slot_he_can_fill(settings, sources):
    # The pairs of Bo Girds: 2 bench RBs for 2 RB and 2 FLEX slots, 2 bench WRs for 2 WR and 2 FLEX slots, and the
    # bench QB for the QB slot. Each Choice names the slot, and its options are the two players.
    jev = _edges({})
    _block(_api(settings, sources, jev=jev))
    [read] = [request for request in jev.requests if "players" in request.state]
    assert len(read.questions) == 2 * 4 + 2 * 4 + 1
    assert {"Aaron Rodgers", "Fernando Mendoza", "Konata Mumpfield"} <= set(read.state["players"])
    assert read.state["players"]["Konata Mumpfield"]["projection"] == 6.8
    qb = next(q for q in read.questions.values() if "Fernando Mendoza" in str(q.options))
    assert "as the QB of" in qb.instructions and len(qb.options) == 2


def test_a_failed_jev_read_gives_the_honest_miss_with_no_lineup_and_no_swap(settings, sources):
    # AT-20: a failed read is never "keep the starter", so no lineup shows and Claude writes nothing.
    writer = Writer()
    api = _api(settings, sources, writer=writer, jev=FakeJev(error=JevError("down")))
    response = api.post(PERSONAL.format(slug="cpc"), json={"topic": "start_sit", "roster_id": BO_GIRDS["cpc"]},
                        headers=HEADERS)
    chunks = _chunks(response)
    assert not any(c["type"] == "data-block" for c in chunks)
    assert [c["data"] for c in chunks if c["type"] == "data-miss"] == [
        {"closest": ["next_matchup", "weak_spots", "waiver_targets"]}]
    assert not any(c["type"] == "error" for c in chunks)
    assert writer.calls == 0


def test_the_total_with_the_swaps_is_the_sum_of_the_projections_of_the_lineup_with_the_swaps(settings, sources):
    # AT-11: the total by projection stays beside the total with the Swaps, so the toggle shows both.
    block = _block(_api(settings, sources, jev=_edges({("Konata Mumpfield", "Matthew Golden"): 0.9})))
    assert block["total"] == 121.7
    assert block["swap_total"] == pytest.approx(sum(row["projection"] for row in block["rows"]), abs=0.05)
    [row] = [row for row in block["rows"] if row["swap"]]
    assert block["swap_total"] == pytest.approx(block["total"] - row["swap"]["over_projection"] + row["projection"],
                                                abs=0.1)
    assert block["swap_total"] == 115.6


def test_a_lineup_with_no_swap_has_the_same_total_both_ways(settings, sources):
    block = _block(_api(settings, sources))
    assert _swaps(block) == {} and block["swap_total"] == block["total"]


def test_each_swap_carries_the_checked_sentence_that_names_its_two_players_as_its_reason(settings, sources):
    # AT-4: Claude writes the reason of each Swap from the two Fact sheets. The block comes again after the check, with
    # the sentence that names both players, so the row opens with its reason. The kept Answer keeps the reason too.
    reason = "Konata Mumpfield starts over Matthew Golden, because the read of his matchup is better this week."
    # A name with a suffix, such as "Jr.", does not end the sentence.
    suffix = "Mike Washington Jr. starts over Kyren Williams, because his role is larger this week."
    writer = Writer(f"{suffix} {reason} Start the rest of your lineup by projection.")
    api = _api(settings, sources, writer=writer, jev=_edges({("Konata Mumpfield", "Matthew Golden"): 0.9,
                                                             ("Mike Washington Jr.", "Kyren Williams"): 0.85}))
    response = api.post(PERSONAL.format(slug="cpc"), json={"topic": "start_sit", "roster_id": BO_GIRDS["cpc"]},
                        headers=HEADERS)
    chunks = _chunks(response)
    blocks = [c["data"] for c in chunks if c["type"] == "data-block"]
    assert [row["swap"]["reason"] for block in blocks for row in block["rows"] if row["swap"]] == [
        None, None, suffix, reason]
    # The reason comes after "checked", so it never shows a sentence that the check did not pass.
    types = [c["type"] if c["type"] != "data-check" else c["data"]["state"] for c in chunks]
    assert types.index("checked") < len(types) - 1 - types[::-1].index("data-block")
    kept = _block(api)
    assert writer.calls == 1
    assert [row["swap"]["reason"] for row in kept["rows"] if row["swap"]] == [suffix, reason]


def test_the_slice_of_claude_names_each_swap_and_the_total_with_the_swaps(settings, sources):
    # Claude and the Jev check read the lineup with the Swaps, with the starter that each Swap benches.
    seen: list[str] = []

    class Reader(Writer):
        async def stream(self, messages, info):
            seen.append(str(messages))
            async for word in super().stream(messages, info):
                yield word

    _block(_api(settings, sources, writer=Reader(), jev=_edges({("Konata Mumpfield", "Matthew Golden"): 0.9})))
    [prompt] = seen
    assert '\\"swap_over\\": \\"Matthew Golden\\"' in prompt or '"swap_over": "Matthew Golden"' in prompt
    assert "projected_total_with_swaps" in prompt


def test_a_locked_player_is_never_a_swap_and_never_loses_his_slot_to_one(settings, sources):
    # After the Thursday kickoff, Austin Ekeler (WAS) and Isaiah Likely (NYG) of norcal are locked starters, and Antonio
    # Williams (WAS) is a locked bench player of cpc. Jev would swap each of them at 0.95, but no pair with a locked
    # player reaches Jev.
    jev = _edges({("Seth McGowan", "Austin Ekeler"): 0.95, ("Eli Raridon", "Isaiah Likely"): 0.95})
    norcal = _block(_api(settings, sources, "norcal", now=AFTER_THURSDAY, jev=jev), "norcal")
    assert _swaps(norcal) == {}
    asked = [str(q.options) for request in jev.requests for q in request.questions.values() if hasattr(q, "options")]
    assert asked and not any("Austin Ekeler" in options or "Isaiah Likely" in options for options in asked)
    cpc = _block(_api(settings, sources, now=AFTER_THURSDAY,
                      jev=_edges({("Antonio Williams", "Matthew Golden"): 0.95})))
    assert _swaps(cpc) == {}
