"""
Tests for the drop value, the drop lines, the drop facts, and the unlucky and lucky award facts.
They use the recorded week 6 nflverse files and the recorded Sleeper data.
"""
from cornerstone.facts_nflverse import drop_lines, drop_value
from cornerstone.models import ExpectedGame, ExpectedPoints, NflverseWeek
from cornerstone.nflverse import nflverse_week
from cornerstone.parse import parse_week
from cornerstone.sheet import NUMBER_TOKEN, build_bundle
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
    assert f["W.drops"].text == ("Most drops this week: Matthew Golden (Bo Girds), 3 drops; "
        "Chris Olave (All You Need Is Love), 3 drops; CeeDee Lamb (behold the lamb), 2 drops.")
    assert dbundle.data.drop_source == "nflverse"


def test_drop_facts_are_in_their_chapters(dbundle):
    chapters = {c.key: c for c in dbundle.sheet.chapters}
    assert "W.drops" in chapters["awards"].fact_ids
    assert "D.12501" in chapters["recap_4"].fact_ids
    assert "M4.dropswing" in chapters["recap_4"].fact_ids


def test_drops_are_not_an_award(dbundle):
    assert [a.key for a in dbundle.data.awards] == [
        "game_changer", "top_scorer", "mvb", "underperformer", "overachiever"]
    assert "D.12501" in dbundle.sheet.facts and "M4.dropswing" in dbundle.sheet.facts


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


def test_nfl_none_equals_drops_none(fixture_raw_dir):
    wk = parse_week(load_raw(fixture_raw_dir))
    down = NflverseWeek(sources={}, gsis={}, drops=None, injuries=None)
    assert drop_lines(wk, None) == drop_lines(wk, down)


def test_pregame_fact(dbundle):
    assert dbundle.sheet.facts["I.2449.pregame"].text == (
        "Stefon Diggs was listed Questionable on the final NFL injury report before his game this week.")


def test_history_listed_this_week(dbundle):
    assert dbundle.sheet.facts["I.2449.history"].text == "Stefon Diggs has been on the NFL injury report 2 weeks."


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


def test_one_drop_is_one_pass(fixture_raw_dir):
    # Sleeper counts one drop and no targets for one starter, and no drop for any other.
    wk = parse_week(load_raw(fixture_raw_dir))
    side = wk.matchups[0].a
    line = next(l for l in side.lines if l.started)
    stats = {p: {k: v for k, v in s.items() if k not in ("rec_drop", "rec_tgt")} for p, s in wk.stats.items()}
    stats[line.player_id] = {**stats.get(line.player_id, {}), "rec_drop": 1}
    week = wk.model_copy(update={"stats": stats})
    f = build_bundle(week, news=lambda pid: []).sheet.facts
    assert f[f"D.{line.player_id}"].text == f"{line.name} dropped 1 pass this week."
    assert f["W.drops"].text == f"Most drops this week: {line.name} ({wk.teams[side.roster_id].name}), 1 drop."


def test_missing_yardline_is_not_the_end_zone(fixture_raw_dir):
    from cornerstone.models import DropPlay
    wk = parse_week(load_raw(fixture_raw_dir))
    play = DropPlay(game_id="g", play_id="p", air_yards=23.0, yardline_100=None)
    # One reception and 23 air yards, with no touchdown.
    assert drop_value(play, wk.scoring) == drop_value(play.model_copy(update={"yardline_100": 99.0}), wk.scoring)


def _expected_bundle(fixture_raw_dir, nfl_week6, games: dict[str, list[tuple[int, float]]], through_week: int = 6):
    """The week 6 sheet with hand-set expected points, by Sleeper ID, as (week, expected) per game."""
    expected = ExpectedPoints(through_week=through_week, players={
        pid: [ExpectedGame(week=w, game_id=f"2026_{w:02d}_{pid}", expected=x) for w, x in played]
        for pid, played in games.items()})
    nfl = nfl_week6.model_copy(update={"expected": expected})
    return build_bundle(parse_week(load_raw(fixture_raw_dir)), news=lambda pid: [], nfl=nfl)


