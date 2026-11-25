"""
Tests for the Finish lists and the Paths of The Race: a small hand-built league at the seam of season_sim, read
through the page of each team. The real data of CPC and NorCal runs in tests/test_sim.py of the pipeline.
"""
import pytest

from league.league_settings import LeagueSettings
from sim.season import SetResult, season_sim

SEASON = 2026
ROSTERS = range(1, 9)
# A league in its regular season: 2 weeks played, 2 weeks left, as in test_page.py.
SCORES = {rid: [100.0 + 7 * rid, 120.0 - 5 * rid] for rid in ROSTERS}
RECORDS = {rid: (2 + rid % 3, 2 - rid % 3, 220.0 + rid, 200.0 + rid) for rid in ROSTERS}
REMAINING = {3: [(1, 2), (3, 4), (5, 6), (7, 8)], 4: [(1, 3), (2, 4), (5, 7), (6, 8)]}


def _settings(*, median_game: bool) -> LeagueSettings:
    return LeagueSettings(
        team_count=len(ROSTERS), playoff_spots=4, bye_count=2, star_rank_by_position={}, roster_slots=("QB",),
        last_regular_week=4, reception_points=0.5, median_game=median_game, reseed=True,
    )


def _sim(median_game: bool = True, runs: int = 6_000):
    return season_sim(SCORES, RECORDS, REMAINING, season=SEASON, week=2, settings=_settings(median_game=median_game),
                      runs=runs, pages=list(ROSTERS))


@pytest.fixture(scope="module")
def sim():
    return _sim()


def test_each_finish_list_runs_from_all_wins_to_none_and_sums_to_100(sim):
    for rid, page in sim.pages.items():
        for goal in page.goals:
            finishes = page.finishes[goal]
            # Two weeks left with a median game: 4-0 down to 0-4.
            assert [f.more_wins for f in finishes] == [4, 3, 2, 1, 0]
            assert sum(f.chance for f in finishes) == pytest.approx(100, abs=1)
            wins, losses = RECORDS[rid][:2]
            assert [f.record for f in finishes] == [(wins + k, losses + 4 - k) for k in (4, 3, 2, 1, 0)]


def test_the_spot_finish_list_agrees_with_the_ladder(sim):
    for page in sim.pages.values():
        ladder = {step.more_wins: (step.playoff, step.chance) for step in page.ladder}
        assert {f.more_wins: (f.odds, f.chance) for f in page.finishes["spot"]} == ladder


def _all_finishes(sim):
    return [(page, goal, finish) for page in sim.pages.values() for goal, finishes in page.finishes.items()
            for finish in finishes]


def test_a_league_with_no_median_game_has_one_win_a_week_in_each_finish():
    plain = _sim(median_game=False, runs=2_000)
    for page in plain.pages.values():
        assert [f.more_wins for f in page.finishes["spot"]] == [2, 1, 0]


def test_each_path_names_1_to_3_other_teams_with_400_runs_and_reaches_90_unless_it_is_full_or_the_best_chance(sim):
    paths = 0
    for page, goal, finish in _all_finishes(sim):
        for path in finish.paths:
            paths += 1
            teams = [c.roster_id for c in path.conditions]
            assert 1 <= len(teams) <= 3 and len(set(teams)) == len(teams) and page.you not in teams
            assert path.runs >= 400
            assert path.odds > finish.odds
            assert path.odds >= 90 or len(teams) == 3 or finish.case == "best"
            # A condition is a final record at most: the team ends at the record or worse.
            for c in path.conditions:
                wins, losses = RECORDS[c.roster_id][:2]
                assert c.record[0] - wins + c.record[1] - losses == 4 and c.record[0] - wins < 4
    assert paths > 0


def test_no_path_repeats_and_only_the_spot_and_the_bye_hold_paths(sim):
    for _, goal, finish in _all_finishes(sim):
        sets = [frozenset((c.roster_id, tuple(c.record)) for c in path.conditions) for path in finish.paths]
        assert len(sets) == len(set(sets))
        if goal.startswith("seed-"):
            assert finish.paths == []


def test_a_sure_or_hopeless_finish_has_no_path_and_a_best_chance_holds_one(sim):
    cases = {finish.case for _, _, finish in _all_finishes(sim)}
    assert {"sure", "none"} <= cases
    for _, goal, finish in _all_finishes(sim):
        if finish.case in ("sure", "none", "open"):
            assert finish.paths == []
        if finish.case == "best":
            assert len(finish.paths) == 1 and finish.paths[0].odds < 90
        if finish.case == "paths":
            assert finish.paths and all(path.odds >= 90 for path in finish.paths)


def _plans(sim):
    """Each Week plan of each page: the plan of each Path of the spot and the bye, and of each Finish of a seed."""
    for page, goal, finish in _all_finishes(sim):
        for path in finish.paths:
            yield page, goal, finish, path.plan
        if finish.plan is not None:
            yield page, goal, finish, finish.plan


