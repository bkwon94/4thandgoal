"""
Tests for the Week line of each side: the count of the players who play in the trade week and the next week, the
opponent of each player the side gets, each bye, and each player who is out. They grade real trades at the document seam.
"""
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest
from cpc import cpc_client

from analyzer.advisor import TextGuard, inner_word_failures
from analyzer.cache import cache_key
from analyzer.trade import ProposedTrade, TradeSide
from analyzer.trade_facts import trade_fact_sheet
from analyzer.week_line import week_lines
from league.paths import returns_path
from league.provider.sleeper import load_raw
from league.slow_sources import load_slow_sources
from league.snapshot import build_snapshot, load_out_for_season, load_returns

CLIENT = cpc_client()
SAVED = CLIENT.folder / "data" / "2026"
ET = ZoneInfo("America/New_York")
# The nflverse fixture holds the real 2026 schedule, so the saved week 8 data reads the real games of weeks 9 and 10.
NFLVERSE = Path(__file__).parent / "fixtures" / "nflverse"
# A Thursday and a Tuesday of the week 9 trade window, in US Eastern time.
THURSDAY = datetime(2026, 11, 5, 12, 0, tzinfo=ET)
TUESDAY = datetime(2026, 11, 3, 12, 0, tzinfo=ET)

# Trade A: roster 10 gives Omar Cooper Jr. (NYJ) to roster 6 for Parker Washington (JAX). Roster 10 asks.
COOPER, WASHINGTON = "13276", "9487"


def _snapshot(now: datetime):
    returns_file = returns_path(CLIENT.nfl_dir, 2026)
    slow = load_slow_sources(NFLVERSE, 2026, 9, SAVED / "history")
    return build_snapshot(load_raw(SAVED / "week-08" / "raw"), SAVED / "history", None, slow, trade_week=9,
                          returns=load_returns(returns_file), out_for_season=load_out_for_season(returns_file),
                          now=now, client=CLIENT)


@pytest.fixture(scope="module")
def thursday():
    return _snapshot(THURSDAY)


def _trade(first: int, first_gives: list[str], second: int, second_gives: list[str]) -> ProposedTrade:
    return ProposedTrade(season=2026, asker=first, sides=(
        TradeSide(roster_id=first, gives=[{"player_id": pid, "to": second} for pid in first_gives]),
        TradeSide(roster_id=second, gives=[{"player_id": pid, "to": first} for pid in second_gives])))


TRADE_A = _trade(10, [COOPER], 6, [WASHINGTON])


def _lines(trade: ProposedTrade, snapshot, roster_id: int) -> list[dict]:
    return [line.model_dump() for line in week_lines(trade, snapshot)[roster_id]]


def test_each_side_has_a_week_line_for_the_trade_week_and_the_next_week_only(thursday):
    for roster_id in (10, 6):
        assert [line["week"] for line in _lines(TRADE_A, thursday, roster_id)] == [9, 10]


def _texts(trade: ProposedTrade, snapshot, roster_id: int) -> list[str]:
    return [line["text"] for line in _lines(trade, snapshot, roster_id)]


def test_trade_a_gives_the_count_the_opponent_the_byes_and_the_outs_of_each_week(thursday):
    # Worked from the saved week 8 data and the 2026 schedule. Roster 10 has Nacua (WR2) and Cooper (WR27) in the top
    # 36 by the grade's Position rank, and gets Washington (WR20) for Cooper. Egbuka (TB) and Samuel (SF) are listed
    # Out. PIT, the team of Bernard, has its bye in week 9, and TB has its bye in week 10. JAX plays at BAL, 9th in
    # points allowed to WRs, then at TEN, the most. Out counts in week 9 only, so Egbuka names only his bye in week 10.
    assert _texts(TRADE_A, thursday, 10) == [
        ("Week 9: WRs in the top 36 who play stay at 2. Washington plays at BAL, 9th most points to WRs. "
         "Bernard has a bye. Egbuka and Samuel are listed Out."),
        ("Week 10: WRs in the top 36 who play stay at 2. Washington plays at TEN, the most points to WRs. "
         "Egbuka has a bye."),
    ]


