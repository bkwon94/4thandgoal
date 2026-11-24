"""
The page block of the season sim: the numbers of the sim page for one team, each by a split of the runs of one
weighted sim (decision 07), and the league fact of the Sim tile. sim.json and the What-if share this one shape.
"""
from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel

from league.models import OddsStatus
from sim.goals import GoalOdds, open_goal
from sim.paths import Finish, ScoreToBeat
from sim.percent import percent, shown, tenths
from sim.tunables import ABOUT_RUNS, IN_ODDS, RACE_FLOOR, ROOT_FOR_LIFT, ROOT_FOR_ROWS

Pair = tuple[int, int]
Reason = Literal["2 wins ahead of you", "1 win ahead of you", "Level with you", "1 win behind you",
                 "In the race for the last spot"]
# The reason of a root-for row by the gap in real wins from the loser to Your team.
_REASONS: dict[int, Reason] = {2: "2 wins ahead of you", 1: "1 win ahead of you", 0: "Level with you",
                               -1: "1 win behind you"}
_RACE: Reason = "In the race for the last spot"
# A loser of any other gap gets the race reason only when its real wins sit within this count of the real wins of the
# team that holds the last playoff spot. One win is the gap that one result closes, so the loser can take the spot or
# lose it this week, and the reason stays true. A loser further away gets no reason, and its row drops, because the PRD
# gives a row one of the five reasons only.
RACE_GAP = 1


@dataclass(frozen=True)
class RunRecord:
    """What the page block reads of one run: its weight, the regular-season wins, the playoff teams, and for each
    regular week left the winners of the head-to-head games and the teams above the median."""
    weight: float
    wins: dict[int, int]
    made: frozenset[int]
    weeks: list[tuple[frozenset[int], frozenset[int]]]
    # The seeds in seed order, the games of each bracket round, and the champion of the run.
    seeds: tuple[int, ...] = ()
    rounds: tuple[tuple[Pair, ...], ...] = ()
    champion: int | None = None


class LadderStep(BaseModel):
    """One count of more wins in the weeks left. A head-to-head win and a win over the median each count one."""
    more_wins: int
    # The playoff odds over the runs with this count. None when no run has it.
    playoff: int | None
    # The chance of the count in percent of all runs, with one decimal.
    chance: float
    about: bool


class WeekResult(BaseModel):
    """One result of Your team in one week: the game, and the median in a league with a median game."""
    game: Literal["win", "loss"]
    median: Literal["above", "below"] | None
    wins_added: int
    # The playoff odds after the result. None when no run has it.
    playoff: int | None
    chance: float
    about: bool


class RootFor(BaseModel):
    """One result of another game that lifts the odds of Your team after a loss."""
    winner: int
    loser: int
    reason: Reason
    # The playoff odds after a loss of Your team and this result, in whole points.
    playoff: int
    about: bool


class PageWeek(BaseModel):
    """One regular week left, for Your team."""
    week: int
    opponent: int
    # Four results with a median game, best first: win above, win below, loss above, loss below. Two with none.
    results: list[WeekResult]
    # The playoff odds over all runs where Your team loses its game. A tie is a loss, as in a set result.
    loss_playoff: int | None
    loss_about: bool
    # At most ROOT_FOR_ROWS rows, by the lift, then by the standings place of the loser.
    root_for: list[RootFor]


class PlayoffResult(BaseModel):
    """One result of Your team in its bracket game of this round, with the title odds after it."""
    game: Literal["win", "loss"]
    # The title odds after the result, in whole percent. None when no run has it. A loss ends the season, so it is 0.
    title: int | None
    chance: float
    about: bool


class PlayoffGame(BaseModel):
    """The bracket game of Your team in this round. It exists only when both of its teams are set."""
    week: int
    opponent: int
    # Two results: a win, then a loss.
    results: list[PlayoffResult]


class BracketGame(BaseModel):
    """One game of a bracket round. A side is None while the runs do not agree on it, so its team is not set."""
    # The higher seed first.
    teams: tuple[int | None, int | None]
    # The real scores of a played game, in the order of `teams`. None before the game.
    scores: tuple[float, float] | None
    # The winner of a played game. A tie goes to the higher seed.
    winner: int | None


