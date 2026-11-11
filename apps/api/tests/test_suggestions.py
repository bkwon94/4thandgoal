"""
Tests for the Suggestions of Your team, the head start of the top personal Suggestion, and the check of kept Answers.
They run at the route seam with FakeJev, a function model of Pydantic AI, and the recorded week 6 Sleeper data.
"""
import dataclasses
import json
import logging
import re
import shutil
from pathlib import Path

import test_api
from fakes import FakeJev
from fastapi.testclient import TestClient
from test_api import HEADERS, _here
from test_personal_topics import LIL_FRIDGE, Checks, Fetches, Writer, _api, _ask, _chunks, _text

from analyzer.sell_facts import sheet_players
from analyzer.trade_jev import weak_starting_slots
from cornerstone_api.suggestion_wording import SELL_CHOICE, SELL_NOUL
from league.jev_port import ChoiceQuestion, JevError, NoulQuestion
from league.provider.sleeper import load_raw

repo = test_api.repo
settings = test_api.settings
sources = test_api.sources

# Bo Girds starts no weak player in the recorded week 6 data.
BO_GIRDS = 6
SUGGESTIONS = "/clients/cpc/suggestions"
CURRENT = "/clients/cpc/personal/current"
# The order of Wednesday on the site: the waivers lead, then the weak spots (topics.ts).
WEDNESDAY = ["waiver_targets", "weak_spots", "power_rankings", "week_recap", "playoff_race", "last_matchup",
             "next_matchup", "your_season", "leaders_trades", "stack_up", "sell_high", "trade_ideas", "trade_check"]
# The order of Tuesday on the site: the recap leads.
TUESDAY = ["week_recap", "last_matchup", "power_rankings", "playoff_race", "next_matchup", "your_season",
           "leaders_trades", "waiver_targets", "stack_up", "weak_spots", "sell_high", "trade_ideas", "trade_check"]
# The real Topics file of the latest published week of cpc.
PUBLISHED_TOPICS = Path(__file__).resolve().parents[3] / "clients" / "cpc" / "published" / "2026" / "week-08" / "topics.json"


def _publish_topics(settings) -> dict:
    folder = settings.repo / "published" / "2026" / "week-06"
    folder.mkdir(parents=True, exist_ok=True)
    shutil.copy(PUBLISHED_TOPICS, folder / "topics.json")
    return json.loads(PUBLISHED_TOPICS.read_text())


class Lifts:
    """The Jev answers of the lift Nouls by Topic, and a pass of each claim check."""

    def __init__(self, urgent: dict[str, float] | None = None):
        self.urgent = urgent or {}

    def answer(self, key: str, question: NoulQuestion, state: dict) -> float:
        if key.startswith("lift_"):
            return self.urgent.get(key.removeprefix("lift_"), 0.1)
        return 0.95


def _suggest(api: TestClient, order: list[str] = WEDNESDAY, opened: dict | None = None, roster_id: int = LIL_FRIDGE):
    return api.post(SUGGESTIONS, json={"roster_id": roster_id, "order": order, "opened": opened or {}}, headers=HEADERS)


def test_a_lift_above_the_cutoff_puts_its_topic_first_above_the_order_of_the_day(settings, sources):
    # AT-6: Jev reads the playoff race of Lil Fridge as urgent, so it leads Wednesday, above the waivers.
    _publish_topics(settings)
    writer = Writer()
    jev = FakeJev(answer=Lifts({"playoff_race": 0.85}).answer)
    api = _api(settings, sources, jev, writer)
    body = _suggest(api).json()
    assert body["picks"][0] == "playoff_race"
    assert body["urgent"] == ["playoff_race"]
    assert body["picks"][1:] == ["waiver_targets", "weak_spots"]
    # One Noul per Topic with a fact, each over the same fact that its Suggestion shows.
    assert set(body["lifts"]) == set(body["facts"])
    [request] = [r for r in jev.requests if any(k.startswith("lift_") for k in r.questions)]
    assert request.state["topics"]["playoff_race"]["fact"] == body["facts"]["playoff_race"] == "86% playoff odds"
    assert body["jev"]["nouls"]["lift_playoff_race"] == 0.85