def test_trade_a_names_the_home_game_of_the_player_the_other_side_gets(thursday):
    # Roster 6 has Flowers (WR9), Golden (WR12), and Washington (WR20) in the top 36, and gets Cooper (WR27). No WR of
    # roster 6 has a bye or is out in week 9 or 10. NYJ plays at KC, then BUF at home.
    texts = _texts(TRADE_A, thursday, 6)
    assert texts[0].startswith("Week 9: WRs in the top 36 who play stay at 3. Cooper plays at KC, ")
    assert texts[1].startswith("Week 10: WRs in the top 36 who play stay at 3. Cooper plays BUF at home, ")
    # KC is 31st of 32 in points allowed to WRs, so it reads from the other end. BUF is 3rd.
    allowed = thursday.points_allowed
    assert (allowed["KC"]["WR"].rank, allowed["BUF"]["WR"].rank, len(allowed)) == (31, 3, 32)
    assert texts[0].endswith("at KC, 2nd fewest points to WRs.")
    assert texts[1].endswith("BUF at home, 3rd most points to WRs.")


def test_a_grade_on_a_tuesday_says_listed_out_last_week():
    texts = _texts(TRADE_A, _snapshot(TUESDAY), 10)
    assert texts[0].endswith("Egbuka and Samuel were listed Out last week.")
    assert "Out" not in texts[1]


NACUA = "9493"


def _nacua(snapshot, status: str | None = None, back: int | None = None, season: bool = False):
    """The snapshot with Puka Nacua of roster 10 given a status, a return week on file, or out for the season."""
    player = snapshot.players[NACUA].model_copy(update={"injury_status": status})
    returns = {**snapshot.returns, NACUA: back} if back is not None else snapshot.returns
    out = snapshot.out_for_season | {NACUA} if season else snapshot.out_for_season
    return snapshot.model_copy(update={"players": {**snapshot.players, NACUA: player}, "returns": returns,
                                       "out_for_season": out})


@pytest.mark.parametrize("change, week_9, week_10", [
    # IR, PUP, NA, and Sus count in both weeks. Nacua and Cooper are in the top 36 before, and Nacua and Washington
    # after, so with Nacua out the count stays at 1.
    ({"status": "IR"}, "Nacua is on IR.", "Nacua is on IR."),
    ({"status": "PUP"}, "Nacua is on the PUP list.", "Nacua is on the PUP list."),
    ({"status": "NA"}, "Nacua is not active.", "Nacua is not active."),
    ({"status": "Sus"}, "Nacua is suspended.", "Nacua is suspended."),
    # Out for the season and a return week after the next week count in both weeks.
    ({"season": True}, "Nacua is out for the season.", "Nacua is out for the season."),
    ({"status": "Out", "back": 11}, "Nacua is out until week 11.", "Nacua is out until week 11."),
])
def test_a_long_absence_counts_in_both_weeks(thursday, change, week_9, week_10):
    texts = _texts(TRADE_A, _nacua(thursday, **change), 10)
    assert "WRs in the top 36 who play stay at 1." in texts[0] and week_9 in texts[0]
    assert "WRs in the top 36 who play stay at 1." in texts[1] and week_10 in texts[1]


def test_out_and_a_return_in_the_next_week_count_in_the_trade_week_only(thursday):
    for snapshot, words in ((_nacua(thursday, "Out"), "Egbuka, Samuel and Nacua are listed Out."),
                            (_nacua(thursday, back=10), "Nacua is out until week 10.")):
        texts = _texts(TRADE_A, snapshot, 10)
        assert "stay at 1." in texts[0] and words in texts[0]
        assert "stay at 2." in texts[1] and "Nacua" not in texts[1]


@pytest.mark.parametrize("status", ["Questionable", "Doubtful"])
def test_questionable_and_doubtful_never_count(thursday, status):
    texts = _texts(TRADE_A, _nacua(thursday, status), 10)
    assert all("stay at 2." in text and "Nacua" not in text for text in texts)