class BracketRound(BaseModel):
    """One round of the bracket, one week. A bye plays no game, so it has no entry."""
    week: int
    played: bool
    games: list[BracketGame]


class BracketTeam(BaseModel):
    """One seed of the bracket, with its title odds in whole percent. A team that lost a played game is not alive."""
    roster_id: int
    seed: int
    title: int
    alive: bool


class Playoffs(BaseModel):
    """The playoff part of the page block, with no regular week left. Your team first: its seed, whether it is still
    in, its title odds, and its game of this round. Then the bracket with the title odds of each seed."""
    # The seed of Your team. None when Your team is not in the bracket.
    seed: int | None
    alive: bool
    title: int
    # The week of the round to play. None after the final.
    week: int | None
    # True when Your team is alive and has no game in this round.
    bye: bool
    # The game of Your team in this round. None with a bye, for a team that is out, and after the final.
    game: PlayoffGame | None
    teams: list[BracketTeam]
    rounds: list[BracketRound]
    # The champion after the final. None before it.
    champion: int | None


class SimPage(BaseModel):
    """The page block of one team. The page reads one shape before and after a What-if."""
    you: int
    playoff: int
    status: OddsStatus
    # The real wins and losses at the start of the sim. The median game counts in both.
    record: tuple[int, int]
    weeks_left: int
    # The most more wins the weeks left can give.
    wins_left: int
    # The smallest count of more wins with playoff odds of IN_ODDS or more. None when no count reaches it.
    need: int | None
    sentence: str
    ladder: list[LadderStep]
    weeks: list[PageWeek]
    # The playoff part, with no regular week left. None in the regular season.
    playoffs: Playoffs | None = None
    # The odds and the status of each Goal of The Race, by its key: "spot", "bye", and "seed-1" to the last seed.
    # Empty with no regular week left. A file written before The Race has none.
    goals: dict[str, GoalOdds] = {}
    # The Goal the page opens on. None with no Goal.
    open_goal: str | None = None
    # The Finish list of each Goal by its key, best Finish first. The spot and the bye hold the Paths of each Finish.
    # Empty with no regular week left. A file written before the Finish lists has none.
    finishes: dict[str, list[Finish]] = {}
    # The Score to beat of each regular week left, in week order. The Week plans and the week card read it. A file
    # written before the Week plans has none.
    score_to_beat: list[ScoreToBeat] = []


