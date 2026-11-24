"""
The season sim: a Monte Carlo of the rest of the regular season and the playoff bracket. It is the one odds engine: it
gives the weekly odds, the swings, the seed odds, the final-win odds, and a sample of runs. No network and no Claude.
"""
import math
import random
from collections import defaultdict
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from statistics import NormalDist
from typing import Literal

from pydantic import BaseModel, field_validator

from league.league_settings import LeagueSettings
from league.models import OddsResult, OddsStatus, Swing, TeamOdds
from league.standings_table import roster_status
from sim.goals import BoardTeam, GoalOdds
from sim.page import RunRecord, SimPage, league_fact, team_page
from sim.percent import shown, tenths
from sim.tunables import (
    LEVEL_SHRINK_WEEKS,
    PROJECTION_WEIGHT,
    SAMPLE_RUNS,
    SCORE_DECIMALS,
    SEED_SHOW_AT,
    SIM_RUNS,
    STOP_CHECK_RUNS,
)

Pair = tuple[int, int]
# A bracket hold sets the scores of one round before its winners count, and gives the weight of that round.
Hold = Callable[[int, list[Pair], int, dict[int, int]], float]
_NORMAL = NormalDist()
# Half a rounding cell of a drawn score. A rounded score is above a line on the 0.1 grid exactly when its raw draw is
# above the line plus this half cell, so a cut at that edge keeps whole cells.
_HALF_CELL = 0.05


class SetResult(BaseModel):
    """One result of a What-if: the result of Your team in one week left. GLOSSARY.md, "What-if".

    A regular week of a league with a median game sets both the game and the median. A league with no median game,
    and a bracket week, set the game only. A loss is no win, so an exact tie in a regular week is a loss.
    """
    week: int
    game: Literal["win", "loss"]
    median: Literal["above", "below"] | None = None


class SimStopped(Exception):
    """The sim stopped on a stop check before it ran all its runs. A What-if stops so when its client went away."""

    def __init__(self, done: int, runs: int) -> None:
        super().__init__(f"the sim stopped after {done} of {runs} runs")
        self.done = done
        self.runs = runs


@dataclass(frozen=True)
class DrawModel:
    """The numbers of the draw. `SimParameters` holds the same numbers for the file."""
    league_mean: float
    spread: float
    level_mean: dict[int, float]
    level_se: dict[int, float]
    # The shift of each roster's drawn score in each week that a run draws.
    shifts: dict[int, list[float]]


class SimRun(BaseModel):
    """One stored run of the sim. GLOSSARY.md, "Sim run". The replay plays it with no draw of its own."""
    # The drawn score of each roster in each week of `SimResult.weeks`: the regular weeks left, then the bracket weeks.
    # A bracket week of a roster with no game that week holds None, which keeps the file under its size cap.
    scores: dict[int, list[float | None]]
    # The roster IDs in the final order of the regular season. The first `playoff_spots` are the seeds.
    table: list[int]
    # The games of each bracket round, by roster ID, the higher seed first. A bye plays no game.
    bracket: list[list[Pair]]
    champion: int


class TeamSim(BaseModel):
    """The odds of one team over all runs."""
    roster_id: int
    # The playoff odds and the bye odds in whole percent, by the rule of the weekly odds: 100 for a sure spot, 0 for
    # no chance, and 1 to 99 for an open race.
    playoff: int
    bye: int
    # The most common seed over the runs where the team makes the playoffs, the better seed on a tie. None when the
    # playoff odds are below SEED_SHOW_AT.
    seed: int | None
    # In for a sure spot, out for no chance, and open for a race, by the plain check on wins.
    status: OddsStatus
    # The odds in percent of all runs, with one decimal: the final, the title, each seed, and each final win total.
    final: float
    title: float
    seeds: dict[int, float]
    final_wins: dict[int, float]
    # The mean wins at the end of the regular season. The page orders the teams by it.
    mean_wins: float


class SimParameters(BaseModel):
    """The numbers of the draw, so a live sim in the browser can draw the same model later.

    Each number is unrounded. A JSON float reads back to the same float, so a rerun of the week file draws the same
    runs as the build, and a What-if with no set result gives the numbers of the file.
    """
    league_mean: float
    # The league spread of a weekly score around a roster's level.
    spread: float
    # The mean and the standard error of each roster's level.
    level_mean: dict[int, float]
    level_se: dict[int, float]
    # The shift of each roster's drawn score in each week of `SimResult.weeks`.
    shifts: dict[int, list[float]]
    projection_weight: float
    shrink_weeks: float
    playoff_spots: int
    bye_count: int
    median_game: bool
    reseed: bool


