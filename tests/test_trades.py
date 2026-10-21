"""
Tests for the trade window and the late-trade test.
They read the recorded week 6 data and the saved history.
They also test the trade facts and the trade chapters.
"""
import re
from datetime import date, datetime
from importlib import resources
from zoneinfo import ZoneInfo

from conftest import _decisive_trade, _trade_bundle
from cornerstone.history import load_history
from cornerstone.models import Blurb, DraftPick, NflverseWeek, Sentence, Trade
from cornerstone.parse import parse_trades, parse_week
from cornerstone.sheet import _trade_ids, build_bundle
from cornerstone.sleeper import load_raw
from cornerstone.trades import default_cutoff, is_late, trades_for_week
from cornerstone.verifier import code_check

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


def test_one_chapter_per_trade(tbundle):
    keys = [c.key for c in tbundle.sheet.chapters]
    trade_keys = [k for k in keys if k.startswith("trade")]
    assert trade_keys == [f"trade_{n}" for n in range(1, 7)]
    assert keys.index("trade_1") > keys.index("recap_6") and keys.index("trade_6") < keys.index("median")


def test_trade_chapter(tbundle):
    ch = next(c for c in tbundle.sheet.chapters if c.key == "trade_5")
    assert ch.title == "Unsolicited Dak Picks and Amon-Ra Dawg Your Team"
    assert ch.grade_keys == ["T5.11", "T5.12"]
    assert (ch.min_sentences, ch.max_sentences) == (3, 5)
    assert set(ch.fact_ids) == {fid for fid in tbundle.sheet.facts if fid.startswith("T5.")}
    assert ch.scope_teams == ["Unsolicited Dak Picks", "Amon-Ra Dawg Your Team"]


def test_trade_chapters_take_no_week_facts(dbundle):
    for ch in (c for c in dbundle.sheet.chapters if c.key.startswith("trade_")):
        n = ch.key.removeprefix("trade_")
        assert ch.fact_ids and all(fid.startswith(f"T{n}.") for fid in ch.fact_ids)


def test_three_team_chapter_title(fixture_raw_dir, fixture_history_root):
    raw = load_raw(fixture_raw_dir)
    h = load_history(fixture_history_root, raw, week=6)
    three = next(t for t in h.weeks[5].trades if len(t.roster_ids) == 3)
    bundle = build_bundle(parse_week(raw), news=lambda pid: [], history=h, trades=[three])
    ch = next(c for c in bundle.sheet.chapters if c.key == "trade_1")
    assert ch.title == "To Infinity and Bijan, Return of T Mac and Amon-Ra Dawg Your Team"
    assert ch.grade_keys == ["T1.7", "T1.8", "T1.12"]


def test_no_trades_no_trade_chapter(hbundle):
    assert not any(c.key.startswith("trade") for c in hbundle.sheet.chapters)


def test_trade_ids_take_one_trade(tbundle):
    facts = {**tbundle.sheet.facts, "T10.sides": tbundle.sheet.facts["T1.sides"], "TOTAL.x": tbundle.sheet.facts["T1.sides"]}
    ids = _trade_ids(facts, 1)
    assert "T1.sides" in ids and "T10.sides" not in ids and "TOTAL.x" not in ids


def test_three_team_trade(fixture_raw_dir, fixture_history_root):
    raw = load_raw(fixture_raw_dir)
    h = load_history(fixture_history_root, raw, week=6)
    three = next(t for t in h.weeks[5].trades if len(t.roster_ids) == 3)
    f = build_bundle(parse_week(raw), news=lambda pid: [], history=h, trades=[three]).sheet.facts
    assert f["T1.sides"].text.startswith("In a 3-team trade,")
    assert all(name in f["T1.sides"].text for name in ("To Infinity and Bijan", "Return of T Mac", "Amon-Ra Dawg Your Team"))


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


def test_got_and_gave_facts_end_before_the_trade(tbundle):
    f = tbundle.sheet.facts
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


def test_no_profile_fact_says_this_week(dbundle):
    profile = re.compile(r"T\d+\.\d+\.(got|gave)\.\d+")
    texts = [f.text for fid, f in dbundle.sheet.facts.items() if profile.fullmatch(fid)]
    assert texts and not any("this week" in t or "final NFL injury report" in t for t in texts)


def test_got_fact_without_history(fixture_raw_dir, tbundle):
    f = build_bundle(parse_week(load_raw(fixture_raw_dir)), news=lambda pid: [], trades=tbundle.data.trades).sheet.facts
    assert f["T5.12.got.12490"].text == "Amon-Ra Dawg Your Team got Bhayshul Tuten."
    assert "T5.12.team" not in f


def test_got_fact_drops_the_profile_on_a_stats_outage(fixture_raw_dir, fixture_history_root, tbundle):
    text = _got_tuten(fixture_raw_dir, fixture_history_root, tbundle, keep_points=True)
    assert text.startswith("Amon-Ra Dawg Your Team got Bhayshul Tuten.") and "points per game" not in text


