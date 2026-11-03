"""
Tests for the drop value, the drop lines, the drop facts, the unlucky and lucky award facts, the shootout
facts, and the leader volume facts.
They use the recorded week 6 nflverse files and the recorded Sleeper data.
"""
import re
from pathlib import Path

import pytest

from cornerstone.config import cornerstone_config
from cornerstone.facts_nflverse import EXPECTED_AWARD_FLOOR, drop_lines, drop_value, volume_ranks
from cornerstone.models import ExpectedGame, ExpectedPoints, NflverseWeek, TeamWeek, UsageWeek
from cornerstone.nflverse import nflverse_week
from cornerstone.parse import parse_week
from cornerstone.provider.sleeper import load_raw
from cornerstone.sheet import NUMBER_TOKEN, build_bundle, fmt

CONFIG = cornerstone_config()


def test_drop_value_golden(nfl_week6, fixture_raw_dir):
    wk = parse_week(load_raw(fixture_raw_dir))
    assert [drop_value(p, wk.scoring) for p in nfl_week6.drops["12501"]] == [4.4, 8.8, 1.0]


def test_negative_air_yards_count_as_zero(nfl_week6, fixture_raw_dir):
    wk = parse_week(load_raw(fixture_raw_dir))
    assert [drop_value(p, wk.scoring) for p in nfl_week6.drops["8150"]] == [0.9, 0.5]


def test_drop_lines_sum_value_and_end_zone(nfl_week6, fixture_raw_dir):
    wk = parse_week(load_raw(fixture_raw_dir))
    golden = next(line for line in drop_lines(wk, nfl_week6) if line.player_id == "12501")
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
    stale = nflverse_week(2026, 7, [], raw.players, cache, fetch=lambda url: b"")
    assert stale.drops is None
    lines = drop_lines(parse_week(raw), stale)
    assert lines and all(line.value is None and line.end_zone is None for line in lines)


def test_no_drops_gives_source_none(fixture_raw_dir):
    wk = parse_week(load_raw(fixture_raw_dir))
    wk = wk.model_copy(update={"stats": {}})
    bundle = build_bundle(wk, news=lambda pid: [], config=CONFIG)
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
    bundle = build_bundle(wk.model_copy(update={"stats": stats}), news=lambda pid: [], nfl=nfl_week6, config=CONFIG)
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
    line = next(line for line in side.lines if line.started)
    stats = {p: {k: v for k, v in s.items() if k not in ("rec_drop", "rec_tgt")} for p, s in wk.stats.items()}
    stats[line.player_id] = {**stats.get(line.player_id, {}), "rec_drop": 1}
    week = wk.model_copy(update={"stats": stats})
    f = build_bundle(week, news=lambda pid: [], config=CONFIG).sheet.facts
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
    return build_bundle(parse_week(load_raw(fixture_raw_dir)), news=lambda pid: [], nfl=nfl, config=CONFIG)


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
    b = build_bundle(parse_week(load_raw(fixture_raw_dir)), news=lambda pid: [], nfl=nfl, config=CONFIG)
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
        # The verifier removes the names first, so a digit in a team name is not a number.
        bare = facts[fid].text
        for name in (*facts[fid].teams, *facts[fid].players):
            bare = bare.replace(name, "")
        for token in NUMBER_TOKEN.findall(bare):
            assert token in facts[fid].numbers, (fid, token)


def test_a_starter_with_an_award_can_win_an_expected_award(fixture_raw_dir, nfl_week6):
    # Bijan Robinson is the Underperformer and Tre Tucker the Game Changer and the Overachiever.
    # Each gets the largest gap on his side.
    games = {**HAND_SET, "9509": [(6, 30.0)], "10213": [(6, 2.0)]}
    facts = _expected_bundle(fixture_raw_dir, nfl_week6, games).sheet.facts
    assert "Bijan Robinson" in facts["AW.unlucky"].text
    assert "Tre Tucker" in facts["AW.lucky"].text


def test_the_vocabulary_rule_lines_carry_the_floor():
    vocabulary = (Path(__file__).parents[1] / "src" / "cornerstone" / "prompts" / "vocabulary.md").read_text()
    floor = fmt(EXPECTED_AWARD_FLOOR)
    unlucky = next(line for line in vocabulary.splitlines() if line.startswith("- **Unlucky**"))
    lucky = next(line for line in vocabulary.splitlines() if line.startswith("- **Lucky**"))
    assert f"at least {floor} under" in unlucky
    assert f"at least {floor} over" in lucky