class SimResult(BaseModel):
    """The result of the sim after week `week`."""
    season: int
    week: int
    runs: int
    # The effective sample size of the weights of the runs. It equals `runs` with no set result.
    effective_runs: int
    # The random seed of the draw. It derives from the season and the week, so one input gives one output.
    random_seed: int
    # The weeks that a run draws: the regular weeks left, then one week per bracket round.
    weeks: list[int]
    # The weeks of the bracket, a subset of `weeks`.
    bracket_weeks: list[int]
    # The real wins, losses, points for, and points against of each roster at the start of the sim.
    records: dict[int, tuple[int, int, float, float]]
    # The head-to-head pairs of each regular week left.
    schedule: dict[int, list[Pair]]
    parameters: SimParameters
    teams: dict[int, TeamSim]
    # The swing of each head-to-head game of the next regular week, in pair order. Empty with no regular week left.
    swings: list[Swing]
    sample: list[SimRun]
    # The weight of each stored run, in the order of `sample`. Each is 1 with no set result. The replay picks a stored
    # run with a chance in proportion to its weight, so it follows the set results.
    sample_weights: list[float] = []
    # The page block of each team that the call asks for, by roster ID.
    pages: dict[int, SimPage] = {}
    # The league fact of the Sim tile. None with no regular week left: the week file then writes the playoff fact.
    fact: str | None = None
    # The real scores of each played bracket week, by week and roster ID. Each run keeps them, so the bracket of a
    # played round is the real one in each run.
    played: dict[int, dict[int, float]] = {}
    # The League board: the Goals of each team, by roster ID. Empty with no regular week left.
    board: list[BoardTeam] = []

    @field_validator("records", mode="before")
    @classmethod
    def _records_of_an_older_file(cls, records):
        """A sim file written before points against held three values. Its tie falls to the roster ID, as before."""
        return {rid: (*record, 0.0) if len(record) == 3 else record for rid, record in records.items()}


def season_sim(
    scores: Mapping[int, list[float]],
    records: Mapping[int, tuple[int, int, float, float]],
    remaining: Mapping[int, list[Pair]],
    *,
    season: int,
    week: int,
    settings: LeagueSettings,
    projected: Mapping[int, Mapping[int, float]] | None = None,
    runs: int = SIM_RUNS,
    sample: int = SAMPLE_RUNS,
    you: int | None = None,
    set_results: Sequence[SetResult] = (),
    pages: Sequence[int] = (),
    stop: Callable[[], bool] | None = None,
    played: Mapping[int, Mapping[int, float]] | None = None,
) -> SimResult:
    """The sim of the rest of the season after week `week`, through the playoff bracket.

    The draw is the draw of the weekly playoff odds. `scores` holds each roster's played-week scores, oldest first.
    `records` holds the real wins, losses, and points for. `remaining` holds the pairs of each regular week left.
    Each run first draws each roster's level: a normal around its season average, shrunk toward the league average
    with weight n over n plus the shrink weeks. Then each week's score is a normal around the level with the league
    spread, moved by the projection weight times the gap from the projected best-lineup total of that week to the
    roster's season average. `projected` holds the totals by roster ID and week, through the bracket weeks.
    The bracket plays one round a week after `settings.last_regular_week`. A tie in a bracket game goes to the higher
    seed. With `settings.reseed`, the top seed left meets the lowest seed left in each round.

    `set_results` holds the What-if of Your team `you`, at most one result per week. Each run draws the held scores
    cut to the side of each set result, so each run holds them, and the run gets the chance of the cut as a weight
    (decision 07). Each count of the result is a sum of weights. The level of a team has no injury term.

    `pages` holds the roster IDs whose page block the result gives, each by a split of the runs of this one sim.
    `stop` runs every STOP_CHECK_RUNS runs. When it gives True, the sim raises SimStopped.
    `played` holds the real scores of each bracket week already played, by week and roster ID. Each run keeps them.
    """
    bracket_weeks = list(range(settings.last_regular_week + 1, settings.last_season_week + 1))
    model = draw_model(scores, records, sorted(remaining) + bracket_weeks, projected)
    return _season_sim(model, records, remaining, season=season, week=week, spots=settings.playoff_spots,
                       bye_count=settings.bye_count, median_game=settings.median_game, reseed=settings.reseed,
                       bracket_weeks=bracket_weeks, runs=runs, sample=sample, you=you, set_results=set_results,
                       pages=pages, stop=stop, played=played or {})


