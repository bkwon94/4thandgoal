"""
The Week lineup of one roster for the live week, by projection: each slot in Sleeper order with its starter, the Q tag
and the Pivot of a Questionable starter, and the players who cannot play. Code holds only facts and legal rules.
"""
from dataclasses import dataclass
from datetime import datetime

from cornerstone_api.game_lock import Kickoff
from league.lineup import BENCH_SLOTS, allowed_positions, fill_slots
from league.provider.raw import RawWeek

# The injury statuses of Sleeper with which a player cannot play: Out, IR, suspended, the PUP list, not active, and did
# not report. Questionable and Doubtful players can still play, so they keep their slot.
CANNOT_PLAY_STATUSES = frozenset({"Out", "IR", "Sus", "PUP", "NA", "DNR"})
QUESTIONABLE = "Questionable"
# The Q tag before the first practice report of the week, when `practice_participation` is null for every player.
NO_PRACTICE_REPORT = "No practice report yet"
# The status of a player whose NFL team has no game this week, and of a player with no NFL team.
BYE = "Bye"
NO_TEAM = "No team"


@dataclass(frozen=True)
class Player:
    """One rostered player as the lineup reads him from the Sleeper players file and the projections of the week."""

    player_id: str
    name: str
    short_name: str
    position: str
    nfl_team: str | None
    injury_status: str | None
    body_part: str | None
    practice: str | None
    # The projection in the points of the league, or None with no projection row.
    projection: float | None
    # The projected stat line, only the stats that the league scores.
    stat_line: dict[str, float]


@dataclass(frozen=True)
class Risk:
    """The Q tag of a Questionable starter: his body part, his practice level, and the Pivot line."""

    body_part: str | None
    practice: str
    pivot: str


@dataclass(frozen=True)
class Row:
    """One slot of the lineup: the slot, its starter or None, his game, and whether his game has started."""

    slot: str
    player: Player | None
    opponent: str | None
    kickoff: datetime | None
    locked: bool
    risk: Risk | None


@dataclass(frozen=True)
class Absent:
    """A rostered player who cannot play this week, with his status, such as Out, IR, or Bye, and his body part."""

    player: Player
    status: str
    body_part: str | None


@dataclass(frozen=True)
class WeekLineup:
    """The lineup by projection of one roster, its bench, and the players who cannot play."""

    week: int
    rows: list[Row]
    bench: list[Player]
    cannot_play: list[Absent]

    @property
    def total(self) -> float:
        """The sum of the projections of the starters."""
        return sum(row.player.projection or 0.0 for row in self.rows if row.player is not None)

    @property
    def shown_total(self) -> float:
        """The sum of the projections that the rows show, each to one decimal, so a reader who adds the rows gets the
        total of the header. The block, the facts of Claude, and the live matchup card all show this total."""
        return round(sum(round(row.player.projection or 0.0, 1) for row in self.rows if row.player is not None), 1)


def score(stats: dict[str, float], scoring: dict[str, float]) -> float:
    """The points of a stat line in the scoring of the league: each stat times its points, summed."""
    return sum(value * scoring[key] for key, value in stats.items() if key in scoring)


def _short(entry: dict, position: str) -> str:
    """The short name of the lines, such as "J. Jacobs". A defense goes by its nickname, such as "Jaguars"."""
    first, last = entry.get("first_name") or "", entry.get("last_name") or ""
    if position == "DEF" or not first:
        return last or first
    return f"{first[0]}. {last}"


def full_name(entry: dict, pid: str) -> str:
    """The full name of a player from his entry of the Sleeper players file, such as "Jacksonville Jaguars" for a
    defense, or his id with no name."""
    return entry.get("full_name") or " ".join(part for part in (entry.get("first_name"), entry.get("last_name"))
                                              if part) or pid


def _players(raw: RawWeek, ids: list[str]) -> dict[str, Player]:
    scoring = raw.league.scoring_settings
    projected = {row.player_id: row.stats for row in raw.projections}
    players = {}
    for pid in ids:
        entry = raw.players.get(pid, {})
        position = entry.get("position") or ""
        stats = projected.get(pid)
        name = full_name(entry, pid)
        players[pid] = Player(
            player_id=pid, name=name, short_name=_short(entry, position), position=position,
            nfl_team=entry.get("team"), injury_status=entry.get("injury_status"),
            body_part=entry.get("injury_body_part"), practice=entry.get("practice_participation"),
            projection=None if stats is None else round(score(stats, scoring), 2),
            stat_line={} if stats is None else {key: value for key, value in stats.items() if key in scoring})
    return players