def _team_weeks(*weeks: tuple[int, int, float]) -> list[TeamWeek]:
    # Only the plays and the pass_oe sum feed the pass rate over expected.
    return [TeamWeek(week=w, plays=plays, passes=0, rushes=0, rush_successes=0, neutral_plays=0, neutral_passes=0,
                     pass_oe=pass_oe) for w, plays, pass_oe in weeks]


def _shootout_bundle(fixture_raw_dir, environment, next_games=(("KC", "SEA"), ("DAL", "PHI"), ("NYG", "HOU"))):
    wk = parse_week(load_raw(fixture_raw_dir))
    nfl = NflverseWeek(sources={}, gsis={}, drops=None, injuries=None, environment=environment,
                       next_games=None if next_games is None else list(next_games))
    return build_bundle(wk, news=lambda pid: [], nfl=nfl, config=CONFIG)


# KC has a positive pass rate over expected over its last 3 games, though week 3 had many runs: 1530 over 300
# plays is 5.1. SEA has 2 games, so its rate is 640 over 200 plays, 3.2. PHI sits at 0, ARI is under 0, and NYG
# has no games. No week 6 starter plays for MIA or MIN.
SHOOTOUT_ENVIRONMENT = {
    "KC": _team_weeks((3, 100, -9000.0), (4, 100, 600.0), (5, 100, 300.0), (6, 100, 630.0)),
    "SEA": _team_weeks((5, 100, 400.0), (6, 100, 240.0)),
    "DAL": _team_weeks((4, 100, 500.0), (5, 100, 500.0), (6, 100, 500.0)),
    "PHI": _team_weeks((4, 100, 100.0), (5, 100, -200.0), (6, 100, 100.0)),
    "HOU": _team_weeks((6, 100, 800.0)),
    "DEN": _team_weeks((6, 100, 300.0)),
    "ARI": _team_weeks((6, 100, -150.0)),
    "SF": _team_weeks((6, 100, 200.0)),
    "LAR": _team_weeks((6, 100, 100.0)),
    "MIA": _team_weeks((6, 100, 400.0)),
    "MIN": _team_weeks((6, 100, 404.0)),
}


def _shootout_ids(bundle) -> list[str]:
    return [fid for fid in bundle.sheet.facts if fid.startswith("NX.shootout.")]


def test_a_game_where_both_teams_have_a_positive_pass_rate_over_expected_is_a_shootout(fixture_raw_dir):
    f = _shootout_bundle(fixture_raw_dir, SHOOTOUT_ENVIRONMENT).sheet.facts["NX.shootout.KCvSEA"]
    assert f.text == (
        "KC at SEA next week is a shootout. KC's pass rate over expected is 5.1 percentage points over its last "
        "3 games. SEA's is 3.2 over its last 2 games. 8 league starters on 6 rosters: "
        "Lil Fridge (Travis Kelce, Jaxon Smith-Njigba); Amon-Ra Dawg Your Team (Emanuel Wilson); "
        "Bo Girds (Kenneth Walker); "
        "London Cooking (Seattle Seahawks); To Infinity and Bijan (Patrick Mahomes); "
        "Pukancun on 3 (Xavier Worthy, Kansas City Chiefs).")
    assert f.teams == [
        "Lil Fridge", "Amon-Ra Dawg Your Team", "Bo Girds", "London Cooking", "To Infinity and Bijan", "Pukancun on 3"]
    assert "Patrick Mahomes" in f.players and "Seattle Seahawks" in f.players


def test_a_game_with_a_team_at_or_under_zero_or_with_no_games_is_no_shootout(fixture_raw_dir):
    assert _shootout_ids(_shootout_bundle(fixture_raw_dir, SHOOTOUT_ENVIRONMENT)) == ["NX.shootout.KCvSEA"]


def test_a_game_with_one_team_under_zero_is_no_shootout(fixture_raw_dir):
    bundle = _shootout_bundle(fixture_raw_dir, SHOOTOUT_ENVIRONMENT, [("DEN", "ARI"), ("ARI", "DEN")])
    assert _shootout_ids(bundle) == []


def test_a_rate_that_rounds_to_zero_is_no_shootout(fixture_raw_dir):
    # MIA's rate is 4 over 100 plays, 0.04, which the fact would show as 0.0.
    environment = {**SHOOTOUT_ENVIRONMENT, "MIA": _team_weeks((6, 100, 4.0))}
    assert _shootout_ids(_shootout_bundle(fixture_raw_dir, environment, [("MIA", "MIN")])) == []


