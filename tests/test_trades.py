"""
Tests for the trade window and the late-trade test.
They read the recorded week 6 data and the saved history.
They also test the trade recap facts, the grade input facts, and that the weekly sheet has neither.
"""
import re
from datetime import date, datetime
from importlib import resources
from zoneinfo import ZoneInfo

from conftest import _decisive_trade, _trade_inputs, grade_inputs, recap_facts
from cornerstone.history import load_history
from cornerstone.models import DraftPick, NflverseWeek, Trade
from cornerstone.parse import parse_trades, parse_week
from cornerstone.sheet import build_bundle
from cornerstone.sleeper import load_raw
from cornerstone.trades import default_cutoff, is_late, trades_for_week

ET = ZoneInfo("America/New_York")


def _week(fixture_raw_dir, fixture_history_root, week):
    raw = load_raw(fixture_raw_dir)
    h = load_history(fixture_history_root, raw, week=6)
    return trades_for_week(parse_trades(raw["transactions"]), h.weeks[5].trades,
                           default_cutoff(date(2026, 9, 9), week, ET), default_cutoff(date(2026, 9, 9), week + 1, ET))


def _six(fixture_raw_dir, fixture_history_root, until):
    raw = load_raw(fixture_raw_dir)
    h = load_history(fixture_history_root, raw, week=6)
    return trades_for_week(parse_trades(raw["transactions"]), h.weeks[5].trades,
                           default_cutoff(date(2026, 9, 9), 6, ET), until)


def test_default_cutoff_week_6():
    assert default_cutoff(date(2026, 9, 9), 6, ET) == datetime(2026, 10, 13, 8, 0, tzinfo=ET)


def test_week_6_window_holds_the_five_trades_before_the_cutoff(fixture_raw_dir, fixture_history_root):
    t = _week(fixture_raw_dir, fixture_history_root, 6)
    assert [x.roster_ids for x in t] == [[4, 12], [7, 12], [4, 7], [6, 7], [11, 12]]


def test_week_7_window_holds_the_tuesday_trade(fixture_raw_dir, fixture_history_root):
    t = _week(fixture_raw_dir, fixture_history_root, 7)
    assert [x.roster_ids for x in t] == [[7, 8]]


def _trade_at(fixture_raw_dir, created):
    trade = parse_trades(load_raw(fixture_raw_dir)["transactions"])[0]
    return trade.model_copy(update={"created": created})


def _holds(trade, week):
    return trades_for_week(
        [trade], [], default_cutoff(date(2026, 9, 9), week, ET), default_cutoff(date(2026, 9, 9), week + 1, ET)
    )


def test_a_trade_at_the_week_6_cutoff_is_in_week_5_only(fixture_raw_dir):
    trade = _trade_at(fixture_raw_dir, datetime(2026, 10, 13, 8, 0, tzinfo=ET))
    assert _holds(trade, 5) == [trade]
    assert _holds(trade, 6) == []


def test_a_trade_at_the_week_7_cutoff_is_in_week_6_only(fixture_raw_dir):
    trade = _trade_at(fixture_raw_dir, datetime(2026, 10, 20, 8, 0, tzinfo=ET))
    assert _holds(trade, 6) == [trade]
    assert _holds(trade, 7) == []


def test_late_trade(fixture_raw_dir, fixture_history_root):
    t = _six(fixture_raw_dir, fixture_history_root, datetime(2026, 10, 20, 12, 0, tzinfo=ET))
    wk = parse_week(load_raw(fixture_raw_dir))
    assert [is_late(x, wk) for x in t] == [False, False, False, False, False, True]


def test_roster_slots_count_the_reserve_slot(fixture_raw_dir):
    assert parse_week(load_raw(fixture_raw_dir)).roster_slots == 15


def test_sides_fact(rfacts):
    assert rfacts["T5.sides"].text == (
        "Unsolicited Dak Picks traded Bhayshul Tuten and Garrett Wilson to "
        "Amon-Ra Dawg Your Team for Devaughn Vele and Josh Jacobs.")


def test_swing_facts(rfacts):
    f = rfacts
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
    f = recap_facts(week, trades=[trade])
    # The winner got the points and the loser gave them, so both sides point the same way as the result.
    assert "above the margin of" in f[f"T1.{winner}.swing"].text
    assert "above the margin of" in f[f"T1.{loser}.swing"].text
    assert "not enough" not in f[f"T1.{loser}.swing"].text


