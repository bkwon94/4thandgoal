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
from cornerstone.history import load_history
from cornerstone.models import History
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


def _motw_with(fixture_raw_dir, margins, before=None, far_from_cut=()):
    """Run the pick on the week 6 fixture with set margins, ranks before, and cut distance."""
    wk, mf = _setup(fixture_raw_dir)
    mf = [f.model_copy(update={"margin": margins.get(f.matchup_id, f.margin)}) for f in mf]
    table = [
        s.model_copy(update={"games_from_cut": 3}) if s.roster_id in far_from_cut else s
        for s in standings(wk)
    ]
    return matchup_of_the_week(wk, mf, table, {**ranks_before(wk, table), **(before or {})})


def test_motw_label_is_the_upset_when_the_pick_leads_only_there(fixture_raw_dir):
    # Matchup 3 is the closest game. Matchup 1 wins on total and has the biggest upset.
    # Closeness is its largest weighted score, but it does not lead in closeness.
    pick = _motw_with(fixture_raw_dir, {1: 10, 3: 5}, {3: 12, 1: 1})
    assert pick.matchup_id == 1 and pick.reason == "Upset"
    assert pick.scores["closeness"] > pick.scores["upset"]


def test_motw_label_is_closest_finish_for_the_closest_game(fixture_raw_dir):
    # Matchup 4 has the smallest margin and also the biggest upset. Closeness weighs more.
    wk, mf = _setup(fixture_raw_dir)
    assert min(mf, key=lambda f: f.margin).matchup_id == 4
    pick = matchup_of_the_week(wk, mf, standings(wk))
    assert pick.matchup_id == 4 and pick.reason == "Closest Finish"


def test_motw_label_falls_back_to_the_largest_score_with_no_lead(fixture_raw_dir):
    # Matchup 5 is second in closeness, upset, and table, and far from the cut.
    # It leads in no signal, so its largest weighted score names it.
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