def _games(kickoffs: list[Kickoff]) -> dict[str, tuple[str, Kickoff]]:
    """The opponent and the game of each NFL team that plays this week. A team with no entry has a bye."""
    games = {}
    for game in kickoffs:
        games[game.home] = (game.away, game)
        games[game.away] = (game.home, game)
    return games


def _status(player: Player, games: dict[str, tuple[str, Kickoff]]) -> str | None:
    """Why the player cannot play this week, or None when he can."""
    if player.injury_status in CANNOT_PLAY_STATUSES:
        return player.injury_status
    if player.nfl_team is None:
        return NO_TEAM
    if player.nfl_team not in games:
        return BYE
    return None


def week_lineup(raw: RawWeek, roster_id: int, kickoffs: list[Kickoff], now: datetime) -> WeekLineup:
    """The lineup by projection of the roster for the week of `raw`.

    The slots are the starting slots of the league in Sleeper order. A player whose game has started is locked: a locked
    starter keeps the slot that he holds in Sleeper, and a locked bench player stays on the bench. Each other slot takes
    the free player with the best projection that the slot allows, the fixed slots first, then the flex slots.
    """
    roster = next(r for r in raw.rosters if r.roster_id == roster_id)
    taxi = set(getattr(roster, "taxi", None) or [])
    ids = [pid for pid in roster.players or [] if pid not in taxi]
    players = _players(raw, ids)
    games = _games(kickoffs)
    slots = [slot for slot in raw.league.roster_positions if slot not in BENCH_SLOTS]
    matchup = next((m for m in raw.matchups if m.roster_id == roster_id), None)
    held = list(matchup.starters or []) if matchup is not None else []

    def locked(pid: str) -> bool:
        team = players[pid].nfl_team
        return team in games and games[team][1].locked(now)

    absent = {pid: status for pid in ids if (status := _status(players[pid], games)) is not None}
    # A locked starter stays in his Sleeper slot, so each slot index he holds is pinned to him.
    pinned = {index: held[index] for index in range(min(len(held), len(slots)))
              if held[index] in players and locked(held[index])}
    free = [pid for pid in ids if pid not in absent and not locked(pid)]
    open_slots = [slots[index] for index in range(len(slots)) if index not in pinned]
    filled = fill_slots(free, open_slots, {pid: players[pid].position for pid in free},
                        {pid: players[pid].projection or 0.0 for pid in free})
    # fill_slots gives the fixed slots first, so each open slot takes the next pick of its own slot name.
    picks: dict[str, list[str | None]] = {}
    for slot, pid in filled:
        picks.setdefault(slot, []).append(pid)
    starters = [pinned[index] if index in pinned else picks[slots[index]].pop(0) for index in range(len(slots))]
    started = {pid for pid in starters if pid is not None}
    bench = [pid for pid in free if pid not in started]

    rows = []
    for slot, pid in zip(slots, starters, strict=True):
        if pid is None:
            rows.append(Row(slot=slot, player=None, opponent=None, kickoff=None, locked=False, risk=None))
            continue
        player = players[pid]
        opponent, game = games.get(player.nfl_team or "", (None, None))
        is_locked = locked(pid)
        risk = None
        if player.injury_status == QUESTIONABLE and not is_locked:
            risk = Risk(body_part=player.body_part, practice=player.practice or NO_PRACTICE_REPORT,
                        pivot=_pivot(player, slot, [players[b] for b in bench]))
        rows.append(Row(slot=slot, player=player, opponent=opponent, kickoff=None if game is None else game.start,
                        locked=is_locked, risk=risk))
    return WeekLineup(week=raw.state.display_week, rows=rows, bench=[players[pid] for pid in bench],
                      cannot_play=[Absent(players[pid], status, players[pid].body_part)
                                   for pid, status in absent.items()])


def _pivot(starter: Player, slot: str, bench: list[Player]) -> str:
    """The Pivot line of a Questionable starter: the best bench player by projection that his slot allows."""
    allowed = allowed_positions(slot)
    fits = [player for player in bench if player.position in allowed]
    if not fits:
        return f"Start {starter.short_name} if he is active."
    best = max(fits, key=lambda player: (player.projection or 0.0, player.player_id))
    # A name such as "K. Pitts Sr." ends the sentence with its own period.
    end = "" if best.short_name.endswith(".") else "."
    return f"Start {starter.short_name} if he is active. If he is ruled out, start {best.short_name}{end}"
