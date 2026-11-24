"""
Tests for the Finish lists and the Paths of The Race: a small hand-built league at the seam of season_sim, read
through the page of each team. The real data of CPC and NorCal runs in tests/test_sim.py of the pipeline.
"""
import pytest

from league.league_settings import LeagueSettings
from sim.season import season_sim

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
