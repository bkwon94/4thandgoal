"""
Tests for the drop value, the drop lines, the drop facts, and the Butterfingers award.
They use the recorded week 6 nflverse files and the recorded Sleeper data.
"""
from cornerstone.facts_nflverse import drop_lines, drop_value
from cornerstone.models import NflverseWeek
from cornerstone.nflverse import nflverse_week
from cornerstone.parse import parse_week
from cornerstone.sheet import build_bundle
from cornerstone.sleeper import load_raw


def test_drop_value_golden(nfl_week6, fixture_raw_dir):
    wk = parse_week(load_raw(fixture_raw_dir))
    assert [drop_value(p, wk.scoring) for p in nfl_week6.drops["12501"]] == [4.4, 8.8, 1.0]


def test_negative_air_yards_count_as_zero(nfl_week6, fixture_raw_dir):
    wk = parse_week(load_raw(fixture_raw_dir))
    assert [drop_value(p, wk.scoring) for p in nfl_week6.drops["8150"]] == [0.9, 0.5]


def test_drop_lines_sum_value_and_end_zone(nfl_week6, fixture_raw_dir):
    wk = parse_week(load_raw(fixture_raw_dir))
    golden = next(l for l in drop_lines(wk, nfl_week6) if l.player_id == "12501")
    assert (golden.drops, golden.targets, golden.value, golden.end_zone) == (3, 13, 14.2, 1)


def test_drop_facts(dbundle):
    f = dbundle.sheet.facts
    assert f["D.12501"].text == "Matthew Golden dropped 3 of 13 targets this week."
    assert f["D.12501.value"].text == (
        "Matthew Golden's drops were worth about 14.2 points by the drop value method, with 1 in the end zone.")
    assert f["M4.dropswing"].text == (
        "Bo Girds's starters dropped 7 passes worth about 17.8, at least the margin of 5.34.")
    assert f["W.drops"].text == ("Most drops this week: Matthew Golden (Bo Girds), 3; "
        "Chris Olave (All You Need Is Love), 3; CeeDee Lamb (behold the lamb), 2.")
    assert dbundle.data.drop_source == "nflverse"


def test_drop_facts_are_in_their_chapters(dbundle):
    chapters = {c.key: c for c in dbundle.sheet.chapters}
    assert "W.drops" in chapters["awards"].fact_ids
    assert "D.12501" in chapters["recap_4"].fact_ids
    assert "M4.dropswing" in chapters["recap_4"].fact_ids


def test_butterfingers(dbundle):
    a = next(x for x in dbundle.data.awards if x.key == "butterfingers")
    assert a.line.name == "Matthew Golden" and "14.2" in dbundle.sheet.facts["AW.butterfingers"].text


def test_drops_degrade_to_sleeper_count(tbundle):
    f = tbundle.sheet.facts
    assert f["D.9487"].text.startswith("Parker Washington dropped 3 ")
    assert "D.12501.value" not in f and "M4.dropswing" not in f
    assert tbundle.data.drop_source == "sleeper"


def test_stale_nflverse_week_degrades(fixture_nflverse_dir, fixture_raw_dir, tmp_path):
    raw = load_raw(fixture_raw_dir)
    cache = tmp_path / "nflverse"
    cache.mkdir()
    for f in fixture_nflverse_dir.iterdir():
        (cache / f.name).write_bytes(f.read_bytes())
    stale = nflverse_week(2026, 7, [], raw["players"], cache, fetch=lambda url: b"")
    assert stale.drops is None
    lines = drop_lines(parse_week(raw), stale)
    assert lines and all(l.value is None and l.end_zone is None for l in lines)


def test_no_drops_gives_source_none(fixture_raw_dir):
    wk = parse_week(load_raw(fixture_raw_dir))
    wk = wk.model_copy(update={"stats": {}})
    bundle = build_bundle(wk, news=lambda pid: [])
    assert bundle.data.drop_source == "none" and bundle.data.drops == []
    assert "W.drops" not in bundle.sheet.facts
    assert not any(a.key == "butterfingers" for a in bundle.data.awards)


def test_nfl_none_equals_drops_none(fixture_raw_dir):
    wk = parse_week(load_raw(fixture_raw_dir))
    down = NflverseWeek(sources={}, gsis={}, drops=None, injuries=None)
    assert drop_lines(wk, None) == drop_lines(wk, down)
