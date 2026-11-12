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
from league.jev_port import NoulQuestion
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
    """A stand-in for Claude: one sentence that names the first starter of the facts, and a count of its calls."""

    def __init__(self):
        self.calls = 0

    async def stream(self, messages: list[ModelMessage], info: AgentInfo) -> AsyncIterator[str]:
        self.calls += 1
        for word in ["Start", "your", "lineup", "by", "projection."]:
            yield word + " "


def _checks(key: str, question: NoulQuestion, state: dict) -> float:
    return 0.95


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
         **source_changes) -> TestClient:
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
                     jev=FakeJev(answer=_checks))
    app.state.personal_model = FunctionModel(stream_function=(writer or Writer()).stream)
    return TestClient(app)


def _chunks(response) -> list[dict]:
    lines = [line.removeprefix("data: ") for line in response.text.splitlines() if line.startswith("data: ")]
    return [json.loads(line) for line in lines if line != "[DONE]"]


def _block(api: TestClient, slug: str = "cpc", roster_id: int | None = None) -> dict:
    response = api.post(PERSONAL.format(slug=slug), json={"topic": "start_sit", "roster_id": roster_id or BO_GIRDS[slug]},
                        headers=HEADERS if slug == "cpc" else NORCAL_HEADERS)
    assert response.status_code == 200, response.text
    [block] = [c["data"] for c in _chunks(response) if c["type"] == "data-block"]
    return block


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
