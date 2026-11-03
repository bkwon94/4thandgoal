"""
Tests for the impact fact `M<n>.impact`: what the week did to each team of one matchup.
They run on the recorded week 6 data and its history, and on the saved weeks 7 and 8.
"""
import re
import shutil
from pathlib import Path

import pytest
from fakes import no_news

from cornerstone.config import cornerstone_config
from cornerstone.history import load_history
from cornerstone.parse import parse_week
from cornerstone.paths import history_root, week_dir
from cornerstone.pipeline import make_bundle
from cornerstone.provider.sleeper import load_raw
from cornerstone.sheet import base, build_bundle

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


def test_a_week_with_no_saved_odds_before_it_has_no_odds_part_and_keeps_the_other_parts(hbundle):
    # Week 6 is `ODDS_FROM_WEEK`, so no week before it saved odds. Its own odds are in the bundle.
    assert hbundle.odds is not None
    for mid in range(1, 7):
        text = hbundle.sheet.facts[f"M{mid}.impact"].text
        assert "playoff odds" not in text and "%" not in text
        assert "in the standings" in text and "the median to go" in text


SAVED = Path(__file__).parent.parent / "data" / "2026"


def _saved_repo(tmp_path, week):
    """A repo of links to the saved raw data of `week`, the saved history, and the saved facts of the week before."""
    for path in (week_dir(tmp_path, 2026, week), history_root(tmp_path, 2026).parent):
        path.mkdir(parents=True, exist_ok=True)
    (week_dir(tmp_path, 2026, week) / "raw").symlink_to(SAVED / f"week-{week:02d}" / "raw")
    history_root(tmp_path, 2026).symlink_to(SAVED / "history")
    before = week_dir(tmp_path, 2026, week - 1)
    before.mkdir(parents=True)
    shutil.copy(SAVED / f"week-{week - 1:02d}" / "facts.json", before / "facts.json")
    return tmp_path


@pytest.fixture(scope="module")
def week_8(tmp_path_factory):
    """The week 8 bundle from the saved week 8 data, with the saved week 7 odds as the odds before."""
    repo = _saved_repo(tmp_path_factory.mktemp("repo"), 8)
    bundle, _ = make_bundle(repo, 2026, 8, news=no_news, config=CONFIG)
    return bundle


@pytest.mark.skipif(not (SAVED / "week-08" / "raw").is_dir(), reason="no saved week 8 data")
def test_the_impact_fact_gives_the_playoff_odds_before_and_after_the_week(week_8):
    # The saved week 7 odds give Lil Fridge 99 and Maye d'force B with U 49.
    text = next(f.text for fid, f in week_8.sheet.facts.items() if fid.endswith(".impact") and "Lil Fridge" in f.text)
    fridge, maye = (s for s in text.split(". ") if s.startswith(("Lil Fridge", "Maye")))
    for sentence, rid, before in ((fridge, 3, 99), (maye, 9, 49)):
        after = week_8.odds.teams[rid].playoff
        assert f"saw its playoff odds go from about {before}% to about {after}% this week" in sentence
    # The odds part sits after the place and before the median.
    assert fridge.index("in the standings") < fridge.index("playoff odds") < fridge.index("the median")


@pytest.mark.skipif(not (SAVED / "week-08" / "raw").is_dir(), reason="no saved week 8 data")
def test_the_odds_after_the_week_match_the_saved_playoff_odds_of_each_team(week_8):
    team = {t.name: rid for rid, t in week_8.data.teams.items()}
    impacts = [f for fid, f in week_8.sheet.facts.items() if fid.endswith(".impact")]
    assert len(impacts) == 6
    for f in impacts:
        for sentence in f.text.split(". "):
            name = next(n for n in f.teams if sentence.startswith(n))
            after = re.search(r"playoff odds go from (?:about )?\d+% to (?:about )?(\d+)% this week", sentence)
            assert after is not None and int(after.group(1)) == week_8.odds.teams[team[name]].playoff, sentence
            assert after.group(1) in f.numbers


@pytest.mark.skipif(not (SAVED / "week-08" / "raw").is_dir(), reason="no saved week 8 data")
def test_the_build_runs_the_odds_engine_once_per_week(tmp_path, monkeypatch):
    runs = []
    engine = base.playoff_odds

    def counted(*args, **kwargs):
        runs.append(kwargs["week"])
        return engine(*args, **kwargs)

    monkeypatch.setattr(base, "playoff_odds", counted)
    make_bundle(_saved_repo(tmp_path, 8), 2026, 8, news=no_news, config=CONFIG)
    assert runs == [8]


def test_a_sure_100_or_0_takes_no_about_and_an_engine_number_does(fixture_raw_dir, fixture_history_root, hbundle):
    # The odds before are the week 6 odds, with Lil Fridge at a sure 100 and Brock 'N' Roll at a sure 0.
    teams = dict(hbundle.odds.teams)
    teams[3] = teams[3].model_copy(update={"playoff": 100, "status": "in"})
    teams[1] = teams[1].model_copy(update={"playoff": 0, "status": "out"})
    raw = load_raw(fixture_raw_dir)
    b = build_bundle(parse_week(raw), news=lambda pid: [], history=load_history(fixture_history_root, raw, week=6),
                     odds_before=hbundle.odds.model_copy(update={"teams": teams}), config=CONFIG)
    brock, fridge = b.sheet.facts["M1.impact"].text.split(". ")[:2]
    assert f"saw its playoff odds go from 100% to about {b.odds.teams[3].playoff}% this week" in fridge
    assert f"saw its playoff odds go from 0% to about {b.odds.teams[1].playoff}% this week" in brock