def team_page(
    you: int, runs: Sequence[RunRecord], *, playoff: int, status: OddsStatus,
    records: Mapping[int, tuple[int, int, float, float]], schedule: Mapping[int, list[Pair]], median_game: bool,
    effective_runs: int, set_weeks: int = 0, set_wins: int = 0, bracket_weeks: Sequence[int] = (),
    played: Mapping[int, Mapping[int, float]] | None = None, goals: Mapping[str, GoalOdds] | None = None,
    finishes: Mapping[str, list[Finish]] | None = None, score_to_beat: Sequence[ScoreToBeat] = (),
) -> SimPage:
    """The page block of `you` by a split of the `runs` of one sim. `schedule` holds the pairs of each regular week
    left, in the order of `RunRecord.weeks`. `playoff` and `status` are the odds of the team over all runs.

    `set_weeks` and `set_wins` count the regular weeks that a What-if of `you` holds and the wins they add. The ladder
    still counts every win left, and the sentence counts only the wins still open, so it agrees with the set results.

    With no regular week left, the block holds the playoffs of `bracket_weeks`, with the real scores of the `played`
    bracket weeks. `goals` holds the Goals of `you`, and the page opens on the best of them."""
    regular = sorted(schedule)
    weeks_left = len(regular)
    per_week = 2 if median_game else 1
    wins_left = per_week * weeks_left
    total = 0.0
    ladder: list[list[float]] = [[0.0, 0.0] for _ in range(wins_left + 1)]
    results: list[defaultdict[tuple[bool, bool], list[float]]] = [defaultdict(lambda: [0.0, 0.0]) for _ in regular]
    losses: list[list[float]] = [[0.0, 0.0] for _ in regular]
    winners: list[defaultdict[int, list[float]]] = [defaultdict(lambda: [0.0, 0.0]) for _ in regular]
    for run in runs:
        weight, made = run.weight, you in run.made
        total += weight
        step = ladder[run.wins[you] - records[you][0]]
        step[0] += weight
        step[1] += weight if made else 0.0
        for i, (won, above) in enumerate(run.weeks):
            win = you in won
            cell = results[i][(win, median_game and you in above)]
            cell[0] += weight
            cell[1] += weight if made else 0.0
            if win:
                continue
            losses[i][0] += weight
            losses[i][1] += weight if made else 0.0
            for rid in won:
                side = winners[i][rid]
                side[0] += weight
                side[1] += weight if made else 0.0

    def odds(part: list[float]) -> int | None:
        return shown(status, part[1], part[0], weeks_left) if part[0] else None

    def about(part: float) -> bool:
        # The flag reads the chance as the page shows it, so a reader of the file gets the same flag from its numbers.
        return tenths(part, total) / 100 * effective_runs < ABOUT_RUNS

    steps = [LadderStep(more_wins=k, playoff=odds(part), chance=tenths(part[0], total), about=about(part[0]))
             for k, part in enumerate(ladder)]
    need = next((s.more_wins for s in steps if s.playoff is not None and s.playoff >= IN_ODDS), None)
    table = sorted(records, key=lambda rid: (-records[rid][0], -records[rid][2], -records[rid][3], rid))
    place = {rid: n for n, rid in enumerate(table, start=1)}
    # Each run puts the same count of teams in the playoffs, so the first run gives the count of playoff spots.
    spots = len(runs[0].made) if runs else 0
    last_wins = records[table[min(spots, len(table)) - 1]][0] if spots else None
    combos: list[tuple[bool, bool, Literal["win", "loss"], Literal["above", "below"] | None]] = (
        [(True, True, "win", "above"), (True, False, "win", "below"), (False, True, "loss", "above"),
         (False, False, "loss", "below")] if median_game else [(True, False, "win", None), (False, False, "loss", None)])
    weeks = []
    for i, week in enumerate(regular):
        opponent = next((b if a == you else a for a, b in schedule[week] if you in (a, b)), None)
        if opponent is None:
            continue
        week_results = [
            WeekResult(game=game, median=median, wins_added=(game == "win") + (median == "above"),
                       playoff=odds(results[i][(win, up)]), chance=tenths(results[i][(win, up)][0], total),
                       about=about(results[i][(win, up)][0]))
            for win, up, game, median in combos]
        loss_playoff = odds(losses[i])
        rows = _root_for(you, schedule[week], winners[i], loss_playoff, odds, about, records, place, last_wins)
        weeks.append(PageWeek(week=week, opponent=opponent, results=week_results, loss_playoff=loss_playoff,
                              loss_about=about(losses[i][0]), root_for=rows))
    playoffs = (_playoffs(you, runs, total, list(bracket_weeks), played or {}, about)
                if not weeks_left and runs and runs[0].rounds else None)
    return SimPage(you=you, playoff=playoff, status=status, record=(records[you][0], records[you][1]),
                   weeks_left=weeks_left, wins_left=wins_left, need=need,
                   sentence=_sentence(status, need, wins_left, steps, set_weeks * per_week, set_wins),
                   ladder=steps, weeks=weeks, playoffs=playoffs, goals=dict(goals or {}),
                   open_goal=open_goal(goals or {}), finishes=dict(finishes or {}),
                   score_to_beat=list(score_to_beat))


def _whole(part: float, total: float) -> int:
    """A title odds number in whole percent: 0 with no run, 100 in each run, else clamped to 1 to 99, so a team with a
    small chance never reads 0 and a team with a sure title reads 100 only when it is sure."""
    if not part:
        return 0
    if part >= total:
        return 100
    return min(99, max(1, percent(part, total)))


