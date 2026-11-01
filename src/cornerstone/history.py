"""
Cache of past weeks of Sleeper data under data/{season}/history.
It fetches only the weeks that are not on disk.
It also builds the profile of a player from the weeks before a trade.
"""
import json
import shutil
from collections.abc import Callable
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from typing import Literal

from cornerstone.facts_league import TREND_WEEKS
from cornerstone.files import write_bytes_atomic
from cornerstone.models import History, PastWeek, UsageShare
from cornerstone.numbers import round_half_up
from cornerstone.parse import parse_past_week
from cornerstone.paths import history_raw_dir, history_week_dir
from cornerstone.provider.raw import RawMatchup, RawPastWeek, RawTransaction, RawWeek
from cornerstone.provider.sleeper import SLEEPER, read_prev_transactions
from cornerstone.tunables import HANDCUFF_CARRY_GAMES, HANDCUFF_MIN_GAMES, SHARE_WEEKS

# The past leg fetch takes the league id, the season, the week, and the folder, and saves the week there.
# It has the shape of Provider.fetch_past_leg. The history reads the saved files and not the return, so a fake that
# gives None fits too.
PastLegFetcher = Callable[[str, int, int, Path], RawPastWeek | None]

HISTORY_FILES: tuple[str, ...] = ("matchups", "transactions", "stats", "projections")
UNOFFICIAL_FILES: tuple[str, ...] = ("stats", "projections")
# Percentage points of change in a share that count as "up" or "down".
SHARE_SWING = 5
# A direction needs two windows of SHARE_WEEKS weeks each.
SHARE_DIRECTION_WEEKS = 2 * SHARE_WEEKS


def _is_saved(directory: Path) -> bool:
    if not all((directory / f"{name}.json").exists() for name in HISTORY_FILES):
        return False
    # The unofficial endpoints return an empty list on an outage, so an empty file is not saved data.
    return all(json.loads((directory / f"{name}.json").read_text()) for name in UNOFFICIAL_FILES)


def fetch_history(
    league_id: str,
    season: int,
    through: int,
    root: Path,
    force: bool = False,
    fetch: PastLegFetcher = SLEEPER.fetch_past_leg,
) -> list[int]:
    fetched = []
    for week in range(1, through + 1):
        directory = history_week_dir(root, week)
        if not force and _is_saved(directory):
            continue
        fetch(league_id, season, week, directory)
        fetched.append(week)
    return fetched


def _read_week(directory: Path) -> RawPastWeek | None:
    # A week with a missing file is left out, so a gap removes facts and never makes one wrong.
    if not all((directory / f"{name}.json").exists() for name in HISTORY_FILES):
        return None
    return RawPastWeek.model_validate({
        name: json.loads((directory / f"{name}.json").read_text())
        for name in HISTORY_FILES
    })


def _fresh_transactions(root: Path, week: int) -> list[RawTransaction] | None:
    """The full leg of `week` that the fetch of the next week saved, or None when that file is not saved.

    The week N build runs before the Tuesday night waiver run, so the saved copy misses the adds after it.
    Sleeper keeps the leg at N until the next week starts, and the fetch of week N+1 saves the full leg.
    """
    return read_prev_transactions(history_raw_dir(root, week + 1))


def load_saved_weeks(root: Path, through: int) -> dict[int, PastWeek]:
    """The saved weeks 1 to `through`, by week. A week that is not saved has no entry."""
    weeks = {}
    for past in range(1, through + 1):
        saved = _read_week(history_week_dir(root, past))
        if saved is not None:
            fresh = _fresh_transactions(root, past)
            if fresh is not None:
                saved.transactions = fresh
            weeks[past] = parse_past_week(saved, past)
    return weeks


def saved_through(root: Path, week: int) -> int:
    """The last week at or after `week` such that every week from `week` to it is saved."""
    last = week
    while _read_week(history_week_dir(root, last + 1)) is not None:
        last += 1
    return last


def load_history(root: Path, raw: RawWeek, week: int) -> History:
    weeks = load_saved_weeks(root, week - 1)
    # The current week comes from the raw data of this run, not from the cache.
    weeks[week] = parse_past_week(raw, week)
    return History(week=week, weeks=weeks)



def player_points(past: PastWeek, player_id: str) -> float | None:
    """Points of a player in a past week. The roster points come first, then the stat line."""
    if player_id in past.points:
        return past.points[player_id]
    return (past.stats.get(player_id) or {}).get("pts_half_ppr")


