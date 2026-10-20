"""
Parse the raw Sleeper JSON into the domain models.
This is the only module that knows the shape of the raw data.
"""
from collections import defaultdict
from datetime import date, datetime, timezone

from cornerstone.models import DraftPick, Matchup, Move, PastWeek, PlayerLine, Side, Team, Trade, Week

AVATAR_THUMB_URL = "https://sleepercdn.com/avatars/thumbs/{avatar}"
MOVE_KINDS = ("waiver", "free_agent", "trade")


def _avatar_url(user: dict) -> str | None:
    metadata_avatar = (user.get("metadata") or {}).get("avatar")
    if metadata_avatar:
        return metadata_avatar
    if user.get("avatar"):
        return AVATAR_THUMB_URL.format(avatar=user["avatar"])
    return None


def _teams(raw: dict, brian_user: str) -> dict[int, Team]:
    users = {u["user_id"]: u for u in raw["users"]}
    teams = {}
    for roster in raw["rosters"]:
        user = users[roster["owner_id"]]
        settings = roster["settings"]
        # Sleeper splits the points into a whole part and a two-digit decimal part.
        points_for = settings["fpts"] + settings.get("fpts_decimal", 0) / 100
        teams[roster["roster_id"]] = Team(
            roster_id=roster["roster_id"],
            name=(user.get("metadata") or {}).get("team_name") or user["display_name"],
            owner=user["display_name"],
            avatar_url=_avatar_url(user),
            wins=settings["wins"],
            losses=settings["losses"],
            points_for=points_for,
            is_brian=user["display_name"] == brian_user,
        )
    return teams


def _projection_map(raw: dict) -> dict[str, float | None]:
    return {
        item["player_id"]: item["stats"].get("pts_half_ppr")
        for item in raw["projections"]
    }


def _player_name(player_id: str, entry: dict | None) -> str:
    if entry is None:
        return player_id
    if entry.get("full_name"):
        return entry["full_name"]
    # A defense has no full_name, only a city in first_name and a nickname in last_name.
    return f"{entry.get('first_name', '')} {entry.get('last_name', '')}".strip() or player_id


def _line(player_id, entry, roster_positions, projections, players, starters) -> PlayerLine:
    player = players.get(player_id)
    started = player_id in starters
    return PlayerLine(
        player_id=player_id,
        name=_player_name(player_id, player),
        position=player["position"] if player else "?",
        nfl_team=player.get("team") if player else None,
        points=entry["players_points"].get(player_id, 0.0),
        projection=projections.get(player_id),
        # Version 1 has no season history, so no season average exists yet.
        season_avg=None,
        started=started,
        slot=roster_positions[starters.index(player_id)] if started else None,
        injury_status=player.get("injury_status") if player else None,
        injury_body_part=player.get("injury_body_part") if player else None,
    )


EMPTY_SLOT = "0"


def _side(entry: dict, roster_positions, projections, players) -> Side:
    # Sleeper marks an empty starter slot with "0". The starters list keeps it, so the slot
    # index of every other starter stays right, but "0" is never a player line.
    starters = entry["starters"]
    lines = [
        _line(pid, entry, roster_positions, projections, players, starters)
        for pid in entry["players"]
        if pid != EMPTY_SLOT
    ]
    return Side(roster_id=entry["roster_id"], points=entry["points"], lines=lines)


def _matchups(raw: dict) -> list[Matchup]:
    roster_positions = raw["league"]["roster_positions"]
    projections = _projection_map(raw)
    groups = defaultdict(list)
    for entry in raw["matchups"]:
        if entry["matchup_id"] is not None:
            groups[entry["matchup_id"]].append(entry)
    matchups = []
    for matchup_id in sorted(groups):
        first, second = sorted(groups[matchup_id], key=lambda e: e["roster_id"])
        matchups.append(Matchup(
            matchup_id=matchup_id,
            a=_side(first, roster_positions, projections, raw["players"]),
            b=_side(second, roster_positions, projections, raw["players"]),
        ))
    return matchups


def _next_matchups(raw: dict) -> list[tuple[int, int]]:
    groups = defaultdict(list)
    for entry in raw["matchups_next"]:
        if entry["matchup_id"] is not None:
            groups[entry["matchup_id"]].append(entry["roster_id"])
    # A pair is a matchup. A lone entry, such as a bye, has no opponent to name.
    return [tuple(sorted(groups[mid])) for mid in sorted(groups) if len(groups[mid]) == 2]


def parse_moves(transactions: list[dict]) -> list[Move]:
    moves = []
    for transaction in transactions:
        if transaction["status"] != "complete" or transaction["type"] not in MOVE_KINDS:
            continue
        settings = transaction.get("settings") or {}
        for player_id, roster_id in (transaction["adds"] or {}).items():
            moves.append(Move(
                player_id=player_id,
                roster_id=roster_id,
                kind=transaction["type"],
                week=transaction["leg"],
                bid=settings.get("waiver_bid"),
            ))
    return moves


def parse_trades(transactions: list[dict]) -> list[Trade]:
    return [
        Trade(
            transaction_id=t["transaction_id"],
            created=datetime.fromtimestamp(t["created"] / 1000, tz=timezone.utc),
            roster_ids=t["roster_ids"],
            adds=t["adds"] or {},
            drops=t["drops"] or {},
            draft_picks=[DraftPick(**pick) for pick in t["draft_picks"]],
        )
        for t in transactions
        if t["type"] == "trade" and t["status"] == "complete"
    ]


def parse_week(raw: dict[str, object], brian_user: str = "bkwon", week: int | None = None) -> Week:
    state = raw["state"]
    return Week(
        season=int(state["season"]),
        # state.week is the current NFL week, not the scored week, so use display_week by default.
        week=week if week is not None else state["display_week"],
        teams=_teams(raw, brian_user),
        matchups=_matchups(raw),
        next_matchups=_next_matchups(raw),
        moves=parse_moves(raw["transactions"]),
        last_scored_week=raw["league"]["settings"]["last_scored_leg"],
        season_start=date.fromisoformat(state["season_start_date"]),
        # The reserve slot counts: matchups.json lists the injured reserve player with the others.
        roster_slots=len(raw["league"]["roster_positions"]) + raw["league"]["settings"]["reserve_slots"],
    )


def parse_past_week(raw: dict[str, object], week: int) -> PastWeek:
    entries = raw["matchups"]
    groups = defaultdict(list)
    points: dict[str, float] = {}
    for entry in entries:
        if entry["matchup_id"] is not None:
            groups[entry["matchup_id"]].append(entry["roster_id"])
        # The empty slot "0" is not a player, so it never gets points.
        points.update({
            pid: pts for pid, pts in (entry.get("players_points") or {}).items()
            if pid != EMPTY_SLOT
        })
    return PastWeek(
        week=week,
        scores={e["roster_id"]: e["points"] for e in entries},
        pairs=[tuple(sorted(groups[mid])) for mid in sorted(groups) if len(groups[mid]) == 2],
        points=points,
        projections={
            item["player_id"]: item["stats"]["pts_half_ppr"]
            for item in raw["projections"]
            if item["stats"].get("pts_half_ppr") is not None
        },
        stats={item["player_id"]: item["stats"] for item in raw["stats"]},
        moves=parse_moves(raw["transactions"]),
        trades=parse_trades(raw["transactions"]),
    )