def _playoffs(
    you: int, runs: Sequence[RunRecord], total: float, bracket_weeks: list[int], played: Mapping[int, Mapping[int, float]],
    about,
) -> Playoffs:
    """The playoff part of the page of `you` by a split of the runs. With no regular week left, each run has the same
    seeds, so the first run gives them. A side of a game is set when each run with weight has the same team there."""
    live = [run for run in runs if run.weight > 0] or list(runs)
    seeds = live[0].seeds
    seed_of = {rid: n for n, rid in enumerate(seeds, start=1)}
    titles: defaultdict[int, float] = defaultdict(float)
    for run in runs:
        if run.champion is not None:
            titles[run.champion] += run.weight
    rounds: list[BracketRound] = []
    out: set[int] = set()
    for r, week in enumerate(bracket_weeks[:len(live[0].rounds)]):
        scores = played.get(week)
        games = []
        for g in range(len(live[0].rounds[r])):
            sides = tuple(_set_side(live, r, g, i) for i in (0, 1))
            pair: tuple[int | None, int | None] = (sides[0], sides[1])
            score: tuple[float, float] | None = None
            winner = None
            if scores is not None and sides[0] is not None and sides[1] is not None:
                a, b = sides[0], sides[1]
                score = (scores[a], scores[b])
                winner = a if scores[a] > scores[b] or (scores[a] == scores[b] and seed_of[a] < seed_of[b]) else b
                out.add(b if winner == a else a)
            games.append(BracketGame(teams=pair, scores=score, winner=winner))
        rounds.append(BracketRound(week=week, played=scores is not None, games=games))
    current = next((r for r, rnd in enumerate(rounds) if not rnd.played), None)
    champion = rounds[-1].games[0].winner if current is None and rounds and rounds[-1].games else None
    alive = you in seed_of and you not in out
    game = None
    bye = False
    if current is not None and alive:
        mine = next((g for g in rounds[current].games if you in g.teams), None)
        bye = mine is None
        if mine is not None and None not in mine.teams:
            opponent = next(rid for rid in mine.teams if rid is not None and rid != you)
            game = _playoff_game(you, live, total, current, rounds[current].week, opponent, about)
    seeded = [BracketTeam(roster_id=rid, seed=n, title=_whole(titles[rid], total), alive=rid not in out)
             for n, rid in enumerate(seeds, start=1)]
    return Playoffs(seed=seed_of.get(you), alive=alive, title=_whole(titles[you], total),
                    week=rounds[current].week if current is not None else None, bye=bye, game=game, teams=seeded,
                    rounds=rounds, champion=champion)


def _set_side(runs: Sequence[RunRecord], r: int, g: int, side: int) -> int | None:
    """The team on `side` of game `g` of round `r` when each run has the same team there, else None."""
    found = {run.rounds[r][g][side] for run in runs}
    return found.pop() if len(found) == 1 else None


def _playoff_game(
    you: int, runs: Sequence[RunRecord], total: float, current: int, week: int, opponent: int, about,
) -> PlayoffGame:
    """The game of `you` in round `current`: the title odds after a win and after a loss, by a split of the runs. A
    win is a place in the next round, or the title after the final."""
    won = [0.0, 0.0]
    lost = 0.0
    for run in runs:
        nxt = run.rounds[current + 1] if current + 1 < len(run.rounds) else None
        win = any(you in pair for pair in nxt) if nxt is not None else run.champion == you
        if win:
            won[0] += run.weight
            won[1] += run.weight if run.champion == you else 0.0
        else:
            lost += run.weight
    results = [
        PlayoffResult(game="win", title=_whole(won[1], won[0]) if won[0] else None, chance=tenths(won[0], total),
                      about=about(won[0])),
        PlayoffResult(game="loss", title=0 if lost else None, chance=tenths(lost, total), about=about(lost)),
    ]
    return PlayoffGame(week=week, opponent=opponent, results=results)


