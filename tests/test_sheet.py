"""
Tests for the fact sheet, the bundle, and the week gate.
They run on the recorded week 6 data.
"""
import logging
import re
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

import pytest

from cornerstone import sheet
from cornerstone.history import load_history
from cornerstone.models import History, NextMatchup, PowerRow, Standing, Storyline
from cornerstone.odds import OddsResult, Swing, TeamOdds, playoff_odds
from cornerstone.parse import parse_week
from cornerstone.sheet import (
    Context,
    build_bundle,
    check_week_is_buildable,
    fmt,
    is_motw_recap,
    odds_facts,
    power_facts,
    projected_totals,
    read_bundle,
    standings_facts,
    storyline_facts,
    swing_facts,
    week_dates,
    write_bundle,
)
from cornerstone.sleeper import load_raw
from cornerstone.snapshot import week_snapshot


@pytest.fixture
def bundle(fixture_raw_dir):
    return build_bundle(parse_week(load_raw(fixture_raw_dir)), news=lambda pid: [])


def test_week_dates():
    assert week_dates(date(2026, 9, 9), 6) == "Oct 15 – Oct 19, 2026"


def test_gate_messages():
    assert check_week_is_buildable(6, 6) is None
    assert "not final" in check_week_is_buildable(7, 6)
    assert "playoff" in check_week_is_buildable(15, 15)


def test_fmt_keeps_the_shortest_form():
    assert [fmt(106.83), fmt(24.2), fmt(21.0), fmt(106.80)] == ["106.83", "24.2", "21", "106.8"]


def test_bundle_roundtrip_and_ids(bundle, tmp_path):
    b = bundle
    assert b.data.dates == "Oct 15 – Oct 19, 2026"
    assert {c.key for c in b.sheet.chapters} >= {"motw", "game_changer", "awards", "median", "next_week", "recap_4"}
    motw = next(c for c in b.sheet.chapters if c.key == "motw")
    assert all(fid in b.sheet.facts for fid in motw.fact_ids)
    assert set(motw.scope_teams) == {"behold the lamb", "Bo Girds"}
    f = b.sheet.facts["MED.value"]
    assert "106.83" in f.text and "106.83" in f.numbers
    write_bundle(b, tmp_path / "facts.json")
    assert read_bundle(tmp_path / "facts.json").data.week == 6


@pytest.fixture(params=["bundle", "hbundle", "tbundle", "dbundle"])
def any_bundle(request):
    return request.getfixturevalue(request.param)


def test_every_number_appears_in_its_text(any_bundle):
    for f in any_bundle.sheet.facts.values():
        assert all(n in f.text for n in f.numbers), f.id


def test_every_chapter_fact_id_exists(bundle):
    for c in bundle.sheet.chapters:
        assert all(fid in bundle.sheet.facts for fid in c.fact_ids), c.key


def test_upset_fact_exists_for_matchup_4_only_when_the_lower_rank_won(bundle):
    # Before this week, behold the lamb was 11th and Bo Girds was 2nd, so M4 is an upset.
    text = bundle.sheet.facts["M4.upset"].text
    assert "upset" in text and "11th" in text and "2nd" in text
    assert "M1.upset" not in bundle.sheet.facts


def test_game_changer_chapter_holds_only_his_own_facts(bundle):
    chapter = next(c for c in bundle.sheet.chapters if c.key == "game_changer")
    pid = "10213"
    matchup = [fid for fid in chapter.fact_ids if fid.startswith("M6.")]
    # The default bundle has no news item. The news test below checks that the news fact joins this chapter.
    assert "AW.game_changer" in chapter.fact_ids
    assert "M6.result" in matchup
    assert f"M6.driver.{pid}" in matchup and f"M6.swing.{pid}" in matchup
    # Every other matchup fact names an opponent or a teammate, so the chapter drops it.
    assert all(fid in ("M6.result", "M6.upset") or fid.endswith(f".{pid}") for fid in matchup)
    other_starters = [f for f in bundle.sheet.facts if f.startswith("M6.starter.") and not f.endswith(f".{pid}")]
    assert other_starters and not set(other_starters) & set(chapter.fact_ids)
    assert chapter.scope_players == ["Tre Tucker"]


def test_median_closest_carries_the_gap(bundle):
    assert "2.79" in bundle.sheet.facts["MED.closest"].text


def test_recap_scope_players_cover_both_rosters(bundle):
    recap = next(c for c in bundle.sheet.chapters if c.key == "recap_4")
    assert "Tyler Shough" in recap.scope_players
    assert "Tre Tucker" not in recap.scope_players


# A record such as 8-4 is one token. A leading minus belongs to a negative score.
TOKEN = re.compile(r"\d+-\d+|(?<!\d)-?\d+(?:\.\d+)?|\d+(?:\.\d+)?")


def test_every_number_token_in_text_is_in_numbers(any_bundle):
    # Digits inside a team or player name are not number tokens.
    for f in any_bundle.sheet.facts.values():
        text = f.text
        for name in sorted([*f.teams, *f.players], key=len, reverse=True):
            text = text.replace(name, "")
        tokens = set(TOKEN.findall(text))
        assert tokens <= set(f.numbers), (f.id, tokens - set(f.numbers))


def test_rank_fact_names_its_team(bundle):
    for f in bundle.sheet.facts.values():
        if f.id.startswith("RANK."):
            assert all(t in f.text for t in f.teams), f.id


def test_news_fact_uses_the_newest_item(fixture_raw_dir):
    def news(_player_id):
        return [
            {"metadata": {"description": "Old note."}, "published": "1792427710312"},
            {"metadata": {"description": "Newest note, 3 targets."}, "published": "1792500000000"},
        ]

    b = build_bundle(parse_week(load_raw(fixture_raw_dir)), news=news)
    fact = b.sheet.facts["AW.game_changer.news"]
    assert "Newest note" in fact.text and "Old note" not in fact.text
    assert "3" in fact.numbers
    assert "AW.game_changer.news" in next(c for c in b.sheet.chapters if c.key == "game_changer").fact_ids


def test_news_failure_skips_the_fact(fixture_raw_dir):
    def broken(_player_id):
        raise RuntimeError("network down")

    b = build_bundle(parse_week(load_raw(fixture_raw_dir)), news=broken)
    assert "AW.game_changer.news" not in b.sheet.facts


def test_no_season_history_facts(bundle):
    # Version 1 holds one week only, so a "season high" claim would be false.
    for f in bundle.sheet.facts.values():
        assert not f.id.startswith("HIST."), f.id
        assert "season high" not in f.text, f.id


def test_strength_facts_name_next_week_only(bundle):
    sos = [f for f in bundle.sheet.facts.values() if f.id.startswith("SOS.")]
    assert sos
    for f in sos:
        assert "next week" in f.text and "remaining" not in f.text, f.id


def test_news_with_bad_published_skips_the_fact(fixture_raw_dir):
    def news(_player_id):
        return [{"metadata": {"description": "A note."}, "published": "yesterday"}]

    b = build_bundle(parse_week(load_raw(fixture_raw_dir)), news=news)
    assert "AW.game_changer.news" not in b.sheet.facts