def test_an_unsure_lift_is_no_lift_and_the_order_of_the_day_holds(settings, sources):
    # The cutoff is the hard rule of the spec: 0.7 reads as unsure, so the Topic stays in its place.
    _publish_topics(settings)
    api = _api(settings, sources, FakeJev(answer=Lifts({"playoff_race": 0.7}).answer), Writer())
    body = _suggest(api, order=TUESDAY).json()
    assert body["urgent"] == []
    assert body["picks"] == ["week_recap", "last_matchup", "power_rankings"]


def test_the_api_serves_the_live_facts_of_the_personal_topics_and_skips_each_opened_topic(settings, sources):
    _publish_topics(settings)
    api = _api(settings, sources, FakeJev(answer=Lifts().answer), Writer())
    first = _suggest(api).json()
    assert {"weak_spots", "stack_up", "waiver_targets"} <= set(first["facts"])
    # A Topic opened at the same fact drops off.
    opened = {"waiver_targets": first["facts"]["waiver_targets"]}
    body = _suggest(api, opened=opened).json()
    assert body["picks"] == ["weak_spots", "power_rankings", "week_recap"]


def _sure_on(name: str | None):
    """A Choice of sell high that puts 0.9 on the option of `name`, or spreads its weight when `name` is None."""

    def choose(key: str, question: ChoiceQuestion, state: dict) -> dict[str, float]:
        if name is None:
            return {option: 1 / len(question.options) for option in question.options}
        return {option: (0.9 if state["players"][option]["name"] == name else 0.1 / (len(question.options) - 1))
                for option in question.options}

    return choose


def _sell_request(jev: FakeJev):
    [request] = [r for r in jev.requests if SELL_CHOICE in r.questions]
    return request


def test_trade_ideas_has_the_first_weak_starter_that_the_finder_fills_as_its_fact(settings, sources):
    # AT-26: the fact names a weak starting slot that /find reads, so the offers fill the slot the fact names.
    _publish_topics(settings)
    api = _api(settings, sources, FakeJev(answer=Lifts().answer), Writer())
    facts = _suggest(api).json()["facts"]
    snapshot = _here(sources, settings).snapshot(2026)
    first = weak_starting_slots(snapshot, LIL_FRIDGE)[0]
    assert facts["trade_ideas"] == f"Offers for your {first}" == "Offers for your WR2: Stefon Diggs (WR28)"


def test_a_team_with_no_weak_starter_has_no_trade_ideas_fact(settings, sources):
    # Bo Girds starts no player past the weak rank in the recorded week, so the Finder has no slot to fill.
    _publish_topics(settings)
    api = _api(settings, sources, FakeJev(answer=Lifts().answer), Writer())
    body = _suggest(api, roster_id=BO_GIRDS).json()
    assert "trade_ideas" not in body["facts"] and "trade_ideas" not in body["picks"]


def test_the_trade_check_has_no_weekly_fact_so_it_never_shows_as_a_suggestion(settings, sources):
    _publish_topics(settings)
    api = _api(settings, sources, FakeJev(answer=Lifts({"trade_check": 0.99}).answer), Writer())
    body = _suggest(api).json()
    assert "trade_check" not in body["facts"] and "trade_check" not in body["picks"]


def test_sell_high_asks_one_choice_over_the_players_of_your_team_with_their_facts_side_by_side(settings, sources):
    _publish_topics(settings)
    jev = FakeJev(answer=Lifts().answer, choose=_sure_on(None))
    api = _api(settings, sources, jev, Writer())
    _suggest(api)
    request = _sell_request(jev)
    snapshot = _here(sources, settings).snapshot(2026)
    names = {snapshot.players[pid].name for pid in sheet_players(snapshot, LIL_FRIDGE)}
    players = request.state["players"]
    assert {player["name"] for player in players.values()} == names
    assert set(request.questions[SELL_CHOICE].options) == set(players)
    # Each player carries his facts of the sell sheet: the trend and the schedule among them.
    for player in players.values():
        assert any("points per game, against" in text for text in player["facts"])
        assert any("schedule ahead" in text for text in player["facts"])