def rerun(
    result: SimResult, *, you: int | None = None, set_results: Sequence[SetResult] = (), pages: Sequence[int] = (),
    stop: Callable[[], bool] | None = None,
) -> SimResult:
    """The sim of `result` again, on the numbers of its draw, with the What-if `set_results` of Your team `you`.

    The What-if of the API reads the week file and calls no network (decision 03). The draw has the same numbers, the
    same seed, and the same count of runs, so with no set result it gives the numbers of `result` again.
    """
    p = result.parameters
    model = DrawModel(league_mean=p.league_mean, spread=p.spread, level_mean=dict(p.level_mean),
                      level_se=dict(p.level_se), shifts={rid: list(values) for rid, values in p.shifts.items()})
    remaining = {w: [(a, b) for a, b in pairs] for w, pairs in result.schedule.items()}
    return _season_sim(model, result.records, remaining, season=result.season, week=result.week,
                       spots=p.playoff_spots, bye_count=p.bye_count, median_game=p.median_game, reseed=p.reseed,
                       bracket_weeks=list(result.bracket_weeks), runs=result.runs, sample=len(result.sample), you=you,
                       set_results=set_results, pages=pages, stop=stop, played=result.played)


def _season_sim(
    model: DrawModel,
    records: Mapping[int, tuple[int, int, float, float]],
    remaining: Mapping[int, list[Pair]],
    *,
    season: int,
    week: int,
    spots: int,
    bye_count: int,
    median_game: bool,
    reseed: bool,
    bracket_weeks: list[int],
    runs: int,
    sample: int,
    you: int | None,
    set_results: Sequence[SetResult],
    pages: Sequence[int],
    stop: Callable[[], bool] | None,
    played: Mapping[int, Mapping[int, float]],
) -> SimResult:
    """The sim of `season_sim` on the numbers `model` of its draw."""
    rosters = sorted(records)
    regular = sorted(remaining)
    weeks = regular + bracket_weeks
    seed = season * 100 + week
    rng = random.Random(seed)
    spread, level_mean, level_se, shifts = model.spread, model.level_mean, model.level_se, model.shifts
    if not set(played) <= set(bracket_weeks):
        raise ValueError("a played week must be a bracket week")
    # The column of each played bracket week, and its real scores.
    kept = [(weeks.index(w), dict(scores)) for w, scores in sorted(played.items())]
    held = _checked(set_results, you, rosters, remaining, bracket_weeks, median_game, frozenset(played))
    # The set results of the regular weeks, as (column, opponent, result), in week order.
    held_regular = [(weeks.index(r.week), _opponent(remaining[r.week], you), r) for r in held if r.week in remaining]
    held_bracket = {weeks.index(r.week): r for r in held if r.week not in remaining}
    # The opponent of Your team in each set bracket week, from the first run. Each later run must give the same game.
    bracket_opponent: dict[int, int] = {}
    # The line of the median game is the k-th highest score of the week (decision 07).
    k = len(rosters) // 2

    # Each count is a sum of run weights. With no set result each weight is 1, so each sum is a whole count.
    total = squares = 0.0
    made: defaultdict[int, float] = defaultdict(float)
    byes: defaultdict[int, float] = defaultdict(float)
    finals: defaultdict[int, float] = defaultdict(float)
    titles: defaultdict[int, float] = defaultdict(float)
    seeds: dict[int, defaultdict[int, float]] = {rid: defaultdict(float) for rid in rosters}
    wins_count: dict[int, defaultdict[int, float]] = {rid: defaultdict(float) for rid in rosters}
    stored: list[SimRun] = []
    stored_weights: list[float] = []
    # The page block reads each run again, so the sim keeps a record of each run only when a page is asked for.
    log: list[RunRecord] = []
    next_pairs = list(remaining[regular[0]]) if regular else []
    # Per next-week pair and per winner, three sums: the runs, the runs side a made it, the runs side b made it.
    halves = {pair: {"a": [0.0, 0.0, 0.0], "b": [0.0, 0.0, 0.0]} for pair in next_pairs}
    for index in range(runs):
        if stop is not None and index and index % STOP_CHECK_RUNS == 0 and stop():
            raise SimStopped(index, runs)
        # The draws read the rosters in sorted order and the weeks in order, so the seed gives the same runs.
        level = {rid: rng.gauss(level_mean[rid], level_se[rid]) for rid in rosters}
        drawn = {rid: [round(rng.gauss(level[rid], spread) + shift, SCORE_DECIMALS) for shift in shifts[rid]]
                 for rid in rosters}
        # A played bracket week keeps its real scores. The draws above still run, so the seed gives the same runs.
        for column, real in kept:
            for rid, score in real.items():
                drawn[rid][column] = score
        weight = 1.0
        for column, opponent, result in held_regular:
            assert you is not None
            mean = {rid: level[rid] + shifts[rid][column] for rid in (you, opponent)}
            weight *= _hold_week(rng, drawn, column, you, opponent, mean, spread, result, k)

        def hold(r: int, pairs: list[Pair], column: int, place: dict[int, int], level=level, drawn=drawn) -> float:
            result = held_bracket.get(column)
            if result is None or you is None:
                return 1.0
            opponent = next((a if b == you else b for a, b in pairs if you in (a, b)), None)
            if opponent is None or bracket_opponent.setdefault(column, opponent) != opponent:
                raise ValueError(f"the bracket game of week {result.week} has no set teams")
            mean = {rid: level[rid] + shifts[rid][column] for rid in (you, opponent)}
            return _hold_bracket(rng, drawn, column, you, opponent, mean, spread, result, place)

        week_log: list[tuple[frozenset[int], frozenset[int]]] | None = [] if pages else None
        wins, points, against = _regular(records, [remaining[w] for w in regular], drawn, median_game, week_log)
        table = sorted(rosters, key=lambda rid: (-wins[rid], -points[rid], -against[rid], rid))
        place = {rid: n for n, rid in enumerate(table[:spots], start=1)}
        rounds, factor = _bracket(table[:spots], drawn, len(regular), reseed, hold if held_bracket else None)
        weight *= factor
        champion = _winner(rounds[-1][0], drawn, len(regular) + len(rounds) - 1, place) if rounds else table[0]
        total += weight
        squares += weight * weight
        for rid in rosters:
            wins_count[rid][wins[rid]] += weight
        for rid, n in place.items():
            made[rid] += weight
            seeds[rid][n] += weight
            if n <= bye_count:
                byes[rid] += weight
        if rounds:
            for rid in rounds[-1][0]:
                finals[rid] += weight
        titles[champion] += weight
        if week_log is not None:
            log.append(RunRecord(weight=weight, wins=wins, made=frozenset(place), weeks=week_log,
                                 seeds=tuple(table[:spots]), rounds=tuple(tuple(r) for r in rounds),
                                 champion=champion))
        for a, b in next_pairs:
            # An exact tie is neither a win nor a loss, so the run lands in neither half.
            if drawn[a][0] == drawn[b][0]:
                continue
            half = halves[(a, b)]["a" if drawn[a][0] > drawn[b][0] else "b"]
            half[0] += weight
            half[1] += weight if a in place else 0.0
            half[2] += weight if b in place else 0.0
        if index < sample:
            stored.append(SimRun(scores=_played(drawn, rounds, len(regular)), table=table, bracket=rounds,
                                 champion=champion))
            stored_weights.append(weight)
    if not total:
        raise ValueError("the set results hold in no run")

    weeks_left = len(regular)
    teams = {}
    status: dict[int, OddsStatus] = {}
    for rid in rosters:
        # With no regular week left, the table is final, so each team is in or out.
        status[rid] = (roster_status(rid, dict(records), weeks_left, spots, median_game=median_game) if weeks_left
                       else "in" if made[rid] else "out")
        bye_status = roster_status(rid, dict(records), weeks_left, bye_count, median_game=median_game)
        playoff = shown(status[rid], made[rid], total, weeks_left)
        bye = 0 if status[rid] == "out" else min(shown(bye_status, byes[rid], total, weeks_left), playoff)
        # The most common seed; a tie between two seeds goes to the better seed.
        modal = min(seeds[rid], key=lambda n, rid=rid: (-seeds[rid][n], n)) if seeds[rid] else None
        teams[rid] = TeamSim(
            roster_id=rid, playoff=playoff, bye=bye, seed=modal if playoff >= SEED_SHOW_AT else None,
            status=status[rid],
            final=tenths(finals[rid], total), title=tenths(titles[rid], total),
            seeds={n: tenths(count, total) for n, count in sorted(seeds[rid].items())},
            final_wins={n: tenths(count, total) for n, count in sorted(wins_count[rid].items())},
            mean_wins=round(sum(n * count for n, count in wins_count[rid].items()) / total, 2),
        )
    effective_runs = round(total * total / squares)
    goals = {rid: team_goals(rid, playoff=teams[rid].playoff, bye=teams[rid].bye, status=teams[rid].status,
                             seeds=seeds[rid], total=total, records=records, weeks_left=weeks_left, spots=spots,
                             bye_count=bye_count, median_game=median_game) for rid in rosters}
    blocks = {rid: team_page(rid, log, playoff=teams[rid].playoff, status=teams[rid].status, records=records,
                             schedule={w: list(remaining[w]) for w in regular}, median_game=median_game,
                             effective_runs=effective_runs,
                             set_weeks=len(held_regular) if rid == you else 0,
                             set_wins=sum((r.game == "win") + (r.median == "above") for _, _, r in held_regular)
                             if rid == you else 0,
                             bracket_weeks=bracket_weeks, played=played, goals=goals[rid])
              for rid in sorted(set(pages))}
    return SimResult(
        season=season, week=week, runs=runs, effective_runs=effective_runs, random_seed=seed, weeks=weeks, bracket_weeks=bracket_weeks,
        records=dict(records), schedule={w: list(remaining[w]) for w in regular},
        parameters=SimParameters(
            league_mean=model.league_mean, spread=spread, level_mean=dict(level_mean), level_se=dict(level_se),
            shifts={rid: list(values) for rid, values in shifts.items()},
            projection_weight=PROJECTION_WEIGHT, shrink_weeks=LEVEL_SHRINK_WEEKS, playoff_spots=spots,
            bye_count=bye_count, median_game=median_game, reseed=reseed,
        ),
        teams=teams, swings=[_swing(a, b, halves[(a, b)], status, teams, weeks_left) for a, b in next_pairs],
        sample=stored, sample_weights=stored_weights, pages=blocks,
        fact=league_fact({rid: t.playoff for rid, t in teams.items()}, spots, weeks_left),
        played={w: dict(scores) for w, scores in played.items()},
        board=[BoardTeam(roster_id=rid, goals=goals[rid]) for rid in rosters] if weeks_left else [],
    )