def test_long_news_ends_on_a_whole_word(fixture_raw_dir):
    # The 300-character limit falls inside a word: the first 300 characters end in "wo".
    description = ("xx " + "word " * 61)[:305]
    assert len(description) == 305 and description[:300].endswith(" wo")

    def news(_player_id):
        return [{"metadata": {"description": description}, "published": "1792500000000"}]

    b = build_bundle(parse_week(load_raw(fixture_raw_dir)), news=news)
    text = b.sheet.facts["AW.game_changer.news"].text
    assert text.endswith(" word")
    assert len(text.split(": ", 1)[1]) <= 300


def test_standings_fact_says_one_game(bundle):
    one = [f for f in bundle.sheet.facts.values() if f.id.startswith("S.") and "1 game " in f.text]
    assert one, "the fixture has teams one game from the cut"
    assert not any("1 games" in f.text for f in bundle.sheet.facts.values())


def test_a_team_level_with_the_cut_gets_one_fixed_phrase(bundle):
    # The fixture has three 6-6 teams: 6th, 7th, and 8th.
    facts = bundle.sheet.facts
    assert "in the last playoff spot" in facts["S.6"].text
    assert "1 spot outside the playoff spots" in facts["S.7"].text
    assert "2 spots outside the playoff spots" in facts["S.8"].text
    assert not any("at the cut" in facts[f"S.{rank}"].text for rank in range(1, 13))


def test_a_team_off_the_cut_keeps_its_games_from_the_cut(bundle):
    assert "1 game above the cut" in bundle.sheet.facts["S.5"].text


def _standing_text(fixture_raw_dir, rank, wins, losses, games_from_cut):
    # The fixture table with one row moved level with the last playoff spot, 6th.
    c = Context(parse_week(load_raw(fixture_raw_dir)), news=lambda pid: [])
    c.table = [s.model_copy(update={"wins": wins, "losses": losses, "games_from_cut": games_from_cut})
               if s.rank == rank else s for s in c.table]
    return next(f.text for f in standings_facts(c) if f.id == f"S.{rank}")


def test_a_team_3_spots_below_the_last_playoff_spot_gets_the_phrase_for_its_distance(fixture_raw_dir):
    text = _standing_text(fixture_raw_dir, 9, 6, 6, 0)
    assert text.endswith(", 3 spots outside the playoff spots.")


def test_a_tied_team_above_the_last_playoff_spot_is_level_with_it(fixture_raw_dir):
    text = _standing_text(fixture_raw_dir, 5, 6, 6, 0)
    assert text.endswith(", level with the last playoff spot.")


def test_move_facts_say_recent_add(bundle):
    moves = [f for f in bundle.sheet.facts.values() if ".move." in f.id]
    assert moves, "the fixture has a recent move"
    assert all("recent add" in f.text for f in moves)


def test_injury_fact_says_listed_status(bundle):
    # In the fixture players blob, started Ladd McConkey (M5) is listed Out with a concussion.
    f = bundle.sheet.facts["M5.inj.11635"]
    assert f.text == (
        "Ladd McConkey is now listed Out (Concussion) on Sleeper as of the Tuesday after "
        "this week's games. The status may have come from this game."
    )
    assert f.numbers == [] and f.teams == ["To Infinity and Bijan"] and f.players == ["Ladd McConkey"]
    recap = next(c for c in bundle.sheet.chapters if c.key == "recap_5")
    assert "M5.inj.11635" in recap.fact_ids


def test_no_injury_status_gets_no_injury_fact(bundle):
    # Tyler Shough starts in M4 and has no injury_status in the fixture.
    assert "M4.inj.12545" not in bundle.sheet.facts
    assert not any(".inj." in fid and "Tyler Shough" in f.players for fid, f in bundle.sheet.facts.items())


def test_injury_fact_without_body_part_drops_the_parenthesis(fixture_raw_dir):
    raw = load_raw(fixture_raw_dir)
    raw["players"]["11635"]["injury_body_part"] = None
    b = build_bundle(parse_week(raw), news=lambda pid: [])
    assert b.sheet.facts["M5.inj.11635"].text == (
        "Ladd McConkey is now listed Out on Sleeper as of the Tuesday after this week's games. "
        "The status may have come from this game."
    )


def test_injured_aggregate_lists_every_injured_starter(bundle):
    f = bundle.sheet.facts["W.injured"]
    assert f.text.startswith("Now on the injury report after this week's games: ")
    assert "Ladd McConkey (To Infinity and Bijan, Out)" in f.text
    assert f.numbers == [] and "Ladd McConkey" in f.players
    awards = next(c for c in bundle.sheet.chapters if c.key == "awards")
    assert "W.injured" in awards.fact_ids


def test_streak_facts(hbundle):
    f = hbundle.sheet.facts
    assert f["H.8.streak"].text == "Return of T Mac has won 3 straight."
    assert f["H.6.streak"].text == "Bo Girds has lost 2 straight."
    assert "H.2.streak" not in f  # All You Need Is Love won 1


def test_trend_facts(hbundle):
    f = hbundle.sheet.facts
    assert f["H.8.trend"].text == ("Return of T Mac has scored 128.82 per week over the last 3 weeks, "
                                   "up from a season average of 103.16.")
    assert f["H.6.trend"].text == ("Bo Girds has scored 117.71 per week over the last 3 weeks, "
                                   "down from a season average of 120.53.")


def test_high_low_and_average(hbundle):
    f = hbundle.sheet.facts
    assert f["H.7.high"].text == "To Infinity and Bijan's 46.08 this week is a season low."
    assert f["H.11.high"].text == "Unsolicited Dak Picks's 81.47 this week is a season low."
    assert not any("season high" in x.text for x in f.values())
    assert f["H.6.avg"].text == "Bo Girds averages 120.53 per week this season."


def test_history_facts_capped_per_chapter(hbundle):
    # The rankings chapter gives each of the 12 teams its streak and trend facts, so the cap skips it.
    for c in hbundle.sheet.chapters:
        if c.key == "rankings":
            continue
        assert sum(fid.startswith(("H.", "P.")) for fid in c.fact_ids) <= 6, c.key


def test_no_history_facts_without_history(bundle):
    assert not any(fid.startswith("H.") for fid in bundle.sheet.facts)


def test_player_trend_facts(hbundle):
    f = hbundle.sheet.facts
    assert f["P.12501.trend"].text == "Matthew Golden has beaten projection in 3 of the last 3 weeks."
    assert f["P.9509.trend"].text == "Bijan Robinson has missed projection in 2 of the last 3 weeks."


def test_no_player_trend_facts_without_history(bundle):
    assert not any(fid.startswith("P.") for fid in bundle.sheet.facts)


def test_week_five_add_is_a_recent_add(hbundle, bundle):
    assert "week 5" in hbundle.sheet.facts["M4.move.13274"].text  # Germie Bernard, waiver
    assert "M4.move.13274" not in bundle.sheet.facts


