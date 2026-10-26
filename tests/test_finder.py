"""
Tests for the finder: the ranked win-win trades between two rosters of the week 6 snapshot.
They feed two roster ids and the snapshot at the finder seam, and fixture items at the rank seam.
"""
import shutil
import time
from itertools import combinations
from math import comb

import pytest

from conftest import with_carries

from cornerstone.adjusters import Adjuster, recent_points_per_game
from cornerstone.finder import FinderTrade, candidates, find_win_wins, rank
from cornerstone.rubric import Breakdown, Fairness, FairnessSide, ProposedTrade, TradeSide, fairness, grade
from cornerstone.slow_sources import load_slow_sources
from cornerstone.sleeper import load_raw
from cornerstone.snapshot import build_snapshot, load_returns, load_snapshot


@pytest.fixture
def slow_snap(fixture_raw_dir, fixture_history_root, chart_week6, fixture_nflverse_dir, tmp_path):
    """The week 6 snapshot with the slow sources from the nflverse fixture and the returns file."""
    cache = tmp_path / "nflverse"
    shutil.copytree(fixture_nflverse_dir, cache)
    slow = load_slow_sources(cache, 2026, 6, fixture_history_root)
    return load_snapshot(fixture_raw_dir, fixture_history_root, chart_week6, slow)


# The fixture chart cannot serve the count tests. It lists 25 players, mostly stars, so every trade of listed
# players is lopsided and no pair of the week 6 snapshot has a win-win. Each test gives chart rows to the
# players it needs, with a trade value of their recent points per game, so a trade of two such players starts
# near even and the adjusters decide it.
CHART_POSITIONS = frozenset({"RB", "WR", "TE", "QB"})


def _with_rows(snap, players):
    """The snapshot with a chart row for each player who has none, at his recent points per game, 1 at least."""
    rows = {pid: float(max(1, round(recent_points_per_game(snap, pid)))) for pid in players
            if pid not in snap.chart.values}
    return snap.model_copy(update={"chart": snap.chart.model_copy(update={"values": {**snap.chart.values, **rows}})})


def _roster_rows(snap, *roster_ids):
    """The snapshot with a chart row for every RB, WR, TE, and QB on the rosters."""
    players = [pid for roster_id in roster_ids for pid in snap.rosters[roster_id]
               if snap.players[pid].position in CHART_POSITIONS]
    return _with_rows(snap, players)


# With rows for all of rosters 2 and 3, the pair has many win-wins, and roster 2 gives the same running back
# in most of the best ones. With rows for one running back of roster 2 and
# a quarterback and a receiver of roster 3, the pair has one win-win, a two-for-one. With the fixture chart
# alone, the pair has none.
RB_2, QB_3, WR_3 = "12527", "11560", "5947"


def _win_wins(asker, partner, snap) -> list[FinderTrade]:
    """Every win-win candidate, ranked, with no cut to three."""
    found = []
    for trade in candidates(asker, partner, snap):
        breakdowns = grade(trade, snap)
        result = fairness((breakdowns[0].final_letter, breakdowns[1].final_letter), breakdowns)
        if result.state == "win_win":
            found.append(FinderTrade(trade=trade, breakdowns=breakdowns, fairness=result))
    return rank(found)


def _players(item) -> set[str]:
    return {pid for side in item.trade.sides for pid in side.gives}


def test_a_pair_with_three_or_more_win_wins_returns_three_ranked(slow_snap):
    found = find_win_wins(2, 3, _roster_rows(slow_snap, 2, 3))
    assert len(found) == 3
    assert all(item.fairness.state == "win_win" for item in found)
    assert all(item.trade.asker == 2 and item.trade.sides[0].roster_id == 2 for item in found)
    assert rank(found) == found


def test_the_three_trades_share_no_player_when_the_best_win_wins_do(slow_snap):
    snap = _roster_rows(slow_snap, 2, 3)
    every = _win_wins(2, 3, snap)
    # The data proves a skip: four or more win-wins, and a plain cut to the best three repeats a player.
    assert len(every) >= 4
    assert any(_players(one) & _players(other) for one, other in combinations(every[:3], 2))
    found = find_win_wins(2, 3, snap)
    assert len(found) == 3
    assert not any(_players(one) & _players(other) for one, other in combinations(found, 2))
    # Each kept trade is the best win-win that shares no player with the ones before it.
    assert found[0] == every[0]


