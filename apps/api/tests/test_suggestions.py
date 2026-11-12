"""
Tests for the Suggestions of Your team, the head start of the top personal Suggestion, and the check of kept Answers.
They run at the route seam with FakeJev, a function model of Pydantic AI, and the recorded week 6 Sleeper data.
"""
import dataclasses
import json
import logging
import re
import shutil
from datetime import UTC, datetime
from pathlib import Path

import test_api
from fakes import FakeJev
from fastapi.testclient import TestClient
from test_api import CLIENT, HEADERS, _here
from test_personal_topics import LIL_FRIDGE, Checks, Fetches, Writer, _api, _ask, _chunks, _text
from test_start_sit import BEFORE_KICKOFF, RECORDED, espn_scoreboard, sleeper_scores

from analyzer.sell_facts import sheet_players
from analyzer.trade_jev import weak_starting_slots
from cornerstone_api.settings import RATE_LIMIT_PER_MINUTE
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


def _read_item() -> dict:
    return {"topic": "weak_spots", "roster_id": LIL_FRIDGE, "team": None, "key": "x"}


def test_three_questions_in_a_row_with_their_reads_get_no_429_at_the_default_limit(settings, sources):
    # H24: each question makes 2 reads and 2 counted requests. The 6 reads must not count toward the limit.
    _publish_topics(settings)
    api = _api(settings, sources, FakeJev(answer=Lifts().answer), Writer())
    for _ in range(3):
        assert _suggest(api).status_code == 200
        assert api.post(CURRENT, json={"answers": [_read_item()]}, headers=HEADERS).status_code == 200
        for _ in range(2):
            assert api.get("/teams", params={"season": 2026}, headers=HEADERS).status_code == 200


def test_the_31st_counted_request_in_a_minute_is_429_and_the_reads_still_answer(settings, sources):
    assert RATE_LIMIT_PER_MINUTE == 30
    _publish_topics(settings)
    api = _api(settings, sources, FakeJev(answer=Lifts().answer), Writer())
    for _ in range(30):
        assert api.get("/teams", params={"season": 2026}, headers=HEADERS).status_code == 200
    assert api.get("/teams", params={"season": 2026}, headers=HEADERS).status_code == 429
    assert _suggest(api).status_code == 200
    assert api.post(CURRENT, json={"answers": [_read_item()]}, headers=HEADERS).status_code == 200


def test_a_read_with_a_wrong_passphrase_is_401_even_past_the_limit(settings, sources):
    api = _api(settings, sources, FakeJev(answer=Lifts().answer), Writer())
    for _ in range(31):
        api.get("/teams", params={"season": 2026}, headers=HEADERS)
    wrong = {"X-League-Passphrase": "wrong"}
    assert api.post(SUGGESTIONS, json={"roster_id": LIL_FRIDGE, "order": WEDNESDAY}, headers=wrong).status_code == 401
    assert api.post(CURRENT, json={"answers": [_read_item()]}, headers=wrong).status_code == 401


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


# The order of each day on the site (topics.ts). Start or sit leads Thursday to Sunday, and sits third on Wednesday.
THURSDAY_ORDER = ["start_sit", "next_matchup", "trade_ideas", "sell_high", "weak_spots", "playoff_race", "week_recap",
                  "last_matchup", "power_rankings", "your_season", "leaders_trades", "waiver_targets", "stack_up",
                  "trade_check"]
SUNDAY_ORDER = ["start_sit", "next_matchup", "weak_spots", "playoff_race", "week_recap", "last_matchup",
                "power_rankings", "your_season", "leaders_trades", "waiver_targets", "stack_up", "sell_high",
                "trade_ideas", "trade_check"]
WEDNESDAY_ORDER = ["waiver_targets", "weak_spots", "start_sit", "power_rankings", "week_recap", "playoff_race",
                   "last_matchup", "next_matchup", "your_season", "leaders_trades", "stack_up", "sell_high",
                   "trade_ideas", "trade_check"]