def test_position_leaders_are_the_top_three_started_at_each_position(bundle):
    leaders = bundle.data.leaders
    positions = [leader.position for leader in leaders]
    assert positions == [p for p in ("QB", "RB", "WR", "TE", "DEF") for _ in range(3)]
    for p in ("QB", "RB", "WR", "TE", "DEF"):
        board = [leader for leader in leaders if leader.position == p]
        assert [leader.rank for leader in board] == [1, 2, 3]
        assert all(a.line.points >= b.line.points for a, b in zip(board, board[1:]))
    assert all(leader.line.started for leader in leaders)
    rbs = [
        (leader.line.name, leader.of, bundle.data.teams[leader.roster_id].name)
        for leader in leaders if leader.position == "RB"
    ]
    assert rbs == [
        ("Kenneth Walker", 31, "Bo Girds"),
        ("Christian McCaffrey", 31, "Lil Fridge"),
        ("James Cook", 31, "London Cooking"),
    ]
    assert [leader.line.name for leader in leaders if leader.position == "DEF"] == [
        "Pittsburgh Steelers", "Kansas City Chiefs", "Denver Broncos",
    ]


def test_leader_fact_names_the_player_team_and_numbers(bundle):
    f = bundle.sheet.facts["LEAD.RB.1"]
    assert "Kenneth Walker (RB, KC)" in f.text and "Bo Girds" in f.text
    assert "26.9" in f.text and "1st of 31" in f.text
    assert {"26.9", "1", "31"} <= set(f.numbers)
    assert f.teams == ["Bo Girds"] and f.players == ["Kenneth Walker"]
    assert len([fid for fid in bundle.sheet.facts if fid.startswith("LEAD.")]) == 15


@pytest.mark.parametrize("name", ["bundle", "tbundle"])
def test_position_leaders_chapter_sits_after_awards(request, name):
    b = request.getfixturevalue(name)
    keys = [c.key for c in b.sheet.chapters]
    ch = b.sheet.chapters[keys.index("position_leaders")]
    assert ch.title == "Position Leaders"
    assert ch.fact_ids and all(fid.startswith("LEAD.") for fid in ch.fact_ids)
    assert len(ch.fact_ids) == 15
    assert (ch.min_sentences, ch.max_sentences) == (2, 4)
    assert set(ch.scope_teams) == {t.name for t in b.data.teams.values()}
    assert {leader.line.name for leader in b.data.leaders} == set(ch.scope_players)
    assert keys.index("position_leaders") == keys.index("awards") + 1


def test_tied_players_get_the_same_rank_in_the_rank_and_leader_facts(fixture_raw_dir):
    week = parse_week(load_raw(fixture_raw_dir))
    # Every started RB scores the same, so the name alone orders them.
    for m in week.matchups:
        for side in (m.a, m.b):
            for line in side.lines:
                if line.started and line.position == "RB":
                    line.points = 10.0
    b = build_bundle(week, news=lambda pid: [])
    rank_of = {r.player_id: r.rank for r in b.data.ranks}
    leads = [leader for leader in b.data.leaders if leader.position == "RB"]
    assert len(leads) == 3
    for lead in leads:
        assert rank_of[lead.line.player_id] == lead.rank
        assert f"RANK.{lead.line.player_id}" in b.sheet.facts
        assert f"LEAD.RB.{lead.rank}" in b.sheet.facts


def test_twelve_power_rank_facts_hold_the_team_and_every_ordinal(hbundle):
    facts = {
        fid: f for fid, f in hbundle.sheet.facts.items() if fid.startswith("PR.") and not fid.endswith(".why")
    }
    assert sorted(facts) == sorted(f"PR.{rid}" for rid in hbundle.data.teams)
    for fid, f in facts.items():
        rid = int(fid.split(".")[1])
        assert f.teams == [hbundle.data.teams[rid].name]
        for ordinal in re.findall(r"(\d+)(?:st|nd|rd|th)", f.text):
            assert ordinal in f.numbers
        assert len(re.findall(r"\d+(?:st|nd|rd|th)", f.text)) == 5


def test_power_rank_fact_reads_plainly(hbundle):
    assert hbundle.sheet.facts["PR.1"].text == (
        "Brock ‘N’ Roll is 8th in the power rankings, down 4 places from last week: "
        "6th in standing, 8th in results over the last 3 weeks, 11th in schedule played, 5th in scoring; "
        "1-2 head-to-head and 1-2 at the median over the last 3 weeks."
    )


def test_power_rank_fact_in_week_one_says_first_week():
    row = PowerRow(roster_id=3, power_rank=2, movement=None, power_score=0.6,
                   values={}, ranks={"standing": 1, "form": 4, "schedule_played": 7, "scoring": 3},
                   head_to_head=(1, 0), median=(0, 1), form_weeks=1)
    [f] = power_facts([row], lambda rid: "Bo Girds")
    assert f.text == ("Bo Girds is 2nd in the power rankings, the first week of the power rankings: "
                      "1st in standing, 4th in results over the last 3 weeks, 7th in schedule played, 3rd in scoring; "
                      "1-0 head-to-head and 0-1 at the median over the last week.")
    assert f.numbers == ["2", "1", "4", "3", "7", "3", "1", "0", "1-0", "0", "1", "0-1"]


def test_power_rank_fact_with_no_movement_says_no_move():
    row = PowerRow(roster_id=3, power_rank=4, movement=0, power_score=0.5,
                   values={}, ranks={"standing": 2, "form": 5, "schedule_played": 9, "scoring": 6},
                   head_to_head=(0, 3), median=(3, 0), form_weeks=3)
    [f] = power_facts([row], lambda rid: "Bo Girds")
    assert f.text == ("Bo Girds is 4th in the power rankings, no move from last week: "
                      "2nd in standing, 5th in results over the last 3 weeks, 9th in schedule played, 6th in scoring; "
                      "0-3 head-to-head and 3-0 at the median over the last 3 weeks.")
    assert f.numbers[-7:] == ["0", "3", "0-3", "3", "0", "3-0", "3"]


def test_rankings_chapter_holds_every_team_and_its_four_facts(hbundle):
    ch = next(c for c in hbundle.sheet.chapters if c.key == "rankings")
    facts = hbundle.sheet.facts
    assert ch.title == "Power rankings"
    assert (ch.min_sentences, ch.max_sentences) == (12, 36)
    assert sorted(ch.scope_teams) == sorted(t.name for t in hbundle.data.teams.values())
    rank = {s.roster_id: s.rank for s in hbundle.data.table}
    for rid in hbundle.data.teams:
        expected = [f"PR.{rid}", f"S.{rank[rid]}", f"H.{rid}.streak", f"H.{rid}.trend"]
        assert [fid for fid in expected if fid in facts] == [fid for fid in expected if fid in ch.fact_ids]
        assert f"PR.{rid}" in ch.fact_ids and f"S.{rank[rid]}" in ch.fact_ids
    assert any(fid.endswith(".streak") for fid in ch.fact_ids)
    assert any(fid.endswith(".trend") for fid in ch.fact_ids)
    # The chapter lists the teams in power rank order.
    ranks = [
        int(re.search(r"is (\d+)", facts[fid].text).group(1))
        for fid in ch.fact_ids if fid.startswith("PR.") and not fid.endswith(".why")
    ]
    assert ranks == list(range(1, 13))


