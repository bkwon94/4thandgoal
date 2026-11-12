"""
Tests for Start or sit at the route seam: the FastAPI test client with FakeJev, a function model of Pydantic AI in place
of Claude, and the live Sleeper week 10 of cpc and norcal with the week kickoffs, recorded on 2026-11-12 before the game.
"""
import dataclasses
import json
import shutil
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
# The saved Sleeper stat rows of weeks 1 to 9 of cpc and the Sleeper DEF projections of week 10, recorded on 2026-11-12.
# The stat rows are NFL facts, so both leagues read the same rows.
SAVED_HISTORY = Path(__file__).parents[3] / "clients" / "cpc" / "data" / "2026" / "history"
DEF_PROJECTIONS = Path(__file__).parent / "fixtures" / "nfl-game"


def _recorded(name: str) -> dict:
    return json.loads((RECORDED / name).read_text())


def sleeper_scores(season: int, week: int) -> dict:
    return _recorded(f"sleeper-scores-week-{week}.json")


def espn_scoreboard(season: int, week: int) -> dict:
    return _recorded(f"espn-scoreboard-week-{week}.json")


def def_projections(season: int, week: int) -> list[dict]:
    return json.loads((DEF_PROJECTIONS / f"sleeper-def-projections-week-{week}.json").read_text())


def _saved_weeks(folder: Path) -> None:
    """Put the saved stat rows of weeks 1 to 9 in the history of the client folder of the test."""
    for week in range(1, 10):
        target = folder / "data" / "2026" / "history" / f"week-{week:02d}"
        target.mkdir(parents=True, exist_ok=True)
        shutil.copy(SAVED_HISTORY / f"week-{week:02d}" / "stats.json", target / "stats.json")


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
        fetch_def_projections=calls.wrap("def projections", def_projections),
        fetch_nflverse=_forbidden, fetch_history_week=_forbidden, fetch_trending=_forbidden, read_chart=_forbidden,
        fetch_past=_forbidden)


def _api(settings, sources, slug: str = "cpc", now: datetime = BEFORE_KICKOFF, writer: Writer | None = None,
         jev: FakeJev | None = None, **source_changes) -> TestClient:
    """An app over cpc and norcal, each on its recorded week 10."""
    cpc = _sources(_here(sources, settings), "cpc", now, **source_changes)
    _saved_weeks(cpc.client.folder)
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
    assert set(calls.names) == {"sleeper", "sleeper scores", "def projections"}
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


def _stat_rows(weeks: range) -> dict[int, list[dict]]:
    return {week: json.loads((SAVED_HISTORY / f"week-{week:02d}" / "stats.json").read_text()) for week in weeks}