def test_swing_with_three_teams_names_the_trade_partners(fixture_raw_dir):
    from cornerstone.models import Trade
    week = parse_week(load_raw(fixture_raw_dir))
    a, b, c = week.matchups[0].a, week.matchups[0].b, week.matchups[1].a
    pa, pb = (next(line for line in s.lines if line.started) for s in (a, b))
    trade = Trade(transaction_id="x", created=datetime(2026, 10, 14, tzinfo=ET),
                  roster_ids=[a.roster_id, b.roster_id, c.roster_id],
                  adds={pa.player_id: a.roster_id, pb.player_id: b.roster_id},
                  drops={pa.player_id: c.roster_id, pb.player_id: a.roster_id}, draft_picks=[])
    f = recap_facts(week, trades=[trade])
    assert "the players it gave that its trade partners started scored" in f[f"T1.{a.roster_id}.swing"].text


def test_late_trade_has_no_swing_and_no_need(rfacts):
    f = rfacts
    assert not any(fid.startswith("T6.") and fid.endswith((".swing", ".need")) for fid in f)
    assert "T6.sides" in f


def test_late_fact_says_the_lineup_shows_the_roster_from_before(rfacts):
    f = rfacts
    assert f["T6.late"].text == (
        "The trade came after the lineups locked, so the lineups show the rosters from before it."
    )
    assert f["T6.late"].teams == f["T6.sides"].teams
    assert not any(fid.startswith(f"T{n}.late") for n in range(1, 6) for fid in f)


def test_three_team_trade(fixture_raw_dir, fixture_history_root):
    raw = load_raw(fixture_raw_dir)
    h = load_history(fixture_history_root, raw, week=6)
    three = next(t for t in h.weeks[5].trades if len(t.roster_ids) == 3)
    f = recap_facts(parse_week(raw), history=h, trades=[three])
    assert f["T1.sides"].text.startswith("In a 3-team trade,")
    assert all(
        name in f["T1.sides"].text for name in ("To Infinity and Bijan", "Return of T Mac", "Amon-Ra Dawg Your Team")
    )


def test_need_clamps_open_spots_at_zero(tinputs):
    # Pukancun on 3 lists 15 players against 15 slots.
    need = tinputs["T1.4.need"]
    assert need.text.endswith("and 0 open roster spots.")
    assert "0" in need.numbers


def test_player_with_no_line_stays_in_sides_and_gets_no_got_fact(tbundle, fixture_raw_dir):
    # Player id 99999999 is in no lineup line, so the week has no points to cite for him.
    trade = tbundle.data.trades[4].model_copy(update={
        "adds": {**tbundle.data.trades[4].adds, "99999999": 12},
        "drops": {**tbundle.data.trades[4].drops, "99999999": 11},
    })
    f = recap_facts(parse_week(load_raw(fixture_raw_dir)), trades=[trade])
    assert "an unlisted player" in f["T1.sides"].text
    assert not any(fid.endswith(".99999999") for fid in f)


def test_swing_counts_a_line_only_for_the_roster_that_owns_it(fixture_raw_dir):
    # Two non-late trades move one starter on. Only the final roster started him.
    from cornerstone.models import Trade
    week = parse_week(load_raw(fixture_raw_dir))
    owner = week.matchups[0].a
    star = next(line for line in owner.lines if line.started)
    first, second = [r for r in week.teams if r != owner.roster_id][:2]
    made = datetime(2026, 10, 16, tzinfo=ET)
    trades = [
        Trade(transaction_id="a", created=made, roster_ids=[first, second],
              adds={star.player_id: second}, drops={star.player_id: first}, draft_picks=[]),
        Trade(transaction_id="b", created=made, roster_ids=[second, owner.roster_id],
              adds={star.player_id: owner.roster_id}, drops={star.player_id: second}, draft_picks=[]),
    ]
    f = recap_facts(week, trades=trades)
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
    f = grade_inputs(parse_week(raw), history=h, trades=tbundle.data.trades)
    return f["T5.12.got.12490"].text