MONDAY_ORDER = ["next_matchup", "playoff_race", "power_rankings", "week_recap", "last_matchup", "your_season",
                "leaders_trades", "waiver_targets", "stack_up", "weak_spots", "start_sit", "sell_high", "trade_ideas",
                "trade_check"]
TUESDAY_ORDER = ["week_recap", "last_matchup", "power_rankings", "playoff_race", "next_matchup", "your_season",
                 "leaders_trades", "waiver_targets", "stack_up", "weak_spots", "start_sit", "sell_high", "trade_ideas",
                 "trade_check"]
# The roster of cpc that starts Travis Etienne Jr. on IR in the recorded live week 10, and no Questionable starter.
ETIENNE_ON_IR = 1
# The roster of cpc that starts David Montgomery and Hunter Henry, both Questionable, in the recorded week 10.
TWO_Q = 4


class TwoWeeks:
    """The Sleeper fetch of a Suggestions test: the recorded week 6 for the first load, the live league that the cache
    keeps, and the recorded live week 10 for each later load, the live week of the Start or sit fact. The week 6
    fixture has the past weeks and the charts that a league snapshot reads. The week 10 recording has the kickoffs."""

    def __init__(self, fixture_raw_dir):
        self.weeks = [load_raw(fixture_raw_dir), load_raw(RECORDED / "cpc-week-10")]
        self.calls = 0

    def fetch(self, league_id: str):
        self.calls += 1
        return self.weeks[min(self.calls, 2) - 1], BEFORE_KICKOFF


def _live_week_api(settings, sources, fixture_raw_dir, jev: FakeJev, now=BEFORE_KICKOFF) -> TestClient:
    """An app whose Start or sit fact reads the recorded live week 10 of cpc: the Sleeper week of Thursday 2026-11-12
    and its kickoffs."""
    live = dataclasses.replace(sources, fetch_sleeper=TwoWeeks(fixture_raw_dir).fetch,
                               clock=lambda: now.astimezone(CLIENT.tz), fetch_sleeper_scores=sleeper_scores,
                               fetch_espn_scoreboard=espn_scoreboard)
    _publish_topics(settings)
    return _api(settings, live, jev, Writer())


def test_start_or_sit_leads_thursday_with_the_next_kickoff_as_its_fact(settings, sources, fixture_raw_dir):
    # AT-13 and AT-15: Bo Girds starts no player who cannot play and no Q, so the fact is the next kickoff of his lineup.
    api = _live_week_api(settings, sources, fixture_raw_dir, FakeJev(answer=Lifts().answer))
    body = _suggest(api, order=THURSDAY_ORDER, roster_id=BO_GIRDS).json()
    assert body["picks"][0] == "start_sit"
    assert body["facts"]["start_sit"] == "Next kickoff Sun 1:00 PM"


def test_start_or_sit_leads_sunday_before_the_early_games(settings, sources, fixture_raw_dir):
    # AT-13: Sunday 2026-11-15 at noon in New York, before the 1:00 PM games of the lineup of Bo Girds.
    sunday = datetime(2026, 11, 15, 17, 0, tzinfo=UTC)
    api = _live_week_api(settings, sources, fixture_raw_dir, FakeJev(answer=Lifts().answer), now=sunday)
    body = _suggest(api, order=SUNDAY_ORDER, roster_id=BO_GIRDS).json()
    assert body["picks"][0] == "start_sit"
    assert body["facts"]["start_sit"] == "Next kickoff Sun 1:00 PM"


def test_start_or_sit_is_third_on_wednesday_after_the_waiver_targets(settings, sources, fixture_raw_dir):
    # AT-13: the claims come first on Wednesday.
    wednesday = datetime(2026, 11, 11, 17, 0, tzinfo=UTC)
    api = _live_week_api(settings, sources, fixture_raw_dir, FakeJev(answer=Lifts().answer), now=wednesday)
    body = _suggest(api, order=WEDNESDAY_ORDER, roster_id=BO_GIRDS).json()
    assert body["picks"] == ["waiver_targets", "weak_spots", "start_sit"]