def test_a_sure_sell_high_pick_names_the_player_with_his_recent_run_and_his_season(settings, sources):
    _publish_topics(settings)
    snapshot = _here(sources, settings).snapshot(2026)
    name = snapshot.players[sheet_players(snapshot, LIL_FRIDGE)[0]].name
    jev = FakeJev(answer=Lifts().answer, choose=_sure_on(name))
    api = _api(settings, sources, jev, Writer())
    fact = _suggest(api).json()["facts"]["sell_high"]
    match = re.fullmatch(rf"{re.escape(name)}: (\d+\.\d) a game over 4 weeks, (\d+\.\d) for the season", fact)
    assert match is not None, fact
    # The numbers are the numbers of his trend fact, which Jev read.
    [player] = [p for p in _sell_request(jev).state["players"].values() if p["name"] == name]
    [trend] = [text for text in player["facts"] if "points per game, against" in text]
    assert f"scored {match[1]} points per game, against {match[2]} over the season" in trend


def _clear_sell(clear: float, lifts: dict[str, float] | None = None):
    """The Jev answers of the lift Nouls, with `clear` as the answer of the sell high Noul."""
    lift = Lifts(lifts).answer

    def answer(key: str, question: NoulQuestion, state: dict) -> float:
        return clear if key == SELL_NOUL else lift(key, question, state)

    return answer


def _spread_on(name: str):
    """A Choice of sell high that puts 0.53 on the option of `name` and spreads the rest, as a live Choice does over
    about 15 players."""

    def choose(key: str, question: ChoiceQuestion, state: dict) -> dict[str, float]:
        return {option: (0.53 if state["players"][option]["name"] == name else 0.47 / (len(question.options) - 1))
                for option in question.options}

    return choose


def test_sell_high_asks_its_noul_in_the_same_request_as_its_choice(settings, sources):
    _publish_topics(settings)
    jev = FakeJev(answer=Lifts().answer, choose=_sure_on(None))
    _suggest(_api(settings, sources, jev, Writer()))
    request = _sell_request(jev)
    assert set(request.questions) == {SELL_CHOICE, SELL_NOUL}
    assert isinstance(request.questions[SELL_NOUL], NoulQuestion)


def test_a_clear_sell_high_names_the_top_option_of_a_spread_choice(settings, sources):
    # F1: the Choice spreads its weight over the roster, so its top is seldom above 0.7. The Noul carries the cutoff.
    _publish_topics(settings)
    snapshot = _here(sources, settings).snapshot(2026)
    name = snapshot.players[sheet_players(snapshot, LIL_FRIDGE)[0]].name
    jev = FakeJev(answer=_clear_sell(0.85), choose=_spread_on(name))
    body = _suggest(_api(settings, sources, jev, Writer())).json()
    assert body["facts"]["sell_high"].startswith(f"{name}: ")
    assert body["jev"]["nouls"][SELL_NOUL] == 0.85


def test_an_unsure_sell_high_noul_gives_no_fact_and_no_suggestion(settings, sources):
    # The cutoff is the hard rule: with the Noul at or below 0.7, sell high has no fact, even with a sure Choice.
    _publish_topics(settings)
    snapshot = _here(sources, settings).snapshot(2026)
    name = snapshot.players[sheet_players(snapshot, LIL_FRIDGE)[0]].name
    jev = FakeJev(answer=_clear_sell(0.7, {"sell_high": 0.99}), choose=_sure_on(name))
    body = _suggest(_api(settings, sources, jev, Writer())).json()
    assert "sell_high" not in body["facts"] and "sell_high" not in body["lifts"]
    assert "sell_high" not in body["picks"]


