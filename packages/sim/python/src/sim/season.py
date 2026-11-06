"""
The season sim: a Monte Carlo of the rest of the regular season and the playoff bracket. It gives the odds of each team,
the seed odds, the final-win odds, and a sample of runs to replay. Pure code: no network and no Claude.
"""
import math
import random
from collections import Counter
from collections.abc import Mapping

from pydantic import BaseModel

from league.league_settings import LeagueSettings
from league.models import OddsStatus
from league.standings_table import roster_status
from sim.tunables import LEVEL_SHRINK_WEEKS, PROJECTION_WEIGHT, SAMPLE_RUNS, SCORE_DECIMALS, SIM_RUNS

Pair = tuple[int, int]


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
    # The odds in percent of all runs, with one decimal: the final, the title, each seed, and each final win total.
    final: float
    title: float
    seeds: dict[int, float]
    final_wins: dict[int, float]
    # The mean wins at the end of the regular season. The page orders the teams by it.
    mean_wins: float


class SimParameters(BaseModel):
    """The numbers of the draw, so a live sim in the browser can draw the same model later."""
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
    # The random seed of the draw. It derives from the season and the week, so one input gives one output.
    random_seed: int
    # The weeks that a run draws: the regular weeks left, then one week per bracket round.
    weeks: list[int]
    # The weeks of the bracket, a subset of `weeks`.
    bracket_weeks: list[int]
    # The real wins, losses, and points for of each roster at the start of the sim.
    records: dict[int, tuple[int, int, float]]
    # The head-to-head pairs of each regular week left.
    schedule: dict[int, list[Pair]]
    parameters: SimParameters
    teams: dict[int, TeamSim]
    sample: list[SimRun]