def test_team_facts(tbundle):
    f = tbundle.sheet.facts
    assert f["T5.12.team"].text == "Amon-Ra Dawg Your Team was 4-6, 8th of 12, before the trade."
    assert f["T5.11.team"].text == "Unsolicited Dak Picks was 4-6, 7th of 12, before the trade."
    assert f["T6.8.team"].text == "Return of T Mac was 4-6, 9th of 12, before the trade."


def test_need_fact_has_no_record(tbundle):
    assert tbundle.sheet.facts["T5.12.need"].text == (
        "Amon-Ra Dawg Your Team has 5 RB and 5 WR after the trade and 1 open roster spot.")


def test_impact_facts(tbundle):
    f = tbundle.sheet.facts
    assert f["T5.12.impact.12490"].text == "Bhayshul Tuten scored 22.7 this week for Amon-Ra Dawg Your Team."
    assert f["T5.11.impact.11834"].text == "Devaughn Vele scored 5.7 this week on the bench for Unsolicited Dak Picks."


def test_late_trade_keeps_profile_team_and_impact(tbundle):
    # Braelon Allen went to roster 7 after his game, so roster 8 started him.
    f = tbundle.sheet.facts
    assert f["T6.7.impact.11576"].text == "Braelon Allen scored 11.4 this week for Return of T Mac."
    assert "T6.7.got.11576" in f and "T6.7.team" in f


def test_vocabulary_has_the_profile_terms():
    text = resources.files("cornerstone.prompts").joinpath("vocabulary.md").read_text(encoding="utf-8")
    for term in ("points per game", "position rank by season points", "trade impact"):
        assert f"**{term}**" in text


def _injured(fixture_raw_dir, fixture_history_root):
    # The week 6 "Out" is after the trade, so no injury fact may count it.
    nfl = NflverseWeek(sources={}, gsis={}, drops=None,
                       injuries={"12490": {4: "Questionable", 5: "Questionable", 6: "Out"}, "8146": {3: "Questionable"}})
    return _trade_bundle(fixture_raw_dir, fixture_history_root, nfl=nfl).sheet.facts


def test_usage_facts(tbundle):
    f = tbundle.sheet.facts
    assert f["T5.12490.usage"].text == (
        "Bhayshul Tuten's snap share was 64 percent over the last 2 weeks before the trade, up from the 2 weeks before that.")
    assert f["T5.12490.targets"].text == (
        "Bhayshul Tuten's target share was 11 percent over the last 2 weeks before the trade, flat from the 2 weeks before that.")
    assert f["T3.7569.usage"].text == "Nico Collins's snap share was 71 percent over 3 games before the trade."


def test_redzone_fact(tbundle):
    assert tbundle.sheet.facts["T5.12490.redzone"].text == (
        "Bhayshul Tuten had 1 red-zone target and 12 red-zone carries this season before the trade.")


def test_quarterback_has_no_target_share(tbundle):
    f = tbundle.sheet.facts
    assert "T4.4046.usage" in f and "T4.4046.targets" not in f


def test_no_scored_game_has_no_usage(tbundle):
    assert not any(fid.startswith("T5.5850.") for fid in tbundle.sheet.facts)


def test_player_in_two_trades_gets_facts_in_both(tbundle):
    f = tbundle.sheet.facts
    assert "T4.8154.usage" in f and "T6.8154.usage" in f


def test_injury_facts_end_at_week_5(fixture_raw_dir, fixture_history_root):
    f = _injured(fixture_raw_dir, fixture_history_root)
    assert f["T5.12490.injury"].text == (
        "Bhayshul Tuten was listed Questionable on the NFL injury report in week 5, and in 2 weeks this season before the trade.")
    assert f["T5.8146.injury"].text == "Garrett Wilson was on the NFL injury report in 1 week this season before the trade."
    assert "T5.11834.injury" not in f
    assert "injury report" not in f["T5.12.got.12490"].text


def test_no_injury_facts_without_nflverse(tbundle):
    assert not any(fid.endswith(".injury") for fid in tbundle.sheet.facts)


def test_vocabulary_has_the_usage_terms():
    text = resources.files("cornerstone.prompts").joinpath("vocabulary.md").read_text(encoding="utf-8")
    for term in ("snap share", "target share", "red-zone use", "injury before the trade"):
        assert f"**{term}**" in text


def test_trade_of_a_player_with_no_points_stat_still_gets_a_got_fact(fixture_raw_dir, fixture_history_root):
    # Higbee has a game in the history with no pts_half_ppr key, which used to stop the build.
    raw = load_raw(fixture_raw_dir)
    week = parse_week(raw)
    first, second = list(week.teams)[:2]
    trade = Trade(transaction_id="higbee", created=datetime(2026, 10, 14, tzinfo=ET), roster_ids=[first, second],
                  adds={"3271": second}, drops={"3271": first}, draft_picks=[])
    h = load_history(fixture_history_root, raw, week=6)
    f = build_bundle(week, news=lambda pid: [], history=h, trades=[trade]).sheet.facts
    assert f"T1.{second}.got.3271" in f


