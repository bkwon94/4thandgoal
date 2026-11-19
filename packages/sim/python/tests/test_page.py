"""
Tests for the page block of the season sim: a small hand-built league at the seam of season_sim, read through the
page of one team. The real data of CPC and NorCal runs in tests/test_sim.py of the pipeline.
"""
import json

import pytest

from league.league_settings import LeagueSettings
from sim.published import read_week_sim, sim_file, week_sim_file, write_sim, write_week_sim
from sim.season import SetResult, season_sim

SEASON = 2026
ROSTERS = range(1, 9)
# A league in its regular season: 2 weeks played, 2 weeks left. The records put roster 5 at 4-0 and roster 3 at 0-4.
SCORES = {rid: [100.0 + 7 * rid, 120.0 - 5 * rid] for rid in ROSTERS}
RECORDS = {rid: (2 + rid % 3, 2 - rid % 3, 220.0 + rid) for rid in ROSTERS}
REMAINING = {3: [(1, 2), (3, 4), (5, 6), (7, 8)], 4: [(1, 3), (2, 4), (5, 7), (6, 8)]}
REASONS = {"2 wins ahead of you", "1 win ahead of you", "Level with you", "1 win behind you",
           "In the race for the last spot"}


def _settings(*, median_game: bool) -> LeagueSettings:
    return LeagueSettings(
        team_count=len(ROSTERS), playoff_spots=4, bye_count=2, star_rank_by_position={}, roster_slots=("QB",),
        last_regular_week=4, reception_points=0.5, median_game=median_game, reseed=True,
    )


def _sim(median_game: bool = True, runs: int = 4_000, **kwargs):
    return season_sim(SCORES, RECORDS, REMAINING, season=SEASON, week=2, settings=_settings(median_game=median_game),
                      runs=runs, pages=list(ROSTERS), **kwargs)


@pytest.fixture(scope="module")
def sim():
    return _sim()


def test_the_sim_gives_one_page_for_each_asked_team_and_none_by_default(sim):
    assert sorted(sim.pages) == list(ROSTERS)
    plain = season_sim(SCORES, RECORDS, REMAINING, season=SEASON, week=2, settings=_settings(median_game=True),
                       runs=100)
    assert plain.pages == {}


def test_the_ladder_lists_each_count_of_more_wins_with_the_chance_of_the_final_win_total(sim):
    for rid, page in sim.pages.items():
        # Two weeks left with a median game: 0 to 4 more wins.
        assert [step.more_wins for step in page.ladder] == [0, 1, 2, 3, 4]
        assert page.wins_left == 4 and page.weeks_left == 2
        final_wins = sim.teams[rid].final_wins
        assert {step.more_wins: step.chance for step in page.ladder if step.chance} == {
            wins - RECORDS[rid][0]: chance for wins, chance in final_wins.items()}


def test_the_ladder_odds_rise_with_the_wins_and_the_sentence_names_the_smallest_count_at_90(sim):
    for page in sim.pages.values():
        shown = [step.playoff for step in page.ladder if step.playoff is not None]
        assert shown == sorted(shown)
        at_90 = [step.more_wins for step in page.ladder if step.playoff is not None and step.playoff >= 90]
        assert page.need == (at_90[0] if at_90 else None)
        if page.status == "open" and page.need:
            assert page.sentence == f"Win {page.need} of the 4 left and you're in."


def test_each_week_has_four_results_with_wins_added_of_2_1_1_and_0(sim):
    page = sim.pages[1]
    assert [w.week for w in page.weeks] == [3, 4]
    assert [w.opponent for w in page.weeks] == [2, 3]
    week = page.weeks[0]
    assert [(r.game, r.median, r.wins_added) for r in week.results] == [
        ("win", "above", 2), ("win", "below", 1), ("loss", "above", 1), ("loss", "below", 0)]
    assert sum(r.chance for r in week.results) == pytest.approx(100, abs=0.2)
    # A win and the median each add a win, so the result with two more wins gives the best odds.
    odds = [r.playoff for r in week.results]
    assert odds[0] >= max(odds[1:]) and odds[3] <= min(odds[:3])


def test_a_league_with_no_median_game_has_two_results():
    sim = _sim(median_game=False, runs=1_000)
    week = sim.pages[1].weeks[0]
    assert [(r.game, r.median, r.wins_added) for r in week.results] == [("win", None, 1), ("loss", None, 0)]
    assert [step.more_wins for step in sim.pages[1].ladder] == [0, 1, 2]


def test_the_odds_after_a_loss_match_the_loss_side_of_the_swing(sim):
    # The swing and the page split the same runs on the next-week game, so both give the odds after a loss. The
    # page counts an exact tie as a loss, as a set result does, and the swing leaves it out, so the two can differ
    # by 1 point.
    swings = {(s.a, s.b): s for s in sim.swings}
    for a, b in REMAINING[3]:
        assert abs(sim.pages[a].weeks[0].loss_playoff - swings[(a, b)].a_loss) <= 1
        assert abs(sim.pages[b].weeks[0].loss_playoff - swings[(a, b)].b_loss) <= 1