def test_a_mover_names_its_game_its_margin_and_the_component_that_moved(hbundle):
    assert hbundle.sheet.facts["PR.10.why"].text == (
        "behold the lamb moved up 5 places after a 5-point win over Bo Girds, the 2nd-place team: "
        "schedule played rose from 8th to 2nd."
    )
    assert hbundle.sheet.facts["PR.1.why"].text == (
        "Brock ‘N’ Roll moved down 4 places after a 38-point loss to Lil Fridge, the 1st-place team: "
        "schedule played fell from 6th to 11th."
    )


def test_a_mover_of_one_place_reads_place(hbundle):
    assert hbundle.sheet.facts["PR.4.why"].text.startswith("Pukancun on 3 moved up 1 place after a ")


def test_a_held_team_names_its_best_and_its_worst_component(hbundle):
    # Lil Fridge is 1st in three components. The tie goes to the first in component order: standing.
    assert hbundle.sheet.facts["PR.3.why"].text == (
        "Lil Fridge held 2nd: standing sits 1st, results over the last 3 weeks 3rd."
    )
    assert hbundle.sheet.facts["PR.12.why"].text == (
        "Amon-Ra Dawg Your Team held 9th: schedule played sits 3rd, standing 9th."
    )


def test_the_opponent_place_is_the_standing_rank_before_this_week(hbundle):
    # Lil Fridge beat Pukancun on 3, which was 12th before this week and is 12th after it.
    # Return of T Mac beat Unsolicited Dak Picks, 7th before this week and 10th after it.
    assert "the 7th-place team" in hbundle.sheet.facts["PR.8.why"].text
    assert hbundle.sheet.facts["PR.8.why"].teams == ["Return of T Mac", "Unsolicited Dak Picks"]


def test_a_team_that_tied_its_game_reads_a_tie_with(fixture_raw_dir, fixture_history_root):
    raw = load_raw(fixture_raw_dir)
    h = load_history(fixture_history_root, raw, week=6)
    w6 = h.weeks[6]
    tied = w6.model_copy(update={"scores": {**w6.scores, 6: w6.scores[10]}})
    h = h.model_copy(update={"weeks": {**h.weeks, 6: tied}})
    b = build_bundle(parse_week(raw), news=lambda pid: [], history=h)
    assert b.sheet.facts["PR.10.why"].text.startswith(
        "behold the lamb moved up 3 places after a tie with Bo Girds, the 2nd-place team: "
    )


def test_a_margin_that_rounds_to_zero_reads_narrow(fixture_raw_dir, fixture_history_root):
    raw = load_raw(fixture_raw_dir)
    h = load_history(fixture_history_root, raw, week=6)
    w6 = h.weeks[6]
    close = w6.model_copy(update={"scores": {**w6.scores, 6: round(w6.scores[10] - 0.3, 2)}})
    h = h.model_copy(update={"weeks": {**h.weeks, 6: close}})
    b = build_bundle(parse_week(raw), news=lambda pid: [], history=h)
    assert b.sheet.facts["PR.10.why"].text.startswith("behold the lamb moved up ")
    assert " after a narrow win over Bo Girds, the 2nd-place team" in b.sheet.facts["PR.10.why"].text


def test_every_rank_why_fact_records_its_digits_and_sits_in_the_rankings_chapter(hbundle):
    ch = next(c for c in hbundle.sheet.chapters if c.key == "rankings")
    for rid in hbundle.data.teams:
        f = hbundle.sheet.facts[f"PR.{rid}.why"]
        # A team name can hold a digit, such as "Pukancun on 3", and a name is not a number.
        text = f.text
        for name in f.teams:
            text = text.replace(name, "")
        for token in re.findall(r"\d+", text):
            assert token in f.numbers
        assert f"PR.{rid}.why" in ch.fact_ids


def test_the_first_week_of_the_rankings_has_no_rank_why(fixture_raw_dir, fixture_history_root):
    raw = load_raw(fixture_raw_dir)
    h = load_history(fixture_history_root, raw, week=6)
    week = parse_week(raw).model_copy(update={"week": 1})
    b = build_bundle(week, news=lambda pid: [], history=History(week=1, weeks={1: h.weeks[1]}))
    assert any(fid.startswith("PR.") for fid in b.sheet.facts)
    assert not any(fid.endswith(".why") for fid in b.sheet.facts)


def test_no_rankings_without_history(bundle):
    assert not any(fid.startswith("PR.") for fid in bundle.sheet.facts)
    assert "rankings" not in [c.key for c in bundle.sheet.chapters]


def test_only_the_recap_of_the_matchup_of_the_week_is_the_motw_recap(bundle):
    sheet = bundle.sheet
    motw = next(c for c in sheet.chapters if c.key == "motw")
    recaps = [c for c in sheet.chapters if c.key.startswith("recap_")]
    found = [c.key for c in recaps if is_motw_recap(c, sheet)]
    assert len(found) == 1
    recap = next(c for c in recaps if c.key == found[0])
    assert set(recap.scope_teams) == set(motw.scope_teams)
    assert not is_motw_recap(motw, sheet)


def _team_odds(rid, playoff, bye, seed, status):
    return TeamOdds(roster_id=rid, playoff=playoff, bye=bye, seed=seed, status=status)


def test_twelve_odds_facts_one_per_team(hbundle):
    ids = [fid for fid in hbundle.sheet.facts if fid.startswith("ODDS.") and not fid.endswith(".why")]
    assert sorted(ids) == sorted(f"ODDS.{rid}" for rid in hbundle.data.teams)


def test_one_swing_fact_per_must_watch_game_in_the_next_week_pair_order(hbundle):
    ids = [fid for fid in hbundle.sheet.facts if fid.startswith("SW.")]
    assert ids == [f"SW.{nx.a}v{nx.b}" for nx in hbundle.data.next if nx.must_watch]
    assert len(ids) == 2


def test_swing_fact_states_both_sides():
    swing = Swing(a=3, b=8, a_win=71, a_loss=38, b_win=84, b_loss=67)
    names = {3: "Lil Fridge", 8: "Bo Girds"}
    teams = {3: _team_odds(3, 55, 5, 4, "open"), 8: _team_odds(8, 75, 10, 3, "open")}
    [f] = swing_facts(OddsResult(teams=teams, swings=[swing]), [(3, 8)], names.get)
    assert f.id == "SW.3v8"
    assert f.text == ("A win puts the playoff odds of Lil Fridge at 71%, a loss at 38%. "
                "A win puts the playoff odds of Bo Girds at 84%, a loss at 67%.")
    assert f.numbers == ["71", "38", "84", "67"]
    assert f.teams == ["Lil Fridge", "Bo Girds"]


def test_open_odds_fact_states_the_playoff_bye_and_seed():
    [f] = odds_facts(OddsResult(teams={3: _team_odds(3, 64, 12, 4, "open")}, swings=[]), lambda rid: "Bo Girds")
    assert f.id == "ODDS.3"
    assert f.text == "Bo Girds makes the playoffs in about 64% of runs, with a bye in 12%, most often as the 4th seed."
    assert f.numbers == ["64", "12", "4"]


def test_open_odds_fact_drops_the_seed_clause_with_no_seed():
    [f] = odds_facts(OddsResult(teams={3: _team_odds(3, 30, 2, None, "open")}, swings=[]), lambda rid: "Bo Girds")
    assert f.text == "Bo Girds makes the playoffs in about 30% of runs, with a bye in 2%."