def _seed_status(rid: int, records: Mapping[int, tuple[int, int, float, float]], weeks_left: int, seed: int,
                 median_game: bool) -> OddsStatus:
    """Seed `seed` is `in` when the top `seed` places are sure and the places above it are out of reach. It is
    `out` when the top `seed` places are out of reach, or a place above it is sure."""
    top = roster_status(rid, dict(records), weeks_left, seed, median_game=median_game)
    above = roster_status(rid, dict(records), weeks_left, seed - 1, median_game=median_game) if seed > 1 else "out"
    if top == "in" and above == "out":
        return "in"
    if top == "out" or above == "in":
        return "out"
    return "open"


def team_goals(
    rid: int, *, playoff: int, bye: int, status: OddsStatus, seeds: Mapping[int, float], total: float,
    records: Mapping[int, tuple[int, int, float, float]], weeks_left: int, spots: int, bye_count: int,
    median_game: bool,
) -> dict[str, GoalOdds]:
    """The Goals of `rid` in the regular season. `playoff` and `bye` are the team odds of the sim, and `seeds`
    holds the run weight of each seed over the `total` weight. The status of a bye or a seed uses the wins of the last
    place of the Goal. With no regular week left, the table is final and the Race has no Goal, so it gives none."""
    if not weeks_left:
        return {}
    goals = {"spot": GoalOdds(odds=playoff, status=status)}
    if bye_count:
        bye_status = roster_status(rid, dict(records), weeks_left, bye_count, median_game=median_game)
        goals["bye"] = GoalOdds(odds=bye, status=bye_status)
    for seed in range(1, spots + 1):
        seed_status = _seed_status(rid, records, weeks_left, seed, median_game)
        goals[f"seed-{seed}"] = GoalOdds(odds=shown(seed_status, seeds.get(seed, 0.0), total, weeks_left),
                                         status=seed_status)
    return goals


