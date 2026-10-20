"""
Tests for standings, awards, Matchup of the Week, next week, and position ranks.
They run on the real week 6 fixture.
"""
import re

from cornerstone.facts_league import (
    awards,
    matchup_of_the_week,
    next_week,
    position_ranks,
    ranks_before,
    season_history,
    standings,
    upset_signal,
)
from cornerstone.facts_matchup import matchup_facts
from cornerstone.parse import parse_week
from cornerstone.sleeper import load_raw


def _setup(d):
    wk = parse_week(load_raw(d))
    mf = [matchup_facts(m, wk.moves, 6) for m in wk.matchups]
    return wk, mf


def test_standings_order_and_cut(fixture_raw_dir):
    wk, _ = _setup(fixture_raw_dir)
    t = standings(wk)
    names = [wk.teams[s.roster_id].name for s in t]
    assert names[:3] == ["Lil Fridge", "London Cooking", "Bo Girds"]
    assert names[-1] == "Pukancun on 3"
    assert [s.in_playoffs for s in t].count(True) == 6
    assert t[5].games_from_cut == 0 and t[0].games_from_cut >= 0


def test_awards_one_player_one_tile(fixture_raw_dir):
    wk, mf = _setup(fixture_raw_dir)
    a = {x.key: x for x in awards(wk, mf)}
    assert a["top_scorer"].line.name == "Trevor Lawrence"
    assert a["mvb"].line.name == "Jayden Daniels"
    assert a["underperformer"].line.name == "Bijan Robinson"
    assert a["game_changer"].line.name == "Tre Tucker"
    assert "Tre Tucker" in a["overachiever"].skipped
    assert a["overachiever"].line.name == "Germie Bernard"
    assert len({x.line.player_id for x in a.values()}) == 5


def test_motw_is_closest(fixture_raw_dir):
    wk, mf = _setup(fixture_raw_dir)
    pick = matchup_of_the_week(wk, mf, standings(wk))
    assert pick.matchup_id == 4 and pick.reason == "Closest Finish"
    assert set(pick.scores) == {"closeness", "upset", "table", "stakes"}


def test_next_week_two_must_watch(fixture_raw_dir):
    wk, _ = _setup(fixture_raw_dir)
    nx = next_week(wk, standings(wk))
    assert len(nx) == 6 and sum(n.must_watch for n in nx) == 2
    assert all(n.reason for n in nx if n.must_watch)
    # The text names ranks and makes no claim about who falls.
    assert all("falls" not in n.reason for n in nx if n.must_watch)
    assert all(n.reason is None for n in nx if not n.must_watch)
    assert all(
        re.fullmatch(r"\d+(st|nd|rd|th) vs \d+(st|nd|rd|th)(, near the playoff cut)?", n.reason)
        for n in nx
        if n.must_watch
    )


def test_position_ranks(fixture_raw_dir):
    wk, _ = _setup(fixture_raw_dir)
    tucker = next(r for r in position_ranks(wk) if r.player_id == "10213")
    assert (tucker.position, tucker.rank) == ("WR", 1)
    nabers = next(r for r in position_ranks(wk) if r.player_id == "11632")
    assert nabers.rank == 2


def test_ranks_before_is_a_permutation(fixture_raw_dir):
    wk, _ = _setup(fixture_raw_dir)
    before = ranks_before(wk, standings(wk))
    assert set(before) == set(wk.teams)
    assert sorted(before.values()) == list(range(1, 13))


def test_upset_signal_direction():
    # A winner ranked 10th that beats a team ranked 2nd is an upset.
    assert upset_signal(winner_rank_before=10, loser_rank_before=2) == 8 / 11
    # A favorite that wins is not an upset.
    assert upset_signal(winner_rank_before=2, loser_rank_before=10) == 0


def test_season_history_covers_this_week_only(fixture_raw_dir):
    wk, _ = _setup(fixture_raw_dir)
    h = season_history(wk)
    assert len(h) == 12
    assert all(x.high == x.low and x.new_high and x.new_low for x in h)
    assert all(set(x.weeks_over) == {100, 110, 120} for x in h)


def test_ranks_before_take_off_this_week(fixture_raw_dir):
    # Checked by hand: with week 6 taken off, behold the lamb is 4-6 on 473.06 (11th),
    # Bo Girds 7-3 on 613.54 (2nd), Return of T Mac 4-6 on 498.68 (9th), and
    # Unsolicited Dak Picks 4-6 on 513.44 (7th).
    wk, _ = _setup(fixture_raw_dir)
    before = ranks_before(wk, standings(wk))
    by_name = {wk.teams[rid].name: rank for rid, rank in before.items()}
    assert by_name["behold the lamb"] == 11
    assert by_name["Bo Girds"] == 2
    assert by_name["Return of T Mac"] == 9
    assert by_name["Unsolicited Dak Picks"] == 7