def test_clinched_and_out_odds_facts_hold_no_digit():
    odds = OddsResult(teams={1: _team_odds(1, 100, 80, 1, "in"), 2: _team_odds(2, 0, 0, None, "out")}, swings=[])
    names = {1: "Lil Fridge", 2: "Bo Girds"}
    facts = {f.id: f for f in odds_facts(odds, names.get)}
    assert facts["ODDS.1"].text == "Lil Fridge has clinched a playoff spot."
    assert facts["ODDS.2"].text == "Bo Girds is out of the playoff race."
    for f in facts.values():
        assert not re.search(r"\d", f.text) and f.numbers == []


def test_a_week_before_the_odds_week_has_no_odds_facts(monkeypatch, fixture_raw_dir, fixture_history_root):
    monkeypatch.setattr(sheet, "ODDS_FROM_WEEK", 7)
    raw = load_raw(fixture_raw_dir)
    b = build_bundle(parse_week(raw), news=lambda pid: [], history=load_history(fixture_history_root, raw, week=6))
    assert not any(fid.startswith(("ODDS.", "SW.")) for fid in b.sheet.facts)


def test_no_odds_facts_without_history(bundle):
    assert not any(fid.startswith(("ODDS.", "SW.")) for fid in bundle.sheet.facts)


def test_next_week_chapter_lists_the_swing_facts_in_2_to_6_sentences(hbundle):
    ch = next(c for c in hbundle.sheet.chapters if c.key == "next_week")
    assert (ch.min_sentences, ch.max_sentences) == (2, 6)
    assert [fid for fid in ch.fact_ids if fid.startswith("SW.")] == [
        fid for fid in hbundle.sheet.facts if fid.startswith("SW.")]


def test_rankings_chapter_lists_every_odds_fact(hbundle):
    ch = next(c for c in hbundle.sheet.chapters if c.key == "rankings")
    assert {fid for fid in ch.fact_ids if fid.startswith("ODDS.") and not fid.endswith(".why")} == {
        f"ODDS.{rid}" for rid in hbundle.data.teams}


def test_a_week_with_no_saved_schedule_has_no_odds_facts(fixture_raw_dir, fixture_history_root):
    raw = load_raw(fixture_raw_dir)
    week = parse_week(raw).model_copy(update={"schedule": {}})
    b = build_bundle(week, news=lambda pid: [], history=load_history(fixture_history_root, raw, week=6))
    assert not any(fid.startswith(("ODDS.", "SW.")) for fid in b.sheet.facts)


def test_median_chapter_lists_every_odds_fact(hbundle):
    ch = next(c for c in hbundle.sheet.chapters if c.key == "median")
    assert {fid for fid in ch.fact_ids if fid.startswith("ODDS.")} == {f"ODDS.{rid}" for rid in hbundle.data.teams}


def test_a_flat_side_stays_near_its_odds_and_a_moving_side_keeps_its_swing():
    swing = Swing(a=3, b=8, a_win=62, a_loss=58, b_win=84, b_loss=67)
    teams = {3: _team_odds(3, 60, 5, 5, "open"), 8: _team_odds(8, 75, 10, 3, "open")}
    names = {3: "Lil Fridge", 8: "Bo Girds"}
    [f] = swing_facts(OddsResult(teams=teams, swings=[swing]), [(3, 8)], names.get)
    assert f.text == ("The playoff odds of Lil Fridge stay near 60% either way. "
                "A win puts the playoff odds of Bo Girds at 84%, a loss at 67%.")
    assert f.numbers == ["60", "84", "67"]


def test_a_clinched_side_and_an_out_side_hold_no_digit():
    swing = Swing(a=3, b=8, a_win=100, a_loss=100, b_win=0, b_loss=0)
    teams = {3: _team_odds(3, 100, 90, 1, "in"), 8: _team_odds(8, 0, 0, None, "out")}
    names = {3: "Lil Fridge", 8: "Bo Girds"}
    [f] = swing_facts(OddsResult(teams=teams, swings=[swing]), [(3, 8)], names.get)
    assert f.text == "Lil Fridge is in either way. Bo Girds is out either way."
    assert f.numbers == []


def test_projected_totals_cover_every_roster_and_every_week_ahead(fixture_raw_dir):
    week = parse_week(load_raw(fixture_raw_dir))
    totals = projected_totals(week)
    assert set(totals) == set(week.teams)
    assert all(sorted(by_week) == list(range(7, 15)) for by_week in totals.values())
    assert all(total > 50 for by_week in totals.values() for total in by_week.values())


def test_the_projected_total_counts_0_for_a_player_with_no_projection(fixture_raw_dir):
    week = parse_week(load_raw(fixture_raw_dir))
    side = week.matchups[0].a
    bench = next(line for line in side.lines if not line.started)
    # Only one bench player has a projection, so the best lineup starts him and every other starter counts 0.
    totals = projected_totals(week.model_copy(update={"projections_ahead": {7: {bench.player_id: 50.0}}}))
    # A roster with no projected player that week has no total, so the engine gives it no shift.
    assert totals == {rid: ({7: 50.0} if rid == side.roster_id else {}) for rid in week.teams}


def test_the_projected_totals_stop_at_the_last_regular_week(fixture_raw_dir):
    week = parse_week(load_raw(fixture_raw_dir))
    # The projections file runs to week 17 for the waiver board. The playoff weeks never reach the odds.
    ahead = {**week.projections_ahead, 15: week.projections_ahead[14], 17: week.projections_ahead[14]}
    totals = projected_totals(week.model_copy(update={"projections_ahead": ahead}))
    assert all(sorted(by_week) == list(range(7, 15)) for by_week in totals.values())


def test_the_projected_total_reads_the_current_roster_not_the_week_lineup(fixture_raw_dir):
    week = parse_week(load_raw(fixture_raw_dir))
    side = week.matchups[0].a
    dropped = side.lines[0].player_id
    # A player added after the lock is on the roster but not in the week's lines. A dropped player is the reverse.
    rosters = {**week.rosters, side.roster_id: {"added": "RB", **{
        pid: pos for pid, pos in week.rosters[side.roster_id].items() if pid != dropped}}}
    totals = projected_totals(week.model_copy(update={
        "rosters": rosters, "projections_ahead": {7: {"added": 30.0, dropped: 20.0}}}))
    assert totals[side.roster_id] == {7: 30.0}


def test_the_facts_step_passes_the_projected_totals_to_the_engine(monkeypatch, fixture_raw_dir, fixture_history_root):
    seen = {}

    def engine(*args, **kwargs):
        seen.update(kwargs)
        return playoff_odds(*args, **kwargs)

    monkeypatch.setattr(sheet, "playoff_odds", engine)
    raw = load_raw(fixture_raw_dir)
    week = parse_week(raw)
    build_bundle(week, news=lambda pid: [], history=load_history(fixture_history_root, raw, week=6))
    assert seen["projected"] == projected_totals(week)


def test_a_week_with_no_projections_file_gives_the_odds_with_no_shift(fixture_raw_dir, fixture_history_root):
    raw = load_raw(fixture_raw_dir)
    raw.pop("projections_ahead")
    week, history = parse_week(raw), load_history(fixture_history_root, raw, week=6)
    inputs = sheet._odds_inputs(week, history)
    plain = sheet._odds(week, history, inputs, projected_totals(week))
    assert sheet._odds(week, history, inputs, None) == plain