def draw_model(
    scores: Mapping[int, list[float]], records: Mapping[int, tuple[int, int, float, float]], weeks: list[int],
    projected: Mapping[int, Mapping[int, float]] | None,
) -> DrawModel:
    """The numbers of the draw of `season_sim` over the drawn `weeks`, from the played-week scores.

    The level mean is the season average shrunk toward the league average with LEVEL_SHRINK_WEEKS weeks of weight.
    It has no injury term: the projection shift of each week holds the roster of that week.
    """
    rosters = sorted(records)
    played = [s for rid in rosters for s in scores[rid]]
    league_mean = sum(played) / len(played)
    averages = {rid: sum(scores[rid]) / len(scores[rid]) for rid in rosters}
    # The spread is pooled over the league, as in the weekly odds, because a roster's few scores do not pin its own.
    freedom = sum(len(scores[rid]) - 1 for rid in rosters)
    squares = sum((s - averages[rid]) ** 2 for rid in rosters for s in scores[rid])
    spread = math.sqrt(squares / freedom) if freedom else 0.0
    level_mean = {rid: (len(scores[rid]) * averages[rid] + LEVEL_SHRINK_WEEKS * league_mean)
                  / (len(scores[rid]) + LEVEL_SHRINK_WEEKS) for rid in rosters}
    level_se = {rid: spread / math.sqrt(len(scores[rid]) + LEVEL_SHRINK_WEEKS) for rid in rosters}
    # A week with no projected total for the roster has no shift.
    shifts = {rid: [PROJECTION_WEIGHT * (projected[rid][w] - averages[rid])
                    if projected and w in projected.get(rid, {}) else 0.0 for w in weeks] for rid in rosters}
    return DrawModel(league_mean=league_mean, spread=spread, level_mean=level_mean, level_se=level_se, shifts=shifts)


