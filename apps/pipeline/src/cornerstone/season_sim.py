"""
The app side of the season sim, the one odds engine: it runs the sim package on the inputs of a week. It gives the
weekly odds to the week build through the chapter port, the week sim file to the build, and the sim to the report.
"""
from decimal import Decimal
from pathlib import Path
from typing import NamedTuple

from league.client import Client
from league.models import Chapter, Fact, History, OddsResult, Week
from league.nflverse import SCHEDULES_URL, cache_path, download, read_schedules
from league.parse import parse_week
from league.paths import nflverse_cache_dir, raw_dir
from league.provider.sleeper import load_raw
from league.standings_table import season_records
from rankings.chapter import odds_inputs
from sim.season import SimResult, SimRun, season_sim, weekly_odds
from sim.tunables import SIM_RUNS
from week.sheet import Context, projected_totals


def schedule_file(nfl: Path, season: int) -> Path | None:
    """The cached NFL schedule of the NFL data `nfl`, at the cache path of each nflverse reader, so the report and the
    sim read one copy. Git ignores the cache, so a fresh worktree fetches it once.

    A saved file stands as it is: the bye weeks of a season do not change, so one input gives one output.
    """
    path = cache_path(nflverse_cache_dir(nfl), SCHEDULES_URL, season)
    if path.exists():
        return path
    return download(SCHEDULES_URL, path)


class SimInputs(NamedTuple):
    """The inputs of the season sim after one week, in the order of the arguments of `season_sim`."""
    scores: dict[int, list[float]]
    records: dict[int, tuple[int, int, float, float]]
    remaining: dict[int, list[tuple[int, int]]]
    projected: dict[int, dict[int, float]]
    # The real scores of each played bracket week, by week and roster ID. Empty in the regular season.
    played: dict[int, dict[int, float]]


def week_inputs(season: int, week: int, history: History, *, client: Client) -> SimInputs | None:
    """The inputs of the sim after `week`, from the saved raw data of the week and the saved history.

    The bye weeks come from the NFL schedule. None when the week gives no odds inputs.
    """
    raw = load_raw(raw_dir(client.folder, season, week))
    parsed = parse_week(raw, week=week, team_count=client.settings.team_count, points_key=client.settings.points_key)
    path = schedule_file(client.nfl_dir, season)
    schedules = read_schedules(path, season) if path is not None else None
    bye_weeks = {team: s.bye_week for team, s in schedules.items() if s.bye_week is not None} if schedules else None
    return inputs_of_week(parsed, history, client=client, bye_weeks=bye_weeks)


def inputs_of_week(
    week: Week, history: History | None, *, client: Client, bye_weeks: dict[str, int] | None,
) -> SimInputs | None:
    """The inputs of the sim after the parsed `week`. None when the week gives no odds inputs.

    The scores and the remaining pairs come from odds_inputs of the weekly odds. The projected totals run through
    the last bracket week. `bye_weeks` holds the bye week of each NFL team, so a bye gives no cover in them.
    """
    inputs = odds_inputs(week, history, client)
    if inputs is None or history is None:
        return None
    scores, remaining = inputs
    projected = projected_totals(week, client, bye_weeks, through=client.settings.last_season_week)
    # A bracket week is no game of the regular season, so the records stop at the last regular week, and the scores of
    # each played bracket week hold the bracket of the sim.
    last = client.settings.last_regular_week
    records = season_records(history, min(week.week, last), median_game=client.settings.median_game)
    played = {w: dict(history.weeks[w].scores) for w in range(last + 1, week.week + 1)}
    return SimInputs(scores, records, remaining, projected, played)


def week_sim(
    season: int, week: int, history: History, *, client: Client, runs: int = SIM_RUNS,
) -> SimResult | None:
    """The sim of the rest of the season after `week`, from the saved raw data of the week and the saved history.

    None when the week gives no odds inputs. The sim draws `runs` seasons. The real build keeps the default of the
    sim tunables.
    """
    inputs = week_inputs(season, week, history, client=client)
    return _sim(inputs, season, week, client, runs)


def week_sim_with_pages(
    season: int, week: int, history: History, *, client: Client, runs: int = SIM_RUNS,
) -> SimResult | None:
    """The sim of the week file after `week`: the sim of `week_sim` with the page block of each team. None when the
    week gives no odds inputs.

    It reads the bye weeks from the NFL schedule, as `week_sim` and the midseason sim do, so each sim file reads one
    source. The nflverse extract of the build reads its bye weeks from the same cached schedule file.
    """
    inputs = week_inputs(season, week, history, client=client)
    if inputs is None:
        return None
    return _sim(inputs, season, week, client, runs, pages=sorted(inputs.records))


def sim_of_week(
    week: Week, history: History | None, *, client: Client, bye_weeks: dict[str, int] | None,
    runs: int = SIM_RUNS,
) -> SimResult | None:
    """The sim of the rest of the season after the parsed `week`. None when the week gives no odds inputs."""
    inputs = inputs_of_week(week, history, client=client, bye_weeks=bye_weeks)
    return _sim(inputs, week.season, week.week, client, runs)