def _why_inputs(fixture_raw_dir, fixture_history_root):
    raw = load_raw(fixture_raw_dir)
    return parse_week(raw), load_history(fixture_history_root, raw, week=6)


def _mean(values):
    return sum(values) / len(values)


def test_one_odds_why_fact_per_team(hbundle):
    ids = [fid for fid in hbundle.sheet.facts if fid.startswith("ODDS.") and fid.endswith(".why")]
    assert sorted(ids) == sorted(f"ODDS.{rid}.why" for rid in hbundle.data.teams)


def test_rankings_chapter_requires_the_why_of_each_mover_and_of_odds_against_the_record(hbundle):
    ch = next(c for c in hbundle.sheet.chapters if c.key == "rankings")
    # Teams 1, 6, 7, 8, 9, 10, and 11 moved 2 or more places. Team 12 is 4-8 at 32%, and team 2 is 7-5 at 21%.
    # Team 10 at 6-6 is at .500, so its odds of 26% require no odds why.
    assert sorted(ch.required) == sorted([
        "PR.1.why", "PR.6.why", "PR.7.why", "PR.8.why", "PR.9.why", "PR.10.why", "PR.11.why",
        "ODDS.12.why", "ODDS.2.why",
    ])


def test_odds_why_paces_are_the_rounded_means_of_the_inputs(fixture_raw_dir, fixture_history_root):
    week, history = _why_inputs(fixture_raw_dir, fixture_history_root)
    b = build_bundle(week, news=lambda pid: [], history=history)
    totals = projected_totals(week)
    for rid in week.teams:
        played = [history.weeks[n].scores[rid] for n in range(1, 7) if rid in history.weeks[n].scores]
        ahead = int(Decimal(str(_mean(list(totals[rid].values())))).quantize(Decimal(1), rounding=ROUND_HALF_UP))
        pace = int(Decimal(str(_mean(played))).quantize(Decimal(1), rounding=ROUND_HALF_UP))
        f = b.sheet.facts[f"ODDS.{rid}.why"]
        article = "an" if 80 <= pace < 90 else "a"
        assert f.text.startswith(
            f"{week.teams[rid].name} projects {ahead} a week from here against {article} {pace} pace,")
        assert f.teams == [week.teams[rid].name]


def test_the_easiest_remaining_schedule_is_rank_1(fixture_raw_dir, fixture_history_root):
    week, history = _why_inputs(fixture_raw_dir, fixture_history_root)
    b = build_bundle(week, news=lambda pid: [], history=history)
    pace = {rid: _mean([history.weeks[n].scores[rid] for n in range(1, 7) if rid in history.weeks[n].scores])
            for rid in week.teams}
    pairs = list(week.next_matchups) + [p for w in sorted(week.schedule) for p in week.schedule[w]]
    faced = {rid: [pace[b_ if a == rid else a] for a, b_ in pairs if rid in (a, b_)] for rid in week.teams}
    easiest = min(week.teams, key=lambda rid: (_mean(faced[rid]), rid))
    hardest = max(week.teams, key=lambda rid: (_mean(faced[rid]), rid))
    assert b.sheet.facts[f"ODDS.{easiest}.why"].text.endswith(", with the easiest remaining schedule.")
    assert b.sheet.facts[f"ODDS.{hardest}.why"].text.endswith(", with the hardest remaining schedule.")
    ranks = sorted(int(m.group(1)) for fid, f in b.sheet.facts.items()
                   if fid.startswith("ODDS.") and fid.endswith(".why")
                   and (m := re.search(r"(\d+)\w\w easiest", f.text)))
    assert ranks == list(range(2, 12))


def test_a_team_with_no_projected_totals_has_no_odds_why(fixture_raw_dir, fixture_history_root):
    week, history = _why_inputs(fixture_raw_dir, fixture_history_root)
    rid = week.matchups[0].a.roster_id
    mine = set(week.rosters[rid])
    ahead = {w: {pid: p for pid, p in proj.items() if pid not in mine} for w, proj in week.projections_ahead.items()}
    b = build_bundle(week.model_copy(update={"projections_ahead": ahead}), news=lambda pid: [], history=history)
    assert f"ODDS.{rid}" in b.sheet.facts
    assert f"ODDS.{rid}.why" not in b.sheet.facts
    assert len([fid for fid in b.sheet.facts if fid.startswith("ODDS.") and fid.endswith(".why")]) == 11


def test_no_odds_means_no_odds_why(monkeypatch, fixture_raw_dir, fixture_history_root):
    monkeypatch.setattr(sheet, "ODDS_FROM_WEEK", 7)
    week, history = _why_inputs(fixture_raw_dir, fixture_history_root)
    b = build_bundle(week, news=lambda pid: [], history=history)
    assert not any(fid.endswith(".why") and fid.startswith("ODDS.") for fid in b.sheet.facts)


def test_rankings_chapter_lists_every_odds_why_fact(hbundle):
    ch = next(c for c in hbundle.sheet.chapters if c.key == "rankings")
    assert {fid for fid in ch.fact_ids if fid.endswith(".why") and fid.startswith("ODDS.")} == {
        f"ODDS.{rid}.why" for rid in hbundle.data.teams}
    median = next(c for c in hbundle.sheet.chapters if c.key == "median")
    assert not any(fid.endswith(".why") for fid in median.fact_ids)


def test_every_storyline_of_week_6_has_a_fact_in_the_next_week_chapter(hbundle):
    # The storylines of the week 6 fixture, as test_week_6_storylines_and_must_watch reads them by hand.
    ids = {fid for fid in hbundle.sheet.facts if re.fullmatch(r"NX\.\d+v\d+\.\w+", fid)}
    assert ids == {"NX.3v8.streak", "NX.3v8.cut", "NX.1v9.cut", "NX.10v11.streak", "NX.10v11.cut",
                   "NX.5v12.streak", "NX.2v6.cut"}
    ch = next(c for c in hbundle.sheet.chapters if c.key == "next_week")
    assert ids <= set(ch.fact_ids)
    f = hbundle.sheet.facts["NX.3v8.streak"]
    assert f.text == ("Return of T Mac has won 3 head-to-head games in a row, "
                      "so the streak is on the line against Lil Fridge.")
    assert f.numbers == ["3"] and f.teams == ["Lil Fridge", "Return of T Mac"]
    assert hbundle.sheet.facts["NX.10v11.streak"].text == (
        "Unsolicited Dak Picks has lost 3 head-to-head games in a row, so the streak is on the line against "
        "behold the lamb.")
    f = hbundle.sheet.facts["NX.1v9.cut"]
    # Brock is at the cut and Maye is 1 game above it.
    assert f.text == ("Brock ‘N’ Roll sits at the playoff cut. Maye d'force B with U sits 1 game above the playoff "
                      "cut. The game is near the cut.")
    assert f.numbers == ["1"]
    # The Must Watch line keeps the reason.
    assert hbundle.sheet.facts["NX.3v8"].text.endswith(
        "Must Watch: Return of T Mac puts a 3-game win streak on the line and sits near the cut.")


