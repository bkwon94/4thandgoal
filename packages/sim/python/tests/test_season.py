"""
Tests for the season sim: small hand-built leagues at the seam of season_sim, with the bracket, the counts, and the
sample of runs. The real data of CPC and NorCal runs in tests/test_sim.py of the pipeline.
"""
import pytest
from rejection import rejection_odds

from league.league_settings import LeagueSettings
from sim.published import SIM_FILE, read_sim, read_week_sim, sim_file, week_sim_file, write_sim, write_week_sim
from sim.season import SetResult, SimStopped, rerun, season_sim

SEASON = 2026
# Eight rosters, 6 playoff spots and 2 byes, as in CPC and NorCal. The regular season ends at week 4.
ROSTERS = range(1, 9)


def _settings(*, reseed: bool, last_regular_week: int = 4, median_game: bool = False) -> LeagueSettings:
    return LeagueSettings(
        team_count=len(ROSTERS), playoff_spots=6, bye_count=2, star_rank_by_position={}, roster_slots=("QB",),
        last_regular_week=last_regular_week, reception_points=0.5, median_game=median_game, reseed=reseed,
    )


def _flat(levels: dict[int, float], weeks: int = 4) -> dict[int, list[float]]:
    """`weeks` played weeks of one fixed score each, so the league spread is 0 and every draw is the shrunk level."""
    return {rid: [level] * weeks for rid, level in levels.items()}


# The seeds follow the roster ID: roster 1 has the most wins. Roster 6, the 6th seed, scores the most each week, so
# it wins every game it plays. Then roster 5 scores more than roster 4, so seed 5 beats seed 4.
FINAL_RECORDS = {rid: (9 - rid, rid - 1, 400.0) for rid in ROSTERS}
LEVELS = {1: 100.0, 2: 99.0, 3: 98.0, 4: 90.0, 5: 95.0, 6: 150.0, 7: 80.0, 8: 70.0}


def _bracket_run(reseed: bool):
    result = season_sim(_flat(LEVELS), FINAL_RECORDS, {}, season=SEASON, week=4, settings=_settings(reseed=reseed),
                        runs=1, sample=1)
    return result.sample[0]


def test_a_reseeded_bracket_gives_seed_1_the_lowest_seed_left_after_round_1():
    run = _bracket_run(reseed=True)
    # Round 1: 3 v 6 and 4 v 5. Seeds 6 and 5 win, so seed 1 meets seed 6 and seed 2 meets seed 5.
    assert run.bracket[0] == [(3, 6), (4, 5)]
    assert run.bracket[1] == [(1, 6), (2, 5)]
    assert run.champion == 6


def test_a_fixed_bracket_gives_seed_1_the_winner_of_4_v_5():
    run = _bracket_run(reseed=False)
    assert run.bracket[0] == [(4, 5), (3, 6)]
    assert run.bracket[1] == [(1, 5), (2, 6)]
    assert run.champion == 6


# A league in its regular season: 2 weeks played, 2 weeks left, real spread, and a median game.
SCORES = {rid: [100.0 + 7 * rid, 120.0 - 5 * rid] for rid in ROSTERS}
RECORDS = {rid: (2 + rid % 3, 2 - rid % 3, 220.0 + rid) for rid in ROSTERS}
REMAINING = {3: [(1, 2), (3, 4), (5, 6), (7, 8)], 4: [(1, 3), (2, 4), (5, 7), (6, 8)]}


def _sim(scores=SCORES, records=RECORDS, remaining=REMAINING, runs=400, **kwargs):
    settings = _settings(reseed=True, median_game=True)
    return season_sim(scores, records, remaining, season=SEASON, week=2, settings=settings, runs=runs, **kwargs)


def test_one_input_gives_one_output_whatever_the_dict_order():
    def backward(d):
        return dict(reversed(list(d.items())))

    assert _sim() == _sim()
    assert _sim(backward(SCORES), backward(RECORDS), backward(REMAINING)) == _sim()


def test_the_counts_add_up_over_all_runs():
    result = _sim()
    assert sum(team.title for team in result.teams.values()) == pytest.approx(100, abs=0.5)
    assert sum(team.final for team in result.teams.values()) == pytest.approx(200, abs=0.5)
    for team in result.teams.values():
        assert sum(team.final_wins.values()) == pytest.approx(100, abs=0.5)
        assert team.title <= team.final
    # Six seeds per run, each held by one team.
    for seed in range(1, 7):
        assert sum(team.seeds.get(seed, 0) for team in result.teams.values()) == pytest.approx(100, abs=0.5)