def test_tied_matchup_gets_no_swing_fact(fixture_raw_dir):
    # Any gap changes a tie, so no swing sentence is true for either side.
    week = parse_week(load_raw(fixture_raw_dir))
    m = week.matchups[0]
    tied = m.model_copy(update={"b": m.b.model_copy(update={"points": m.a.points})})
    week = week.model_copy(update={"matchups": [tied, *week.matchups[1:]]})
    star = next(line for line in m.a.lines if line.started)
    trade = Trade(transaction_id="tie", created=datetime(2026, 10, 14, tzinfo=ET),
                  roster_ids=[m.b.roster_id, m.a.roster_id],
                  adds={star.player_id: m.a.roster_id}, drops={star.player_id: m.b.roster_id}, draft_picks=[])
    assert "tied" in build_bundle(week, news=lambda pid: [], trades=[trade]).sheet.facts["M1.result"].text
    f = recap_facts(week, trades=[trade])
    assert f"T1.{m.a.roster_id}.swing" not in f and f"T1.{m.b.roster_id}.swing" not in f


def test_got_and_gave_facts_end_before_the_trade(tinputs):
    f = tinputs
    assert f["T5.12.got.12490"].text == (
        "Amon-Ra Dawg Your Team got Bhayshul Tuten: 11.8 points per game over 5 games before the trade, "
        "position rank 16 of 77 by season points. Bhayshul Tuten has missed projection in 2 of the last 3 weeks.")
    assert f["T5.12.gave.11834"].text == (
        "Amon-Ra Dawg Your Team gave Devaughn Vele: 9.9 points per game over 5 games before the trade, "
        "position rank 23 of 90 by season points. Devaughn Vele has missed projection in 2 of the last 3 weeks.")
    assert f["T3.4.got.7569"].text == (
        "Pukancun on 3 got Nico Collins: 17.7 points per game over 3 games before the trade, "
        "position rank 21 of 90 by season points.")
    assert f["T5.11.got.5850"].text == "Unsolicited Dak Picks got Josh Jacobs: no scored game before the trade."
    assert f["T5.11.got.5850"].numbers == []


def test_no_profile_fact_says_this_week(fixture_raw_dir, fixture_history_root, nfl_week6):
    profile = re.compile(r"T\d+\.\d+\.(got|gave)\.\d+")
    facts = _trade_inputs(fixture_raw_dir, fixture_history_root, nfl=nfl_week6)
    texts = [f.text for fid, f in facts.items() if profile.fullmatch(fid)]
    assert texts and not any("this week" in t or "final NFL injury report" in t for t in texts)


def test_got_fact_without_history(fixture_raw_dir, tbundle):
    f = grade_inputs(parse_week(load_raw(fixture_raw_dir)), trades=tbundle.data.trades)
    assert f["T5.12.got.12490"].text == "Amon-Ra Dawg Your Team got Bhayshul Tuten."
    assert "T5.12.team" not in f


def test_got_fact_drops_the_profile_on_a_stats_outage(fixture_raw_dir, fixture_history_root, tbundle):
    text = _got_tuten(fixture_raw_dir, fixture_history_root, tbundle, keep_points=True)
    assert text.startswith("Amon-Ra Dawg Your Team got Bhayshul Tuten.") and "points per game" not in text


def test_team_facts(tinputs):
    f = tinputs
    assert f["T5.12.team"].text == "Amon-Ra Dawg Your Team was 4-6, 8th of 12, before the trade."
    assert f["T5.11.team"].text == "Unsolicited Dak Picks was 4-6, 7th of 12, before the trade."
    assert f["T6.8.team"].text == "Return of T Mac was 4-6, 9th of 12, before the trade."


def test_need_fact_has_no_record(tinputs):
    assert tinputs["T5.12.need"].text == (
        "Amon-Ra Dawg Your Team has 5 RB and 5 WR after the trade and 1 open roster spot.")


def test_impact_facts(rfacts):
    f = rfacts
    assert f["T5.12.impact.12490"].text == "Bhayshul Tuten scored 22.7 this week for Amon-Ra Dawg Your Team."
    assert f["T5.11.impact.11834"].text == "Devaughn Vele scored 5.7 this week on the bench for Unsolicited Dak Picks."


def test_late_trade_keeps_profile_team_and_impact(rfacts, tinputs):
    # Braelon Allen went to roster 7 after his game, so roster 8 started him.
    f = rfacts
    assert f["T6.7.impact.11576"].text == "Braelon Allen scored 11.4 this week for Return of T Mac."
    assert "T6.7.got.11576" in tinputs and "T6.7.team" in tinputs