_NAMES = {1: "Brock ‘N’ Roll", 3: "Lil Fridge", 4: "Pukancun on 3", 6: "Bo Girds", 8: "Return of T Mac"}


def _standing(rid, rank, from_cut):
    return Standing(rank=rank, roster_id=rid, wins=0, losses=0, points_for=0.0, in_playoffs=rank <= 6,
                    games_from_cut=from_cut, schedule_strength=None, strength_rank=None)


def _story(kind, weight, **fields):
    return Storyline(kind=kind, weight=weight, **fields)


def test_storyline_facts_give_each_kind_its_numbers():
    by_rank = {3: _standing(3, 1, 4), 6: _standing(6, 3, -1), 1: _standing(1, 6, 0), 4: _standing(4, 12, -5)}
    games = [
        NextMatchup(a=3, b=6, must_watch=True, reason="x", storylines=[
            _story("cut", 3, teams=[6]),
            _story("shootout", 2, totals=(123.0, 118.8)),
            _story("table", 2),
            _story("rematch", 1, roster_id=6, week=3, margin=12.4),
            _story("revenge", 1, roster_id=3, week=3, margin=12.4),
        ]),
        NextMatchup(a=1, b=4, must_watch=False, reason=None, storylines=[
            _story("streak", 3, roster_id=1, length=4),
            _story("streak", 3, roster_id=4, length=-3),
            _story("rematch", 1, roster_id=None, week=2, margin=0.0),
        ]),
    ]
    facts = {f.id: f for f in storyline_facts(games, by_rank, _NAMES.get)}
    assert list(facts) == ["NX.3v6.cut", "NX.3v6.shootout", "NX.3v6.table", "NX.3v6.rematch", "NX.3v6.revenge",
                           "NX.1v4.streak", "NX.1v4.rematch"]
    assert facts["NX.3v6.cut"].text == "Bo Girds sits 1 game below the playoff cut. The game is near the cut."
    assert facts["NX.3v6.shootout"].text == (
        "Lil Fridge projects 123.0 and Bo Girds projects 118.8 for next week. Both best lineups rank in the top four "
        "of the league, so the game is a shootout.")
    assert facts["NX.3v6.shootout"].numbers == ["123.0", "118.8"]
    assert facts["NX.3v6.table"].text == (
        "Lil Fridge (1st) and Bo Girds (3rd) both rank in the top four, so the game is at the top of the table.")
    assert facts["NX.3v6.rematch"].text == (
        "Lil Fridge and Bo Girds met in week 3, and Bo Girds won by 12.4. Next week is a rematch.")
    assert facts["NX.3v6.rematch"].numbers == ["3", "12.4"]
    assert facts["NX.3v6.revenge"].text == (
        "Lil Fridge lost to Bo Girds by 12.4 in week 3, so next week is a chance at revenge.")
    assert facts["NX.1v4.streak"].text == (
        "Brock ‘N’ Roll has won 4 head-to-head games in a row, so the streak is on the line against Pukancun on 3. "
        "Pukancun on 3 has lost 3 head-to-head games in a row, so the streak is on the line against Brock ‘N’ Roll.")
    assert facts["NX.1v4.streak"].numbers == ["4", "3"]
    assert facts["NX.1v4.rematch"].text == (
        "Brock ‘N’ Roll and Pukancun on 3 met in week 2 and tied. Next week is a rematch.")
    assert all(f.teams == [_NAMES[g.a], _NAMES[g.b]] for g in games for k, f in facts.items()
               if k.startswith(f"NX.{g.a}v{g.b}."))


def test_the_checker_accepts_a_cited_streak_length_and_projected_total():
    from cornerstone.verifier import normalize_number, number_failures, remove_names
    by_rank = {3: _standing(3, 1, 4), 6: _standing(6, 3, -1)}
    game = NextMatchup(a=3, b=6, must_watch=True, reason="x", storylines=[
        _story("streak", 3, roster_id=3, length=4), _story("shootout", 2, totals=(123.0, 118.8))])
    facts = storyline_facts([game], by_rank, _NAMES.get)
    cited = {normalize_number(x) for f in facts for x in f.numbers}
    text = " ".join(f.text for f in facts)
    prose = ("Lil Fridge puts a 4-game win streak on the line, and Bo Girds projects 118.8 against 123 "
             "in a projected shootout.")
    assert number_failures(remove_names(prose, list(_NAMES.values())), cited, text) == []
    assert number_failures("a 5-game win streak", cited, text) == ["number 5 is not in the cited facts"]


def _game(bundle, a, b):
    return next(nx for nx in bundle.data.next if (nx.a, nx.b) == (a, b))


def test_each_side_of_a_next_week_game_lists_its_players_on_bye_key_starters_first(dbundle):
    # BUF, JAX, LAC, and WAS have the week 7 bye. Trevor Lawrence started every week, so he is a key starter.
    # Each other JAX, BUF, or LAC player of Amon-Ra Dawg Your Team started 1 or 2 of the last 4 weeks.
    game = _game(dbundle, 5, 12)
    assert [(p.name, p.position, p.key) for p in game.b_byes[:1]] == [("Trevor Lawrence", "QB", True)]
    assert game.b_byes[0].player_id == "7523"
    assert {p.name for p in game.b_byes[1:]} == {"Dalton Kincaid", "Bhayshul Tuten", "Omarion Hampton", "DJ Moore"}
    assert not any(p.key for p in game.b_byes[1:])
    assert {p.name for p in game.a_byes} == {"Jayden Daniels", "James Cook"}


def test_a_bench_player_on_bye_is_on_the_list_and_not_key(dbundle):
    # Stefon Diggs started 2 of the last 4 weeks. Meyers and Shakir sat on the bench. The rest sort by position
    # rank: Meyers is WR42, Diggs WR47, and Shakir WR51.
    game = _game(dbundle, 3, 8)
    assert [(p.name, p.key, p.rank) for p in game.a_byes] == [
        ("Jakobi Meyers", False, 42), ("Stefon Diggs", False, 47), ("Khalil Shakir", False, 51)]
    assert game.b_byes == []


def test_a_build_with_no_schedule_has_empty_bye_lists_and_one_log_line(fixture_raw_dir, fixture_history_root, caplog):
    raw = load_raw(fixture_raw_dir)
    with caplog.at_level(logging.WARNING, logger="cornerstone.facts_league"):
        b = build_bundle(parse_week(raw), news=lambda pid: [], history=load_history(fixture_history_root, raw, week=6))
    assert all(nx.a_byes == [] and nx.b_byes == [] for nx in b.data.next)
    assert [r.message for r in caplog.records if "bye" in r.message] == [
        "no NFL schedule: the next-week games have no bye lists"]


def test_a_build_with_one_saved_week_has_empty_bye_lists(fixture_raw_dir, tmp_path, nfl_week6, caplog):
    raw = load_raw(fixture_raw_dir)
    # An empty history root saves no week, so the history holds week 6 alone.
    with caplog.at_level(logging.WARNING, logger="cornerstone.facts_league"):
        b = build_bundle(parse_week(raw), news=lambda pid: [], history=load_history(tmp_path, raw, week=6),
                         nfl=nfl_week6)
    assert all(nx.a_byes == [] and nx.b_byes == [] for nx in b.data.next)
    assert [r.message for r in caplog.records if "bye" in r.message] == [
        "history has 1 completed weeks: the next-week games have no bye lists"]


