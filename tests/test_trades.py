"""
Tests for the trade window and the late-trade test.
They read the recorded week 6 data and the saved history.
"""
from datetime import date, datetime
from zoneinfo import ZoneInfo

from conftest import _decisive_trade
from cornerstone.history import load_history
from cornerstone.models import Trade
from cornerstone.parse import parse_trades, parse_week
from cornerstone.sheet import build_bundle
from cornerstone.sleeper import load_raw
from cornerstone.trades import default_cutoff, is_late, trades_for_week

ET = ZoneInfo("America/New_York")


def _six(fixture_raw_dir, fixture_history_root, until):
    raw = load_raw(fixture_raw_dir)
    h = load_history(fixture_history_root, raw, week=6)
    return trades_for_week(parse_trades(raw["transactions"]), h.weeks[5].trades,
                           default_cutoff(date(2026, 9, 9), 6), until)


def test_default_cutoff_week_6():
    assert default_cutoff(date(2026, 9, 9), 6) == datetime(2026, 10, 13, 8, 0, tzinfo=ET)


def test_window_holds_the_six_week_6_trades(fixture_raw_dir, fixture_history_root):
    t = _six(fixture_raw_dir, fixture_history_root, datetime(2026, 10, 20, 12, 0, tzinfo=ET))
    assert [x.roster_ids for x in t] == [[4, 12], [7, 12], [4, 7], [6, 7], [11, 12], [7, 8]]


def test_window_end_drops_the_tuesday_trade(fixture_raw_dir, fixture_history_root):
    t = _six(fixture_raw_dir, fixture_history_root, datetime(2026, 10, 20, 8, 0, tzinfo=ET))
    assert len(t) == 5 and t[-1].roster_ids == [11, 12]


def test_late_trade(fixture_raw_dir, fixture_history_root):
    t = _six(fixture_raw_dir, fixture_history_root, datetime(2026, 10, 20, 12, 0, tzinfo=ET))
    wk = parse_week(load_raw(fixture_raw_dir))
    assert [is_late(x, wk) for x in t] == [False, False, False, False, False, True]


def test_roster_slots_count_the_reserve_slot(fixture_raw_dir):
    assert parse_week(load_raw(fixture_raw_dir)).roster_slots == 15


def test_sides_fact(tbundle):
    assert tbundle.sheet.facts["T5.sides"].text == (
        "Unsolicited Dak Picks traded Bhayshul Tuten and Garrett Wilson to "
        "Amon-Ra Dawg Your Team for Devaughn Vele and Josh Jacobs.")


def test_got_facts(tbundle):
    f = tbundle.sheet.facts
    assert f["T5.12.got.12490"].text.startswith(
        "Amon-Ra Dawg Your Team got Bhayshul Tuten: 22.7 this week, 81.9 this season, position rank 4 of 31.")
    assert f["T5.11.got.5850"].text.startswith(
        "Unsolicited Dak Picks got Josh Jacobs: 0 this week, 0 this season.")
    assert f["T5.12.gave.11834"].text.startswith(
        "Amon-Ra Dawg Your Team gave Devaughn Vele: 5.7 this week, 55.4 this season")
    assert "T5.11.gave.12490" in f


def test_need_fact(tbundle):
    assert tbundle.sheet.facts["T5.12.need"].text == (
        "Amon-Ra Dawg Your Team is 4-8, 9th of 12, with 5 RB and 5 WR after the trade and 1 open roster spot.")


def test_swing_facts(tbundle):
    f = tbundle.sheet.facts
    # Amon-Ra Dawg Your Team lost M3 104.04 to 113.55. The trade added points, so it did not decide the loss.
    assert f["T5.12.swing"].text == (
        "The players Amon-Ra Dawg Your Team got and started scored 29.1 this week; "
        "the players it gave that Unsolicited Dak Picks started scored 0. "
        "In its matchup, that is a gap of 29.1 against a margin of 9.51, not enough to change the result.")
    # Devaughn Vele sat, so the got side of Unsolicited Dak Picks counts 0, not his 5.7.
    assert f["T5.11.swing"].text == (
        "The players Unsolicited Dak Picks got and started scored 0 this week; "
        "the players it gave that Amon-Ra Dawg Your Team started scored 29.1. "
        "In its matchup, that is a gap of 29.1 against a margin of 38.82, not enough to change the result.")


