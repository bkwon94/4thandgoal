"""
Tests for the matchup facts and the median game.
They run on the real week 6 fixture and check exact numbers.
"""
from cornerstone.facts_matchup import matchup_facts, median_facts
from cornerstone.models import Matchup, PlayerLine, Side, r2, sub
from cornerstone.parse import parse_week
from cornerstone.sleeper import load_raw


def _wk(d):
    return parse_week(load_raw(d))


def test_r2_rounds_half_up():
    # round(2.785, 2) gives 2.78 because of binary floats.
    assert r2(2.785) == 2.79


def test_sub_uses_exact_decimal_difference():
    assert sub(109.61, 106.825) == 2.79


def test_closest_matchup_facts(fixture_raw_dir):
    wk = _wk(fixture_raw_dir)
    m = next(m for m in wk.matchups if m.matchup_id == 4)
    f = matchup_facts(m, wk.moves, 6)
    assert wk.teams[f.winner].name == "behold the lamb"
    assert (f.score_w, f.score_l, f.margin) == (114.95, 109.61, 5.34)
    bo = next(r for r in f.top_scorer if wk.teams[r].name == "Bo Girds")
    assert f.top_scorer[bo].name == "Tyler Shough"
    assert "Kyren Williams" in {line.name for line in f.drivers}


def test_blowout_top_scorer_is_purdy_not_defense(fixture_raw_dir):
    wk = _wk(fixture_raw_dir)
    m = next(m for m in wk.matchups if m.matchup_id == 1)
    f = matchup_facts(m, wk.moves, 6)
    brock = next(r for r in f.top_scorer if wk.teams[r].name == "Brock ‘N’ Roll")
    assert f.top_scorer[brock].name == "Brock Purdy"


def test_no_projection_never_drives(fixture_raw_dir):
    wk = _wk(fixture_raw_dir)
    for m in wk.matchups:
        f = matchup_facts(m, wk.moves, 6)
        assert all(line.projection is not None for line in f.drivers)


def test_median(fixture_raw_dir):
    wk = _wk(fixture_raw_dir)
    med = median_facts(wk)
    assert round(med.median, 2) == 106.83 and len(med.above) == 6
    assert wk.teams[med.closest_above[0]].name == "Bo Girds"
    assert round(med.closest_above[1], 2) == 2.79
    assert wk.teams[med.closest_below[0]].name == "Amon-Ra Dawg Your Team"


def _matchup_4(fixture_raw_dir):
    wk = _wk(fixture_raw_dir)
    m = next(m for m in wk.matchups if m.matchup_id == 4)
    return wk, m, matchup_facts(m, wk.moves, 6)


def test_bench_regret_only_on_losing_side(fixture_raw_dir):
    _, m, f = _matchup_4(fixture_raw_dir)
    loser = next(s for s in (m.a, m.b) if s.roster_id == f.loser)
    loser_ids = {line.player_id for line in loser.lines}
    for bench, starter in f.bench_regret:
        assert bench.player_id in loser_ids and starter.player_id in loser_ids
        assert not bench.started and starter.started
        assert bench.position == starter.position
        assert bench.points - starter.points > f.margin


def test_swing_is_winning_side_above_margin(fixture_raw_dir):
    _, m, f = _matchup_4(fixture_raw_dir)
    winner = next(s for s in (m.a, m.b) if s.roster_id == f.winner)
    winner_ids = {line.player_id for line in winner.lines if line.started}
    assert f.swing
    assert all(line.player_id in winner_ids and line.points > f.margin for line in f.swing)


def test_drivers_are_started_lines(fixture_raw_dir):
    wk = _wk(fixture_raw_dir)
    for m in wk.matchups:
        assert all(line.started for line in matchup_facts(m, wk.moves, 6).drivers)


def test_recent_moves_are_started_players_on_the_side(fixture_raw_dir):
    wk, m, f = _matchup_4(fixture_raw_dir)
    started = {(s.roster_id, line.player_id) for s in (m.a, m.b) for line in s.lines if line.started}
    assert f.recent_moves
    assert all((mv.roster_id, mv.player_id) in started for mv in f.recent_moves)
    assert all(mv.week in (6, 5) for mv in f.recent_moves)


def _line(pid, points, started, projection=10.0):
    return PlayerLine(
        player_id=pid, name=pid, position="RB", nfl_team=None, points=points,
        projection=projection, season_avg=None, started=started, slot="RB" if started else None,
    )


def test_tie_has_no_winner_and_no_causes():
    a = Side(roster_id=1, points=100.0, lines=[_line("a1", 100.0, True), _line("a2", 50.0, False)])
    b = Side(roster_id=2, points=100.0, lines=[_line("b1", 100.0, True), _line("b2", 50.0, False)])
    f = matchup_facts(Matchup(matchup_id=1, a=a, b=b), [], 6)
    assert f.winner is None and f.loser is None and f.margin == 0.0
    assert f.drivers == [] and f.swing == [] and f.bench_regret == []