def test_a_sheet_with_a_shootout_and_no_league_starter_says_so(fixture_raw_dir):
    f = _shootout_bundle(fixture_raw_dir, SHOOTOUT_ENVIRONMENT, [("MIA", "MIN")]).sheet.facts["NX.shootout.MIAvMIN"]
    assert f.text == (
        "MIA at MIN next week is a shootout. MIA's pass rate over expected is 4.0 percentage points over its last "
        "game. MIN's is 4.0 over its last game. No league starter plays in that game.")
    assert f.teams == [] and f.players == [] and f.numbers == ["4.0", "4.0"]


def test_a_shootout_names_at_most_8_starters(fixture_raw_dir):
    f = _shootout_bundle(fixture_raw_dir, SHOOTOUT_ENVIRONMENT, [("SF", "LAR")]).sheet.facts["NX.shootout.SFvLAR"]
    assert f.text.endswith("; and 2 more.")
    assert " 10 league starters on 7 rosters: " in f.text and len(f.players) == 8


def test_a_team_with_one_game_reads_as_its_last_game(fixture_raw_dir):
    games = [("NYG", "HOU"), ("HOU", "KC")]
    f = _shootout_bundle(fixture_raw_dir, SHOOTOUT_ENVIRONMENT, games).sheet.facts
    assert "HOU's pass rate over expected is 8.0 percentage points over its last game." in f["NX.shootout.HOUvKC"].text


def test_every_number_token_in_a_shootout_fact_is_in_its_numbers(fixture_raw_dir):
    f = _shootout_bundle(fixture_raw_dir, SHOOTOUT_ENVIRONMENT).sheet.facts["NX.shootout.KCvSEA"]
    text = f.text
    for name in sorted([*f.teams, *f.players], key=len, reverse=True):
        text = text.replace(name, "")
    assert set(re.findall(r"\d+(?:\.\d+)?", text)) == {"5.1", "3", "3.2", "2", "8", "6"}
    assert {"5.1", "3", "3.2", "2", "8", "6"} <= set(f.numbers)


def test_only_the_next_week_chapter_cites_the_shootout_facts(fixture_raw_dir):
    for chapter in _shootout_bundle(fixture_raw_dir, SHOOTOUT_ENVIRONMENT).sheet.chapters:
        cited = "NX.shootout.KCvSEA" in chapter.fact_ids
        assert cited == (chapter.key == "next_week"), chapter.key


def test_a_sheet_with_the_environment_missing_has_no_shootout_fact(fixture_raw_dir):
    assert _shootout_ids(_shootout_bundle(fixture_raw_dir, None)) == []
    assert _shootout_ids(_shootout_bundle(fixture_raw_dir, SHOOTOUT_ENVIRONMENT, next_games=None)) == []
    wk = parse_week(load_raw(fixture_raw_dir))
    assert _shootout_ids(build_bundle(wk, news=lambda pid: [], config=CONFIG)) == []


def _usage(week: int = 6, wopr: int | None = None, carry_share: int = 0) -> UsageWeek:
    return UsageWeek(week=week, team="KC", snaps=None, snap_share=None, targets=0, target_share=0, carries=0,
                     carry_share=carry_share, red_zone_touches=0, wopr=wopr)


def _volume_facts(fixture_raw_dir, usage):
    wk = parse_week(load_raw(fixture_raw_dir))
    nfl = NflverseWeek(sources={}, gsis={}, drops=None, injuries=None, usage=usage)
    return build_bundle(wk, news=lambda pid: [], nfl=nfl, config=CONFIG)


def _bench_id(fixture_raw_dir, position: str) -> str:
    wk = parse_week(load_raw(fixture_raw_dir))
    return next(line.player_id for m in wk.matchups for s in (m.a, m.b) for line in s.lines
                if not line.started and line.position == position)


@pytest.fixture
def vbundle(fixture_raw_dir):
    usage = {
        # Wide receivers: Lamb ties Nabers, so both take the same rank. Golden has no WOPR, so no rank.
        "10213": [_usage(wopr=60)],
        "11632": [_usage(wopr=85)],
        "6786": [_usage(wopr=85)],
        "12501": [_usage(wopr=None)],
        # A leader with a row but no WOPR.
        "13274": [_usage(wopr=None)],
        # A bench receiver and an earlier week do not count.
        _bench_id(fixture_raw_dir, "WR"): [_usage(wopr=140)],
        "2449": [_usage(week=5, wopr=120), _usage(wopr=10)],
        # Running backs: Henry ties Walker, so both take the same rank.
        "4034": [_usage(carry_share=80)],
        "3198": [_usage(carry_share=72)],
        "8151": [_usage(carry_share=72)],
        "8138": [_usage(carry_share=50)],
        # A tight end, and a quarterback with a row.
        "8131": [_usage(wopr=-5)],
        "7523": [_usage(wopr=30, carry_share=20)],
    }
    return _volume_facts(fixture_raw_dir, usage)


