"""
Tests for the fact sheet, the bundle, and the week gate.
They run on the recorded week 6 data.
"""
import re
from datetime import date

import pytest

from cornerstone.parse import parse_week
from cornerstone.sheet import (
    build_bundle,
    check_week_is_buildable,
    fmt,
    read_bundle,
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


@pytest.fixture(params=["bundle", "hbundle"])
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
    for c in hbundle.sheet.chapters:
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
