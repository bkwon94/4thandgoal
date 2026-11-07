"""
Tests for the season sim: small hand-built leagues at the seam of season_sim, with the bracket, the counts, and the
sample of runs. The real data of CPC and NorCal runs in tests/test_sim.py of the pipeline.
"""
import pytest

from league.league_settings import LeagueSettings
from sim.published import SIM_FILE, read_sim, sim_file, write_sim
from sim.season import season_sim

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


def _sim(scores=SCORES, records=RECORDS, remaining=REMAINING, **kwargs):
    settings = _settings(reseed=True, median_game=True)
    return season_sim(scores, records, remaining, season=SEASON, week=2, settings=settings, runs=400, **kwargs)


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