def weekly_odds(result: SimResult) -> OddsResult:
    """The weekly odds of the sim: the playoff odds, the bye odds, the seed, and the status of each team, and the swing
    of each next-week game. The rankings page, the week page, and the facts read them, so each shows one number."""
    teams = {rid: TeamOdds(roster_id=rid, playoff=t.playoff, bye=t.bye, seed=t.seed, status=t.status)
             for rid, t in result.teams.items()}
    return OddsResult(teams=teams, swings=list(result.swings))


def _checked(
    set_results: Sequence[SetResult], you: int | None, rosters: list[int], remaining: Mapping[int, list[Pair]],
    bracket_weeks: list[int], median_game: bool, played: frozenset[int] = frozenset(),
) -> list[SetResult]:
    """The set results in week order, after a check of each against the league. A bad one raises ValueError."""
    if set_results and you not in rosters:
        raise ValueError(f"the set results need Your team, and {you} is not a roster of the league")
    held = sorted(set_results, key=lambda r: r.week)
    if len({r.week for r in held}) < len(held):
        raise ValueError("each week holds at most one set result")
    for r in held:
        if r.week in remaining:
            _opponent(remaining[r.week], you)
            if median_game and r.median is None:
                raise ValueError(f"the set result of week {r.week} needs above or below the median")
            if not median_game and r.median is not None:
                raise ValueError(f"the league has no median game, so week {r.week} sets a win or a loss only")
        elif r.week in played:
            raise ValueError(f"week {r.week} is played, so it takes no set result")
        elif r.week in bracket_weeks:
            if r.median is not None:
                raise ValueError(f"week {r.week} is a bracket week, so it sets a win or a loss only")
            # Before the end of the regular season, no bracket game has two set teams.
            if remaining:
                raise ValueError(f"the bracket game of week {r.week} has no set teams")
        else:
            raise ValueError(f"week {r.week} is not a week left of the sim")
    return held


def _opponent(pairs: list[Pair], you: int | None) -> int:
    """The opponent of Your team in the pairs of one regular week."""
    for a, b in pairs:
        if you in (a, b):
            return b if a == you else a
    raise ValueError(f"roster {you} has no game in a set week")


def _hold_week(
    rng: random.Random, drawn: dict[int, list[float]], column: int, you: int, opponent: int,
    mean: dict[int, float], spread: float, result: SetResult, k: int,
) -> float:
    """Draw the scores of Your team and its opponent in one regular week so the set result holds, and give the weight.

    The other scores of the week stay as drawn. With a median result, Your score comes first (decision 07): with r1
    to r(n-2) the other scores high to low, Your team beats the median exactly when its score is above r(k) after a
    win, or above r(k-1) after a loss. Then the opponent's score lands on its side of Your score. The weight is the
    product of the chances of the two cuts. With no median result, only the opponent's score is cut.
    """
    win = result.game == "win"
    if result.median is not None:
        rest = sorted((scores[column] for rid, scores in drawn.items() if rid not in (you, opponent)), reverse=True)
        line = rest[k - 1] if win else rest[k - 2]
        above = result.median == "above"
        cut = (line + _HALF_CELL, math.inf) if above else (-math.inf, line + _HALF_CELL)
        x, p_you = _held_score(rng, mean[you], spread, cut, lambda x: (x > line) == above)
        drawn[you][column] = x
    else:
        p_you = 1.0
    x = drawn[you][column]
    # A win needs the opponent under Your score. A loss is no win, so a tie is a loss.
    cut = (-math.inf, x - _HALF_CELL) if win else (x - _HALF_CELL, math.inf)
    drawn[opponent][column], p_opponent = _held_score(rng, mean[opponent], spread, cut, lambda xo: (x > xo) == win)
    return p_you * p_opponent