def test_a_key_starter_on_bye_has_a_fact_with_his_rank_the_bye_week_and_his_starts(dbundle):
    f = dbundle.sheet.facts["NX.bye.12.7523"]
    assert f.text == ("Trevor Lawrence, QB10, is on bye in week 7 and started 4 of the last 4 weeks "
                      "for Amon-Ra Dawg Your Team.")
    assert f.numbers == ["10", "7", "4", "4"]
    assert f.teams == ["Amon-Ra Dawg Your Team"] and f.players == ["Trevor Lawrence"]


def test_a_bench_player_on_bye_has_a_fact_with_his_starts_and_no_cover_fact(dbundle):
    facts = dbundle.sheet.facts
    assert facts["NX.bye.3.8134"].text == (
        "Khalil Shakir, WR51, is on bye in week 7 and started 0 of the last 4 weeks for Lil Fridge.")
    assert facts["NX.bye.3.2449"].text == (
        "Stefon Diggs, WR47, is on bye in week 7 and started 2 of the last 4 weeks for Lil Fridge.")
    assert "NX.bye.3.8134.cover" not in facts and "NX.bye.3.2449.cover" not in facts


def test_a_team_with_nobody_on_bye_has_one_none_fact(dbundle):
    f = dbundle.sheet.facts["NX.bye.8.none"]
    assert f.text == "Nobody on Return of T Mac is on bye in week 7."
    assert f.numbers == ["7"] and f.teams == ["Return of T Mac"]
    assert not any(fid.startswith("NX.bye.8.") and fid != "NX.bye.8.none" for fid in dbundle.sheet.facts)


def test_a_key_starter_on_bye_has_a_cover_fact_with_the_best_bench_player_at_his_slot(dbundle):
    # James Cook holds RB1 of the best lineup. Woody Marks is the bench back with the most lineup value.
    f = dbundle.sheet.facts["NX.bye.5.8138.cover"]
    assert f.text == "With James Cook on bye, his slot falls to Woody Marks, RB33, with 9.1 a game."
    assert f.numbers == ["33", "9.1"]
    assert f.teams == ["London Cooking"] and f.players == ["James Cook", "Woody Marks"]


def test_a_key_starter_on_bye_with_no_bench_player_at_his_slot_has_a_no_cover_fact(dbundle):
    # Amon-Ra Dawg Your Team rosters one quarterback, Trevor Lawrence.
    f = dbundle.sheet.facts["NX.bye.12.7523.cover"]
    assert f.text == "With Trevor Lawrence on bye, no bench player can fill his slot."
    assert f.numbers == [] and f.players == ["Trevor Lawrence"]


def test_a_build_with_no_snapshot_reads_the_byes_without_a_rank_or_a_cover(
        fixture_raw_dir, fixture_history_root, nfl_week6):
    raw = load_raw(fixture_raw_dir)
    b = build_bundle(parse_week(raw), news=lambda pid: [], history=load_history(fixture_history_root, raw, week=6),
                     nfl=nfl_week6)
    facts = b.sheet.facts
    assert facts["NX.bye.12.7523"].text == (
        "Trevor Lawrence, QB, is on bye in week 7 and started 4 of the last 4 weeks for Amon-Ra Dawg Your Team.")
    assert facts["NX.bye.12.7523"].numbers == ["7", "4", "4"]
    assert not any(fid.endswith(".cover") for fid in facts)
    # With no rank, the players on bye who are not key starters sort by name.
    assert [p.name for p in _game(b, 3, 8).a_byes] == ["Jakobi Meyers", "Khalil Shakir", "Stefon Diggs"]


def test_the_next_week_chapter_lists_the_bye_facts_in_two_to_six_sentences_with_the_bye_note(dbundle):
    from cornerstone.writer import BYES_NOTE, build_writer_prompt
    chapter = next(c for c in dbundle.sheet.chapters if c.key == "next_week")
    byes = [fid for fid in dbundle.sheet.facts if fid.startswith("NX.bye.")]
    assert set(byes) <= set(chapter.fact_ids)
    assert {"NX.bye.12.7523", "NX.bye.12.7523.cover", "NX.bye.5.8138.cover", "NX.bye.8.none"} <= set(byes)
    assert (chapter.min_sentences, chapter.max_sentences) == (2, 6)
    assert chapter.required == []
    assert {"Trevor Lawrence", "Woody Marks", "Khalil Shakir"} <= set(chapter.scope_players)
    assert {"Amon-Ra Dawg Your Team", "Return of T Mac"} <= set(chapter.scope_teams)
    _, user = build_writer_prompt(chapter, dbundle.sheet, None)
    assert BYES_NOTE in user.splitlines()
    assert BYES_NOTE == "Note: the byes next week are part of the preview."


def test_a_chapter_with_no_bye_fact_has_no_bye_note(hbundle):
    from cornerstone.writer import BYES_NOTE, build_writer_prompt
    chapter = next(c for c in hbundle.sheet.chapters if c.key == "next_week")
    _, user = build_writer_prompt(chapter, hbundle.sheet, None)
    assert BYES_NOTE not in user


@pytest.mark.parametrize("thin", ["no schedule", "one saved week"])
def test_thin_data_makes_no_bye_fact_not_even_a_none_fact(thin, fixture_raw_dir, fixture_history_root, tmp_path,
                                                         nfl_week6):
    raw = load_raw(fixture_raw_dir)
    # An empty history root saves no week, so the history holds week 6 alone.
    root = fixture_history_root if thin == "no schedule" else tmp_path
    b = build_bundle(parse_week(raw), news=lambda pid: [], history=load_history(root, raw, week=6),
                     nfl=None if thin == "no schedule" else nfl_week6, snapshot=week_snapshot(raw, root, 6))
    assert not any(fid.startswith("NX.bye.") for fid in b.sheet.facts)


@pytest.mark.parametrize("out", ["returns", "out for season"])
def test_a_bench_player_who_cannot_play_next_week_is_no_bye_cover(out, fixture_raw_dir, fixture_history_root,
                                                                  nfl_week6):
    # Woody Marks is the only bench back of London Cooking who can play next week. Jordan Mason is on IR.
    # A return in week 9 keeps Marks out next week, and his projection ahead of 10 a game keeps him the best bench
    # back, so only the out rule can skip him. Out for the season, he cannot cover either.
    raw = load_raw(fixture_raw_dir)
    snap = week_snapshot(raw, fixture_history_root, 6)
    ahead = {**snap.projections_ahead, "12474": {week: 10.0 for week in range(9, 15)}}
    snap = snap.model_copy(update={"returns": {"12474": 9}, "projections_ahead": ahead} if out == "returns"
                           else {"out_for_season": {"12474"}})
    b = build_bundle(parse_week(raw), news=lambda pid: [], history=load_history(fixture_history_root, raw, week=6),
                     nfl=nfl_week6, snapshot=snap)
    assert b.sheet.facts["NX.bye.5.8138.cover"].text == "With James Cook on bye, no bench player can fill his slot."
