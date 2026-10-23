"""
Tests for the fact sheet, the bundle, and the week gate.
They run on the recorded week 6 data.
"""
import re
from datetime import date

import pytest

from cornerstone import sheet
from cornerstone.history import load_history
from cornerstone.models import PowerRow
from cornerstone.odds import OddsResult, Swing, TeamOdds
from cornerstone.parse import parse_week
from cornerstone.sheet import (
    Context,
    build_bundle,
    check_week_is_buildable,
    fmt,
    is_motw_recap,
    odds_facts,
    power_facts,
    read_bundle,
    standings_facts,
    swing_facts,
    week_dates,
    write_bundle,
)
from cornerstone.sleeper import load_raw


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
    positions = [l.position for l in leaders]
    assert positions == [p for p in ("QB", "RB", "WR", "TE", "DEF") for _ in range(3)]
    for p in ("QB", "RB", "WR", "TE", "DEF"):
        board = [l for l in leaders if l.position == p]
        assert [l.rank for l in board] == [1, 2, 3]
        assert all(a.line.points >= b.line.points for a, b in zip(board, board[1:]))
    assert all(l.line.started for l in leaders)
    rbs = [(l.line.name, l.of, bundle.data.teams[l.roster_id].name) for l in leaders if l.position == "RB"]
    assert rbs == [
        ("Kenneth Walker", 31, "Bo Girds"),
        ("Christian McCaffrey", 31, "Lil Fridge"),
        ("James Cook", 31, "London Cooking"),
    ]
    assert [l.line.name for l in leaders if l.position == "DEF"] == [
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
    assert {l.line.name for l in b.data.leaders} == set(ch.scope_players)
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
    leads = [l for l in b.data.leaders if l.position == "RB"]
    assert len(leads) == 3
    for lead in leads:
        assert rank_of[lead.line.player_id] == lead.rank
        assert f"RANK.{lead.line.player_id}" in b.sheet.facts
        assert f"LEAD.RB.{lead.rank}" in b.sheet.facts


def test_twelve_power_rank_facts_hold_the_team_and_every_ordinal(hbundle):
    facts = {fid: f for fid, f in hbundle.sheet.facts.items() if fid.startswith("PR.")}
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
        "6th in standing, 7th in results over the last 3 weeks, 11th in schedule played, 5th in scoring."
    )


def test_power_rank_fact_in_week_one_says_first_week():
    row = PowerRow(roster_id=3, power_rank=2, movement=None, power_score=0.6,
                   values={}, ranks={"standing": 1, "form": 4, "schedule_played": 7, "scoring": 3})
    [f] = power_facts([row], lambda rid: "Bo Girds")
    assert f.text == ("Bo Girds is 2nd in the power rankings, the first week of the power rankings: "
                      "1st in standing, 4th in results over the last 3 weeks, 7th in schedule played, 3rd in scoring.")
    assert f.numbers == ["2", "1", "4", "3", "7", "3"]


def test_power_rank_fact_with_no_movement_says_no_move():
    row = PowerRow(roster_id=3, power_rank=4, movement=0, power_score=0.5,
                   values={}, ranks={"standing": 2, "form": 5, "schedule_played": 9, "scoring": 6})
    [f] = power_facts([row], lambda rid: "Bo Girds")
    assert f.text == ("Bo Girds is 4th in the power rankings, no move from last week: "
                      "2nd in standing, 5th in results over the last 3 weeks, 9th in schedule played, 6th in scoring.")