def _hold_bracket(
    rng: random.Random, drawn: dict[int, list[float]], column: int, you: int, opponent: int,
    mean: dict[int, float], spread: float, result: SetResult, place: dict[int, int],
) -> float:
    """Draw the opponent's score of a set bracket game on its side of Your score, and give the chance of the cut.
    A tie goes to the higher seed, as in `_winner`."""
    win = result.game == "win"
    x = drawn[you][column]
    edge = x + _HALF_CELL if place[you] < place[opponent] else x - _HALF_CELL
    cut = (-math.inf, edge) if win else (edge, math.inf)

    def holds(xo: float) -> bool:
        return (x > xo or (x == xo and place[you] < place[opponent])) == win

    drawn[opponent][column], p = _held_score(rng, mean[opponent], spread, cut, holds)
    return p


def _held_score(
    rng: random.Random, mean: float, spread: float, cut: tuple[float, float], holds: Callable[[float], bool],
) -> tuple[float, float]:
    """A rounded score drawn from its normal cut to `cut`, and the chance of the cut.

    The draw is by the inverse CDF, on the tail on the far side of the mean, so a cut far in a tail keeps its
    precision. A raw draw on the exact edge can round across it, so a score that misses `holds` is drawn again.
    A cut with no chance keeps the mean, with weight 0.
    """
    lo, hi = cut
    if spread <= 0:
        return round(mean, SCORE_DECIMALS), 1.0 if lo < mean < hi else 0.0
    flip = lo > mean
    if flip:
        lo, hi = 2 * mean - hi, 2 * mean - lo
    p_lo = _NORMAL.cdf((lo - mean) / spread) if lo > -math.inf else 0.0
    p_hi = _NORMAL.cdf((hi - mean) / spread) if hi < math.inf else 1.0
    chance = p_hi - p_lo
    if chance <= 0:
        return round(mean, SCORE_DECIMALS), 0.0
    while True:
        u = min(max(p_lo + rng.random() * chance, 1e-300), 1 - 1e-16)
        raw = mean + spread * _NORMAL.inv_cdf(u)
        score = round(2 * mean - raw if flip else raw, SCORE_DECIMALS)
        if holds(score):
            return score, chance


def _swing(
    a: int, b: int, half: dict[str, list[float]], status: Mapping[int, OddsStatus], teams: Mapping[int, TeamSim],
    weeks_left: int,
) -> Swing:
    """Both sides' odds in the runs where side a won and in the runs where side b won.

    A half with no run falls back to the full odds, since the runs never saw that result.
    """
    def side(rid: int, runs_and_made: list[float], index: int) -> int:
        count = runs_and_made[0]
        if not count:
            return teams[rid].playoff
        return shown(status[rid], runs_and_made[index], count, weeks_left)

    return Swing(a=a, b=b, a_win=side(a, half["a"], 1), a_loss=side(a, half["b"], 1), b_win=side(b, half["b"], 2),
                 b_loss=side(b, half["a"], 2))


def _regular(
    records: Mapping[int, tuple[int, int, float, float]], order: list[list[Pair]], drawn: dict[int, list[float]],
    median_game: bool, log: list[tuple[frozenset[int], frozenset[int]]] | None = None,
) -> tuple[dict[int, int], dict[int, float], dict[int, float]]:
    """The wins, the points for, and the points against of each roster at the end of the regular season of one run.

    The same rule as the weekly odds: an exact tie gives no win, and the median game counts a win above the line.
    With `log`, each week appends its winners of the head-to-head games and its rosters above the median.
    """
    wins = {rid: r[0] for rid, r in records.items()}
    points = {rid: r[2] for rid, r in records.items()}
    against = {rid: r[3] for rid, r in records.items()}
    for i, pairs in enumerate(order):
        week = {rid: d[i] for rid, d in drawn.items()}
        for a, b in pairs:
            against[a] += week[b]
            against[b] += week[a]
            if week[a] > week[b]:
                wins[a] += 1
            elif week[b] > week[a]:
                wins[b] += 1
        median = _median(list(week.values())) if median_game else None
        for rid, score in week.items():
            if median is not None and score > median:
                wins[rid] += 1
            points[rid] += score
        if log is not None:
            won = frozenset(a if week[a] > week[b] else b for a, b in pairs if week[a] != week[b])
            above = frozenset(rid for rid, score in week.items() if median is not None and score > median)
            log.append((won, above))
    return wins, points, against


