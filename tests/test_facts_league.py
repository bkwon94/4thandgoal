"""
Tests for standings, awards, Matchup of the Week, next week, and position ranks.
They run on the real week 6 fixture.
"""
from pathlib import Path

import pytest

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
from cornerstone.history import load_history
from cornerstone.models import History, PastWeek, Standing
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


def _motw_with(fixture_raw_dir, margins, before=None, far_from_cut=(), ranks=None):
    """Run the pick on the week 6 fixture with set margins, ranks before, and cut distance."""
    wk, mf = _setup(fixture_raw_dir)
    mf = [f.model_copy(update={"margin": margins.get(f.matchup_id, f.margin)}) for f in mf]
    table = [
        s.model_copy(update={"games_from_cut": 3}) if s.roster_id in far_from_cut else s
        for s in standings(wk)
    ]
    table = [s.model_copy(update={"rank": (ranks or {}).get(s.roster_id, s.rank)}) for s in table]
    return matchup_of_the_week(wk, mf, table, {**ranks_before(wk, table), **(before or {})})


def test_motw_label_is_the_upset_when_the_pick_leads_only_there(fixture_raw_dir):
    # Matchup 3 is the closest game. Matchup 1 wins on total and has the biggest upset.
    # Closeness is its largest weighted score, but it does not lead in closeness.
    pick = _motw_with(fixture_raw_dir, {1: 10, 3: 5}, {3: 12, 1: 1})
    assert pick.matchup_id == 1 and pick.reason == "Upset"
    assert pick.scores["closeness"] > pick.scores["upset"]


def test_motw_tie_shared_by_most_games_is_no_lead(fixture_raw_dir):
    # All six matchups tie at 1.0 in stakes, so stakes leads for no pick.
    # Matchup 1 leads only in upset, though its weighted stakes score is larger.
    pick = _motw_with(
        fixture_raw_dir, {1: 8, 3: 5}, {3: 5, 1: 1, 10: 1}, ranks={3: 12}
    )
    assert pick.matchup_id == 1 and pick.reason == "Upset"
    assert pick.scores["stakes"] > pick.scores["upset"]


def test_motw_label_is_closest_finish_for_the_closest_game(fixture_raw_dir):
    # Matchup 4 has the smallest margin and also the biggest upset. Closeness weighs more.
    wk, mf = _setup(fixture_raw_dir)
    assert min(mf, key=lambda f: f.margin).matchup_id == 4
    pick = matchup_of_the_week(wk, mf, standings(wk))
    assert pick.matchup_id == 4 and pick.reason == "Closest Finish"


def test_motw_label_falls_back_to_the_nearest_to_best_with_no_lead(fixture_raw_dir):
    # Matchup 5 is second in closeness, upset, and table, and far from the cut.
    # It leads in no signal. Closeness is its nearest to the best, at 0.99 of it.
    margins = {1: 60, 2: 66, 3: 60, 4: 5.34, 5: 6, 6: 60}
    before = {5: 8, 7: 2, 10: 1, 6: 12, 2: 1, 8: 12, 11: 1}
    pick = _motw_with(fixture_raw_dir, margins, before, far_from_cut={5, 10})
    assert pick.matchup_id == 5 and pick.reason == "Closest Finish"
    assert pick.scores["stakes"] == 0


def test_next_week_two_must_watch(fixture_raw_dir):
    wk, _ = _setup(fixture_raw_dir)
    nx = next_week(wk, standings(wk))
    assert len(nx) == 6 and sum(n.must_watch for n in nx) == 2
    assert all(n.reason for n in nx if n.must_watch)
    # The text names ranks and makes no claim about who falls.
    assert all("falls" not in n.reason for n in nx if n.must_watch)
    assert all(n.reason is None for n in nx if not n.must_watch)
    # With no history, near the cut is the only storyline here. Four games are near the cut: 1st vs 7th,
    # 6th vs 4th, 8th vs 10th, and 5th vs 3rd. The three with a gap of 2 tie, so the schedule order picks two.
    assert [(n.a, n.b, n.reason) for n in nx if n.must_watch] == [
        (1, 9, "Both sit near the cut"),
        (10, 11, "behold the lamb sits near the cut"),
    ]


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