def season_sim(
    scores: Mapping[int, list[float]],
    records: Mapping[int, tuple[int, int, float]],
    remaining: Mapping[int, list[Pair]],
    *,
    season: int,
    week: int,
    settings: LeagueSettings,
    projected: Mapping[int, Mapping[int, float]] | None = None,
    runs: int = SIM_RUNS,
    sample: int = SAMPLE_RUNS,
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
    """
    spots, bye_count, median_game = settings.playoff_spots, settings.bye_count, settings.median_game
    rosters = sorted(records)
    regular = sorted(remaining)
    bracket_weeks = list(range(settings.last_regular_week + 1, settings.last_season_week + 1))
    weeks = regular + bracket_weeks
    seed = season * 100 + week
    rng = random.Random(seed)

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

    made: Counter[int] = Counter()
    byes: Counter[int] = Counter()
    finals: Counter[int] = Counter()
    titles: Counter[int] = Counter()
    seeds: dict[int, Counter[int]] = {rid: Counter() for rid in rosters}
    wins_count: dict[int, Counter[int]] = {rid: Counter() for rid in rosters}
    stored: list[SimRun] = []
    for index in range(runs):
        # The draws read the rosters in sorted order and the weeks in order, so the seed gives the same runs.
        level = {rid: rng.gauss(level_mean[rid], level_se[rid]) for rid in rosters}
        drawn = {rid: [round(rng.gauss(level[rid], spread) + shift, SCORE_DECIMALS) for shift in shifts[rid]]
                 for rid in rosters}
        wins, points = _regular(records, [remaining[w] for w in regular], drawn, median_game)
        table = sorted(rosters, key=lambda rid: (-wins[rid], -points[rid], rid))
        place = {rid: n for n, rid in enumerate(table[:spots], start=1)}
        rounds = _bracket(table[:spots], drawn, len(regular), settings.reseed)
        champion = _winner(rounds[-1][0], drawn, len(regular) + len(rounds) - 1, place) if rounds else table[0]
        for rid in rosters:
            wins_count[rid][wins[rid]] += 1
        for rid, n in place.items():
            made[rid] += 1
            seeds[rid][n] += 1
            byes[rid] += n <= bye_count
        if rounds:
            finals.update(rounds[-1][0])
        titles[champion] += 1
        if index < sample:
            stored.append(SimRun(scores=_played(drawn, rounds, len(regular)), table=table, bracket=rounds,
                                 champion=champion))

    weeks_left = len(regular)
    teams = {}
    for rid in rosters:
        status = roster_status(rid, dict(records), weeks_left, spots, median_game=median_game)
        bye_status = roster_status(rid, dict(records), weeks_left, bye_count, median_game=median_game)
        playoff = _shown(status, made[rid], runs, weeks_left)
        bye = 0 if status == "out" else min(_shown(bye_status, byes[rid], runs, weeks_left), playoff)
        teams[rid] = TeamSim(
            roster_id=rid, playoff=playoff, bye=bye,
            final=_tenths(finals[rid], runs), title=_tenths(titles[rid], runs),
            seeds={n: _tenths(count, runs) for n, count in sorted(seeds[rid].items())},
            final_wins={n: _tenths(count, runs) for n, count in sorted(wins_count[rid].items())},
            mean_wins=round(sum(n * count for n, count in wins_count[rid].items()) / runs, 2),
        )
    return SimResult(
        season=season, week=week, runs=runs, random_seed=seed, weeks=weeks, bracket_weeks=bracket_weeks,
        records=dict(records), schedule={w: list(remaining[w]) for w in regular},
        parameters=SimParameters(
            league_mean=round(league_mean, 2), spread=round(spread, 2),
            level_mean={rid: round(v, 2) for rid, v in level_mean.items()},
            level_se={rid: round(v, 2) for rid, v in level_se.items()},
            shifts={rid: [round(s, 2) for s in values] for rid, values in shifts.items()},
            projection_weight=PROJECTION_WEIGHT, shrink_weeks=LEVEL_SHRINK_WEEKS, playoff_spots=spots,
            bye_count=bye_count, median_game=median_game, reseed=settings.reseed,
        ),
        teams=teams, sample=stored,
    )


def _regular(
    records: Mapping[int, tuple[int, int, float]], order: list[list[Pair]], drawn: dict[int, list[float]],
    median_game: bool,
) -> tuple[dict[int, int], dict[int, float]]:
    """The wins and the points for of each roster at the end of the regular season of one run.

    The same rule as the weekly odds: an exact tie gives no win, and the median game counts a win above the line.
    """
    wins = {rid: r[0] for rid, r in records.items()}
    points = {rid: r[2] for rid, r in records.items()}
    for i, pairs in enumerate(order):
        week = {rid: d[i] for rid, d in drawn.items()}
        for a, b in pairs:
            if week[a] > week[b]:
                wins[a] += 1
            elif week[b] > week[a]:
                wins[b] += 1
        median = _median(list(week.values())) if median_game else None
        for rid, score in week.items():
            if median is not None and score > median:
                wins[rid] += 1
            points[rid] += score
    return wins, points


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


def _bracket(seeded: list[int], drawn: dict[int, list[float]], first: int, reseed: bool) -> list[list[Pair]]:
    """The games of each round of one run. `seeded` holds the roster IDs in seed order. Round r plays in the drawn
    week `first` plus r. Each round halves the field to a power of two, so the top seeds get the byes."""
    place = {rid: n for n, rid in enumerate(seeded, start=1)}
    rounds: list[list[Pair]] = []
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
            losers = {_loser(pair, drawn, column, place) for pair in pairs}
            alive = [rid for rid in ordered if rid not in losers]
        else:
            pairs = []
            advanced: list[int | None] = []
            for a, b in zip(slots[::2], slots[1::2], strict=True):
                if a is None or b is None:
                    advanced.append(a if b is None else b)
                    continue
                pair = (a, b) if place[a] < place[b] else (b, a)
                pairs.append(pair)
                advanced.append(_winner(pair, drawn, column, place))
            slots = advanced
            alive = [rid for rid in slots if rid is not None]
        rounds.append(pairs)
    return rounds


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


def _shown(status: OddsStatus, count: int, runs: int, weeks_left: int) -> int:
    """The odds as the weekly odds show them: 100 for `in`, 0 for `out`, else the whole percent clamped to 1 to 99.
    With no regular week left, the table is final, so the whole percent stands with no clamp."""
    if not weeks_left:
        return _percent(count, runs)
    if status == "in":
        return 100
    if status == "out":
        return 0
    return min(99, max(1, _percent(count, runs)))


def _percent(part: int, total: int) -> int:
    """`part` over `total` as a whole percent, rounded half up."""
    return (200 * part + total) // (2 * total)


def _tenths(part: int, total: int) -> float:
    """`part` over `total` as a percent with one decimal."""
    return round(100 * part / total, 1)