def test_the_sample_holds_the_first_runs_and_each_replays_from_its_scores():
    result = _sim(sample=25)
    assert len(result.sample) == 25
    assert result.weeks == [3, 4, 5, 6, 7]
    assert result.bracket_weeks == [5, 6, 7]
    for run in result.sample:
        assert all(len(scores) == 5 for scores in run.scores.values())
        # Replay the regular season from the stored scores: the head-to-head game and the median game.
        wins = {rid: r[0] for rid, r in RECORDS.items()}
        points = {rid: r[2] for rid, r in RECORDS.items()}
        for column, week in enumerate((3, 4)):
            # A regular week holds a score for every roster. Only a bracket week holds None.
            scores = {rid: float(run.scores[rid][column] or 0.0) for rid in ROSTERS}
            assert all(run.scores[rid][column] is not None for rid in ROSTERS)
            for a, b in REMAINING[week]:
                wins[a] += scores[a] > scores[b]
                wins[b] += scores[b] > scores[a]
            ordered = sorted(scores.values(), reverse=True)
            median = (ordered[3] + ordered[4]) / 2
            for rid, score in scores.items():
                wins[rid] += score > median
                points[rid] += score
        assert run.table == sorted(ROSTERS, key=lambda rid: (-wins[rid], -points[rid], rid))
        assert run.bracket[-1][0] in {(run.champion, x) for x in ROSTERS} | {(x, run.champion) for x in ROSTERS}


def test_a_tie_in_a_bracket_game_goes_to_the_higher_seed():
    levels = {rid: 100.0 for rid in ROSTERS}
    result = season_sim(_flat(levels), FINAL_RECORDS, {}, season=SEASON, week=4, settings=_settings(reseed=True),
                        runs=1, sample=1)
    assert result.sample[0].bracket == [[(3, 6), (4, 5)], [(1, 4), (2, 3)], [(1, 2)]]
    assert result.sample[0].champion == 1


def test_a_final_table_gives_sure_odds_and_one_final_win_total():
    result = season_sim(_flat(LEVELS), FINAL_RECORDS, {}, season=SEASON, week=4, settings=_settings(reseed=True),
                        runs=50)
    assert [result.teams[rid].playoff for rid in ROSTERS] == [100] * 6 + [0, 0]
    assert [result.teams[rid].bye for rid in ROSTERS] == [100, 100] + [0] * 6
    assert result.teams[1].seeds == {1: 100.0}
    assert result.teams[3].final_wins == {6: 100.0}
    assert result.teams[6].title == 100.0


def test_sim_json_holds_the_names_the_odds_and_the_sample_and_reads_back(tmp_path):
    names = {rid: f"Team {rid}" for rid in ROSTERS}
    out = write_sim(sim_file(_sim(sample=10), names), tmp_path)
    assert out == tmp_path / "2026" / SIM_FILE
    data = read_sim(tmp_path / "2026")
    assert data.names == names
    assert len(data.sample) == 10
    assert data.teams[1].roster_id == 1
    assert write_sim(sim_file(_sim(sample=10), names), tmp_path).read_bytes() == out.read_bytes()
    # The season file keeps the shape that the midseason replay reads.
    assert b"effective_runs" not in out.read_bytes()


def test_a_run_with_no_set_result_has_effective_runs_equal_to_runs():
    assert _sim().effective_runs == 400


def _score(run, rid: int, column: int) -> float:
    """The stored score of a regular week, which is never None."""
    score = run.scores[rid][column]
    assert score is not None
    return score


def _gap(weighted, reference: dict[int, float]) -> float:
    """The largest gap in points between the playoff odds of the sim and of the reference, over the open teams."""
    return max(abs(weighted.teams[rid].playoff - odds) for rid, odds in reference.items()
               if weighted.teams[rid].status == "open")


# The gaps allow for the noise of the two draws. At 20,000 runs the weighted sim keeps about 8,000 effective runs, so
# the sample error of a 50 percent number is about 0.75 points for the two draws together. Over 24 seeds the mean gap
# of each team is under 0.3 points, so the method has no bias.
GAP = 2.0


def test_a_set_result_with_a_median_agrees_with_the_rejection_reference():
    held = [SetResult(week=3, game="loss", median="above")]
    result = _sim(you=1, set_results=held, runs=20_000)
    reference, _, kept = rejection_odds(SCORES, RECORDS, REMAINING, _settings(reseed=True, median_game=True), 1,
                                        held, runs=100_000, seed=7)
    assert _gap(result, reference) <= GAP
    # The weight keeps more of each draw than rejection does.
    assert kept / 100_000 < result.effective_runs / result.runs < 1
    # Each stored run is a season where the set result holds: roster 1 loses to roster 2 and beats the median.
    for run in result.sample:
        ordered = sorted((_score(run, rid, 0) for rid in ROSTERS), reverse=True)
        assert _score(run, 1, 0) <= _score(run, 2, 0)
        assert _score(run, 1, 0) > (ordered[3] + ordered[4]) / 2