def test_a_pair_with_one_win_win_returns_one(slow_snap):
    found = find_win_wins(2, 3, _with_rows(slow_snap, [RB_2, QB_3, WR_3]))
    assert len(found) == 1
    assert [b.roster_id for b in found[0].breakdowns] == [2, 3]


def test_a_pair_with_no_win_win_returns_the_empty_list(slow_snap):
    assert find_win_wins(2, 3, slow_snap) == []


def test_a_two_for_one_appears_in_both_directions(slow_snap):
    # The one win-win has roster 3 give two players. With roster 3 as the asker, it gives two.
    snap = _with_rows(slow_snap, [RB_2, QB_3, WR_3])
    gets_two = find_win_wins(2, 3, snap)[0].trade
    gives_two = find_win_wins(3, 2, snap)[0].trade
    assert [len(side.gives) for side in gets_two.sides] == [1, 2]
    assert [len(side.gives) for side in gives_two.sides] == [2, 1]
    assert gives_two.sides[0].gives == gets_two.sides[1].gives


# The seconds one pair may take. The test measures wall-clock time on the fixture. With chart rows for both
# whole rosters, rosters 5 and 9 have the most candidates of the week 6 pairs and took about 3 seconds on a
# laptop. Ticket 04 caches the finder result per pair, so a page asks for one pair once.
PAIR_SECONDS = 5


def test_the_pair_with_the_most_candidates_runs_in_a_few_seconds(slow_snap):
    snap = _roster_rows(slow_snap, 5, 9)
    start = time.perf_counter()
    find_win_wins(5, 9, snap)
    assert time.perf_counter() - start < PAIR_SECONDS


def _traded(trades) -> set[str]:
    return {pid for trade in trades for side in trade.sides for pid in side.gives}


# Breece Hall on roster 8 is Out with no row in the returns file.
# Josh Jacobs on roster 11 is NA, which keeps him out, but the returns file has him back in week 7.
BREECE_HALL, JACOBS = "8155", "5850"


def test_an_out_player_with_no_return_week_is_never_a_candidate(slow_snap):
    snap = _roster_rows(slow_snap, 8, 7)
    assert BREECE_HALL in snap.rosters[8] and BREECE_HALL in snap.chart.values
    assert BREECE_HALL not in _traded(candidates(8, 7, snap))


def test_an_out_player_with_a_return_week_on_file_is_a_candidate(slow_snap):
    assert JACOBS in slow_snap.rosters[11]
    assert JACOBS in _traded(candidates(11, 7, _roster_rows(slow_snap, 11, 7)))


def _jacobs_played_in_week_6(fixture_raw_dir, fixture_history_root, chart_week6, returns):
    """The snapshot of a game day in week 6, where NA-tagged Jacobs has a week 6 game and the returns rows given."""
    snap = build_snapshot(load_raw(fixture_raw_dir), fixture_history_root, chart_week6, trade_week=6, returns=returns)
    assert snap.as_of.stats_through == 6 and snap.players[JACOBS].injury_status == "NA"
    week_6 = snap.stats.weeks[6]
    week_6 = week_6.model_copy(update={"stats": {**week_6.stats, JACOBS: {**week_6.stats[JACOBS], "gp": 1.0}},
                                       "points": {**week_6.points, JACOBS: 21.0}})
    snap = snap.model_copy(update={"stats": snap.stats.model_copy(update={"weeks": {**snap.stats.weeks, 6: week_6}})})
    return _roster_rows(snap, 11, 7)


def test_an_out_player_back_in_a_known_game_is_a_candidate_and_one_with_no_return_week_is_not(
        fixture_raw_dir, fixture_history_root, chart_week6):
    returns = load_returns(fixture_history_root.parent / "returns.json")
    # A returns row of week 6 and a week 6 game: he is back, though his tag still says out.
    back = _jacobs_played_in_week_6(fixture_raw_dir, fixture_history_root, chart_week6, {**returns, JACOBS: 6})
    assert JACOBS in _traded(candidates(11, 7, back))
    # With no returns row, his week 6 game is the game he was hurt in, so he stays out of every trade.
    hurt = _jacobs_played_in_week_6(fixture_raw_dir, fixture_history_root, chart_week6,
                                    {pid: week for pid, week in returns.items() if pid != JACOBS})
    assert JACOBS not in _traded(candidates(11, 7, hurt))