def test_a_three_side_trade_gives_week_lines_for_every_side(thursday):
    # AT-5: roster 4 gives Rome Odunze to roster 12, roster 12 gives Garrett Wilson to roster 7, and roster 7 gives
    # Ryan Flournoy to roster 4.
    trade = ProposedTrade(season=2026, asker=4, sides=(
        TradeSide(roster_id=4, gives=[{"player_id": "11620", "to": 12}]),
        TradeSide(roster_id=12, gives=[{"player_id": "8146", "to": 7}]),
        TradeSide(roster_id=7, gives=[{"player_id": "11783", "to": 4}])))
    lines = week_lines(trade, thursday)
    assert list(lines) == [4, 12, 7]
    for side_lines in lines.values():
        assert [line.week for line in side_lines] == [9, 10]
        assert side_lines[0].text.startswith("Week 9: WRs in the top 36 who play ")


def test_the_fact_sheet_holds_one_week_line_fact_per_side_with_the_text_of_its_two_lines(thursday):
    facts = trade_fact_sheet(TRADE_A, thursday)
    assert [fid for fid in facts if "week_line" in fid] == ["10.week_line", "6.week_line"]
    for roster_id in (10, 6):
        assert facts[f"{roster_id}.week_line"].text == " ".join(_texts(TRADE_A, thursday, roster_id))


def test_the_prose_checks_accept_the_numbers_and_the_names_of_the_week_line(thursday):
    facts = trade_fact_sheet(TRADE_A, thursday)
    guard = TextGuard(TRADE_A, thursday, facts)
    bullets = {10: ["Washington plays at BAL in week 9, 9th most points to WRs.",
                    "The WRs in the top 36 who play stay at 2 in weeks 9 and 10.",
                    "Washington plays at TEN in week 10, the most points to WRs."],
               6: ["Cooper plays BUF at home in week 10.", "The WRs in the top 36 who play stay at 3.",
                   "Cooper plays at KC in week 9, 2nd fewest points to WRs."]}
    failures = [failure for roster_id, texts in bullets.items() for text in texts
                for failure in guard.text_failures("bullet", text, [f"{roster_id}.week_line"])]
    assert failures == []


def test_no_week_line_holds_an_inner_word(thursday):
    texts = [text for roster_id in (10, 6) for text in _texts(TRADE_A, thursday, roster_id)]
    assert [(text, failure) for text in texts if (failure := inner_word_failures("week line", text))] == []


def test_with_no_schedule_the_week_line_says_so_and_names_no_bye_or_opponent(thursday):
    texts = _texts(TRADE_A, thursday.model_copy(update={"schedules": None}), 10)
    assert texts[0] == ("Week 9: WRs in the top 36 who play stay at 2. Egbuka and Samuel are listed Out. "
                        "No NFL schedule is on file, so no bye or opponent shows.")


# The newest real depth chart, of 2026-11-03T07:02:07Z, cut to QB, RB, WR, and TE, with the id map rows of its players.
# The test copies it over the nflverse fixture, so the rest of the slow sources stay the same.
NEWEST_CHART = Path(__file__).parent / "fixtures" / "nflverse-2026-11-03"
CHART_DT = datetime(2026, 11, 3, 7, 2, 7, tzinfo=ZoneInfo("UTC"))
# A grade inside the age limit of the chart, and one more than 48 hours after its dt (AT-16).
FRESH = datetime(2026, 11, 4, 12, 0, tzinfo=ET)
STALE = datetime(2026, 11, 5, 8, 0, tzinfo=ZoneInfo("UTC"))

# Wan'Dale Robinson of roster 2 is TEN WR2, behind Carnell Tate of roster 8, who is Out.
# Chris Godwin Jr. of roster 8 is TB WR2, behind Emeka Egbuka of roster 10, who is Out.
# Makai Lemon of roster 8 is PHI WR3, behind Dontayvion Wicks, who is Out and on no roster.
ROBINSON, TATE, GODWIN, LEMON, WICKS = "8126", "13279", "4037", "13294", "9486"
SAMUEL = "5872"
# Roster 8 gives Tate to roster 2 for Robinson. TEN has its bye in week 9, so Robinson does not step up.
TRADE_TEN = _trade(8, [TATE], 2, [ROBINSON])


@pytest.fixture(scope="module")
def newest_chart_dir(tmp_path_factory):
    directory = tmp_path_factory.mktemp("nflverse")
    for source in (NFLVERSE, NEWEST_CHART):
        for path in source.iterdir():
            shutil.copy(path, directory / path.name)
    return directory


