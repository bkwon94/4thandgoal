"""
Tests for standings, awards, Matchup of the Week, next week, and position ranks.
They run on the real week 6 fixture.
"""
from pathlib import Path

import pytest

from cornerstone.config import cornerstone_config
from cornerstone.facts_league import (
    awards,
    key_starters,
    matchup_of_the_week,
    next_week,
    position_ranks,
    ranks_before,
    season_history,
    upset_signal,
)
from cornerstone.facts_matchup import matchup_facts
from cornerstone.history import load_history
from cornerstone.models import History, PastWeek, Standing
from cornerstone.parse import parse_week
from cornerstone.sheet import projected_totals
from cornerstone.provider.sleeper import load_raw
from cornerstone.standings_table import standings

CONFIG = cornerstone_config()


def _setup(d):
    wk = parse_week(load_raw(d))
    mf = [matchup_facts(m, wk.moves, 6) for m in wk.matchups]
    return wk, mf


def test_standings_order_and_cut(fixture_raw_dir):
    wk, _ = _setup(fixture_raw_dir)
    t = standings(wk, config=CONFIG)
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
    pick = matchup_of_the_week(wk, mf, standings(wk, config=CONFIG))
    assert pick.matchup_id == 4 and pick.reason == "Closest Finish"
    assert set(pick.scores) == {"closeness", "upset", "table", "stakes"}


