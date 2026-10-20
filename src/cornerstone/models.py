"""
Domain models for one week of the league.
They are plain data, so the rest of the code does not read raw Sleeper JSON.
"""
from datetime import date
from typing import Literal

from pydantic import BaseModel


class Team(BaseModel):
    roster_id: int
    name: str
    owner: str
    avatar_url: str | None
    wins: int
    losses: int
    points_for: float
    is_brian: bool


class PlayerLine(BaseModel):
    player_id: str
    name: str
    position: str
    nfl_team: str | None
    points: float
    projection: float | None
    season_avg: float | None
    started: bool
    slot: str | None


class Side(BaseModel):
    roster_id: int
    points: float
    lines: list[PlayerLine]


class Matchup(BaseModel):
    matchup_id: int
    a: Side
    b: Side


class Move(BaseModel):
    player_id: str
    roster_id: int
    kind: Literal["waiver", "free_agent", "trade"]
    week: int
    bid: int | None


class Week(BaseModel):
    season: int
    week: int
    teams: dict[int, Team]
    matchups: list[Matchup]
    next_matchups: list[tuple[int, int]]
    moves: list[Move]
    last_scored_week: int
    season_start: date