def test_vocabulary_has_the_profile_terms():
    text = resources.files("cornerstone.prompts").joinpath("vocabulary.md").read_text(encoding="utf-8")
    for term in ("points per game", "position rank by season points"):
        assert f"**{term}**" in text


def _injured(fixture_raw_dir, fixture_history_root):
    # The week 6 "Out" is after the trade, so no injury fact may count it.
    nfl = NflverseWeek(sources={}, gsis={}, drops=None,
                       injuries={"12490": {4: "Questionable", 5: "Questionable", 6: "Out"},
                                 "8146": {3: "Questionable"}})
    return _trade_inputs(fixture_raw_dir, fixture_history_root, nfl=nfl)


def test_usage_facts(tinputs):
    f = tinputs
    assert f["T5.12490.usage"].text == (
        "Bhayshul Tuten's snap share was 64 percent over the last 2 weeks before the trade, "
        "up from the 2 weeks before that.")
    assert f["T5.12490.targets"].text == (
        "Bhayshul Tuten's target share was 11 percent over the last 2 weeks before the trade, "
        "flat from the 2 weeks before that.")
    assert f["T3.7569.usage"].text == "Nico Collins's snap share was 71 percent over 3 games before the trade."


def test_redzone_fact(tinputs):
    assert tinputs["T5.12490.redzone"].text == (
        "Bhayshul Tuten had 1 red-zone target and 12 red-zone carries this season before the trade.")


def test_quarterback_has_no_target_share(tinputs):
    f = tinputs
    assert "T4.4046.usage" in f and "T4.4046.targets" not in f


def test_no_scored_game_has_no_usage(tinputs):
    assert not any(fid.startswith("T5.5850.") for fid in tinputs)


def test_player_in_two_trades_gets_facts_in_both(tinputs):
    f = tinputs
    assert "T4.8154.usage" in f and "T6.8154.usage" in f


def test_injury_facts_end_at_week_5(fixture_raw_dir, fixture_history_root):
    f = _injured(fixture_raw_dir, fixture_history_root)
    assert f["T5.12490.injury"].text == (
        "Bhayshul Tuten was listed Questionable on the NFL injury report in week 5, "
        "and in 2 weeks this season before the trade.")
    assert f["T5.8146.injury"].text == (
        "Garrett Wilson was on the NFL injury report in 1 week this season before the trade."
    )
    assert "T5.11834.injury" not in f
    assert "injury report" not in f["T5.12.got.12490"].text


def test_no_injury_facts_without_nflverse(tinputs):
    assert not any(fid.endswith(".injury") for fid in tinputs)


def test_vocabulary_drops_the_recap_terms_and_the_grade_terms():
    text = resources.files("cornerstone.prompts").joinpath("vocabulary.md").read_text(encoding="utf-8")
    for term in ("trade impact", "trade swing", "late trade"):
        assert f"**{term}**" not in text
    for term in ("trade grade", "trade value", "roster need", "snap share", "target share", "red-zone use",
                 "injury before the trade"):
        assert f"**{term}**" not in text
    assert "grade" not in text


def test_trade_of_a_player_with_no_points_stat_still_gets_a_got_fact(fixture_raw_dir, fixture_history_root):
    # Higbee has a game in the history with no pts_half_ppr key, which used to stop the build.
    raw = load_raw(fixture_raw_dir)
    week = parse_week(raw)
    first, second = list(week.teams)[:2]
    trade = Trade(transaction_id="higbee", created=datetime(2026, 10, 14, tzinfo=ET), roster_ids=[first, second],
                  adds={"3271": second}, drops={"3271": first}, draft_picks=[])
    h = load_history(fixture_history_root, raw, week=6)
    f = grade_inputs(week, history=h, trades=[trade])
    assert f"T1.{second}.got.3271" in f


def _value_ids(facts):
    return [k for k in facts if k.startswith("T") and k.endswith(".value")]


def test_player_trade_value_fact(vinputs):
    f = vinputs["T1.12507.value"]
    assert f.text == "Omarion Hampton's trade value was 68.5 in the week of the trade."
    assert f.numbers == ["68.5"]
    assert f.players == ["Omarion Hampton"]


def test_side_trade_value_fact_sums_what_each_side_gave_and_got(vinputs):
    # Roster 4 gave Hampton (68.5) and Pollard (9.0), and got 24.0 and 12.5.
    f = vinputs["T1.4.value"]
    assert f.text == "Pukancun on 3 gave 77.5 and got 36.5 in trade value."
    assert f.numbers == ["77.5", "36.5"]
    assert f.teams == ["Pukancun on 3"]


