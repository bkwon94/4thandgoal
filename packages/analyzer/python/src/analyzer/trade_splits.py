"""
The past-season split facts of the traded players: per season of the last 3 complete seasons, the half PPR points per
game in weeks 1 to 8, in weeks 9 to 17, and in cold games, each with its game count. It reads the cache only.
"""
from pathlib import Path
from typing import NamedTuple

from analyzer.rubric import ProposedTrade
from facts.tokens import Nums, fact
from league.models import Fact
from league.nflverse import SCHEDULES_URL, cache_path
from league.nflverse_rows import _number, _rows
from league.numbers import plural
from league.past_seasons import past_seasons, past_stats_path
from league.paths import nflverse_cache_dir
from league.snapshot import Snapshot

EARLY_WEEKS = (1, 8)
LATE_WEEKS = (9, 17)
# A cold game is outdoors at this temperature in F or below.
COLD_F = 40
# The roof values of a game under the open sky. A dome and a closed roof are never cold games.
OUTDOOR_ROOFS = ("outdoors", "open")


COLD_LABEL = "in cold games"


class Split(NamedTuple):
    """The half PPR points per game of a set of games, and the count of those games."""
    points_per_game: float
    games: int


class SeasonSplits(NamedTuple):
    """The splits of one player in one past season. A split with no game is None."""
    season: int
    # The NFL team of his last regular season game of that season.
    team: str
    early: Split | None
    late: Split | None
    cold: Split | None


def _split(points: list[float]) -> Split | None:
    return Split(round(sum(points) / len(points), 2), len(points)) if points else None


def _cold_games(schedules: Path) -> set[str]:
    """The game ids of every outdoor game at COLD_F or below, over every season in the file."""
    return {row["game_id"] for row in _rows(schedules)
            if row["roof"] in OUTDOOR_ROOFS and row["temp"] not in ("", "NA") and float(row["temp"]) <= COLD_F}


def season_splits(cache_dir: Path, season: int, gsis: str) -> list[SeasonSplits]:
    """The splits of a player for each past season of `season` whose file is in the cache and has a game of his.

    The reader counts the regular season games of the file. The schedules file gives the cold games, so with no
    schedules file a season has no cold split.
    """
    # A cache with no past season file gives no split, so the reader skips the schedules file too.
    pasts = [past for past in past_seasons(season) if past_stats_path(cache_dir, past).exists()]
    if not pasts:
        return []
    schedules = cache_path(cache_dir, SCHEDULES_URL, season)
    cold_ids = _cold_games(schedules) if schedules.exists() else set()
    out = []
    for past in pasts:
        path = past_stats_path(cache_dir, past)
        early, late, cold, team = [], [], [], ""
        for row in _rows(path):
            if row["player_id"] != gsis or row["season_type"] != "REG":
                continue
            # The league plays half PPR, which is the mean of the standard points and the full PPR points.
            points = (_number(row["fantasy_points"]) + _number(row["fantasy_points_ppr"])) / 2
            week = int(row["week"])
            # The rows run in week order, so the last row names the team he ended the season with.
            team = row["team"]
            if EARLY_WEEKS[0] <= week <= EARLY_WEEKS[1]:
                early.append(points)
            elif LATE_WEEKS[0] <= week <= LATE_WEEKS[1]:
                late.append(points)
            if row["game_id"] in cold_ids:
                cold.append(points)
        if early or late or cold:
            out.append(SeasonSplits(past, team, _split(early), _split(late), _split(cold)))
    return out


def _clause(n: Nums, label: str, split: Split | None) -> str:
    if split is None:
        return "no cold game" if label == COLD_LABEL else f"no game {label}"
    return f"{n(split.points_per_game)} {label} over {n(split.games)} {plural(split.games, 'game', 'games')}"


def _history_fact(snapshot: Snapshot, pid: str, splits: list[SeasonSplits]) -> Fact:
    n = Nums()
    name = snapshot.players[pid].name
    weeks = {"early": f"in weeks {n(EARLY_WEEKS[0])} to {n(EARLY_WEEKS[1])}",
             "late": f"in weeks {n(LATE_WEEKS[0])} to {n(LATE_WEEKS[1])}", "cold": COLD_LABEL}
    sentences = [f"In {n(s.season)}, {name} played for {s.team} and scored half PPR points per game as follows: "
                 f"{_clause(n, weeks['early'], s.early)}; {_clause(n, weeks['late'], s.late)}; "
                 f"{_clause(n, weeks['cold'], s.cold)}." for s in splits]
    sentences.append(f"A cold game is outdoors at {n(COLD_F)} degrees F or below.")
    return fact(f"{pid}.history", " ".join(sentences), n, [], [name])


def trade_split_facts(trade: ProposedTrade, snapshot: Snapshot) -> dict[str, Fact]:
    """One history fact per traded player who has a past season in the cache, by fact id.

    A player with no gsis id, or with no row in a past season file, has no fact, so no read gives him a number
    from a past season.
    """
    cache = nflverse_cache_dir(snapshot.client.nfl_dir)
    facts = {}
    for pid in trade.player_ids:
        gsis = (snapshot.id_map or {}).get(pid)
        splits = season_splits(cache, snapshot.season, gsis) if gsis else []
        if splits:
            facts[f"{pid}.history"] = _history_fact(snapshot, pid, splits)
    return facts