def test_a_wr_leader_holds_his_wopr_and_its_rank_among_started_wrs(vbundle):
    f = vbundle.sheet.facts
    assert f["LEAD.WR.2.volume"].text == "Malik Nabers (WR, NYG) had a WOPR of 85, 1st among started WRs this week."
    assert f["LEAD.WR.1.volume"].text == "Tre Tucker (WR, LV) had a WOPR of 60, 3rd among started WRs this week."
    assert f["LEAD.WR.1.volume"].teams == f["LEAD.WR.1"].teams
    assert f["LEAD.WR.1.volume"].players == ["Tre Tucker"]
    assert f["LEAD.TE.1.volume"].text == "Isaiah Likely (TE, NYG) had a WOPR of -5, 1st among started TEs this week."


def test_an_rb_leader_holds_his_carry_share_and_its_rank_among_started_rbs(vbundle):
    f = vbundle.sheet.facts
    assert f["LEAD.RB.2.volume"].text == (
        "Christian McCaffrey (RB, SF) had a carry share of 80 percent, 1st among started RBs this week.")
    assert f["LEAD.RB.1.volume"].text == (
        "Kenneth Walker (RB, KC) had a carry share of 72 percent, 2nd among started RBs this week.")
    assert f["LEAD.RB.3.volume"].text == (
        "James Cook (RB, BUF) had a carry share of 50 percent, 4th among started RBs this week.")


def test_equal_volumes_share_a_rank_and_the_next_rank_skips(fixture_raw_dir):
    wk = parse_week(load_raw(fixture_raw_dir))
    usage = {pid: [_usage(wopr=76)] for pid in ("10213", "11632", "6786")} | {"2133": [_usage(wopr=50)]}
    nfl = NflverseWeek(sources={}, gsis={}, drops=None, injuries=None, usage=usage)
    assert volume_ranks(wk, nfl, "WR") == {"10213": (76, 1), "11632": (76, 1), "6786": (76, 1), "2133": (50, 4)}


def test_a_qb_or_def_leader_has_no_volume_fact(vbundle):
    assert not any(fid.endswith(".volume") for fid in vbundle.sheet.facts
                   if fid.startswith(("LEAD.QB.", "LEAD.DEF.")))


def test_a_leader_with_no_usage_row_has_no_volume_fact(vbundle):
    f = vbundle.sheet.facts
    assert "LEAD.TE.2" in f and "LEAD.TE.2.volume" not in f


def test_a_leader_with_no_wopr_has_no_volume_fact_and_the_others_keep_theirs(vbundle):
    f = vbundle.sheet.facts
    assert "LEAD.WR.3" in f and "LEAD.WR.3.volume" not in f
    assert "LEAD.WR.1.volume" in f and "LEAD.WR.2.volume" in f


@pytest.mark.parametrize("usage", [None, {}])
def test_the_chapter_builds_without_usage(fixture_raw_dir, usage):
    b = _volume_facts(fixture_raw_dir, usage)
    assert not any(fid.endswith(".volume") for fid in b.sheet.facts)
    ch = next(c for c in b.sheet.chapters if c.key == "position_leaders")
    leads = {fid for fid in b.sheet.facts if fid.startswith("LEAD.") and not fid.endswith(".volume")}
    assert set(ch.fact_ids) == leads


def test_only_the_position_leaders_chapter_cites_the_volume_facts(vbundle):
    volume = {fid for fid in vbundle.sheet.facts if fid.startswith("LEAD.") and fid.endswith(".volume")}
    assert len(volume) == 6
    for c in vbundle.sheet.chapters:
        cited = volume & set(c.fact_ids)
        assert cited == (volume if c.key == "position_leaders" else set()), c.key


def test_every_number_in_a_volume_fact_text_is_in_its_numbers(vbundle):
    for fid, f in vbundle.sheet.facts.items():
        if fid.endswith(".volume"):
            assert set(NUMBER_TOKEN.findall(f.text)) <= set(f.numbers), fid


def test_the_vocabulary_lines_define_wopr_and_carry_share():
    vocabulary = (Path(__file__).parents[1] / "src" / "cornerstone" / "prompts" / "vocabulary.md").read_text()
    wopr = next(line for line in vocabulary.splitlines() if line.startswith("- **WOPR**"))
    carry = next(line for line in vocabulary.splitlines() if line.startswith("- **carry share**"))
    assert "1.5 times target share plus 0.7 times air yards share" in wopr
    assert "never a percent" in wopr and "pass 100 or go negative" in wopr
    assert "in percent" in carry