# Started: Derrick Henry 4.5, Davante Adams 5.4, Stefon Diggs 13.4, Mike Evans 10.9.
# Bench: Jakobi Meyers 10.8, Alvin Kamara 13.9. Each bench gap is larger than any started gap.
HAND_SET = {
    "3198": [(5, 30.0), (6, 16.5)],
    "2133": [(6, 9.0)],
    "2449": [(6, 7.0)],
    "2216": [(6, 8.9)],
    "5947": [(6, 30.0)],
    "4035": [(6, 0.5)],
}


def test_unlucky_fact_names_the_starter_furthest_under(fixture_raw_dir, nfl_week6):
    f = _expected_bundle(fixture_raw_dir, nfl_week6, HAND_SET).sheet.facts["AW.unlucky"]
    assert f.text == ("Unlucky: Derrick Henry (RB, BAL), Lil Fridge. "
                      "Derrick Henry scored 4.5 on 16.5 expected points, 12 under.")
    assert {"4.5", "16.5", "12"} <= set(f.numbers)
    assert f.players == ["Derrick Henry"]


def test_lucky_fact_names_the_starter_furthest_over(fixture_raw_dir, nfl_week6):
    f = _expected_bundle(fixture_raw_dir, nfl_week6, HAND_SET).sheet.facts["AW.lucky"]
    assert f.text == ("Lucky: Stefon Diggs (WR, WAS), Lil Fridge. "
                      "Stefon Diggs scored 13.4 on 7 expected points, 6.4 over.")
    assert {"13.4", "7", "6.4"} <= set(f.numbers)


def test_no_expected_award_under_the_floor(fixture_raw_dir, nfl_week6):
    # Adams is 3.6 under and Evans 2 over, so neither clears the floor of 5.
    b = _expected_bundle(fixture_raw_dir, nfl_week6, {"2133": [(6, 9.0)], "2216": [(6, 8.9)]})
    assert "AW.unlucky" not in b.sheet.facts and "AW.lucky" not in b.sheet.facts
    assert "awards" in {c.key for c in b.sheet.chapters}


def test_a_gap_of_exactly_the_floor_wins(fixture_raw_dir, nfl_week6):
    b = _expected_bundle(fixture_raw_dir, nfl_week6, {"2133": [(6, 10.4)], "2216": [(6, 5.9)]})
    assert "Davante Adams" in b.sheet.facts["AW.unlucky"].text
    assert "Mike Evans" in b.sheet.facts["AW.lucky"].text


def test_a_lagged_file_gives_no_expected_award(fixture_raw_dir, nfl_week6):
    b = _expected_bundle(fixture_raw_dir, nfl_week6, {"3198": [(5, 30.0)], "2449": [(5, 1.0)]}, through_week=5)
    assert "AW.unlucky" not in b.sheet.facts and "AW.lucky" not in b.sheet.facts


def test_a_bench_player_never_gets_an_expected_award(fixture_raw_dir, nfl_week6):
    b = _expected_bundle(fixture_raw_dir, nfl_week6, {"5947": [(6, 30.0)], "4035": [(6, 0.5)]})
    assert "AW.unlucky" not in b.sheet.facts and "AW.lucky" not in b.sheet.facts


def test_missing_expected_data_builds_without_the_awards(fixture_raw_dir, nfl_week6):
    nfl = nfl_week6.model_copy(update={"expected": None})
    b = build_bundle(parse_week(load_raw(fixture_raw_dir)), news=lambda pid: [], nfl=nfl)
    assert "AW.unlucky" not in b.sheet.facts and "AW.lucky" not in b.sheet.facts
    assert "awards" in {c.key for c in b.sheet.chapters}


def test_only_the_awards_chapter_cites_the_expected_awards(fixture_raw_dir, nfl_week6):
    b = _expected_bundle(fixture_raw_dir, nfl_week6, HAND_SET)
    citing = {c.key for c in b.sheet.chapters if {"AW.unlucky", "AW.lucky"} & set(c.fact_ids)}
    assert citing == {"awards"}
    awards = next(c for c in b.sheet.chapters if c.key == "awards")
    assert {"AW.unlucky", "AW.lucky"} <= set(awards.fact_ids)


def test_every_number_in_an_expected_award_text_is_in_its_numbers(fixture_raw_dir, nfl_week6):
    facts = _expected_bundle(fixture_raw_dir, nfl_week6, HAND_SET).sheet.facts
    for fid in ("AW.unlucky", "AW.lucky"):
        for token in NUMBER_TOKEN.findall(facts[fid].text):
            assert token in facts[fid].numbers, (fid, token)
