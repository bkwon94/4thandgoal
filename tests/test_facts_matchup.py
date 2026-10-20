"""
Tests for the matchup facts and the median game.
They run on the real week 6 fixture and check exact numbers.
"""
from cornerstone.facts_matchup import matchup_facts, median_facts
from cornerstone.models import r2, sub
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
    assert "Kyren Williams" in {l.name for l in f.drivers}


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
        assert all(l.projection is not None for l in f.drivers)


def test_median(fixture_raw_dir):
    wk = _wk(fixture_raw_dir)
    med = median_facts(wk)
    assert round(med.median, 2) == 106.83 and len(med.above) == 6
    assert wk.teams[med.closest_above[0]].name == "Bo Girds"
    assert round(med.closest_above[1], 2) == 2.79
    assert wk.teams[med.closest_below[0]].name == "Amon-Ra Dawg Your Team"
