"""
Domain models for one week of the league.
They are plain data, so the rest of the code does not read raw Sleeper JSON.
"""
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from typing import Literal

from pydantic import BaseModel


def r2(x: float) -> float:
    """Round half up to two decimals. Python's round() gives 2.78 for 2.785."""
    return float(Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def sub(a: float, b: float) -> float:
    """Subtract on exact decimals, then round half up. Float subtraction drifts."""
    return r2(float(Decimal(str(a)) - Decimal(str(b))))


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


class MatchupFacts(BaseModel):
    matchup_id: int
    winner: int | None
    loser: int | None
    score_w: float
    score_l: float
    margin: float
    top_scorer: dict[int, PlayerLine]
    drivers: list[PlayerLine]
    swing: list[PlayerLine]
    bench_regret: list[tuple[PlayerLine, PlayerLine]]
    recent_moves: list[Move]


class MedianFacts(BaseModel):
    median: float
    above: list[int]
    below: list[int]
    closest_above: tuple[int, float]
    closest_below: tuple[int, float]


class Standing(BaseModel):
    rank: int
    roster_id: int
    wins: int
    losses: int
    points_for: float
    in_playoffs: bool
    # Wins minus the wins of sixth place. A positive number is above the cut.
    games_from_cut: int
    schedule_strength: float | None
    strength_rank: int | None


class Award(BaseModel):
    key: Literal["game_changer", "top_scorer", "mvb", "underperformer", "overachiever"]
    line: PlayerLine
    roster_id: int
    matchup_id: int
    reason: str
    skipped: list[str]


class Pick(BaseModel):
    matchup_id: int
    reason: Literal["Closest Finish", "Upset", "Top of the Table", "Playoff Stakes"]
    scores: dict[str, float]


class NextMatchup(BaseModel):
    a: int
    b: int
    must_watch: bool
    reason: str | None


class SeasonHistory(BaseModel):
    roster_id: int
    high: float
    low: float
    # Keyed by 100, 110, and 120.
    weeks_over: dict[int, int]
    new_high: bool
    new_low: bool


class PositionRank(BaseModel):
    player_id: str
    position: str
    rank: int
    of: int


class Fact(BaseModel):
    id: str
    text: str
    # Every number in text, as written on the page.
    numbers: list[str]
    teams: list[str]
    players: list[str]


class Chapter(BaseModel):
    key: str
    title: str
    fact_ids: list[str]
    scope_teams: list[str]
    scope_players: list[str]
    min_sentences: int
    max_sentences: int


class WeekData(BaseModel):
    season: int
    week: int
    dates: str
    publish_date: str
    teams: dict[int, Team]
    matchups: list[MatchupFacts]
    median: MedianFacts
    table: list[Standing]
    awards: list[Award]
    pick: Pick
    next: list[NextMatchup]
    history: list[SeasonHistory]
    ranks: list[PositionRank]


class FactSheet(BaseModel):
    facts: dict[str, Fact]
    chapters: list[Chapter]


class Bundle(BaseModel):
    data: WeekData
    sheet: FactSheet


class Sentence(BaseModel):
    text: str
    fact_ids: list[str]


class Blurb(BaseModel):
    chapter: str
    sentences: list[Sentence]
    attempt: int
    fallback: bool


class WriterOut(BaseModel):
    """The structured output of one writer call."""

    sentences: list[Sentence]


class Verdict(BaseModel):
    index: int
    supported: bool
    reason: str


class VerifyOut(BaseModel):
    """The structured output of one verifier call."""

    verdicts: list[Verdict]


class VerifyResult(BaseModel):
    chapter: str
    code_failures: list[str]
    verdicts: list[Verdict]
    passed: bool