def test_rankings_chapter_holds_every_team_and_its_four_facts(hbundle):
    ch = next(c for c in hbundle.sheet.chapters if c.key == "rankings")
    facts = hbundle.sheet.facts
    assert ch.title == "Power rankings"
    assert (ch.min_sentences, ch.max_sentences) == (12, 24)
    assert sorted(ch.scope_teams) == sorted(t.name for t in hbundle.data.teams.values())
    rank = {s.roster_id: s.rank for s in hbundle.data.table}
    for rid in hbundle.data.teams:
        expected = [f"PR.{rid}", f"S.{rank[rid]}", f"H.{rid}.streak", f"H.{rid}.trend"]
        assert [fid for fid in expected if fid in facts] == [fid for fid in expected if fid in ch.fact_ids]
        assert f"PR.{rid}" in ch.fact_ids and f"S.{rank[rid]}" in ch.fact_ids
    assert any(fid.endswith(".streak") for fid in ch.fact_ids)
    assert any(fid.endswith(".trend") for fid in ch.fact_ids)
    # The chapter lists the teams in power rank order.
    ranks = [int(re.search(r"is (\d+)", facts[fid].text).group(1)) for fid in ch.fact_ids if fid.startswith("PR.")]
    assert ranks == list(range(1, 13))


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


def _odds(rid, playoff, bye, seed, status):
    return TeamOdds(roster_id=rid, playoff=playoff, bye=bye, seed=seed, status=status)


def test_twelve_odds_facts_one_per_team(hbundle):
    ids = [fid for fid in hbundle.sheet.facts if fid.startswith("ODDS.")]
    assert sorted(ids) == sorted(f"ODDS.{rid}" for rid in hbundle.data.teams)


def test_one_swing_fact_per_must_watch_game_in_the_next_week_pair_order(hbundle):
    ids = [fid for fid in hbundle.sheet.facts if fid.startswith("SW.")]
    assert ids == [f"SW.{nx.a}v{nx.b}" for nx in hbundle.data.next if nx.must_watch]
    assert len(ids) == 2


def test_swing_fact_states_both_sides():
    swing = Swing(a=3, b=8, a_win=71, a_loss=38, b_win=84, b_loss=67)
    names = {3: "Lil Fridge", 8: "Bo Girds"}
    [f] = swing_facts(OddsResult(teams={}, swings=[swing]), [(3, 8)], names.get)
    assert f.id == "SW.3v8"
    assert f.text == "A win puts Lil Fridge at 71%, a loss at 38%. A win puts Bo Girds at 84%, a loss at 67%."
    assert f.numbers == ["71", "38", "84", "67"]
    assert f.teams == ["Lil Fridge", "Bo Girds"]


def test_open_odds_fact_states_the_playoff_bye_and_seed():
    [f] = odds_facts(OddsResult(teams={3: _odds(3, 64, 12, 4, "open")}, swings=[]), lambda rid: "Bo Girds")
    assert f.id == "ODDS.3"
    assert f.text == "Bo Girds makes the playoffs in about 64% of runs, with a bye in 12%, most often as the 4th seed."
    assert f.numbers == ["64", "12", "4"]


def test_open_odds_fact_drops_the_seed_clause_with_no_seed():
    [f] = odds_facts(OddsResult(teams={3: _odds(3, 30, 2, None, "open")}, swings=[]), lambda rid: "Bo Girds")
    assert f.text == "Bo Girds makes the playoffs in about 30% of runs, with a bye in 2%."


def test_clinched_and_out_odds_facts_hold_no_digit():
    odds = OddsResult(teams={1: _odds(1, 100, 80, 1, "in"), 2: _odds(2, 0, 0, None, "out")}, swings=[])
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


def test_next_week_chapter_lists_the_swing_facts_in_3_sentences(hbundle):
    ch = next(c for c in hbundle.sheet.chapters if c.key == "next_week")
    assert (ch.min_sentences, ch.max_sentences) == (1, 3)
    assert [fid for fid in ch.fact_ids if fid.startswith("SW.")] == [
        fid for fid in hbundle.sheet.facts if fid.startswith("SW.")]


def test_rankings_chapter_lists_every_odds_fact(hbundle):
    ch = next(c for c in hbundle.sheet.chapters if c.key == "rankings")
    assert {fid for fid in ch.fact_ids if fid.startswith("ODDS.")} == {f"ODDS.{rid}" for rid in hbundle.data.teams}