def _motw_with(fixture_raw_dir, margins, before=None, far_from_cut=(), ranks=None):
    """Run the pick on the week 6 fixture with set margins, ranks before, and cut distance."""
    wk, mf = _setup(fixture_raw_dir)
    mf = [f.model_copy(update={"margin": margins.get(f.matchup_id, f.margin)}) for f in mf]
    table = [
        s.model_copy(update={"games_from_cut": 3}) if s.roster_id in far_from_cut else s
        for s in standings(wk, config=CONFIG)
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
    pick = matchup_of_the_week(wk, mf, standings(wk, config=CONFIG))
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
    nx = next_week(wk, standings(wk, config=CONFIG))
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
    before = ranks_before(wk, standings(wk, config=CONFIG))
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
    before = ranks_before(wk, standings(wk, config=CONFIG))
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
    t = standings(wk, _history(fixture_raw_dir, fixture_history_root), config=CONFIG)
    rows = {wk.teams[s.roster_id].name: (s.rank, s.wins, s.losses, s.points_for) for s in t}
    assert rows["Lil Fridge"] == (1, 10, 2, 739.67)
    assert rows["Bo Girds"] == (3, 8, 4, 723.15)
    assert rows["Pukancun on 3"] == (12, 1, 11, 493.39)


def test_schedule_strength_comes_from_history(fixture_raw_dir, fixture_history_root):
    wk, _ = _setup(fixture_raw_dir)
    real = [s.schedule_strength for s in standings(wk, config=CONFIG)]
    for t in wk.teams.values():
        t.wins, t.losses = 0, 1
    history = _history(fixture_raw_dir, fixture_history_root)
    assert [s.schedule_strength for s in standings(wk, history, config=CONFIG)] == real


def test_ranks_before_from_history(fixture_raw_dir, fixture_history_root):
    wk, _ = _setup(fixture_raw_dir)
    h = _history(fixture_raw_dir, fixture_history_root)
    before = ranks_before(wk, standings(wk, h, config=CONFIG), h)
    by_name = {wk.teams[rid].name: rank for rid, rank in before.items()}
    assert (by_name["behold the lamb"], by_name["Bo Girds"]) == (11, 2)
    assert (by_name["Return of T Mac"], by_name["Unsolicited Dak Picks"]) == (9, 7)


def test_incomplete_history_falls_back_with_a_warning(fixture_raw_dir, caplog):
    wk, _ = _setup(fixture_raw_dir)
    h = History(week=6, weeks={})
    assert standings(wk, h, config=CONFIG) == standings(wk, config=CONFIG)
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
    table = standings(wk, history, config=CONFIG)
    pick = matchup_of_the_week(wk, mf, table, ranks_before(wk, table, history))
    assert pick.matchup_id == 1 and pick.reason == "Top of the Table"


# A hand-made season of 3 weeks for the 12 rosters of the week 6 fixture. Each pair is an odd id and an even id.
# The odd id wins in odd weeks and the even id in even weeks, so every team alternates and no team has a streak.
# Each pair of HAND_NEXT has two odd or two even ids, so the base season has no rematch.
BASE_PAIRS = {
    1: [(1, 2), (3, 4), (5, 6), (7, 8), (9, 10), (11, 12)],
    2: [(1, 4), (3, 6), (5, 8), (7, 10), (9, 12), (2, 11)],
    3: [(1, 6), (3, 8), (5, 10), (7, 12), (2, 9), (4, 11)],
}
HAND_NEXT = [(1, 3), (2, 4), (5, 7), (6, 8), (9, 11), (10, 12)]


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
            winner, loser = (a, b) if a % 2 == number % 2 else (b, a)
            if (number, (a, b)) in flips:
                winner, loser = loser, winner
            week_scores[winner], week_scores[loser] = 110.0, 100.0
        week_scores.update({rid: x for (w, rid), x in (scores or {}).items() if w == number})
        weeks[number] = PastWeek(week=number, scores=week_scores, pairs=week_pairs, points={},
                                 projections={}, stats={}, moves=[])
    return History(week=3, weeks=weeks)


# The base standings order. No pair of HAND_NEXT has both teams in the top four.
BASE_ORDER = [1, 2, 5, 6, 3, 4, 7, 8, 9, 10, 11, 12]


def _hand_table(ranks=None, from_cut=None):
    """The ranks of BASE_ORDER unless `ranks` says so. The top six sit 5 games above the cut and the rest 5 below."""
    ranks = {**{rid: i + 1 for i, rid in enumerate(BASE_ORDER)}, **(ranks or {})}
    from_cut = from_cut or {}
    out = []
    for rid in range(1, 13):
        rank = ranks[rid]
        out.append(Standing(rank=rank, roster_id=rid, wins=0, losses=0, points_for=0.0, in_playoffs=rank <= 6,
                            games_from_cut=from_cut.get(rid, 5 if rank <= 6 else -5), schedule_strength=None,
                            strength_rank=None))
    return sorted(out, key=lambda s: s.rank)


def _game(nx, a, b):
    return next(n for n in nx if (n.a, n.b) == (a, b))


def test_the_hand_made_base_season_has_no_storyline(fixture_raw_dir):
    nx = next_week(_hand_week(fixture_raw_dir), _hand_table(), _hand_history())
    assert all(n.storylines == [] for n in nx)


def test_three_straight_head_to_head_wins_or_losses_put_a_streak_on_the_line(fixture_raw_dir):
    # The flip gives roster 1 a week 2 win over 4. Roster 1 wins weeks 1 to 3, and roster 4 loses weeks 1 to 3.
    nx = next_week(_hand_week(fixture_raw_dir), _hand_table(), _hand_history({(2, (1, 4))}))
    assert [(s.kind, s.roster_id, s.length) for s in _game(nx, 1, 3).storylines] == [("streak", 1, 3)]
    assert [(s.kind, s.roster_id, s.length) for s in _game(nx, 2, 4).storylines] == [("streak", 4, -3)]


def test_two_straight_head_to_head_wins_are_no_streak(fixture_raw_dir):
    # The flip gives roster 2 a week 3 win over 9. Roster 2 loses week 1, then wins 2 in a row.
    nx = next_week(_hand_week(fixture_raw_dir), _hand_table(), _hand_history({(3, (2, 9))}))
    assert _game(nx, 2, 4).storylines == []


def test_the_median_game_never_counts_in_the_streak(fixture_raw_dir):
    # Roster 2 scores 140 each week, over the median of 110, 105, and 105, but loses to roster 1 in week 1.
    # The median wins would make a longer run. Head-to-head alone, roster 2 has 2 wins in a row, so no streak.
    scores = {(1, 1): 150.0, (1, 2): 140.0, (2, 2): 140.0, (3, 2): 140.0}
    nx = next_week(_hand_week(fixture_raw_dir), _hand_table(), _hand_history({(3, (2, 9))}, scores))
    assert _game(nx, 2, 4).storylines == []


def test_no_history_gives_no_streak(fixture_raw_dir):
    nx = next_week(_hand_week(fixture_raw_dir), _hand_table())
    assert all(n.storylines == [] for n in nx)


# The best projected lineups for week 4, the week after the hand-made season. Roster 4 is fifth.
HAND_PROJECTED = {2: {4: 130.0}, 1: {4: 123.04}, 3: {4: 118.75}, 5: {4: 115.0}, 4: {4: 101.0}}


def test_both_teams_in_the_top_four_projected_lineups_give_a_shootout(fixture_raw_dir):
    # 1 projects 123.04 (2nd) and 3 projects 118.75 (3rd). One decimal rounds half up: 123.0 and 118.8.
    nx = next_week(_hand_week(fixture_raw_dir), _hand_table(), _hand_history(), HAND_PROJECTED)
    [s] = _game(nx, 1, 3).storylines
    assert (s.kind, s.totals) == ("shootout", (123.0, 118.8))


def test_one_team_fifth_in_projected_lineups_gives_no_shootout(fixture_raw_dir):
    # 2 projects 130 (1st), but 4 projects 101 (5th). 5 projects 115 (4th), and 7 has no projection.
    nx = next_week(_hand_week(fixture_raw_dir), _hand_table(), _hand_history(), HAND_PROJECTED)
    assert _game(nx, 2, 4).storylines == []
    assert _game(nx, 5, 7).storylines == []


def _kinds(n):
    return [(s.kind, s.roster_id, s.week, s.margin) for s in n.storylines]


def test_a_week_3_meeting_gives_a_rematch_and_revenge_for_the_loser(fixture_raw_dir):
    # Roster 3 beat 8 in week 3, 112.4 to 100, a margin of 12.4.
    week = _hand_week(fixture_raw_dir, [(3, 8)])
    nx = next_week(week, _hand_table(), _hand_history(scores={(3, 3): 112.4}))
    assert _kinds(nx[0]) == [("rematch", 3, 3, 12.4), ("revenge", 8, 3, 12.4)]


def test_the_rematch_reads_the_earliest_meeting(fixture_raw_dir):
    # Roster 8 beat 3 in week 1 by the flip, 110 to 100. Roster 3 beat 8 in week 3. Week 1 is the rematch.
    week1 = [(1, 2), (3, 8), (5, 6), (4, 7), (9, 10), (11, 12)]
    history = _hand_history({(1, (3, 8))}, pairs={1: week1})
    nx = next_week(_hand_week(fixture_raw_dir, [(3, 8)]), _hand_table(), history)
    assert _kinds(nx[0]) == [("rematch", 8, 1, 10.0), ("revenge", 3, 1, 10.0)]


def test_a_tied_meeting_gives_a_rematch_and_no_revenge(fixture_raw_dir):
    history = _hand_history(scores={(3, 3): 100.0, (3, 8): 100.0})
    nx = next_week(_hand_week(fixture_raw_dir, [(3, 8)]), _hand_table(), history)
    assert _kinds(nx[0]) == [("rematch", None, 3, 0.0)]


def test_near_the_cut_names_the_teams_within_one_game(fixture_raw_dir):
    # Roster 1 is 1 game above the cut. Rosters 2 and 4 are at the cut and 1 below. Roster 5 is 2 above.
    table = _hand_table(from_cut={1: 1, 2: 0, 4: -1, 5: 2})
    nx = next_week(_hand_week(fixture_raw_dir), table)
    assert [(s.kind, s.teams) for s in _game(nx, 1, 3).storylines] == [("cut", [1])]
    assert [(s.kind, s.teams) for s in _game(nx, 2, 4).storylines] == [("cut", [2, 4])]
    assert _game(nx, 5, 7).storylines == []


def test_both_teams_ranked_1_to_4_meet_at_the_top_of_the_table(fixture_raw_dir):
    # Roster 3 moves to 4th and roster 6 to 5th: 1st meets 4th, and 5th meets 8th.
    nx = next_week(_hand_week(fixture_raw_dir), _hand_table(ranks={3: 4, 6: 5}))
    assert [s.kind for s in _game(nx, 1, 3).storylines] == ["table"]
    assert _game(nx, 6, 8).storylines == []


def test_the_top_two_games_by_storyline_score_are_must_watch(fixture_raw_dir):
    # 2v4: a 3-game loss streak for 4 and 2 at the cut, 3 + 3 = 6. Three games score 3: 1v3 (streak, gap 4),
    # 6v8 (6 near the cut, gap 4), and 9v11 (9 near the cut, gap 2). The smaller gap puts 9v11 second.
    table = _hand_table(from_cut={2: 0, 6: 1, 9: -1})
    nx = next_week(_hand_week(fixture_raw_dir), table, _hand_history({(2, (1, 4))}))
    assert [sum(s.weight for s in n.storylines) for n in nx] == [3, 6, 0, 3, 3, 0]
    assert [(n.a, n.b) for n in nx if n.must_watch] == [(2, 4), (9, 11)]
    assert all(n.reason is None for n in nx if not n.must_watch)


def test_a_tie_in_score_and_gap_goes_to_the_schedule_order(fixture_raw_dir):
    # 1v3, 2v4, and 6v8 each have one team near the cut and a gap of 4. The schedule order picks 1v3 and 2v4.
    nx = next_week(_hand_week(fixture_raw_dir), _hand_table(from_cut={1: 1, 2: 1, 6: 1}))
    assert [(n.a, n.b) for n in nx if n.must_watch] == [(1, 3), (2, 4)]


def _reason(fixture_raw_dir, pairs, table=None, history=None, projected=None):
    [n] = next_week(_hand_week(fixture_raw_dir, pairs), table or _hand_table(), history, projected)
    return n.reason


def test_the_reason_names_the_top_two_storylines_with_their_numbers(fixture_raw_dir):
    streak = _hand_history({(2, (1, 4))})
    assert _reason(fixture_raw_dir, [(2, 4)], _hand_table(from_cut={2: 0}), streak) == (
        "Pukancun on 3 puts a 3-game loss streak on the line, and All You Need Is Love sits near the cut")
    # One team leads both storylines, so the second drops the name.
    assert _reason(fixture_raw_dir, [(2, 4)], _hand_table(from_cut={4: -1}), streak) == (
        "Pukancun on 3 puts a 3-game loss streak on the line and sits near the cut")
    assert _reason(fixture_raw_dir, [(2, 4)], _hand_table(from_cut={2: 0, 4: 1})) == "Both sit near the cut"
    assert _reason(fixture_raw_dir, [(1, 3)], _hand_table(ranks={3: 4, 6: 5})) == (
        "1st and 4th meet at the top of the table")
    assert _reason(fixture_raw_dir, [(1, 3)], projected=HAND_PROJECTED) == (
        "Lineups project 123.0 and 118.8 in a projected shootout")


def test_the_reason_of_a_rematch_names_the_week_the_winner_and_the_margin(fixture_raw_dir):
    history = _hand_history(scores={(3, 3): 112.4})
    assert _reason(fixture_raw_dir, [(3, 8)], history=history) == (
        "A week 3 rematch Lil Fridge won by 12.4, and Return of T Mac seeks revenge")
    tie = _hand_history(scores={(3, 3): 100.0, (3, 8): 100.0})
    assert _reason(fixture_raw_dir, [(3, 8)], history=tie) == "A week 3 rematch that ended in a tie"


def test_two_streaks_fit_one_sentence_of_25_words_with_the_longest_names(fixture_raw_dir):
    # The flip gives 9 a week 2 win over 12: 9 wins 3 in a row and 12 loses 3 in a row. They met in week 2.
    reason = _reason(fixture_raw_dir, [(9, 12)], history=_hand_history({(2, (9, 12))}))
    assert reason == ("Maye d'force B with U puts a 3-game win streak on the line, "
                      "and Amon-Ra Dawg Your Team a 3-game loss streak")
    assert len(reason.split()) <= 25 and "." not in reason.replace("d'force", "")


def test_week_6_storylines_and_must_watch(fixture_raw_dir, fixture_history_root):
    # Hand read of the week 6 fixture with its history. Head-to-head streaks: Return of T Mac (8) won 3 in a row,
    # Unsolicited Dak Picks (11) lost 3, and London Cooking (5) won 4. Within one game of the cut: Maye (9) +1,
    # All You Need Is Love (2) +1, Brock (1) 0, Return of T Mac (8) 0, behold the lamb (10) 0. The top four
    # projected lineups for week 7 are 9 (123.01), 5 (118.8), 6 (114.5), and 8 (110.25), so no game is a shootout.
    # No two teams of next week met in weeks 1 to 6, and no game has two of the top four in the standings.
    wk, _ = _setup(fixture_raw_dir)
    h = _history(fixture_raw_dir, fixture_history_root)
    nx = next_week(wk, standings(wk, h, config=CONFIG), h, projected_totals(wk, config=CONFIG))
    assert [(n.a, n.b, [s.kind for s in n.storylines]) for n in nx] == [
        (3, 8, ["streak", "cut"]),
        (1, 9, ["cut"]),
        (10, 11, ["streak", "cut"]),
        (5, 12, ["streak"]),
        (2, 6, ["cut"]),
        (4, 7, []),
    ]
    assert [(n.a, n.b, n.reason) for n in nx if n.must_watch] == [
        (3, 8, "Return of T Mac puts a 3-game win streak on the line and sits near the cut"),
        (10, 11, "Unsolicited Dak Picks puts a 3-game loss streak on the line, and behold the lamb sits near the cut"),
    ]


def test_the_storyline_weights_come_from_the_tunables(fixture_raw_dir, monkeypatch):
    from cornerstone import facts_league, tunables
    assert tunables.STORYLINE_WEIGHTS == {"streak": 3, "cut": 3, "shootout": 2, "table": 2, "rematch": 1, "revenge": 1}
    monkeypatch.setattr(facts_league, "STORYLINE_WEIGHTS", {**tunables.STORYLINE_WEIGHTS, "cut": 7})
    nx = next_week(_hand_week(fixture_raw_dir), _hand_table(from_cut={1: 1}))
    assert [s.weight for s in _game(nx, 1, 3).storylines] == [7]


def test_week_7_must_watch_games_and_reasons():
    # Week 7 of 2026, read by hand: Return of T Mac (8) won 4 head-to-head games in a row, Bo Girds (6) and
    # To Infinity and Bijan (7) each lost 3. Return of T Mac is at the cut and behold the lamb (10) 1 below.
    # 6v7 scores 6 on two streaks, and 8v10 scores 6 on a streak and the cut. Every other game scores 3.
    season_root = Path(__file__).parents[1] / "data" / "2026"
    if not (season_root / "week-07" / "raw").exists():
        pytest.skip("saved week 7 is not on this machine")
    raw = load_raw(season_root / "week-07" / "raw")
    wk = parse_week(raw)
    history = load_history(season_root / "history", raw, 7)
    nx = next_week(wk, standings(wk, history, config=CONFIG), history, projected_totals(wk, config=CONFIG))
    assert [(n.a, n.b, n.reason) for n in nx if n.must_watch] == [
        (8, 10, "Return of T Mac puts a 4-game win streak on the line, and both sit near the cut"),
        (6, 7, "Bo Girds puts a 3-game loss streak on the line, and To Infinity and Bijan a 3-game loss streak"),
    ]


# The key starter rule. A roster maps each player on it now to his position.
KEY_ROSTER = {"qb": "QB", "rb": "RB", "wr": "WR", "te": "TE", "k": "K", "def": "DEF"}


def test_a_key_starter_started_3_of_the_last_4_weeks():
    weeks = [["qb", "rb"], ["qb", "rb"], ["qb"], ["qb", "rb"]]
    assert key_starters(weeks, KEY_ROSTER) == {"qb", "rb"}


def test_2_of_the_last_4_weeks_is_not_a_key_starter():
    weeks = [["rb"], ["qb", "rb"], ["qb"], ["wr"]]
    assert key_starters(weeks, KEY_ROSTER) == set()


def test_a_start_before_the_last_4_weeks_does_not_count():
    weeks = [["wr"], ["wr"], ["wr"], ["qb"], ["qb"], ["qb"]]
    assert key_starters(weeks, KEY_ROSTER) == {"qb"}


def test_with_3_weeks_2_starts_make_a_key_starter():
    weeks = [["qb", "rb"], ["qb"], ["rb", "wr"]]
    assert key_starters(weeks, KEY_ROSTER) == {"qb", "rb"}


def test_with_2_weeks_2_starts_make_a_key_starter():
    assert key_starters([["qb", "rb"], ["qb"]], KEY_ROSTER) == {"qb"}


def test_with_1_week_no_player_is_a_key_starter():
    assert key_starters([["qb", "rb", "wr"]], KEY_ROSTER) == set()
    assert key_starters([], KEY_ROSTER) == set()


def test_a_flex_start_counts():
    # The starters list holds the flex slot too, so the third back in the list is a start.
    weeks = [["qb", "rb2", "rb"], ["qb", "rb2", "rb"], ["qb", "rb2", "rb"], ["qb", "rb2"]]
    assert key_starters(weeks, {**KEY_ROSTER, "rb2": "RB"}) == {"qb", "rb", "rb2"}


def test_a_player_not_on_the_roster_now_is_not_a_key_starter():
    weeks = [["qb", "gone"], ["qb", "gone"], ["qb", "gone"], ["qb", "gone"]]
    assert key_starters(weeks, KEY_ROSTER) == {"qb"}


def test_a_new_add_is_not_a_key_starter():
    # The add has no starts on his new roster, whatever he did on his old one.
    weeks = [["qb"], ["qb"], ["qb"], ["qb", "add"]]
    assert key_starters(weeks, {**KEY_ROSTER, "add": "WR"}) == {"qb"}


def test_a_kicker_and_a_defense_are_never_key_starters():
    weeks = [["k", "def", "te"]] * 4
    assert key_starters(weeks, KEY_ROSTER) == {"te"}
