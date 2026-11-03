"""
Tests for the impact fact `M<n>.impact`: what the week did to each team of one matchup.
They run on the recorded week 6 data and its history.
"""
from cornerstone.config import cornerstone_config
from cornerstone.history import load_history
from cornerstone.parse import parse_week
from cornerstone.provider.sleeper import load_raw
from cornerstone.sheet import build_bundle

CONFIG = cornerstone_config()


def _impact(raw_dir, history_root, config=CONFIG, history=None):
    """The impact fact text of each matchup of week 6, keyed by matchup id."""
    raw = load_raw(raw_dir)
    h = history if history is not None else load_history(history_root, raw, week=6)
    b = build_bundle(parse_week(raw), news=lambda pid: [], history=h, config=config)
    return {int(fid[1:].split(".")[0]): f.text for fid, f in b.sheet.facts.items() if fid.endswith(".impact")}


def test_the_impact_fact_gives_the_standings_place_before_and_after_for_both_teams(hbundle):
    f = hbundle.sheet.facts
    # Return of T Mac was 9th before week 6 and is 7th after it. Unsolicited Dak Picks went from 7th to 10th.
    assert "Return of T Mac rose from 9th to 7th in the standings" in f["M2.impact"].text
    assert "Unsolicited Dak Picks fell from 7th to 10th in the standings" in f["M2.impact"].text
    # Lil Fridge was 1st before and after.
    assert "Lil Fridge stayed 1st in the standings" in f["M1.impact"].text
    assert f["M2.impact"].teams == ["Return of T Mac", "Unsolicited Dak Picks"]


def test_the_impact_fact_gives_the_median_result_and_the_week_record_of_both_teams(hbundle):
    f = hbundle.sheet.facts
    # Lil Fridge beat Brock 'N' Roll and beat the median. Brock 'N' Roll lost and missed the median.
    assert "beat the median to go 2-0 this week" in f["M1.impact"].text.split(". ")[1]
    assert "missed the median to go 0-2 this week" in f["M1.impact"].text.split(". ")[0]


def test_a_loser_who_beat_the_median_went_1_1(hbundle):
    # behold the lamb beat Bo Girds, and both scored above the median.
    text = hbundle.sheet.facts["M4.impact"].text
    bo, lamb = text.split(". ")[:2]
    assert bo.startswith("Bo Girds") and "beat the median to go 1-1 this week" in bo
    assert lamb.startswith("behold the lamb") and "beat the median to go 2-0 this week" in lamb


def test_a_game_that_starts_or_extends_a_streak_of_3_names_it(hbundle):
    f = hbundle.sheet.facts
    # Return of T Mac had won 2 straight and won again. Unsolicited Dak Picks had lost 2 straight and lost again.
    assert "Return of T Mac" in f["M2.impact"].text and "has now won 3 straight" in f["M2.impact"].text
    assert "has now lost 3 straight" in f["M2.impact"].text
    # London Cooking had won 3 straight and won again.
    assert "London Cooking" in f["M5.impact"].text and "has now won 4 straight" in f["M5.impact"].text


def test_a_streak_under_3_is_left_out(hbundle):
    # Lil Fridge has won 2 straight. Bo Girds has lost 2 straight.
    for mid in (1, 4):
        assert "straight" not in hbundle.sheet.facts[f"M{mid}.impact"].text
        assert "streak" not in hbundle.sheet.facts[f"M{mid}.impact"].text


def test_a_game_that_ends_a_streak_of_3_names_it(fixture_raw_dir, fixture_history_root):
    # behold the lamb won week 3 by 92.26 to 90.02. A score of 89 makes it a loss, so the lamb enters week 6 on 3
    # straight losses and ends the streak with its win over Bo Girds.
    raw = load_raw(fixture_raw_dir)
    h = load_history(fixture_history_root, raw, week=6)
    w3 = h.weeks[3]
    h = h.model_copy(update={"weeks": {**h.weeks, 3: w3.model_copy(update={"scores": {**w3.scores, 10: 89.0}})}})
    text = _impact(fixture_raw_dir, fixture_history_root, history=h)[4]
    lamb = text.split(". ")[1]
    assert lamb.startswith("behold the lamb") and "ended a 3-game losing streak" in lamb