def _played(drawn: dict[int, list[float]], rounds: list[list[Pair]], first: int) -> dict[int, list[float | None]]:
    """The drawn scores of one run as the replay needs them: every regular week, and a bracket week only for a roster
    with a game that week."""
    out: dict[int, list[float | None]] = {rid: list(scores[:first]) for rid, scores in drawn.items()}
    for rid, scores in drawn.items():
        for r, column in enumerate(range(first, len(scores))):
            plays = r < len(rounds) and any(rid in pair for pair in rounds[r])
            out[rid].append(scores[column] if plays else None)
    return out


def _median(scores: list[float]) -> float:
    """The line of the median game: the mean of the two middle scores. The same rule as week_median."""
    ordered = sorted(scores, reverse=True)
    middle = len(ordered) // 2
    return (ordered[middle - 1] + ordered[middle]) / 2


def _bracket(
    seeded: list[int], drawn: dict[int, list[float]], first: int, reseed: bool, hold: Hold | None = None,
) -> tuple[list[list[Pair]], float]:
    """The games of each round of one run, and the product of the weights of `hold`. `seeded` holds the roster IDs in
    seed order. Round r plays in the drawn week `first` plus r. Each round halves the field to a power of two, so the
    top seeds get the byes. `hold` sets the scores of a round before its winners count."""
    place = {rid: n for n, rid in enumerate(seeded, start=1)}
    rounds: list[list[Pair]] = []
    weight = 1.0
    # A fixed bracket keeps the slots of the standard seeded bracket, with an empty slot for each bye.
    slots: list[int | None] = [seeded[s - 1] if s <= len(seeded) else None for s in _positions(len(seeded))]
    alive = list(seeded)
    while len(alive) > 1:
        column = first + len(rounds)
        if reseed:
            ordered = sorted(alive, key=place.__getitem__)
            games = len(ordered) - 2 ** (math.ceil(math.log2(len(ordered))) - 1)
            playing = ordered[len(ordered) - 2 * games:]
            pairs = [(playing[i], playing[-1 - i]) for i in range(games)]
            if hold:
                weight *= hold(len(rounds), pairs, column, place)
            losers = {_loser(pair, drawn, column, place) for pair in pairs}
            alive = [rid for rid in ordered if rid not in losers]
        else:
            games = list(zip(slots[::2], slots[1::2], strict=True))
            pairs = [(a, b) if place[a] < place[b] else (b, a) for a, b in games if a is not None and b is not None]
            if hold:
                weight *= hold(len(rounds), pairs, column, place)
            advanced: list[int | None] = [a if b is None else b if a is None else _winner((a, b), drawn, column, place)
                                          for a, b in games]
            slots = advanced
            alive = [rid for rid in slots if rid is not None]
        rounds.append(pairs)
    return rounds, weight


def _positions(spots: int) -> list[int]:
    """The seeds in the slot order of a standard bracket of the next power of two: 1, 8, 4, 5, 2, 7, 3, 6 for 8.
    A seed above `spots` is a bye."""
    order = [1]
    size = 2 ** math.ceil(math.log2(spots)) if spots > 1 else 1
    while len(order) < size:
        total = 2 * len(order) + 1
        order = [s for seed in order for s in (seed, total - seed)]
    return order


def _winner(pair: Pair, drawn: dict[int, list[float]], column: int, place: dict[int, int]) -> int:
    """The winner of one bracket game. A tie goes to the higher seed."""
    a, b = pair
    if drawn[a][column] == drawn[b][column]:
        return a if place[a] < place[b] else b
    return a if drawn[a][column] > drawn[b][column] else b


def _loser(pair: Pair, drawn: dict[int, list[float]], column: int, place: dict[int, int]) -> int:
    a, b = pair
    return b if _winner(pair, drawn, column, place) == a else a