def _sim(
    inputs: SimInputs | None, season: int, week: int, client: Client, runs: int, pages: list[int] | None = None,
) -> SimResult | None:
    if inputs is None:
        return None
    return season_sim(inputs.scores, inputs.records, inputs.remaining, season=season, week=week,
                      settings=client.settings, projected=inputs.projected, runs=runs, pages=pages or (),
                      played=inputs.played)


# The weeks of the playoff fixtures of ACCEPTANCE.md: the bracket of week 15 set, the bracket of week 16 set after a
# played round, and the season end. The fixtures of the site tests carry these names.
FIXTURE_WEEKS = {14: "week-sim-playoffs.json", 15: "week-sim-round-2.json", 17: "week-sim-final.json"}


def fixture_inputs(inputs: SimInputs, run: SimRun, through: int, client: Client) -> SimInputs:
    """The inputs of the sim after week `through` when the weeks after the week of `inputs` play out as the stored `run`.

    The regular weeks of the run add to the scores and the records, as `season_records` counts them: a tie gives
    neither a win nor a loss, and the median game counts against the mean of the two middle scores. The bracket weeks
    of the run up to `through` become played weeks, with the scores of the rosters that played.
    """
    settings = client.settings
    regular = sorted(inputs.remaining)
    scores = {rid: list(own) for rid, own in inputs.scores.items()}
    wins = {rid: r[0] for rid, r in inputs.records.items()}
    losses = {rid: r[1] for rid, r in inputs.records.items()}
    points = {rid: Decimal(str(r[2])) for rid, r in inputs.records.items()}
    against = {rid: Decimal(str(r[3])) for rid, r in inputs.records.items()}

    def settle(rid: int, mine: float, theirs: float) -> None:
        if mine > theirs:
            wins[rid] += 1
        elif mine < theirs:
            losses[rid] += 1

    for column, w in enumerate(regular):
        if w > through:
            break
        week_scores = {rid: _regular_score(run, rid, column) for rid in scores}
        for a, b in inputs.remaining[w]:
            settle(a, week_scores[a], week_scores[b])
            settle(b, week_scores[b], week_scores[a])
            against[a] += Decimal(str(week_scores[b]))
            against[b] += Decimal(str(week_scores[a]))
        ordered = sorted(week_scores.values(), reverse=True)
        median = (ordered[len(ordered) // 2 - 1] + ordered[len(ordered) // 2]) / 2
        for rid, score in week_scores.items():
            if settings.median_game:
                settle(rid, score, median)
            points[rid] += Decimal(str(score))
            scores[rid].append(score)
    played = {}
    for column, w in enumerate(range(settings.last_regular_week + 1, through + 1), start=len(regular)):
        played[w] = {rid: s[column] for rid, s in run.scores.items() if s[column] is not None}
    records = {rid: (wins[rid], losses[rid], round(float(points[rid]), 2), round(float(against[rid]), 2))
               for rid in scores}
    return SimInputs(scores, records, {w: p for w, p in inputs.remaining.items() if w > through}, inputs.projected,
                     played)


def _regular_score(run: SimRun, rid: int, column: int) -> float:
    """The score of `rid` in a regular week of the stored `run`. Each roster plays each regular week."""
    score = run.scores[rid][column]
    if score is None:
        raise ValueError(f"roster {rid} has no score in column {column} of the run")
    return score


def playoff_fixtures(
    season: int, week: int, history: History, *, client: Client, runs: int = SIM_RUNS,
) -> dict[int, tuple[SimResult, SimRun]]:
    """The sims of the playoff fixtures by the week of each, each with the stored run 1 that fills it.

    Each takes the inputs of `week` and plays the weeks after it as stored run 1 of the sim of `week`. The first stored
    run is the first draw of the seed of the week, so a sim of one run gives the run 1 of the week file.
    """
    inputs = week_inputs(season, week, history, client=client)
    if inputs is None:
        raise ValueError(f"week {week} gives the sim no inputs")
    first = _sim(inputs, season, week, client, 1)
    assert first is not None
    run = first.sample[0]
    out = {}
    for through in FIXTURE_WEEKS:
        filled = fixture_inputs(inputs, run, through, client)
        sim = season_sim(filled.scores, filled.records, filled.remaining, season=season, week=through,
                         settings=client.settings, projected=filled.projected, runs=runs, pages=sorted(filled.records),
                         played=filled.played)
        out[through] = (sim, run)
    return out


class SimOdds:
    """The odds of the week from the season sim, through the chapter port of week.sheet.port (ADR 0037).

    The sim runs once per build here, and the odds reach the saved facts, so a rewrite never runs it. It gives no
    facts and no chapter: the rankings chapter writes the odds facts from these odds.
    """

    def odds(self, c: Context) -> OddsResult | None:
        bye_weeks = c.nfl.bye_weeks if c.nfl is not None else None
        sim = sim_of_week(c.week, c.history, client=c.client, bye_weeks=bye_weeks)
        return weekly_odds(sim) if sim is not None else None

    def facts(self, c: Context) -> list[Fact]:
        return []

    def chapter(self, c: Context, facts: dict[str, Fact]) -> Chapter | None:
        return None


SIM_ODDS = SimOdds()