def test_swing_is_decisive_only_in_the_direction_of_the_result(fixture_raw_dir):
    week = parse_week(load_raw(fixture_raw_dir))
    trade, winner, loser = _decisive_trade(week)
    f = build_bundle(week, news=lambda pid: [], trades=[trade]).sheet.facts
    # The winner got the points and the loser gave them, so both sides point the same way as the result.
    assert "above the margin of" in f[f"T1.{winner}.swing"].text
    assert "above the margin of" in f[f"T1.{loser}.swing"].text
    assert "not enough" not in f[f"T1.{loser}.swing"].text


def test_swing_with_three_teams_names_the_trade_partners(fixture_raw_dir):
    from cornerstone.models import Trade
    week = parse_week(load_raw(fixture_raw_dir))
    a, b, c = week.matchups[0].a, week.matchups[0].b, week.matchups[1].a
    pa, pb = (next(l for l in s.lines if l.started) for s in (a, b))
    trade = Trade(transaction_id="x", created=datetime(2026, 10, 14, tzinfo=ET), roster_ids=[a.roster_id, b.roster_id, c.roster_id],
                  adds={pa.player_id: a.roster_id, pb.player_id: b.roster_id},
                  drops={pa.player_id: c.roster_id, pb.player_id: a.roster_id}, draft_picks=[])
    f = build_bundle(week, news=lambda pid: [], trades=[trade]).sheet.facts
    assert "the players it gave that its trade partners started scored" in f[f"T1.{a.roster_id}.swing"].text


def test_late_trade_has_no_swing_and_no_need(tbundle):
    f = tbundle.sheet.facts
    assert not any(fid.startswith("T6.") and fid.endswith((".swing", ".need")) for fid in f)
    assert "T6.sides" in f


def test_trades_chapter(tbundle):
    ch = next(c for c in tbundle.sheet.chapters if c.key == "trades")
    assert ch.grade_keys == ["T1.4", "T1.12", "T2.7", "T2.12", "T3.4", "T3.7",
                             "T4.6", "T4.7", "T5.11", "T5.12", "T6.7", "T6.8"]
    assert (ch.min_sentences, ch.max_sentences) == (4, 6)


def test_no_trades_no_chapter(hbundle):
    assert "trades" not in {c.key for c in hbundle.sheet.chapters}


def test_three_team_trade(fixture_raw_dir, fixture_history_root):
    raw = load_raw(fixture_raw_dir)
    h = load_history(fixture_history_root, raw, week=6)
    three = next(t for t in h.weeks[5].trades if len(t.roster_ids) == 3)
    f = build_bundle(parse_week(raw), news=lambda pid: [], history=h, trades=[three]).sheet.facts
    assert f["T1.sides"].text.startswith("In a 3-team trade,")
    assert all(name in f["T1.sides"].text for name in ("To Infinity and Bijan", "Return of T Mac", "Amon-Ra Dawg Your Team"))


def test_got_fact_without_history(fixture_raw_dir, fixture_history_root, tbundle):
    raw = load_raw(fixture_raw_dir)
    f = build_bundle(parse_week(raw), news=lambda pid: [], trades=tbundle.data.trades).sheet.facts
    assert f["T5.12.got.12490"].text == (
        "Amon-Ra Dawg Your Team got Bhayshul Tuten: 22.7 this week, position rank 4 of 31.")


def test_need_clamps_open_spots_at_zero(tbundle):
    # Pukancun on 3 lists 15 players against 15 slots.
    need = tbundle.sheet.facts["T1.4.need"]
    assert need.text.endswith("and 0 open roster spots.")
    assert "0" in need.numbers


def test_player_with_no_line_stays_in_sides_and_gets_no_got_fact(tbundle, fixture_raw_dir):
    # Player id 99999999 is in no lineup line, so the week has no points to cite for him.
    trade = tbundle.data.trades[4].model_copy(update={
        "adds": {**tbundle.data.trades[4].adds, "99999999": 12},
        "drops": {**tbundle.data.trades[4].drops, "99999999": 11},
    })
    f = build_bundle(parse_week(load_raw(fixture_raw_dir)), news=lambda pid: [], trades=[trade]).sheet.facts
    assert "an unlisted player" in f["T1.sides"].text
    assert not any(fid.endswith(".99999999") for fid in f)