def _history(raw_dir, root):
    return load_history(root, load_raw(raw_dir), week=6)


def test_standings_come_from_history(fixture_raw_dir, fixture_history_root):
    wk, _ = _setup(fixture_raw_dir)
    for t in wk.teams.values():
        t.wins, t.losses, t.points_for = 0, 0, 0.0
    t = standings(wk, _history(fixture_raw_dir, fixture_history_root))
    rows = {wk.teams[s.roster_id].name: (s.rank, s.wins, s.losses, s.points_for) for s in t}
    assert rows["Lil Fridge"] == (1, 10, 2, 739.67)
    assert rows["Bo Girds"] == (3, 8, 4, 723.15)
    assert rows["Pukancun on 3"] == (12, 1, 11, 493.39)


def test_schedule_strength_comes_from_history(fixture_raw_dir, fixture_history_root):
    wk, _ = _setup(fixture_raw_dir)
    real = [s.schedule_strength for s in standings(wk)]
    for t in wk.teams.values():
        t.wins, t.losses = 0, 1
    assert [s.schedule_strength for s in standings(wk, _history(fixture_raw_dir, fixture_history_root))] == real


def test_ranks_before_from_history(fixture_raw_dir, fixture_history_root):
    wk, _ = _setup(fixture_raw_dir)
    h = _history(fixture_raw_dir, fixture_history_root)
    before = ranks_before(wk, standings(wk, h), h)
    by_name = {wk.teams[rid].name: rank for rid, rank in before.items()}
    assert (by_name["behold the lamb"], by_name["Bo Girds"]) == (11, 2)
    assert (by_name["Return of T Mac"], by_name["Unsolicited Dak Picks"]) == (9, 7)


def test_incomplete_history_falls_back_with_a_warning(fixture_raw_dir, caplog):
    wk, _ = _setup(fixture_raw_dir)
    h = History(week=6, weeks={})
    assert standings(wk, h) == standings(wk)
    assert "history incomplete" in caplog.text


def test_motw_week_7_label_is_the_nearest_to_best():
    # Week 7 of 2026: matchup 1 wins on total but leads no signal. Stakes is shared by
    # four of six games, so it is no lead. Table is nearest to the best, at 0.895 of it.
    season_root = Path(__file__).parents[1] / "data" / "2026"
    if not (season_root / "week-07" / "raw").exists():
        pytest.skip("saved week 7 is not on this machine")
    raw = load_raw(season_root / "week-07" / "raw")
    wk = parse_week(raw)
    history = load_history(season_root / "history", raw, 7)
    mf = [matchup_facts(m, wk.moves, 7) for m in wk.matchups]
    table = standings(wk, history)
    pick = matchup_of_the_week(wk, mf, table, ranks_before(wk, table, history))
    assert pick.matchup_id == 1 and pick.reason == "Top of the Table"


# A hand-made season of 3 weeks for the 12 rosters of the week 6 fixture. No pair of BASE_PAIRS meets in
# HAND_NEXT, so the base season has no rematch. The winner alternates by week, so no team has a streak.
BASE_PAIRS = {
    1: [(1, 2), (3, 4), (5, 6), (7, 8), (9, 10), (11, 12)],
    2: [(1, 3), (2, 4), (5, 7), (6, 8), (9, 11), (10, 12)],
    3: [(1, 5), (2, 6), (3, 7), (4, 8), (9, 12), (10, 11)],
}
HAND_NEXT = [(1, 12), (2, 11), (3, 10), (4, 9), (5, 8), (6, 7)]