def _newest(directory: Path, now: datetime | None):
    returns_file = returns_path(CLIENT.nfl_dir, 2026)
    slow = load_slow_sources(directory, 2026, 9, SAVED / "history")
    return build_snapshot(load_raw(SAVED / "week-08" / "raw"), SAVED / "history", None, slow, trade_week=9,
                          returns=load_returns(returns_file), out_for_season=load_out_for_season(returns_file),
                          now=now, client=CLIENT)


@pytest.fixture(scope="module")
def fresh(newest_chart_dir):
    return _newest(newest_chart_dir, FRESH)


def test_the_snapshot_holds_the_dt_of_the_newest_depth_chart(fresh):
    assert fresh.depth_chart_dt == CHART_DT


def test_a_player_behind_an_out_player_steps_up_in_the_trade_week(fresh):
    texts = _texts(TRADE_TEN, fresh, 8)
    assert texts[0] == "Week 9: WRs in the top 36 who play stay at 1. Robinson has a bye. Lemon and Godwin step up."
    # Out counts in the trade week only, so in week 10 the player ahead plays and no one steps up.
    assert "step" not in texts[1]


def test_the_player_ahead_on_no_roster_counts(fresh):
    # Wicks is on no roster, so only the full Sleeper players file holds his status.
    assert all(WICKS not in roster for roster in fresh.rosters.values())
    assert fresh.ahead_on_chart[LEMON].player_id == WICKS
    assert fresh.ahead_on_chart[LEMON].injury_status == "Out"


@pytest.mark.parametrize("now", [STALE, None])
def test_a_chart_more_than_48_hours_old_or_a_grade_with_no_time_names_no_step_up(newest_chart_dir, now):
    # AT-16: the grade time is more than 48 hours after the dt of the newest chart. With no grade time, the age of
    # the chart is not known.
    snapshot = _newest(newest_chart_dir, now)
    texts = [text for roster_id in (8, 2) for text in _texts(TRADE_TEN, snapshot, roster_id)]
    assert not any("step" in text for text in texts)


def test_a_chart_exactly_48_hours_old_still_names_a_step_up(fresh):
    snapshot = fresh.model_copy(update={"as_of": fresh.as_of.model_copy(
        update={"graded_at": CHART_DT + timedelta(hours=48)})})
    assert _texts(TRADE_TEN, snapshot, 8)[0].endswith(" Lemon and Godwin step up.")


def _with_ahead_status(snapshot, player_id: str, status: str | None):
    """The snapshot with the player ahead of `player_id` on the depth chart given a status."""
    ahead = snapshot.ahead_on_chart[player_id].model_copy(update={"injury_status": status})
    return snapshot.model_copy(update={"ahead_on_chart": {**snapshot.ahead_on_chart, player_id: ahead}})


def test_a_player_ahead_on_ir_makes_a_step_up_in_both_weeks(fresh):
    # Tate on IR is out in week 10 too, and TEN plays in week 10, so Robinson steps up then.
    texts = _texts(TRADE_TEN, _with_ahead_status(fresh, ROBINSON, "IR"), 8)
    assert texts[1].endswith(" Robinson steps up.")


@pytest.mark.parametrize("status", ["Questionable", "Doubtful", None])
def test_a_player_ahead_who_can_play_makes_no_step_up(fresh, status):
    texts = _texts(TRADE_TEN, _with_ahead_status(fresh, LEMON, status), 8)
    assert texts[0].endswith(" Godwin steps up.")


def test_a_player_who_is_out_himself_does_not_step_up(fresh):
    # Samuel of roster 10 is SF WR2 behind Mike Evans, who is Out. Samuel is Out too, so he does not step up.
    assert fresh.ahead_on_chart[SAMUEL].name == "Mike Evans"
    texts = _texts(TRADE_A, fresh, 10)
    assert "Samuel" in texts[0] and "step" not in texts[0]