def test_unlisted_player_gets_no_value_fact_and_a_clause_on_each_side(vinputs):
    # Kenyon Sadiq (13330) is left out of the chart on purpose.
    facts = vinputs
    assert "T2.13330.value" not in facts
    assert "T2.10236.value" in facts
    assert facts["T2.7.value"].text == (
        "To Infinity and Bijan gave 31.5 and got 0 in trade value, with Kenyon Sadiq unlisted."
    )
    assert facts["T2.12.value"].text == (
        "Amon-Ra Dawg Your Team gave 0 and got 31.5 in trade value, with Kenyon Sadiq unlisted."
    )
    assert facts["T2.12.value"].players == ["Kenyon Sadiq"]


def test_two_unlisted_players_join_with_and(fixture_raw_dir, fixture_history_root, chart_week6):
    # Roster 7 gave Braelon Allen (11576) and Marvin Harrison (11628) in trade 6.
    unlisted = chart_week6.model_copy(update={"values": {k: v for k, v in chart_week6.values.items()
                                                         if k not in ("11576", "11628")}})
    text = _trade_inputs(fixture_raw_dir, fixture_history_root, chart=unlisted)["T6.7.value"].text
    assert text.endswith("in trade value, with Braelon Allen and Marvin Harrison unlisted.")


def test_trade_with_no_valued_player_has_no_side_fact(fixture_raw_dir, fixture_history_root, chart_week6):
    empty = chart_week6.model_copy(update={"values": {}})
    facts = _trade_inputs(fixture_raw_dir, fixture_history_root, chart=empty)
    assert not _value_ids(facts)


def test_draft_picks_are_not_valued(fixture_raw_dir, fixture_history_root, chart_week6):
    raw = load_raw(fixture_raw_dir)
    week = parse_week(raw)
    h = load_history(fixture_history_root, raw, week=6)
    made = datetime(2026, 10, 14, tzinfo=ET)

    def pick(rnd):
        return DraftPick(season="2027", round=rnd, roster_id=4, previous_owner_id=4, owner_id=12)

    def trade(picks):
        return Trade(transaction_id="p", created=made, roster_ids=[4, 12], adds={"12507": 12},
                     drops={"12507": 4}, draft_picks=picks)

    one = grade_inputs(week, history=h, trades=[trade([pick(1)])], chart=chart_week6)
    two = grade_inputs(week, history=h, trades=[trade([pick(1), pick(2)])], chart=chart_week6)
    assert one["T1.4.value"].text.endswith("gave 68.5 and got 0 in trade value; the pick is not valued.")
    assert two["T1.4.value"].text.endswith("in trade value; the picks are not valued.")


def test_without_chart_values_there_are_no_value_facts(tinputs):
    assert not _value_ids(tinputs)


def test_late_trade_keeps_its_value_facts(vinputs):
    # T6 is the late trade of week 6. The chart is for the week of the trade, so the late rule does not drop it.
    assert "T6.7.value" in vinputs and "T6.8.value" in vinputs


def test_player_with_no_line_is_outside_the_value_sums(fixture_raw_dir, fixture_history_root, chart_week6):
    # A chain trade moves a player who is on no roster at lock. He has no name on the sheet, so the sums skip him.
    raw = load_raw(fixture_raw_dir)
    h = load_history(fixture_history_root, raw, week=6)
    trade = Trade(transaction_id="chain", created=datetime(2026, 10, 14, tzinfo=ET), roster_ids=[4, 12],
                  adds={"gone": 4, "8154": 12}, drops={"gone": 12, "8154": 4}, draft_picks=[])
    chart = chart_week6.model_copy(update={"values": {**chart_week6.values, "gone": 50.0}})
    f = grade_inputs(parse_week(raw), history=h, trades=[trade], chart=chart)
    assert "T1.gone.value" not in f
    assert f["T1.12.value"].text == "Amon-Ra Dawg Your Team gave 0 and got 22 in trade value."


def test_the_week_6_sheet_has_no_trade_chapter_and_no_trade_fact(tbundle):
    assert tbundle.data.trades and tbundle.data.trade_players
    assert not [c.key for c in tbundle.sheet.chapters if c.key.startswith("trade")]
    assert not [fid for fid in tbundle.sheet.facts if re.match(r"T\d+\.", fid)]