def test_a_team_that_crossed_the_cut_names_it(fixture_raw_dir, fixture_history_root):
    # With 4 playoff spots, Maye d'force B with U rose from 6th to 4th and crossed into the playoff spots, and
    # Brock 'N' Roll fell from 4th to 6th and fell out of them.
    impact = _impact(fixture_raw_dir, fixture_history_root, config=CONFIG.model_copy(update={"playoff_spots": 4}))
    assert "Maye d'force B with U rose from 6th to 4th in the standings, crossed into the playoff spots" in impact[3]
    assert "Brock ‘N’ Roll fell from 4th to 6th in the standings, fell out of the playoff spots" in impact[1]


def test_no_cut_shows_when_the_same_six_teams_hold_the_playoff_spots(hbundle):
    # The six teams in the playoff spots are the same before and after week 6.
    for mid in range(1, 7):
        assert "playoff spots" not in hbundle.sheet.facts[f"M{mid}.impact"].text


def test_a_first_clinch_and_a_first_out_are_named(fixture_raw_dir, fixture_history_root):
    # With week 7 as the last regular week, one week is left after week 6. The plain check gives Lil Fridge and
    # London Cooking a clinch and Pukancun on 3 an out. With two weeks left after week 5, no team had either.
    impact = _impact(fixture_raw_dir, fixture_history_root,
                     config=CONFIG.model_copy(update={"last_regular_week": 7}))
    assert "Lil Fridge" in impact[1] and "clinched a playoff spot" in impact[1]
    assert "London Cooking" in impact[5] and "clinched a playoff spot" in impact[5]
    pukancun = impact[6].split(". ")[1]
    assert pukancun.startswith("Pukancun on 3") and "is now out of the playoff race" in pukancun


def test_a_clinch_or_an_out_from_an_earlier_week_is_left_out(fixture_raw_dir, fixture_history_root):
    # With week 6 as the last regular week, Lil Fridge, London Cooking, and Bo Girds clinched after week 5, and
    # Pukancun on 3 was out after week 5. Maye d'force B with U clinches and Amon-Ra Dawg Your Team is out in week 6.
    impact = _impact(fixture_raw_dir, fixture_history_root,
                     config=CONFIG.model_copy(update={"last_regular_week": 6}))
    for mid in (1, 4, 5):
        assert "clinched" not in impact[mid]
    assert "out of the playoff race" not in impact[6]
    assert "clinched a playoff spot" in impact[3].split(". ")[0]
    assert "is now out of the playoff race" in impact[3].split(". ")[1]


def test_no_clinch_and_no_out_with_eight_weeks_left(hbundle):
    for mid in range(1, 7):
        text = hbundle.sheet.facts[f"M{mid}.impact"].text
        assert "clinched" not in text and "playoff race" not in text


def test_the_matchup_of_the_week_and_each_recap_hold_their_impact_fact_and_no_other_block_does(hbundle):
    chapters = {c.key: c for c in hbundle.sheet.chapters}
    pick = next(fid for fid in chapters["motw"].fact_ids if fid.endswith(".result"))
    assert pick.replace(".result", ".impact") in chapters["motw"].fact_ids
    for mid in range(1, 7):
        impacts = [fid for fid in chapters[f"recap_{mid}"].fact_ids if fid.endswith(".impact")]
        assert impacts == [f"M{mid}.impact"]
    for key in ("next_week", "game_changer"):
        assert not [fid for fid in chapters[key].fact_ids if fid.endswith(".impact")], key


def test_the_impact_fact_never_says_moved_or_rank(hbundle):
    for mid in range(1, 7):
        text = hbundle.sheet.facts[f"M{mid}.impact"].text
        assert "moved" not in text and "rank" not in text and "movement" not in text
