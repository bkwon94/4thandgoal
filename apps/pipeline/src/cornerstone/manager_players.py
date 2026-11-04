"""
The players of a managers file entry: the best adds and the top performers of one roster.
Pure code over the saved history and the raw players file of the current week.
"""
from pydantic import BaseModel

from league.models import History
from league.parse import player_name

BEST_ADDS = 3
TOP_PERFORMERS = 5
# A trade is a move, but not an add: the Best Adds chapter reads pickups only.
ADD_KINDS = {"waiver", "free_agent"}


class BestAdd(BaseModel):
    """One add of a roster, with the points and the projection of the weeks on the roster since the add."""
    player_id: str
    name: str
    position: str | None
    week: int
    points: float
    projection: float
    games: int


class TopPerformer(BaseModel):
    """One player of a roster, with the points of the weeks he started for it."""
    player_id: str
    name: str
    position: str | None
    points: float
    games: int
    per_game: float


def _name_and_position(history: History, player_id: str, players: dict[str, dict]) -> tuple[str, str | None]:
    """The name and the position from the raw players file. A player not in it falls back to the id and the
    position of the latest saved week that has one, or None."""
    entry = players.get(player_id)
    if entry is not None and entry.get("position"):
        return player_name(player_id, entry), entry["position"]
    saved = [history.weeks[w].positions[player_id] for w in sorted(history.weeks)
             if player_id in history.weeks[w].positions]
    return player_name(player_id, entry), saved[-1] if saved else None


def best_adds(history: History, roster_id: int, players: dict[str, dict]) -> list[BestAdd]:
    """The top three adds of the roster by points for it since the add. Ties go to the earlier add."""
    # A later add of the same player overwrites the earlier one, so a drop and a re-add counts from the last add.
    last_add: dict[str, int] = {}
    for w in sorted(history.weeks):
        for move in history.weeks[w].moves:
            if move.roster_id == roster_id and move.kind in ADD_KINDS:
                last_add[move.player_id] = move.week
    adds = []
    for pid, added in last_add.items():
        # The span counts only the weeks the player is on the roster, so a short stint ends where he leaves.
        span = [history.weeks[w] for w in sorted(history.weeks)
                if added <= w <= history.week and pid in history.weeks[w].rosters.get(roster_id, [])]
        name, position = _name_and_position(history, pid, players)
        adds.append(BestAdd(
            player_id=pid, name=name, position=position, week=added,
            points=round(sum(p.points.get(pid, 0.0) for p in span), 2),
            projection=round(sum(p.projections.get(pid, 0.0) for p in span), 2),
            games=len(span),
        ))
    # The sort is stable, so two adds of the same week and points keep the order of the moves.
    return sorted(adds, key=lambda a: (-a.points, a.week))[:BEST_ADDS]


def top_performers(history: History, roster_id: int, players: dict[str, dict]) -> list[TopPerformer]:
    """The top five players of the roster by points while started for it, year to date."""
    # The starts read the roster of each week, so a player traded away keeps the starts he made here.
    points: dict[str, float] = {}
    games: dict[str, int] = {}
    for w in sorted(history.weeks):
        if w > history.week:
            continue
        past = history.weeks[w]
        for pid in past.starters.get(roster_id, []):
            points[pid] = points.get(pid, 0.0) + past.points.get(pid, 0.0)
            games[pid] = games.get(pid, 0) + 1
    # The player id breaks a tie on points, so the order of the file does not change between builds.
    ranked = sorted(points, key=lambda pid: (-points[pid], pid))[:TOP_PERFORMERS]
    performers = []
    for pid in ranked:
        name, position = _name_and_position(history, pid, players)
        performers.append(TopPerformer(
            player_id=pid, name=name, position=position, points=round(points[pid], 2), games=games[pid],
            per_game=round(points[pid] / games[pid], 1),
        ))
    return performers