def test_monday_keeps_the_order_of_today_with_start_or_sit_below_the_top_three(settings, sources, fixture_raw_dir):
    # AT-13: Monday does not change, so the next matchup, the playoff race, and the power rankings lead.
    monday = datetime(2026, 11, 16, 17, 0, tzinfo=UTC)
    api = _live_week_api(settings, sources, fixture_raw_dir, FakeJev(answer=Lifts().answer), now=monday)
    body = _suggest(api, order=MONDAY_ORDER, roster_id=BO_GIRDS).json()
    assert body["picks"] == ["next_matchup", "playoff_race", "power_rankings"]


def test_a_starter_on_ir_lifts_start_or_sit_first_on_a_tuesday(settings, sources, fixture_raw_dir):
    # AT-14: Etienne starts on IR, so the lift reads "1 can't play" and Start or sit leads the recap day.
    tuesday = datetime(2026, 11, 10, 17, 0, tzinfo=UTC)
    jev = FakeJev(answer=Lifts({"start_sit": 0.9}).answer)
    api = _live_week_api(settings, sources, fixture_raw_dir, jev, now=tuesday)
    body = _suggest(api, order=TUESDAY_ORDER, roster_id=ETIENNE_ON_IR).json()
    assert body["picks"][0] == "start_sit" and body["urgent"] == ["start_sit"]
    [lift] = [r for r in jev.requests if "lift_start_sit" in r.questions]
    assert lift.state["topics"]["start_sit"]["name"] == "Start or sit"
    assert lift.state["topics"]["start_sit"]["fact"] == body["facts"]["start_sit"] == "1 can't play"


def test_the_fact_counts_the_q_starters_and_the_suggestions_ask_jev_nothing_for_it(settings, sources, fixture_raw_dir):
    # AT-15: Montgomery and Hunter Henry start as Questionable. The fact comes from code, so Jev gets no question of it.
    jev = FakeJev(answer=Lifts().answer)
    api = _live_week_api(settings, sources, fixture_raw_dir, jev)
    body = _suggest(api, order=THURSDAY_ORDER, roster_id=TWO_Q).json()
    assert body["facts"]["start_sit"] == "2 Q"
    assert "start_sit" not in body["kickoffs"]
    asked = {key for request in jev.requests for key in request.questions}
    assert asked == {*(f"lift_{topic}" for topic in body["facts"]), SELL_CHOICE, SELL_NOUL}


def test_the_kickoff_fact_carries_the_kickoff_in_epoch_ms_for_the_browser(settings, sources, fixture_raw_dir):
    # The site shows the kickoff in the time zone of the browser: Sunday 2026-11-15 at 18:00 UTC.
    api = _live_week_api(settings, sources, fixture_raw_dir, FakeJev(answer=Lifts().answer))
    body = _suggest(api, order=THURSDAY_ORDER, roster_id=BO_GIRDS).json()
    assert body["kickoffs"] == {"start_sit": int(datetime(2026, 11, 15, 18, 0, tzinfo=UTC).timestamp() * 1000)}


def test_an_empty_slot_counts_as_a_starter_who_cannot_play(settings, sources, fixture_raw_dir):
    # Roster 11 of cpc leaves one starting slot empty in the recorded week 10.
    api = _live_week_api(settings, sources, fixture_raw_dir, FakeJev(answer=Lifts().answer))
    assert _suggest(api, order=THURSDAY_ORDER, roster_id=11).json()["facts"]["start_sit"] == "1 can't play"


def test_a_live_week_that_does_not_load_drops_only_the_start_or_sit_fact(settings, sources):
    # The test sources give no kickoffs, as a down source does, so the other Suggestions still show.
    _publish_topics(settings)
    api = _api(settings, sources, FakeJev(answer=Lifts().answer), Writer())
    response = _suggest(api, order=THURSDAY_ORDER)
    assert response.status_code == 200
    body = response.json()
    assert "start_sit" not in body["facts"] and body["picks"]