def test_an_unlisted_player_is_never_a_candidate(slow_snap):
    # An unlisted player starts both sides at C by rule, not by the chart, so the finder skips him.
    traded = _traded(candidates(4, 12, slow_snap))
    assert traded and traded <= set(slow_snap.chart.values)
    # Both rosters hold unlisted running backs and receivers, so the test proves a skip and not an absence.
    assert any(pid not in slow_snap.chart.values and slow_snap.players[pid].position in CHART_POSITIONS
               for pid in slow_snap.rosters[4] + slow_snap.rosters[12])


def test_a_kicker_and_a_defense_are_never_candidates(slow_snap):
    # The chart lists no kicker and no defense, so both are always unlisted, even when every other player is listed.
    snap = _roster_rows(slow_snap, 4, 12)
    positions = {snap.players[pid].position for pid in _traded(candidates(4, 12, snap))}
    assert "K" not in positions and "DEF" not in positions
    # Both rosters hold a defense, so the test proves a skip and not an absence.
    assert any(slow_snap.players[pid].position == "DEF" for pid in slow_snap.rosters[4] + slow_snap.rosters[12])


# The LAC depth chart: Omarion Hampton on roster 12 first, then Keaton Mitchell and Kimani Vidal on roster 11.
# The NE depth chart: Rhamondre Stevenson on roster 7 first, then TreVeyon Henderson on roster 8.
# The id map fixture lacks them, so the tests join their gsis_ids here.
MITCHELL, HAMPTON, VIDAL = "9511", "12507", "11647"
STEVENSON, HENDERSON = "7611", "12529"
IDS = {MITCHELL: "00-0038454", HAMPTON: "00-0040666", VIDAL: "00-0039391",
       STEVENSON: "00-0036875", HENDERSON: "00-0040734"}


def _with_ids(snap):
    # The tests trade these players, so each one also gets a chart row.
    snap = snap.model_copy(update={"id_map": {**snap.id_map, **IDS}})
    return _roster_rows(snap, 4, 7, 8, 11, 12)


def test_a_handcuff_on_his_own_roster_is_never_a_candidate(slow_snap):
    # Mitchell moves to roster 12, so he backs up Hampton on his own roster.
    rosters = {**slow_snap.rosters, 11: [p for p in slow_snap.rosters[11] if p != MITCHELL],
               12: slow_snap.rosters[12] + [MITCHELL]}
    # At 4 carries a game in weeks 3 to 5, Mitchell takes 15% of the LAC carries, below the gate.
    snap = with_carries(_with_ids(slow_snap), MITCHELL, {3: 4.0, 4: 4.0, 5: 4.0})
    snap = snap.model_copy(update={"rosters": rosters})
    assert MITCHELL not in _traded(candidates(12, 4, snap))
    # With no depth chart, no player is a handcuff, so Mitchell is a candidate.
    assert MITCHELL in _traded(candidates(12, 4, snap.model_copy(update={"depth_charts": None})))


# At 3 carries a game in weeks 3 to 5, Henderson takes 15% of the NE carries, below the gate.
THIN = {3: 3.0, 4: 3.0, 5: 3.0}


def test_a_player_who_is_a_handcuff_on_the_roster_that_gets_him_is_never_a_candidate(slow_snap):
    # Henderson backs up Stevenson, who is on roster 7. A trade of Henderson to roster 7 is a handcuff trade,
    # unless roster 7 gives Stevenson in the same trade.
    snap = with_carries(_with_ids(slow_snap), HENDERSON, THIN)
    with_henderson = [trade for trade in candidates(8, 7, snap) if HENDERSON in trade.sides[0].gives]
    assert with_henderson
    assert all(STEVENSON in trade.sides[1].gives for trade in with_henderson)
    # Roster 4 has no NE starter, so Henderson is a candidate there.
    assert HENDERSON in _traded(candidates(8, 4, snap))


def test_a_backup_with_real_carries_can_go_to_the_roster_of_his_starter(slow_snap):
    # Henderson takes 26 of 79 NE carries in weeks 3 to 5, or 33%, so he is a running back and no handcuff.
    with_henderson = [trade for trade in candidates(8, 7, _with_ids(slow_snap)) if HENDERSON in trade.sides[0].gives]
    assert any(STEVENSON not in trade.sides[1].gives for trade in with_henderson)