def test_a_lift_of_a_trade_topic_puts_it_first_with_the_same_cutoff(settings, sources):
    _publish_topics(settings)
    snapshot = _here(sources, settings).snapshot(2026)
    name = snapshot.players[sheet_players(snapshot, LIL_FRIDGE)[0]].name
    jev = FakeJev(answer=Lifts({"sell_high": 0.9, "trade_ideas": 0.8}).answer, choose=_sure_on(name))
    body = _suggest(_api(settings, sources, jev, Writer())).json()
    assert body["urgent"] == ["sell_high", "trade_ideas"]
    assert body["picks"][:2] == ["sell_high", "trade_ideas"]
    [lift] = [r for r in jev.requests if any(k.startswith("lift_") for k in r.questions)]
    assert lift.state["topics"]["sell_high"]["fact"] == body["facts"]["sell_high"]


def test_a_failed_sell_high_choice_is_an_error_never_a_no(settings, sources):
    _publish_topics(settings)

    def choose(key: str, question: ChoiceQuestion, state: dict) -> dict[str, float]:
        raise JevError("down")

    api = _api(settings, sources, FakeJev(answer=Lifts().answer, choose=choose), Writer())
    assert _suggest(api).status_code == 503


def test_the_head_start_builds_the_top_personal_suggestion_on_open_and_the_tap_gets_it_kept(settings, sources,
                                                                                          caplog):
    # AT-8: the top Suggestion of Wednesday is waiver targets, a personal Topic, so it builds on open. The tap then
    # gets the kept Answer at once with no Claude call.
    _publish_topics(settings)
    writer = Writer()
    api = _api(settings, sources, FakeJev(answer=Lifts().answer), writer)
    order = ["weak_spots", *(key for key in WEDNESDAY if key != "weak_spots")]
    with caplog.at_level(logging.INFO, logger="cornerstone_api"):
        body = _suggest(api, order=order).json()
    assert body["picks"][0] == "weak_spots" and body["head_start"] == "weak_spots"
    assert writer.calls == 1
    assert "head start builds the personal Topic weak_spots on open" in caplog.text
    caps, now = api.app.state.askers["cpc"].caps, api.app.state.askers["cpc"].clock()
    # The head start costs the league and counts toward no team.
    assert caps.month_usd(now) > 0 and caps.answers_today(LIL_FRIDGE, now) == 0
    with caplog.at_level(logging.INFO, logger="cornerstone_api"):
        tap = _chunks(_ask(api, "weak_spots"))
    assert writer.calls == 1
    assert "came from the store" in caplog.text
    assert _text(tap) and [c["data"]["state"] for c in tap if c["type"] == "data-check"] == ["checked"]
    # A second open finds the kept Answer, so it builds nothing.
    _suggest(api, order=order)
    assert writer.calls == 1


def test_a_league_topic_at_the_top_builds_nothing_on_open(settings, sources):
    _publish_topics(settings)
    writer = Writer()
    api = _api(settings, sources, FakeJev(answer=Lifts().answer), writer)
    body = _suggest(api, order=TUESDAY).json()
    assert body["head_start"] is None
    assert writer.calls == 0


def test_past_the_league_cap_the_head_start_builds_nothing(settings, sources):
    _publish_topics(settings)
    writer = Writer()
    api = _api(settings, sources, FakeJev(answer=Lifts().answer), writer)
    caps, now = api.app.state.askers["cpc"].caps, api.app.state.askers["cpc"].clock()
    caps.record(None, 25.00, now, counts=False)
    body = _suggest(api).json()
    assert body["picks"][0] == "waiver_targets" and body["head_start"] is None
    assert writer.calls == 0


def test_a_failed_lift_call_is_an_error_never_a_no(settings, sources):
    _publish_topics(settings)
    api = _api(settings, sources, FakeJev(error=JevError("down")), Writer())
    assert _suggest(api).status_code == 503