def test_the_cache_key_changes_with_the_dt_of_the_chart_and_each_status_a_week_line_reads(fresh):
    # AT-30: trade A, then a new chart dt, then a new status of Mike Evans, who is on roster 1, not in the trade.
    # The Week line of roster 10 reads his status, because he is ahead of Samuel on the SF chart.
    key = cache_key(TRADE_A, fresh)
    later_chart = fresh.model_copy(update={"depth_chart_dt": CHART_DT + timedelta(hours=1)})
    assert cache_key(TRADE_A, later_chart) != key
    assert cache_key(TRADE_A, _with_ahead_status(fresh, SAMUEL, "IR")) != key
    # A status of a rostered player in the trade that the Week line reads.
    assert cache_key(TRADE_A, _with_status(fresh, NACUA, "IR")) != key


def test_the_cache_key_changes_with_the_status_of_a_player_ahead_on_no_roster(fresh):
    key = cache_key(TRADE_TEN, fresh)
    assert cache_key(TRADE_TEN, _with_ahead_status(fresh, LEMON, None)) != key
    # A status that the Week line never counts reads the same as no status, so it keeps the hit.
    assert cache_key(TRADE_TEN, _with_ahead_status(fresh, LEMON, "Questionable")) == cache_key(
        TRADE_TEN, _with_ahead_status(fresh, LEMON, None))


def test_the_cache_key_changes_when_the_chart_grows_too_old(fresh):
    # The same snapshot graded 48 hours and 49 hours after the chart: the second names no step-up.
    at = {hours: fresh.model_copy(update={"as_of": fresh.as_of.model_copy(
        update={"graded_at": CHART_DT + timedelta(hours=hours)})}) for hours in (47, 48, 49)}
    assert cache_key(TRADE_TEN, at[47]) == cache_key(TRADE_TEN, at[48])
    assert cache_key(TRADE_TEN, at[48]) != cache_key(TRADE_TEN, at[49])


def _with_status(snapshot, player_id: str, status: str | None):
    player = snapshot.players[player_id].model_copy(update={"injury_status": status})
    return snapshot.model_copy(update={"players": {**snapshot.players, player_id: player}})


# Week 6: Josh Jacobs on roster 11 is NA. Roster 11 gives Keaton Mitchell to roster 7 for Brian Robinson, so the trade
# touches RB and the Week line of roster 11 reads Jacobs.
JACOBS, MITCHELL, B_ROBINSON = "5850", "9511", "8154"
TRADE_RB = _trade(11, [MITCHELL], 7, [B_ROBINSON])


def _jacobs_played_in_week_6(fixture_raw_dir, fixture_history_root, chart_week6, back: int | None):
    """The snapshot of a game day in week 6, where Jacobs has a week 6 game, with his returns row set to `back`."""
    returns = {pid: week for pid, week in load_returns(fixture_history_root.parent / "returns.json").items()
               if pid != JACOBS}
    if back is not None:
        returns[JACOBS] = back
    snap = build_snapshot(load_raw(fixture_raw_dir), fixture_history_root, chart_week6, trade_week=6, returns=returns,
                          client=CLIENT)
    assert snap.as_of.stats_through == 6 and snap.players[JACOBS].injury_status == "NA"
    week_6 = snap.stats.weeks[6]
    week_6 = week_6.model_copy(update={"stats": {**week_6.stats, JACOBS: {**week_6.stats[JACOBS], "gp": 1.0}}})
    return snap.model_copy(update={"stats": snap.stats.model_copy(update={"weeks": {**snap.stats.weeks, 6: week_6}})})


def test_a_player_back_in_a_known_game_of_the_trade_week_is_not_out(fixture_raw_dir, fixture_history_root,
                                                                     chart_week6):
    # A returns row of week 6 and a week 6 game: he is back, as due_back_week reads it, though his tag still says NA.
    back = _jacobs_played_in_week_6(fixture_raw_dir, fixture_history_root, chart_week6, 6)
    assert all("Jacobs" not in text for text in _texts(TRADE_RB, back, 11))
    # With no returns row, his week 6 game is the game he was hurt in, so he stays out in both weeks.
    hurt = _jacobs_played_in_week_6(fixture_raw_dir, fixture_history_root, chart_week6, None)
    assert all("Jacobs is not active." in text for text in _texts(TRADE_RB, hurt, 11))