def test_each_path_and_each_seed_finish_with_a_way_in_holds_a_week_plan(sim):
    for _, goal, finish in _all_finishes(sim):
        assert all(path.plan is not None for path in finish.paths)
        if goal.startswith("seed-"):
            assert (finish.plan is None) == (finish.case == "none")
        else:
            assert finish.plan is None


def test_a_week_plan_has_one_row_per_week_left_and_its_results_add_up_to_its_finish(sim):
    plans = 0
    for page, _, finish, plan in _plans(sim):
        plans += 1
        assert [week.week for week in plan.weeks] == sorted(REMAINING)
        for week in plan.weeks:
            assert week.opponent == next(b if a == page.you else a for a, b in REMAINING[week.week] if page.you in (a, b))
        assert sum((w.game == "win") + (w.median == "above") for w in plan.weeks) == finish.more_wins
    assert plans > 0


def test_each_row_of_a_week_plan_holds_the_score_to_beat_of_its_result(sim):
    # AT-12. A win row holds the scores to beat the opponent, and a row above the median holds the scores to beat the
    # median, as the Score to beat of the page gives them. A loss row and a median miss hold none.
    kinds = set()
    for page, _, _, plan in _plans(sim):
        beat = {s.week: s for s in page.score_to_beat}
        for week in plan.weeks:
            kinds.add((week.game, week.median))
            s = beat[week.week]
            win = (s.win, s.win_sure) if week.game == "win" else (None, None)
            median = (s.median, s.median_sure) if week.median == "above" else (None, None)
            assert (week.win, week.win_sure) == win
            assert (week.median_score, week.median_sure) == median
    assert {("win", "above"), ("loss", "below")} <= kinds


def test_a_week_plan_row_of_a_league_with_no_median_game_holds_no_median_score():
    plain = _sim(median_game=False, runs=2_000)
    rows = [week for _, _, _, plan in _plans(plain) for week in plan.weeks]
    assert rows and all(week.median_score is None and week.median_sure is None for week in rows)
    assert all((week.win is None) == (week.game == "loss") for week in rows)


def test_each_game_to_root_for_in_a_plan_is_another_game_of_its_week(sim):
    rows = 0
    for page, _, _, plan in _plans(sim):
        for week in plan.weeks:
            assert len(week.root_for) <= 2
            for game in week.root_for:
                rows += 1
                assert page.you not in (game.winner, game.loser)
                assert tuple(sorted((game.winner, game.loser))) in {tuple(sorted(p)) for p in REMAINING[week.week]}
    assert rows > 0


def test_a_plan_with_one_order_says_the_order_matters():
    # A Finish of every win or of no win has one order of results, which holds all its runs.
    plain = _sim(median_game=False, runs=3_000)
    for page in plain.pages.values():
        for finish in page.finishes["seed-1"]:
            if finish.plan is not None and finish.more_wins in (0, 2):
                assert finish.plan.any_order is False


def test_the_score_to_beat_of_each_week_puts_the_sure_score_above_the_coin_flip(sim):
    for page in sim.pages.values():
        assert [s.week for s in page.score_to_beat] == sorted(REMAINING)
        for s in page.score_to_beat:
            assert s.opponent == next(b if a == page.you else a for a, b in REMAINING[s.week] if page.you in (a, b))
            assert s.win_sure > s.win and s.median_sure > s.median


def test_a_league_with_no_median_game_has_no_median_score_to_beat():
    plain = _sim(median_game=False, runs=2_000)
    for page in plain.pages.values():
        assert page.score_to_beat and all(s.median is None and s.median_sure is None for s in page.score_to_beat)


def test_the_try_it_odds_of_a_plan_equal_a_what_if_of_the_plan_within_the_error_of_the_sample():
    # The plan of the most likely Finish of the spot of each team with a Path. "Try it" reads the runs that follow
    # the plan, and the What-if draws them with weights, so the two agree within the error of the sample of the plan.
    # At 30,000 runs a plan holds about 3,000 runs, and 3 points is about 3 standard errors of the gap.
    big = _sim(runs=30_000)
    checked = 0
    for page in big.pages.values():
        finishes = [f for f in page.finishes["spot"] if f.paths]
        if not finishes:
            continue
        plan = max(finishes, key=lambda f: f.chance).paths[0].plan
        assert plan is not None
        held = [SetResult(week=w.week, game=w.game, median=w.median) for w in plan.weeks]
        what_if = season_sim(SCORES, RECORDS, REMAINING, season=SEASON, week=2, settings=_settings(median_game=True),
                             runs=30_000, you=page.you, set_results=held)
        odds = what_if.teams[page.you].playoff
        print(f"team {page.you}: Try it {plan.odds}, What-if {odds}")
        assert abs(odds - plan.odds) <= 3
        checked += 1
    assert checked