def test_the_fact_sheet_of_a_player_holds_his_matchup_his_game_his_team_tilt_and_his_usage(settings, sources):
    # Zay Flowers of Bo Girds plays for BAL against LAC in week 10. The Jev read of the Swaps reads his Fact sheet.
    jev = _edges({})
    _block(_api(settings, sources, jev=jev))
    [read] = [request for request in jev.requests if "players" in request.state]
    sheet = read.state["players"]["Zay Flowers"]
    assert sheet["opponent"] == "LAC" and sheet["projection"] == 13.5 and sheet["projected_stat_line"]
    # The expected margin is the gap of the two DEF projections: BAL scores what the LAC defense allows.
    defenses = {row["player_id"]: row["stats"]["pts_allow"] for row in def_projections(2026, 10)}
    assert sheet["team_projected_points"] == defenses["LAC"]
    assert sheet["opponent_projected_points"] == defenses["BAL"]
    assert sheet["expected_margin"] == round(defenses["LAC"] - defenses["BAL"], 2)
    # The LAC defense against WRs: the mean of `fan_pts_allow_wr` over its games of weeks 1 to 9, and its place.
    season = _stat_rows(range(1, 10))
    games = [row["stats"]["fan_pts_allow_wr"] for rows in season.values() for row in rows
             if row["player_id"] == "LAC" and row["stats"].get("gp")]
    defense = sheet["defense_against_position"]
    assert defense["position"] == "WR" and defense["of"] == 32
    assert defense["allowed_per_game"] == round(sum(games) / len(games), 1)
    assert 1 <= defense["place"] <= 32 and defense["league_average"] is not None
    # The pass tilt of BAL against the league, over the saved weeks.
    rows = [row for rows in season.values() for row in rows]
    passes = sum(row["stats"].get("pass_att", 0) for row in rows if row.get("team") == "BAL")
    runs = sum(row["stats"].get("rush_att", 0) for row in rows if row.get("team") == "BAL")
    assert sheet["team_pass_share"] == round(passes / (passes + runs), 3)
    assert 0 < sheet["league_pass_share"] < 1
    # His share of the targets, the carries, and the snaps of BAL in his games of weeks 7 to 9.
    last = _stat_rows(range(7, 10))
    mine = [row for rows in last.values() for row in rows if row["player_id"] == "9997" and row["stats"].get("gp")]
    team = [row for week_rows in last.values() for row in week_rows if row.get("team") == "BAL"]
    usage = sheet["last_3_weeks"]
    assert usage["weeks"] == [7, 8, 9]
    assert usage["target_share"] == round(sum(r["stats"].get("rec_tgt", 0) for r in mine)
                                          / sum(r["stats"].get("rec_tgt", 0) for r in team), 3)
    assert usage["carry_share"] == round(sum(r["stats"].get("rush_att", 0) for r in mine)
                                         / sum(r["stats"].get("rush_att", 0) for r in team), 3)
    assert usage["snap_share"] == round(sum(r["stats"]["off_snp"] for r in mine)
                                        / sum(r["stats"]["tm_off_snp"] for r in mine), 3)
    assert sheet["injury_status"] is None
    # The state says what each fact of a sheet means, so the read and the check read the same meaning.
    assert set(read.state["what_each_fact_means"]) >= {"expected_margin", "defense_against_position", "last_3_weeks"}


ASK = "/clients/cpc/ask"
# The route answers of a typed start question: about the league, a fit for a Topic, and no team named.
START_ROUTE = {"about_league": 0.99, "fits_topic": 0.95, "data_can_answer": 0.6}


class Router(Edges):
    """A stand-in for Jev that routes each typed question to Start or sit, and reads each pair of two players by the
    edges of Edges, the first option first."""

    def noul(self, key: str, question: NoulQuestion, state: dict) -> float:
        return START_ROUTE.get(key, 0.01) if "topics" in state else 0.95

    def choose(self, key: str, question: ChoiceQuestion, state: dict) -> dict[str, float]:
        if "topics" in state:
            return {option: float(option == ("start_sit" if key == "topic" else next(iter(question.options))))
                    for option in question.options}
        return super().choose(key, question, state)


def _routed(edges: dict[tuple[str, str], float] | None = None) -> FakeJev:
    router = Router(edges)
    return FakeJev(answer=router.noul, choose=router.choose)


def _ask(api: TestClient, question: str) -> dict:
    response = api.post(ASK, json={"question": question, "roster_id": BO_GIRDS["cpc"], "week": 9}, headers=HEADERS)
    assert response.status_code == 200, response.text
    return response.json()


def _typed(api: TestClient, question: str) -> list[dict]:
    response = api.post(PERSONAL.format(slug="cpc"), json={"topic": "start_sit", "roster_id": BO_GIRDS["cpc"],
                                                          "question": question}, headers=HEADERS)
    assert response.status_code == 200, response.text
    return _chunks(response)