def test_the_root_for_rows_follow_the_rules_of_the_spec(sim):
    rows_seen = 0
    for rid, page in sim.pages.items():
        for week in page.weeks:
            assert len(week.root_for) <= 3
            lifts = [row.playoff - week.loss_playoff for row in week.root_for]
            assert all(lift >= 1 for lift in lifts)
            assert lifts == sorted(lifts, reverse=True)
            for row in week.root_for:
                assert row.reason in REASONS
                assert rid not in (row.winner, row.loser)
                assert (row.winner, row.loser) in REMAINING[week.week] or (row.loser, row.winner) in REMAINING[week.week]
            rows_seen += len(week.root_for)
    assert rows_seen > 0


def test_the_reason_names_the_gap_in_real_wins_to_the_loser(sim):
    named = {2: "2 wins ahead of you", 1: "1 win ahead of you", 0: "Level with you", -1: "1 win behind you"}
    for rid, page in sim.pages.items():
        for week in page.weeks:
            for row in week.root_for:
                gap = RECORDS[row.loser][0] - RECORDS[rid][0]
                assert row.reason == named.get(gap, "In the race for the last spot")


def test_a_result_is_about_when_its_chance_times_the_effective_runs_is_under_400(sim):
    flagged = 0
    for page in sim.pages.values():
        for week in page.weeks:
            for r in week.results:
                assert r.about == (r.chance / 100 * sim.effective_runs < 400)
                flagged += r.about
    # At 4,000 runs a result under 10 percent is about, so the fixture league has both cases.
    assert 0 < flagged < sum(len(w.results) for p in sim.pages.values() for w in p.weeks)


def test_a_set_result_holds_in_the_page_of_your_team():
    sim = _sim(you=1, set_results=[SetResult(week=3, game="win", median="above")], runs=2_000)
    week = sim.pages[1].weeks[0]
    assert week.results[0].chance == 100.0
    assert [r.playoff for r in week.results[1:]] == [None, None, None]
    assert all(r.about for r in week.results[1:])


def test_the_weights_of_the_stored_runs_are_1_with_no_set_result_and_under_1_with_one(sim):
    assert sim.sample_weights == [1.0] * len(sim.sample)
    held = _sim(you=1, set_results=[SetResult(week=3, game="loss", median="below")], runs=500)
    assert len(held.sample_weights) == len(held.sample)
    assert all(0 < w < 1 for w in held.sample_weights)


def test_the_league_fact_names_the_race_for_the_last_spots(sim):
    safe = sum(t.playoff >= 90 for t in sim.teams.values())
    race = sum(10 <= t.playoff < 90 for t in sim.teams.values())
    left = 4 - safe
    if race > left > 0:
        spots = "spot" if left == 1 else f"{left} spots"
        assert sim.fact == f"{race} managers fight for the last {spots}"
    else:
        assert sim.fact == "The playoff field is all but set"


def test_the_week_file_holds_the_pages_and_the_season_file_keeps_its_shape(sim, tmp_path):
    names = {rid: f"Team {rid}" for rid in ROSTERS}
    out = write_week_sim(week_sim_file(sim, names), tmp_path)
    assert out == tmp_path / "2026" / "week-02" / "sim.json"
    data = json.loads(out.read_text(encoding="utf-8"))
    assert {"schema_version", "effective_runs", "sample", "sample_weights", "pages", "fact", "names"} <= set(data)
    assert sorted(data["pages"]) == [str(rid) for rid in ROSTERS]
    assert read_week_sim(out) == week_sim_file(sim, names)
    season = write_sim(sim_file(sim, names), tmp_path).read_text(encoding="utf-8")
    for key in ("effective_runs", "sample_weights", "pages", "fact"):
        assert f'"{key}"' not in season


def test_the_sentence_after_a_set_result_counts_only_the_wins_still_open():
    # Week 3 holds a win over the opponent and the median, so 2 of the 4 wins left are set and 2 stay open.
    sim = _sim(you=1, set_results=[SetResult(week=3, game="win", median="above")], runs=2_000)
    page = sim.pages[1]
    assert page.need is not None and page.need >= 2
    open_need = page.need - 2
    if page.status == "open":
        assert page.sentence == (f"Win {open_need} of the 2 left and you're in." if open_need
                                 else "You're in at 90% or better even with no more wins.")
    # The page of another team holds no set result, so its sentence counts all 4 wins left.
    other = sim.pages[2]
    if other.status == "open" and other.need:
        assert other.sentence == f"Win {other.need} of the 4 left and you're in."


def test_the_sentence_with_every_week_left_set_says_so():
    held = [SetResult(week=3, game="win", median="below"), SetResult(week=4, game="loss", median="above")]
    sim = _sim(you=1, set_results=held, runs=2_000)
    if sim.pages[1].status == "open":
        assert sim.pages[1].sentence == "Every week left is set."