def test_chain_trade_keeps_the_moved_player_in_scope(fixture_raw_dir, fixture_history_root):
    # Bucky Irving goes 2 to 3 in trade 1 and 3 to 1 in trade 2, so his line sits on roster 1.
    raw = load_raw(fixture_raw_dir)
    h = load_history(fixture_history_root, raw, week=6)
    made = datetime(2026, 10, 14, tzinfo=ET)
    pid = next(l.player_id for m in parse_week(raw).matchups for s in (m.a, m.b) if s.roster_id == 1
               for l in s.lines if l.name == "Bucky Irving")
    trades = [
        Trade(transaction_id="a", created=made, roster_ids=[2, 3],
              adds={pid: 3}, drops={pid: 2}, draft_picks=[]),
        Trade(transaction_id="b", created=made, roster_ids=[3, 1],
              adds={pid: 1}, drops={pid: 3}, draft_picks=[]),
    ]
    sheet = build_bundle(parse_week(raw), news=lambda p: [], history=h, trades=trades).sheet
    chapter = next(c for c in sheet.chapters if c.key == "trade_1")
    for fid in ("T1.sides", f"T1.3.got.{pid}"):
        blurb = Blurb(chapter="trade_1", attempt=1, fallback=False,
                      sentences=[Sentence(text=sheet.facts[fid].text, fact_ids=[fid])])
        assert not [m for m in code_check(blurb, chapter, sheet) if "not on a team" in m]


def _value_facts(bundle, i):
    return {k: f for k, f in bundle.sheet.facts.items() if k.startswith(f"T{i}.") and k.endswith(".value")}


def test_player_trade_value_fact(vbundle):
    f = vbundle.sheet.facts["T1.12507.value"]
    assert f.text == "Omarion Hampton's trade value was 68.5 in the week of the trade."
    assert f.numbers == ["68.5"]
    assert f.players == ["Omarion Hampton"]


def test_side_trade_value_fact_sums_what_each_side_gave_and_got(vbundle):
    # Roster 4 gave Hampton (68.5) and Pollard (9.0), and got 24.0 and 12.5.
    f = vbundle.sheet.facts["T1.4.value"]
    assert f.text == "Pukancun on 3 gave 77.5 and got 36.5 in trade value."
    assert f.numbers == ["77.5", "36.5"]
    assert f.teams == ["Pukancun on 3"]


def test_unlisted_player_gets_no_value_fact_and_a_clause_on_each_side(vbundle):
    # Kenyon Sadiq (13330) is left out of the chart on purpose.
    facts = vbundle.sheet.facts
    assert "T2.13330.value" not in facts
    assert "T2.10236.value" in facts
    assert facts["T2.7.value"].text == "To Infinity and Bijan gave 31.5 and got 0 in trade value, with Kenyon Sadiq unlisted."
    assert facts["T2.12.value"].text == (
        "Amon-Ra Dawg Your Team gave 0 and got 31.5 in trade value, with Kenyon Sadiq unlisted."
    )
    assert facts["T2.12.value"].players == ["Kenyon Sadiq"]


def test_two_unlisted_players_join_with_and(fixture_raw_dir, fixture_history_root, chart_week6):
    # Roster 7 gave Braelon Allen (11576) and Marvin Harrison (11628) in trade 6.
    unlisted = chart_week6.model_copy(update={"values": {k: v for k, v in chart_week6.values.items()
                                                         if k not in ("11576", "11628")}})
    text = _trade_bundle(fixture_raw_dir, fixture_history_root, chart=unlisted).sheet.facts["T6.7.value"].text
    assert text.endswith("in trade value, with Braelon Allen and Marvin Harrison unlisted.")


def test_trade_with_no_valued_player_has_no_side_fact(fixture_raw_dir, fixture_history_root, chart_week6):
    empty = chart_week6.model_copy(update={"values": {}})
    facts = _trade_bundle(fixture_raw_dir, fixture_history_root, chart=empty).sheet.facts
    assert not [k for k in facts if k.endswith(".value") and k.startswith("T")]


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

    one = build_bundle(week, news=lambda p: [], history=h, trades=[trade([pick(1)])], chart=chart_week6)
    two = build_bundle(week, news=lambda p: [], history=h, trades=[trade([pick(1), pick(2)])], chart=chart_week6)
    assert one.sheet.facts["T1.4.value"].text.endswith("gave 68.5 and got 0 in trade value; the pick is not valued.")
    assert two.sheet.facts["T1.4.value"].text.endswith("in trade value; the picks are not valued.")


def test_without_chart_values_the_sheet_has_no_value_facts(tbundle):
    assert not [k for k in tbundle.sheet.facts if k.endswith(".value") and k.startswith("T")]


def test_vocabulary_has_the_trade_value_term():
    text = resources.files("cornerstone.prompts").joinpath("vocabulary.md").read_text(encoding="utf-8")
    assert "**trade value**" in text