def test_start_a_or_b_with_two_players_of_your_team_gives_the_comparison_and_the_pick_of_the_swap_read(settings,
                                                                                                    sources):
    # AT-16: Matthew Golden starts at WR by projection, 12.9 to the 6.8 of Konata Mumpfield. The read gives Golden 0.2,
    # so the pick is Mumpfield, with a pair of values for each fact and the side that wins each fact.
    jev = _routed({("Matthew Golden", "Konata Mumpfield"): 0.2})
    writer = Writer("Start Konata Mumpfield. His 6.8 projection trails, but the read of his matchup is better.")
    api = _api(settings, sources, jev=jev, writer=writer)
    route = _ask(api, "Start Golden or Mumpfield?")
    assert (route["route"], route["topic"]) == ("topic", "start_sit")
    chunks = _typed(api, "Start Golden or Mumpfield?")
    blocks = [c["data"] for c in chunks if c["type"] == "data-block"]
    first, last = blocks[0], blocks[-1]
    assert first["kind"] == "comparison" and first["topic"] == "start_sit" and first["team"] == BO_GIRDS["cpc"]
    assert [player["name"] for player in first["players"]] == ["M. Golden", "K. Mumpfield"]
    assert [player["projection"] for player in first["players"]] == [12.9, 6.8]
    assert first["pick"] == 1
    facts = {fact["key"]: fact for fact in first["facts"]}
    assert {"projection", "defense", "team_points", "margin", "snap_share", "target_share", "pass_share"} <= set(facts)
    assert facts["projection"]["values"] == [12.9, 6.8] and facts["projection"]["winner"] == 0
    assert all(len(fact["values"]) == 2 and fact["winner"] in (0, 1, None) for fact in first["facts"])
    # The pick comes from the Choice of the Swaps, over the same Fact sheets.
    [read] = [request for request in jev.requests if "players" in request.state]
    [question] = read.questions.values()
    assert "as the WR of Bo Girds" in question.instructions
    assert [option.split(",")[0] for option in question.options.values()] == ["Matthew Golden", "Konata Mumpfield"]
    assert set(read.state["players"]) == {"Matthew Golden", "Konata Mumpfield"}
    assert read.state["players"]["Konata Mumpfield"]["last_3_weeks"]["weeks"] == [7, 8, 9]
    # No fact is cited before the check. After it, the fact whose number the checked text gives carries the dot.
    assert not any(fact["cited"] for fact in first["facts"])
    assert [fact["key"] for fact in last["facts"] if fact["cited"]] == ["projection"]


def test_a_failed_read_of_the_two_players_gives_the_honest_miss(settings, sources):
    api = _api(settings, sources, jev=FakeJev(error=JevError("down")))
    chunks = _typed(api, "Start Golden or Mumpfield?")
    assert not any(c["type"] == "data-block" for c in chunks)
    assert [c["type"] for c in chunks if c["type"] == "data-miss"] == ["data-miss"]


def test_a_start_question_with_three_wrs_gives_the_lineup_block_for_the_wr_and_flex_slots(settings, sources):
    # AT-17: Zay Flowers and Matthew Golden start at WR, and Konata Mumpfield sits on the bench.
    jev = _routed()
    api = _api(settings, sources, jev=jev)
    assert _ask(api, "Should I start Flowers, Golden, or Mumpfield?")["topic"] == "start_sit"
    blocks = [c["data"] for c in _typed(api, "Should I start Flowers, Golden, or Mumpfield?") if c["type"] == "data-block"]
    block = blocks[-1]
    assert block["kind"] == "lineup"
    assert [row["slot"] for row in block["rows"]] == ["WR", "WR", "FLEX", "FLEX"]
    assert block["total"] == pytest.approx(sum(row["projection"] for row in block["rows"]), abs=0.05)


@pytest.mark.parametrize("question", ["Start Golden or Stefon Diggs?", "start golden or diggs"])
def test_a_start_question_with_a_player_off_your_roster_goes_to_a_free_answer(settings, sources, question):
    # AT-18: Stefon Diggs is on the roster of Lil Fridge, so the question is not about the lineup of Bo Girds.
    jev = _routed()
    route = _ask(_api(settings, sources, jev=jev), question)
    assert (route["route"], route["topic"]) == ("free", None)