def _root_for(
    you: int, pairs: list[Pair], winners: Mapping[int, list[float]], loss_playoff: int | None, odds, about,
    records: Mapping[int, tuple[int, int, float, float]], place: Mapping[int, int], last_wins: int | None,
) -> list[RootFor]:
    """The root-for rows of one week: for each other game, the side whose win lifts the odds after a loss the most.
    A row stays when it lifts them by ROOT_FOR_LIFT whole points or more and its loser has a true reason. The rows
    rank by the lift, then by the standings place of the loser, so a loss of a team higher in the table comes first.
    `last_wins` holds the real wins of the team in the last playoff spot."""
    if loss_playoff is None:
        return []
    found: list[tuple[int, int, RootFor]] = []
    for a, b in pairs:
        if you in (a, b):
            continue
        sides = []
        for winner, loser in ((a, b), (b, a)):
            after = odds(winners.get(winner, [0.0, 0.0]))
            if after is not None:
                sides.append((after - loss_playoff, winner, loser, after))
        if not sides:
            continue
        lift, winner, loser, after = max(sides, key=lambda side: (side[0], -place[side[2]]))
        if lift < ROOT_FOR_LIFT:
            continue
        reason = _reason(records[loser][0], records[you][0], last_wins)
        if reason is None:
            continue
        found.append((lift, place[loser], RootFor(winner=winner, loser=loser, reason=reason, playoff=after,
                                                  about=about(winners[winner][0]))))
    found.sort(key=lambda row: (-row[0], row[1]))
    return [row for _, _, row in found[:ROOT_FOR_ROWS]]


def _reason(loser_wins: int, your_wins: int, last_wins: int | None) -> Reason | None:
    """The true reason of a root-for row by the real wins: the gap to Your team first, then the race for the last
    playoff spot. None when no reason of the five is true."""
    reason = _REASONS.get(loser_wins - your_wins)
    if reason is None and last_wins is not None and abs(loser_wins - last_wins) <= RACE_GAP:
        reason = _RACE
    return reason


def _sentence(status: OddsStatus, need: int | None, wins_left: int, ladder: list[LadderStep], set_left: int = 0,
              set_wins: int = 0) -> str:
    """The one line of more wins: the smallest count with playoff odds of IN_ODDS or more. A What-if holds `set_wins`
    of the `set_left` wins of its set weeks, so the line names only the wins still open."""
    if status == "in":
        return "You're in."
    if status == "out":
        return "You're out of the playoff race."
    wins_left -= set_left
    if not wins_left:
        return "Every week left is set."
    # No run of a What-if has fewer more wins than its set wins, so `need` is never under `set_wins`.
    need = None if need is None else need - set_wins
    if need == 0:
        return f"You're in at {IN_ODDS}% or better even with no more wins."
    if need is not None:
        return f"Win {need} of the {wins_left} left and you're in."
    # The best case wins every open win on top of the set wins.
    best = ladder[set_wins + wins_left].playoff
    return f"Win all {wins_left} left for a {best}% shot." if best is not None else "No run gives you a playoff spot."


def league_fact(playoff: Mapping[int, int], spots: int, weeks_left: int) -> str | None:
    """The league fact of the Sim tile in the regular season: the race for the last spots. A team at IN_ODDS or more
    is safe, and a team from RACE_FLOOR to under IN_ODDS is in the race. None with no regular week left."""
    if not weeks_left:
        return None
    safe = sum(odds >= IN_ODDS for odds in playoff.values())
    race = sum(RACE_FLOOR <= odds < IN_ODDS for odds in playoff.values())
    left = spots - safe
    if not 0 < left < race:
        return "The playoff field is all but set"
    return f"{race} managers fight for the last {'spot' if left == 1 else f'{left} spots'}"


def playoff_fact(page: SimPage, names: Mapping[int, str], season: int) -> str | None:
    """The league fact of the Sim tile with no regular week left: the favorite of the teams left, or the champion
    after the final. None in the regular season."""
    playoffs = page.playoffs
    if playoffs is None:
        return None
    if playoffs.champion is not None:
        return f"{names.get(playoffs.champion, f'Team {playoffs.champion}')} is the {season} champion"
    left = [team for team in playoffs.teams if team.alive]
    favorite = max(left, key=lambda team: (team.title, -team.seed))
    return (f"{len(left)} teams left, {names.get(favorite.roster_id, f'Team {favorite.roster_id}')} is the favorite "
            f"at {favorite.title}%")
