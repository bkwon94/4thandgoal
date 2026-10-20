"""
Domain models for one week of the league.
They are plain data, so the rest of the code does not read raw Sleeper JSON.
"""
from datetime import date, datetime
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
    # The Sleeper designation, such as "Out", as of the time the players blob was fetched.
    injury_status: str | None = None
    injury_body_part: str | None = None


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


class DraftPick(BaseModel):
    season: str
    round: int
    roster_id: int
    previous_owner_id: int
    owner_id: int


class Trade(BaseModel):
    transaction_id: str
    # The aware time of Sleeper's epoch milliseconds.
    created: datetime
    roster_ids: list[int]
    # Player id to the roster that got him, and player id to the roster that gave him.
    adds: dict[str, int]
    drops: dict[str, int]
    draft_picks: list[DraftPick]


class PastWeek(BaseModel):
    week: int
    scores: dict[int, float]
    # Sorted roster id pairs. A lone entry, such as a bye, is not a pair.
    pairs: list[tuple[int, int]]
    # The points of every player of every roster, keyed by player id.
    points: dict[str, float]
    projections: dict[str, float]
    stats: dict[str, dict[str, float]]
    moves: list[Move]
    trades: list[Trade] = []


class History(BaseModel):
    week: int
    weeks: dict[int, PastWeek]

    def complete(self) -> bool:
        """True when every week from 1 to the current week is present."""
        return all(w in self.weeks for w in range(1, self.week + 1))


class Week(BaseModel):
    season: int
    week: int
    teams: dict[int, Team]
    matchups: list[Matchup]
    next_matchups: list[tuple[int, int]]
    moves: list[Move]
    last_scored_week: int
    season_start: date
    # Lineup lines a full roster holds: the roster positions plus the reserve slots.
    roster_slots: int = 0
    # The league scoring rates and the Sleeper stats of the week, keyed by player id.
    scoring: dict[str, float] = {}
    stats: dict[str, dict[str, float]] = {}


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
    key: Literal["game_changer", "top_scorer", "mvb", "underperformer", "overachiever", "butterfingers"]
    line: PlayerLine
    roster_id: int
    matchup_id: int
    reason: str
    skipped: list[str]


class DropLine(BaseModel):
    player_id: str
    roster_id: int
    matchup_id: int
    drops: int
    targets: int | None
    # value and end_zone are None when nflverse is down, because only nflverse has the plays.
    value: float | None
    end_zone: int | None


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
    # Points for per week over weeks 1 to N, and the mean of the last 3 weeks.
    average: float = 0.0
    trend: float | None = None
    # Head-to-head results: positive counts wins, negative counts losses, a tie ends it.
    streak: int = 0


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
    # Keys such as "T1.4" that the writer grades. Only the trades chapter sets them.
    grade_keys: list[str] = []


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
    trades: list[Trade] = []
    drops: list[DropLine] = []
    drop_source: Literal["nflverse", "sleeper", "none"] = "none"


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
    # Keyed by T{n}.{rid}: one roster can make several trades in a week.
    grades: dict[str, str] = {}


class WriterOut(BaseModel):
    """The structured output of one writer call."""

    sentences: list[Sentence]


class Grade(BaseModel):
    key: str
    letter: str


class TradesWriterOut(WriterOut):
    """The Trades output. A list keeps the structured output schema to fixed keys."""

    grades: list[Grade] = []


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


class BuildRecord(BaseModel):
    """When a build started and which data sources it had. A false source was missing or incomplete."""

    started: datetime
    sources: dict[str, bool]
    # The fetch time of this week's transactions.json. It is the end of the trade window.
    fetched: datetime | None = None


class VerifyFile(BaseModel):
    """The content of verify.json. A version 1 file has no build record."""

    build: BuildRecord | None = None
    chapters: dict[str, list[VerifyResult]]


class DropPlay(BaseModel):
    game_id: str
    play_id: str
    air_yards: float
    yardline_100: float


class NflverseWeek(BaseModel):
    # sources says which of the four files gave data, so a chapter can say what it lacks.
    sources: dict[str, bool]
    gsis: dict[str, str]
    # None means the source gave no data for the week. An empty dict means no player matched.
    drops: dict[str, list[DropPlay]] | None
    injuries: dict[str, dict[int, str]] | None