def player_trend(history: History, player_id: str, through: int | None = None) -> int | None:
    """The count of the last 3 weeks up to `through` in which the player beat the projection.

    `through` is the current week when it is None.
    It is None when any of the 3 weeks lacks points or a projection, so a gap never gives a wrong count.
    """
    last = history.week if through is None else through
    beaten = 0
    for week in range(last - TREND_WEEKS + 1, last + 1):
        past = history.weeks.get(week)
        if past is None:
            return None
        points = player_points(past, player_id)
        projection = past.projections.get(player_id)
        if points is None or projection is None:
            return None
        beaten += points > projection
    return beaten


def stats_complete(history: History, through: int) -> bool:
    """True when every week from 1 to `through` is present and has stat lines.

    A stats outage gives an empty file, and a profile built on a gap would be wrong.
    """
    return all(
        (week_data := history.weeks.get(week)) is not None and week_data.stats
        for week in range(1, through + 1)
    )


def scored_weeks(history: History, player_id: str, through: int) -> list[int]:
    """The weeks from 1 to `through` in which the player played a game."""
    return [
        week for week in range(1, through + 1)
        if week in history.weeks
        and (history.weeks[week].stats.get(player_id) or {}).get("gp", 0) > 0
    ]


def points_per_game(history: History, player_id: str, through: int) -> tuple[float, int] | None:
    """The points per game and the count of games from week 1 to `through`.

    The sum is exact decimals, so 21.395 rounds to 21.4.
    """
    if not stats_complete(history, through):
        return None
    weeks = scored_weeks(history, player_id, through)
    if not weeks:
        return (0.0, 0)
    # Sleeper leaves out a stat whose value is 0, so a game with no pts_half_ppr scored 0.
    total = sum(Decimal(str(player_points(history.weeks[w], player_id) or 0)) for w in weeks)
    mean = (total / len(weeks)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
    return (float(mean), len(weeks))


def season_rank(history: History, player_id: str, through: int) -> tuple[int, int] | None:
    """The rank of the player by points among the players of his position, and the count of them.

    Only weeks 1 to `through` count, for the player and for every peer.
    """
    if not stats_complete(history, through):
        return None
    totals: dict[str, float] = {}
    positions: dict[str, str] = {}
    for week in range(1, through + 1):
        past = history.weeks[week]
        positions.update(past.positions)
        for pid, line in past.stats.items():
            totals[pid] = totals.get(pid, 0.0) + line.get("pts_half_ppr", 0.0)
    position = positions.get(player_id)
    if position is None or player_id not in totals:
        return None
    peers = [pid for pid in totals if positions.get(pid) == position]
    above = sum(totals[pid] > totals[player_id] for pid in peers)
    return (above + 1, len(peers))


def share_direction(recent: float, prior: float) -> Literal["up", "down", "flat"]:
    """Compare two unrounded percents. A change of SHARE_SWING points or more has a direction."""
    if recent - prior >= SHARE_SWING:
        return "up"
    if prior - recent >= SHARE_SWING:
        return "down"
    return "flat"


def _usage_share(
    history: History,
    player_id: str,
    through: int,
    numerator: Callable[[PastWeek], float],
    denominator: Callable[[PastWeek], float],
) -> UsageShare | None:
    """The share of the player in the last SHARE_WEEKS scored weeks,
    and its direction against the SHARE_WEEKS before."""
    if not stats_complete(history, through):
        return None
    weeks = [w for w in scored_weeks(history, player_id, through) if denominator(history.weeks[w]) > 0]
    if not weeks:
        return None

    def pct(ws: list[int]) -> float:
        return 100 * sum(numerator(history.weeks[w]) for w in ws) / sum(denominator(history.weeks[w]) for w in ws)

    if len(weeks) < SHARE_DIRECTION_WEEKS:
        return UsageShare(percent=int(round_half_up(pct(weeks))), weeks=len(weeks), direction=None, weeks_used=weeks)
    recent, prior = weeks[-SHARE_WEEKS:], weeks[-SHARE_DIRECTION_WEEKS:-SHARE_WEEKS]
    return UsageShare(
        percent=int(round_half_up(pct(recent))),
        weeks=SHARE_WEEKS,
        direction=share_direction(pct(recent), pct(prior)),
        weeks_used=recent,
    )


def snap_share(history: History, player_id: str, through: int) -> UsageShare | None:
    """The share of the offense snaps of the team that the player played."""
    return _usage_share(
        history, player_id, through,
        numerator=lambda past: past.stats[player_id].get("off_snp", 0.0),
        denominator=lambda past: past.stats[player_id].get("tm_off_snp", 0.0),
    )


def _team_total(past: PastWeek, player_id: str, stat: str) -> float:
    """The sum of one stat over every player of the player's NFL team in one week. No team gives 0."""
    team = past.nfl_teams.get(player_id)
    if team is None:
        return 0.0
    return sum(
        past.stats.get(pid, {}).get(stat, 0.0)
        for pid, nfl_team in past.nfl_teams.items() if nfl_team == team
    )


def target_share(history: History, player_id: str, through: int) -> UsageShare | None:
    """The share of the targets of his NFL team that the player took."""
    return _usage_share(
        history, player_id, through,
        numerator=lambda past: past.stats[player_id].get("rec_tgt", 0.0),
        denominator=lambda past: _team_total(past, player_id, "rec_tgt"),
    )


def air_yards_share(history: History, player_id: str, through: int) -> UsageShare | None:
    """The share of the air yards of his NFL team that the player took."""
    return _usage_share(
        history, player_id, through,
        numerator=lambda past: past.stats[player_id].get("rec_air_yd", 0.0),
        denominator=lambda past: _team_total(past, player_id, "rec_air_yd"),
    )


def carry_share(history: History, player_id: str, through: int) -> float | None:
    """The exact percent of his NFL team's carries that the player took in his last HANDCUFF_CARRY_GAMES played
    games. It is not rounded, so a gate can compare it.

    None with fewer than HANDCUFF_MIN_GAMES played games, with a gap in the stats, or with no team carries.
    """
    if not stats_complete(history, through):
        return None
    weeks = scored_weeks(history, player_id, through)
    if len(weeks) < HANDCUFF_MIN_GAMES:
        return None
    recent = [history.weeks[w] for w in weeks[-HANDCUFF_CARRY_GAMES:]]
    team = sum(_team_total(past, player_id, "rush_att") for past in recent)
    if team == 0:
        return None
    carries = sum(past.stats[player_id].get("rush_att", 0.0) for past in recent)
    return 100 * carries / team


def red_zone(history: History, player_id: str, through: int) -> tuple[int, int] | None:
    """The red-zone targets and the red-zone rushes of the player from week 1 to `through`."""
    weeks = scored_weeks(history, player_id, through)
    if not stats_complete(history, through) or not weeks:
        return None
    lines = [history.weeks[w].stats[player_id] for w in weeks]
    return (
        int(sum(line.get("rec_rz_tgt", 0.0) for line in lines)),
        int(sum(line.get("rush_rz_att", 0.0) for line in lines)),
    )


def save_week_to_history(raw_dir: Path, out_dir: Path) -> None:
    """Put a built week into the history, so the next week reads it from disk.

    The files are copies, not symlinks. A refetch or a move of the raw directory must not change the history.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    for name in HISTORY_FILES:
        shutil.copyfile(raw_dir / f"{name}.json", out_dir / f"{name}.json")
    matchups = [RawMatchup.model_validate(m)
                for m in json.loads((raw_dir / "matchups.json").read_text(encoding="utf-8"))]
    players = json.loads((raw_dir / "players.json").read_text(encoding="utf-8"))
    _save_injuries(matchups, players, out_dir)


def save_raw_to_history(raw: RawWeek, out_dir: Path) -> None:
    """Put the raw data of a week, held in memory, into the history. It writes the same files as save_week_to_history.

    The live path has no raw directory, so it writes the parsed raw data instead of a copy.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    for name in HISTORY_FILES:
        write_bytes_atomic(out_dir / f"{name}.json", json.dumps(raw.file_json(name)).encode("utf-8"))
    _save_injuries(raw.matchups, raw.players, out_dir)


def _save_injuries(matchups: list[RawMatchup], players: dict[str, dict], out_dir: Path) -> None:
    injuries = {}
    for roster in matchups:
        for player_id in roster.players or []:
            status = (players.get(player_id) or {}).get("injury_status")
            if status:
                injuries[player_id] = status
    write_bytes_atomic(out_dir / "injuries.json", json.dumps(injuries, indent=2).encode("utf-8"))