def test_the_candidates_are_every_one_for_one_and_every_two_for_one_in_both_directions(slow_snap):
    trades = candidates(4, 12, _roster_rows(slow_snap, 4, 12))
    shapes = {(len(trade.sides[0].gives), len(trade.sides[1].gives)) for trade in trades}
    assert shapes == {(1, 1), (2, 1), (1, 2)}
    # The asker's side is first, and every trade is for the asker.
    assert all(trade.sides[0].roster_id == 4 and trade.asker == 4 for trade in trades)
    ones = [trade for trade in trades if (len(trade.sides[0].gives), len(trade.sides[1].gives)) == (1, 1)]
    mine = {pid for trade in ones for pid in trade.sides[0].gives}
    theirs = {pid for trade in ones for pid in trade.sides[1].gives}
    assert len(ones) == len(mine) * len(theirs)
    # Each pair of players gives once, with no order, so no two trades are the same.
    keys = [(frozenset(trade.sides[0].gives), frozenset(trade.sides[1].gives)) for trade in trades]
    assert len(keys) == len(set(keys))
    two_for_ones = len(trades) - len(ones)
    # No trade of rosters 4 and 12 makes a handcuff, so every pair of players on each side gives a two-for-one.
    assert two_for_ones == comb(len(mine), 2) * len(theirs) + len(mine) * comb(len(theirs), 2)


STEPPED = ("roster fit", "standing", "trend and usage", "injury", "handcuff")


def _breakdown(roster_id: int, final: str, ups: int, downs: int = 0) -> Breakdown:
    # The first adjusters step up, the last ones step down, and the rest hold.
    steps = [1] * ups + [0] * (len(STEPPED) - ups - downs) + [-1] * downs
    adjusters = [Adjuster(name=name, step=step, reason=f"{name} reason") for name, step in zip(STEPPED, steps)]
    return Breakdown(roster_id=roster_id, start_letter="C", reason="Even.", adjusters=adjusters, final_letter=final)


def _item(mine: str, theirs: str, ups: tuple[int, int] = (1, 1), gives: tuple[str, str] = ("1", "2"),
          downs: tuple[int, int] = (0, 0)) -> FinderTrade:
    trade = ProposedTrade(season=2026, asker=4, sides=(TradeSide(roster_id=4, gives=[gives[0]]),
                                                         TradeSide(roster_id=12, gives=[gives[1]])))
    breakdowns = (_breakdown(4, mine, ups[0], downs[0]), _breakdown(12, theirs, ups[1], downs[1]))
    sides = (FairnessSide(roster_id=4, reason="A gain."), FairnessSide(roster_id=12, reason="A gain."))
    return FinderTrade(trade=trade, breakdowns=breakdowns,
                       fairness=Fairness(state="win_win", gives_more=None, sides=sides))


def _order(items) -> list[str]:
    return [item.trade.sides[0].gives[0] for item in rank(items)]


def test_the_rank_puts_the_highest_net_steps_on_both_sides_first():
    items = [_item("A", "A", ups=(1, 1), gives=("low", "x")), _item("B", "B", ups=(2, 1), gives=("high", "x"))]
    assert _order(items) == ["high", "low"]


def test_a_step_down_counts_against_a_step_up_in_the_rank():
    # Three steps up and one down net two, the same as two up. The tie then goes to the higher lower letter.
    items = [_item("B", "B", ups=(2, 1), downs=(1, 0), gives=("mixed", "x")),
             _item("A", "A", ups=(1, 1), gives=("clean", "x"))]
    assert _order(items) == ["clean", "mixed"]


def test_at_equal_net_steps_the_higher_lower_letter_ranks_first():
    items = [_item("A", "B", gives=("ab", "x")), _item("A", "A", gives=("aa", "x"))]
    assert _order(items) == ["aa", "ab"]


def test_at_equal_net_steps_and_lower_letters_the_smaller_gap_ranks_first():
    # Both lower letters are B. Only a win-win reaches the rank, so A over B is the widest gap there.
    items = [_item("A", "B", gives=("gap", "x")), _item("B", "B", gives=("even", "x"))]
    assert _order(items) == ["even", "gap"]


def test_at_equal_net_steps_lower_letters_and_gaps_the_higher_asker_letter_ranks_first():
    items = [_item("B", "A", gives=("theirs", "x")), _item("A", "B", gives=("mine", "x"))]
    assert _order(items) == ["mine", "theirs"]


def test_at_a_full_tie_the_player_ids_rank_the_trades_the_same_way_every_time():
    items = [_item("A", "A", gives=("b", "x")), _item("A", "A", gives=("a", "x"))]
    assert _order(items) == ["a", "b"]
    assert _order(list(reversed(items))) == ["a", "b"]