def _hand_week(fixture_raw_dir, next_pairs=HAND_NEXT):
    wk, _ = _setup(fixture_raw_dir)
    return wk.model_copy(update={"week": 3, "next_matchups": next_pairs})


def _hand_history(flips=(), scores=None, pairs=None):
    """The base season. A pair in `flips` has its winner flipped. `scores` sets a score by (week, roster)."""
    weeks = {}
    for number, base in BASE_PAIRS.items():
        week_pairs = (pairs or {}).get(number, base)
        week_scores = {}
        for a, b in week_pairs:
            # The lower id wins in odd weeks, the higher id in even weeks.
            winner, loser = (a, b) if number % 2 else (b, a)
            if (number, (a, b)) in flips:
                winner, loser = loser, winner
            week_scores[winner], week_scores[loser] = 110.0, 100.0
        week_scores.update({rid: x for (w, rid), x in (scores or {}).items() if w == number})
        weeks[number] = PastWeek(week=number, scores=week_scores, pairs=week_pairs, points={},
                                 projections={}, stats={}, moves=[])
    return History(week=3, weeks=weeks)


def _hand_table(ranks=None, from_cut=None):
    """Rank = roster id unless `ranks` says so. The top six sit 5 games above the cut and the rest 5 below."""
    ranks = ranks or {}
    from_cut = from_cut or {}
    out = []
    for rid in range(1, 13):
        rank = ranks.get(rid, rid)
        out.append(Standing(rank=rank, roster_id=rid, wins=0, losses=0, points_for=0.0, in_playoffs=rank <= 6,
                            games_from_cut=from_cut.get(rid, 5 if rank <= 6 else -5), schedule_strength=None,
                            strength_rank=None))
    return sorted(out, key=lambda s: s.rank)


def _game(nx, a, b):
    return next(n for n in nx if (n.a, n.b) == (a, b))


def test_three_straight_head_to_head_wins_put_a_streak_on_the_line(fixture_raw_dir):
    # Roster 1 beats 2 in week 1, 3 in week 2 by the flip, and 5 in week 3: 3 straight wins.
    # Roster 2 loses week 1, then beats 4 by the flip and 6: 2 straight wins, no streak.
    flips = {(2, (1, 3)), (2, (2, 4))}
    nx = next_week(_hand_week(fixture_raw_dir), _hand_table(), _hand_history(flips))
    assert [(s.kind, s.roster_id, s.length) for s in _game(nx, 1, 12).storylines] == [("streak", 1, 3)]
    assert _game(nx, 2, 11).storylines == []


def test_three_straight_head_to_head_losses_put_a_streak_on_the_line(fixture_raw_dir):
    # Roster 12 loses to 11 in week 1, to 10 in week 2 by the flip, and to 9 in week 3: 3 losses.
    flips = {(2, (10, 12))}
    nx = next_week(_hand_week(fixture_raw_dir), _hand_table(), _hand_history(flips))
    assert [(s.kind, s.roster_id, s.length) for s in _game(nx, 1, 12).storylines] == [("streak", 12, -3)]


def test_the_median_game_never_counts_in_the_streak(fixture_raw_dir):
    # Roster 2 scores 140 each week, over the median of 110, 105, and 105, but loses to roster 1 in week 1.
    # The median wins would make a longer run. Head-to-head alone, roster 2 has 2 wins in a row, so no streak.
    flips = {(2, (2, 4))}
    scores = {(1, 1): 150.0, (1, 2): 140.0, (2, 2): 140.0, (3, 2): 140.0}
    nx = next_week(_hand_week(fixture_raw_dir), _hand_table(), _hand_history(flips, scores))
    assert _game(nx, 2, 11).storylines == []


def test_no_history_gives_no_streak(fixture_raw_dir):
    nx = next_week(_hand_week(fixture_raw_dir), _hand_table())
    assert all(n.storylines == [] for n in nx)