def test_a_set_result_in_a_league_with_no_median_game_agrees_with_the_rejection_reference():
    settings = _settings(reseed=True, median_game=False)
    held = [SetResult(week=4, game="win")]
    result = season_sim(SCORES, RECORDS, REMAINING, season=SEASON, week=2, settings=settings, runs=20_000, you=8,
                        set_results=held)
    reference, _, _ = rejection_odds(SCORES, RECORDS, REMAINING, settings, 8, held, runs=40_000, seed=7)
    assert _gap(result, reference) <= GAP
    assert result.effective_runs < result.runs
    for run in result.sample:
        assert _score(run, 8, 1) > _score(run, 6, 1)


# The regular season is over, so the seeds are set: roster 4 meets roster 5 in round 1, in week 5.
BRACKET_SCORES = {rid: [100.0 + 4 * rid, 112.0 - 3 * rid, 95.0 + rid] for rid in ROSTERS}


def _bracket_sim(held: list[SetResult], runs: int = 20_000):
    return season_sim(BRACKET_SCORES, FINAL_RECORDS, {}, season=SEASON, week=4, settings=_settings(reseed=True),
                      runs=runs, you=4, set_results=held)


def test_a_set_bracket_game_agrees_with_the_rejection_reference():
    held = [SetResult(week=5, game="loss")]
    result = _bracket_sim(held)
    _, titles, _ = rejection_odds(BRACKET_SCORES, FINAL_RECORDS, {}, _settings(reseed=True), 4, held, runs=40_000,
                                  seed=7)
    assert result.teams[4].title == 0 and result.teams[4].final == 0
    assert result.effective_runs < result.runs
    assert max(abs(result.teams[rid].title - titles[rid]) for rid in ROSTERS) <= GAP
    for run in result.sample:
        assert (4, 5) in run.bracket[0] and 5 in {rid for pair in run.bracket[1] for rid in pair}


@pytest.mark.parametrize(("you", "week"), [(1, 5), (4, 6)])
def test_a_bracket_game_whose_teams_are_not_set_raises(you, week):
    # Roster 1 has a bye in week 5. The opponent of roster 4 in week 6 depends on the other game of round 1.
    with pytest.raises(ValueError, match=f"week {week} has no set teams"):
        season_sim(BRACKET_SCORES, FINAL_RECORDS, {}, season=SEASON, week=4, settings=_settings(reseed=True),
                   runs=200, you=you, set_results=[SetResult(week=week, game="win")])


def test_the_same_set_results_give_the_same_output_byte_for_byte():
    held = [SetResult(week=3, game="win", median="below"), SetResult(week=4, game="loss", median="above")]
    first = _sim(you=3, set_results=held, sample=20).model_dump_json()
    assert _sim(you=3, set_results=list(reversed(held)), sample=20).model_dump_json() == first


@pytest.mark.parametrize(("held", "message"), [
    ([SetResult(week=2, game="win", median="above")], "week 2 is not a week left"),
    ([SetResult(week=3, game="win")], "week 3 needs above or below the median"),
    ([SetResult(week=5, game="win")], "week 5 has no set teams"),
    ([SetResult(week=3, game="win", median="above"), SetResult(week=3, game="loss", median="below")], "one set"),
])
def test_a_bad_set_result_raises_a_value_error_that_names_it(held, message):
    with pytest.raises(ValueError, match=message):
        _sim(you=1, set_results=held)


def _week_file(tmp_path, **kwargs):
    """The sim of the week, written to its week file and read back, as the What-if of the API reads it."""
    result = _sim(pages=list(ROSTERS), **kwargs)
    out = write_week_sim(week_sim_file(result, {rid: f"Team {rid}" for rid in ROSTERS}), tmp_path)
    return result, read_week_sim(out)


def test_a_rerun_of_the_week_file_with_no_set_result_gives_the_numbers_of_the_file(tmp_path):
    result, file = _week_file(tmp_path)
    again = rerun(file, pages=[1])
    assert again.pages[1] == result.pages[1] == file.pages[1]
    assert again.teams == result.teams
    assert again.sample == result.sample


def test_a_rerun_of_the_week_file_with_a_set_result_equals_the_sim_of_the_week_with_it(tmp_path):
    held = [SetResult(week=3, game="win", median="above")]
    _, file = _week_file(tmp_path)
    expected = _sim(you=1, set_results=held, pages=[1])
    again = rerun(file, you=1, set_results=held, pages=[1])
    assert again.model_dump_json() == expected.model_dump_json()


def test_a_stop_ends_the_sim_between_blocks_before_all_its_runs():
    checks = []

    def stop() -> bool:
        checks.append(1)
        return len(checks) > 1

    with pytest.raises(SimStopped) as stopped:
        _sim(runs=5_000, stop=stop)
    assert 0 < stopped.value.done < 5_000
