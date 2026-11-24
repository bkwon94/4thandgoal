"""
The exact rejection reference of a What-if: it draws plain runs of the season sim and keeps only the runs where each
set result holds. The tests of the sim package and of the pipeline compare the weighted draw of season_sim with it.
"""
import random
from collections.abc import Mapping, Sequence

from league.league_settings import LeagueSettings
from sim.season import Pair, SetResult, _bracket, _median, _regular, _winner, draw_model
from sim.tunables import SCORE_DECIMALS


def rejection_odds(
    scores: Mapping[int, list[float]], records: Mapping[int, tuple[int, int, float, float]],
    remaining: Mapping[int, list[Pair]], settings: LeagueSettings, you: int, set_results: Sequence[SetResult], *,
    runs: int, seed: int, projected: Mapping[int, Mapping[int, float]] | None = None,
) -> tuple[dict[int, float], dict[int, float], int]:
    """The playoff odds and the title odds of each roster in percent over the kept runs, and the count of kept runs.

    The draw is the draw of season_sim: the same model and the same rounded scores, with no weight.
    """
    rosters = sorted(records)
    regular = sorted(remaining)
    weeks = regular + list(range(settings.last_regular_week + 1, settings.last_season_week + 1))
    model = draw_model(scores, records, weeks, projected)
    rng = random.Random(seed)
    made = dict.fromkeys(rosters, 0)
    titles = dict.fromkeys(rosters, 0)
    kept = 0
    for _ in range(runs):
        level = {rid: rng.gauss(model.level_mean[rid], model.level_se[rid]) for rid in rosters}
        drawn = {rid: [round(rng.gauss(level[rid], model.spread) + shift, SCORE_DECIMALS)
                       for shift in model.shifts[rid]] for rid in rosters}
        wins, points, against = _regular(records, [remaining[w] for w in regular], drawn, settings.median_game)
        table = sorted(rosters, key=lambda rid: (-wins[rid], -points[rid], -against[rid], rid))
        place = {rid: n for n, rid in enumerate(table[:settings.playoff_spots], start=1)}
        rounds, _ = _bracket(table[:settings.playoff_spots], drawn, len(regular), settings.reseed)
        if not all(_holds(r, you, weeks, remaining, drawn, rounds, place) for r in set_results):
            continue
        kept += 1
        for rid in place:
            made[rid] += 1
        champion = _winner(rounds[-1][0], drawn, weeks.index(weeks[-1]), place) if rounds else table[0]
        titles[champion] += 1
    return ({rid: 100 * n / kept for rid, n in made.items()}, {rid: 100 * n / kept for rid, n in titles.items()},
            kept)


def _holds(
    result: SetResult, you: int, weeks: list[int], remaining: Mapping[int, list[Pair]], drawn: dict[int, list[float]],
    rounds: list[list[Pair]], place: dict[int, int],
) -> bool:
    column = weeks.index(result.week)
    if result.week in remaining:
        (a, b), = [pair for pair in remaining[result.week] if you in pair]
        opponent = b if a == you else a
        x = drawn[you][column]
        week = [scores[column] for scores in drawn.values()]
        above = x > _median(week)
        return (x > drawn[opponent][column]) == (result.game == "win") and (
            result.median is None or above == (result.median == "above"))
    games = [pair for pair in rounds[column - len(remaining)] if you in pair]
    return bool(games) and (_winner(games[0], drawn, column, place) == you) == (result.game == "win")