def test_swing_counts_a_line_only_for_the_roster_that_owns_it(fixture_raw_dir):
    # Two non-late trades move one starter on. Only the final roster started him.
    from cornerstone.models import Trade
    week = parse_week(load_raw(fixture_raw_dir))
    owner = week.matchups[0].a
    star = next(l for l in owner.lines if l.started)
    first, second = [r for r in week.teams if r != owner.roster_id][:2]
    made = datetime(2026, 10, 16, tzinfo=ET)
    trades = [
        Trade(transaction_id="a", created=made, roster_ids=[first, second],
              adds={star.player_id: second}, drops={star.player_id: first}, draft_picks=[]),
        Trade(transaction_id="b", created=made, roster_ids=[second, owner.roster_id],
              adds={star.player_id: owner.roster_id}, drops={star.player_id: second}, draft_picks=[]),
    ]
    f = build_bundle(week, news=lambda pid: [], trades=trades).sheet.facts
    assert f"T1.{first}.swing" not in f and f"T1.{second}.swing" not in f
    # The roster that gave him on to the owner sees his points as the gave side.
    assert f"{week.teams[owner.roster_id].name} started scored {star.points:g}." in f[f"T2.{second}.swing"].text
    assert f"T2.{owner.roster_id}.swing" in f
    assert f"scored {star.points:g} this week" in f[f"T2.{owner.roster_id}.swing"].text


def _got_tuten(fixture_raw_dir, fixture_history_root, tbundle, keep_points):
    """The got fact of Bhayshul Tuten with the week 2 stats empty, as after an outage of the stats endpoint."""
    raw = load_raw(fixture_raw_dir)
    h = load_history(fixture_history_root, raw, week=6)
    h.weeks[2].stats = {}
    if not keep_points:
        # He was on no roster in week 2, so only the empty stats could give his points.
        h.weeks[2].points.pop("12490", None)
    f = build_bundle(parse_week(raw), news=lambda pid: [], history=h, trades=tbundle.data.trades).sheet.facts
    return f["T5.12.got.12490"].text


def test_got_fact_drops_the_season_total_when_a_week_has_no_stats(fixture_raw_dir, fixture_history_root, tbundle):
    text = _got_tuten(fixture_raw_dir, fixture_history_root, tbundle, keep_points=False)
    assert text.startswith("Amon-Ra Dawg Your Team got Bhayshul Tuten: 22.7 this week, position rank 4 of 31.")


def test_got_fact_keeps_the_season_total_when_roster_points_cover_the_week(fixture_raw_dir, fixture_history_root, tbundle):
    text = _got_tuten(fixture_raw_dir, fixture_history_root, tbundle, keep_points=True)
    assert text.startswith("Amon-Ra Dawg Your Team got Bhayshul Tuten: 22.7 this week, 81.9 this season,")


def test_trades_chapter_takes_trade_facts_only(tbundle):
    from cornerstone.sheet import _trade_ids
    facts = {**tbundle.sheet.facts, "TOTAL.x": tbundle.sheet.facts["T5.sides"]}
    ids = _trade_ids(facts)
    assert "TOTAL.x" not in ids and "T5.sides" in ids and "T5.12.swing" in ids


def test_tied_matchup_gets_no_swing_fact(fixture_raw_dir):
    # Any gap changes a tie, so no swing sentence is true for either side.
    week = parse_week(load_raw(fixture_raw_dir))
    m = week.matchups[0]
    tied = m.model_copy(update={"b": m.b.model_copy(update={"points": m.a.points})})
    week = week.model_copy(update={"matchups": [tied, *week.matchups[1:]]})
    star = next(l for l in m.a.lines if l.started)
    trade = Trade(transaction_id="tie", created=datetime(2026, 10, 14, tzinfo=ET), roster_ids=[m.b.roster_id, m.a.roster_id],
                  adds={star.player_id: m.a.roster_id}, drops={star.player_id: m.b.roster_id}, draft_picks=[])
    f = build_bundle(week, news=lambda pid: [], trades=[trade]).sheet.facts
    assert "M1.result" in f and "tied" in f["M1.result"].text
    assert f"T1.{m.a.roster_id}.swing" not in f and f"T1.{m.b.roster_id}.swing" not in f