def test_an_unknown_topic_in_the_order_is_422(settings, sources):
    api = _api(settings, sources, FakeJev(answer=Lifts().answer), Writer())
    assert _suggest(api, order=["week_recap", "write_me_a_poem"]).status_code == 422
    assert _suggest(api, roster_id=99).status_code == 422


def test_the_suggestions_need_the_passphrase(settings, sources):
    api = _api(settings, sources, FakeJev(answer=Lifts().answer), Writer())
    assert api.post(SUGGESTIONS, json={"roster_id": LIL_FRIDGE, "order": WEDNESDAY}).status_code == 401


def _key(chunks: list[dict]) -> str:
    [key] = [c["data"]["key"] for c in chunks if c["type"] == "data-key"]
    return key


def test_the_key_check_reads_a_kept_answer_as_current_until_the_roster_changes(settings, sources, fixture_raw_dir,
                                                                               tmp_path):
    # AT-34: the weak spots Answer of Lil Fridge is current. Then the roster gains one player, so it is stale, with the
    # time that the API kept it.
    writer = Writer()
    api = _api(settings, sources, FakeJev(answer=Checks([True]).answer), writer)
    key = _key(_chunks(_ask(api, "weak_spots")))
    item = {"topic": "weak_spots", "roster_id": LIL_FRIDGE, "team": None, "key": key}
    [now] = api.post(CURRENT, json={"answers": [item]}, headers=HEADERS).json()["answers"]
    assert now["key"] == key and now["current"] is True
    raw = tmp_path / "raw-after-an-add"
    shutil.copytree(fixture_raw_dir, raw)
    rosters = json.loads((raw / "rosters.json").read_text())
    mine = next(roster for roster in rosters if roster["roster_id"] == LIL_FRIDGE)
    other = next(roster for roster in rosters if roster["roster_id"] != LIL_FRIDGE)
    mine["players"] = [*mine["players"], other["players"][0]]
    (raw / "rosters.json").write_text(json.dumps(rosters))
    changed = dataclasses.replace(sources, fetch_sleeper=lambda league_id: (load_raw(raw), test_api.FETCHED))
    api = _api(settings, changed, FakeJev(answer=Checks([True]).answer), writer)
    [stale] = api.post(CURRENT, json={"answers": [item]}, headers=HEADERS).json()["answers"]
    assert stale["key"] == key and stale["current"] is False
    assert stale["kept_at"] is not None and stale["kept_at"].startswith("2026-")
    # The check costs nothing: no Claude call and no Jev call.
    assert writer.calls == 1


def test_the_key_check_needs_the_passphrase_and_a_known_team(settings, sources):
    api = _api(settings, sources, FakeJev(answer=Checks([True]).answer), Writer())
    item = {"topic": "weak_spots", "roster_id": LIL_FRIDGE, "team": None, "key": "x"}
    assert api.post(CURRENT, json={"answers": [item]}).status_code == 401
    assert api.post(CURRENT, json={"answers": [{**item, "roster_id": 99}]}, headers=HEADERS).status_code == 422


def test_the_tap_after_the_open_reads_the_league_of_the_open_and_no_sleeper_data(settings, sources, fixture_raw_dir):
    # AT-8: the open loads the league once, the head start builds on it, and the tap gets the kept Answer from it.
    _publish_topics(settings)
    fetches = Fetches(fixture_raw_dir)
    writer = Writer()
    api = _api(settings, dataclasses.replace(sources, fetch_sleeper=fetches.fetch), FakeJev(answer=Lifts().answer),
               writer)
    order = ["weak_spots", *(key for key in WEDNESDAY if key != "weak_spots")]
    assert _suggest(api, order=order).json()["head_start"] == "weak_spots"
    loads = fetches.calls
    tap = _chunks(_ask(api, "weak_spots"))
    assert fetches.calls == loads
    assert writer.calls == 1
    assert _text(tap) and not any(c["type"].startswith("tool-") for c in tap)
