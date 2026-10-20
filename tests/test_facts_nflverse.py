"""
Tests for the drop value, the drop lines, the drop facts, and the Butterfingers award.
They use the recorded week 6 nflverse files and the recorded Sleeper data.
"""
from cornerstone.facts_league import awards
from cornerstone.facts_nflverse import drop_lines, drop_value
from cornerstone.models import DropLine, NflverseWeek
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


def test_butterfingers_reason_says_tied_on_a_tie(dbundle):
    assert "tied for the most of any started player" in dbundle.sheet.facts["AW.butterfingers"].text


def test_butterfingers_reason_after_a_skip(hbundle, fixture_raw_dir):
    # The top scorer holds an earlier award, so the next line wins with fewer drops.
    wk = parse_week(load_raw(fixture_raw_dir))
    top = next(a for a in hbundle.data.awards if a.key == "top_scorer")
    other = next(l for m in wk.matchups for s in (m.a, m.b) for l in s.lines
                 if l.started and l.player_id != top.line.player_id)
    where = {l.player_id: (s.roster_id, m.matchup_id)
             for m in wk.matchups for s in (m.a, m.b) for l in s.lines}
    lines = [DropLine(player_id=p, roster_id=where[p][0], matchup_id=where[p][1],
                      drops=n, targets=None, value=None, end_zone=None)
             for p, n in ((top.line.player_id, 5), (other.player_id, 2))]
    award = next(a for a in awards(wk, hbundle.data.matchups, lines) if a.key == "butterfingers")
    assert award.line.player_id == other.player_id and award.skipped == [top.line.name]
    assert award.reason == (f"{other.name} dropped 2 passes, "
                            "the most among started players with no other award this week.")


def test_pregame_fact(dbundle):
    assert dbundle.sheet.facts["I.2449.pregame"].text == (
        "Stefon Diggs was listed Questionable on the final NFL injury report before his game this week.")


def test_history_listed_this_week(dbundle):
    assert dbundle.sheet.facts["I.2449.history"].text == "Stefon Diggs has been on the report 2 weeks."


def test_history_returned_this_week(dbundle):
    assert dbundle.sheet.facts["I.5927.history"].text == (
        "Terry McLaurin was on the NFL injury report in 2 earlier weeks this season and plays this week.")
    assert "I.5927.pregame" not in dbundle.sheet.facts


def test_no_return_claim_without_games_played(fixture_raw_dir, fixture_history_root, nfl_week6):
    raw = load_raw(fixture_raw_dir)
    wk = parse_week(raw)
    stats = {**wk.stats, "5927": {**wk.stats.get("5927", {}), "gp": 0}}
    bundle = build_bundle(wk.model_copy(update={"stats": stats}), news=lambda pid: [], nfl=nfl_week6)
    assert "I.5927.history" not in bundle.sheet.facts


def test_no_injury_facts_without_the_file(tbundle):
    assert not any(fid.startswith("I.") for fid in tbundle.sheet.facts)


def test_injury_facts_are_in_their_chapters(dbundle):
    chapters = {c.key: c for c in dbundle.sheet.chapters}
    assert any("I.2449.pregame" in c.fact_ids for c in chapters.values())


def test_got_fact_carries_the_pregame_status(fixture_raw_dir, fixture_history_root, nfl_week6):
    from conftest import _trade_bundle
    nfl = nfl_week6.model_copy(update={"injuries": {**nfl_week6.injuries, "12490": {6: "Questionable"}}})
    f = _trade_bundle(fixture_raw_dir, fixture_history_root, nfl=nfl).sheet.facts
    assert "Bhayshul Tuten was listed Questionable on the final NFL injury report" in f["T5.12.got.12490"].text
