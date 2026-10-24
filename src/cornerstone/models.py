"""
Domain models for one week of the league.
They are plain data, so the rest of the code does not read raw Sleeper JSON.
"""
from datetime import date, datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Literal

from pydantic import BaseModel

from cornerstone.odds import OddsResult


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


class ChartValues(BaseModel):
    """The trade values of one chart week, keyed by Sleeper player ID.

    They come from the half-PPR redraft trade value chart for that week and never appear on the page.
    """

    week: int
    date: date
    values: dict[str, float]


class ChartRow(BaseModel):
    value: float
    name: str
    position: str


class ChartRead(BaseModel):
    """What Claude reads off the chart image: the header week and date, and the rows top to bottom."""

    week: int
    date: date
    rows: list[ChartRow]


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
    # The position and the NFL team of each player with a stat line, keyed by player id.
    positions: dict[str, str] = {}
    nfl_teams: dict[str, str] = {}


class UsageShare(BaseModel):
    """A share of the snaps or targets, in percent, over the last `weeks` weeks."""
    percent: int
    weeks: int
    # None when the player has fewer than 4 share weeks, because two windows need 4.
    direction: Literal["up", "down", "flat"] | None
    # The scored weeks with share data behind the percent. A week with no team snaps or targets is not in it.
    weeks_used: list[int]


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
    # The pairs of weeks N+2 to 14, keyed by week, in the shape of next_matchups.
    schedule: dict[int, list[tuple[int, int]]] = {}
    # The half-PPR projection of each rostered player in weeks N+1 to 14, by week and player id.
    projections_ahead: dict[int, dict[str, float]] = {}
    # The league's lineup slots, in Sleeper's order, such as QB, RB, RB, WR, and BN.
    roster_positions: list[str] = []
    # The position of each player on each current roster in rosters.json, by roster id and player id.
    rosters: dict[int, dict[str, str]] = {}


def week_lines(week: Week) -> list[PlayerLine]:
    """Every lineup line of both sides of every matchup of the week."""
    return [line for m in week.matchups for side in (m.a, m.b) for line in side.lines]


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


class DropLine(BaseModel):
    player_id: str
    roster_id: int
    matchup_id: int
    drops: int
    targets: int | None
    # value and end_zone are None when nflverse is down, because only nflverse has the plays.
    value: float | None
    end_zone: int | None


class Shootout(BaseModel):
    """An NFL game of week N+1 by Sleeper team codes, with the recent pass rate over expected of each team."""
    away: str
    home: str
    # The rates are in percentage points, from the last games of each team up to SHOOTOUT_GAMES.
    away_rate: float
    home_rate: float
    away_games: int
    home_games: int


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


class PowerRow(BaseModel):
    """One team in the power rankings of one week."""
    roster_id: int
    power_rank: int
    # Last week's power rank minus this week's, so positive is up. None in week 1.
    movement: int | None
    power_score: float
    # Keyed by component: standing, form, schedule_played, scoring. Each value is 0 to 1, each rank 1 to 12.
    values: dict[str, float]
    ranks: dict[str, int]


class PositionRank(BaseModel):
    player_id: str
    position: str
    rank: int
    of: int


class PositionLeader(BaseModel):
    """One of the three started players with the most points at one position, league wide."""
    line: PlayerLine
    position: str
    rank: int
    # The count of started players at the position, so a row can say "1st of 31".
    of: int
    roster_id: int


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
    # The fact IDs the writer must cite. The code check fails a blurb that leaves one uncited.
    required: list[str] = []


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
    # An old bundle has no leaders field.
    leaders: list[PositionLeader] = []
    trades: list[Trade] = []
    # The name of each traded player with a lineup line, by player ID. The trade card reads it.
    trade_players: dict[str, str] = {}
    drops: list[DropLine] = []
    drop_source: Literal["nflverse", "sleeper", "none"] = "none"


class FactSheet(BaseModel):
    facts: dict[str, Fact]
    chapters: list[Chapter]


class BoardScores(BaseModel):
    """The three scores of a pool player, each from 0 to 1. A score with no input stays 0."""
    usage: float = 0.0
    environment: float = 0.0
    projection: float = 0.0


class LastLike(BaseModel):
    """The most recent winning claim at a player's position this season: the player, the team, the week, the bid."""
    player_id: str
    name: str
    roster_id: int
    team: str
    week: int
    bid: int


class WaiverPrice(BaseModel):
    """The bid to win of one pool player, a whole dollar, with the fact that holds its inputs."""
    bid: int
    fact: Fact
    # None when no claim at the position won this season.
    last_like: LastLike | None
    # Per budget left in the league, the count of other rosters with more budget left than a viewer at that level
    # can bid. The site looks it up.
    outbid: dict[int, int]


# The bucket reasons: best adds, trending, the two sneaky rules, and the two stash rules.
WaiverReason = Literal["board_score", "trending", "usage_rise", "behind_injury", "return", "handcuff"]


class ResearchClaim(BaseModel):
    """One research claim on a player from the web: one sentence, its source, and its stance.

    `stance` says whether the claim backs the engine's facts, disputes them, or is plain news.
    """
    text: str
    # The search can give a claim with no URL. The research step drops it, as it has no citation.
    url: str
    source: str
    date: str
    stance: Literal["backs", "disputes", "news"]


class ResearchOut(BaseModel):
    """The output of one research call: the claims on one player."""
    claims: list[ResearchClaim]


class WaiverPlayer(BaseModel):
    """One ranked player of a bucket. The week projection is for week N+1, the rest of season one for N+1 to 17."""
    player_id: str
    name: str
    position: str
    team: str
    week_projection: float
    ros_projection: float
    scores: BoardScores
    board_score: float
    # The adds across all Sleeper leagues in the last day. 0 when he is not in the trending file.
    trending_count: int = 0
    # The facts of the player. Every digit in a fact's text is in its numbers.
    facts: list[Fact] = []
    # None for a drop, and in a facts file saved before the price.
    price: WaiverPrice | None = None
    # The roster that holds a drop candidate and the pool player who beats him. None for a pool player.
    drop: "DropInfo | None" = None
    # The code of the rule that put him in the bucket. A drop candidate keeps his reason in his own record, so his
    # reason here is None. A facts file saved before the reasons has None too.
    reason: WaiverReason | None = None
    # The bye week of his team. None when the schedules are missing or show no bye.
    bye: int | None = None
    # The Sleeper injury status, such as Out or IR. None for a healthy player.
    injury_status: str | None = None
    # The week he is back, for a player who is out. None when he is healthy or no source knows the week.
    return_week: int | None = None
    # The research claims on him. Empty for a drop, for a player past the research cap, and in an older file.
    research: list[ResearchClaim] = []


class BudgetRow(BaseModel):
    """The FAAB budget left and the waiver order of one roster."""
    roster_id: int
    budget_left: int
    waiver_order: int


class WaiverBoard(BaseModel):
    """The board of one week: the buckets by key, each in rank order, and the budget table in roster order."""
    week: int
    built: datetime
    buckets: dict[str, list[WaiverPlayer]]
    budgets: list[BudgetRow]
    # True when the search failed for every player, so the page says the experts are missing this week.
    experts_missing: bool = False


class UsageWeek(BaseModel):
    """The usage of one player in one week, from the play by play, the snap counts, and the weekly player file.

    A share is in percent. The targets and the target share come from the weekly player file when it has a row
    for him that week, and from our count of the play by play when it does not.
    """
    week: int
    # The Sleeper code of the team he played for.
    team: str
    # None when the snap counts have no row for him, such as a player with no PFR ID in the id map.
    snaps: int | None
    snap_share: int | None
    targets: int
    target_share: int
    carries: int
    carry_share: int
    # The targets and the carries at the opponent's 20-yard line or closer.
    red_zone_touches: int
    # From the nflverse weekly player file. None when the file is missing or has no row for him that week.
    # A real value can be negative or above 100, because a target behind the line of scrimmage has negative air yards.
    air_yards_share: int | None = None
    # Weighted opportunity rating, 1.5 times the target share plus 0.7 times the air yards share. None as above.
    # It is a weighted sum and not a share, so a real value can be negative or above 100.
    wopr: int | None = None


class TeamWeek(BaseModel):
    """The counts of one team's offense in one week. The environment rates come from the sums of these counts."""
    week: int
    plays: int
    passes: int
    rushes: int
    rush_successes: int
    neutral_plays: int
    neutral_passes: int
    # The sums over the plays of nflverse epa and pass_oe. A week extract saved without them reads them as 0.
    epa: float = 0.0
    pass_oe: float = 0.0

    @property
    def epa_per_play(self) -> float:
        """The mean nflverse epa of the plays."""
        return self.epa / self.plays if self.plays else 0.0

    # The waiver rates are fractions, such as 0.55. This rate is in percentage points, such as 5.1, so do not mix them.
    @property
    def pass_rate_over_expected(self) -> float:
        """The mean pass_oe of the plays, in percentage points over the dropback rate the nflverse model expects."""
        return self.pass_oe / self.plays if self.plays else 0.0


class ExpectedGame(BaseModel):
    """The expected points of one player in one game, from ffopportunity, rescaled to the league scoring."""
    week: int
    game_id: str
    expected: float


class ExpectedPoints(BaseModel):
    """The expected window of each player by Sleeper ID, and the last week the file holds in full."""
    # The week N of the build, or N-1 when the file lacks the games of the last game day of week N.
    through_week: int
    # The last games played through `through_week`, in week order. A bye is not a game.
    players: dict[str, list[ExpectedGame]]


class WaiverClaim(BaseModel):
    """One waiver claim of the season: the bid, the player, his position, the week, and whether the claim won."""
    player_id: str
    roster_id: int
    # None when the players file has no row for the player.
    position: str | None
    week: int
    bid: int
    won: bool


# The reason code of a drop candidate whose snap share fell DROP_WEEKS weeks in a row.
THREE_FALLS = "three_falls"


class DropInfo(BaseModel):
    """The roster that holds a drop candidate, the rule that put him in the bucket, and the pool player who beats him.

    A pool player has no DropInfo, so the site tells a drop candidate by it.
    """
    roster_id: int
    # The team name of the roster that holds him.
    holder: str
    reason: str = THREE_FALLS
    # The best pool player at his position by rest of season projection.
    beaten_by: str
    beaten_by_name: str
    # The rest of season projection of beaten_by minus his, per remaining week, to one decimal.
    margin: float


class Bundle(BaseModel):
    data: WeekData
    sheet: FactSheet
    # The engine's odds of the week, so the rankings file gets them without a second run.
    # None before `ODDS_FROM_WEEK`, or in a facts file with no `odds` key.
    odds: OddsResult | None = None
    # The waiver board of the week, so a rewrite writes the week file without a second run.
    # None in a facts file with no `waiver` key.
    waiver: WaiverBoard | None = None


class Sentence(BaseModel):
    text: str
    fact_ids: list[str]
    # The roster tag: the team the sentence is about. Only the rankings chapter sets it, so the season
    # file can put each sentence in its team's row.
    roster_id: int | None = None


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


class BuildRecord(BaseModel):
    """When a build started and which data sources it had. A false source was missing or incomplete."""

    started: datetime
    # An older record may also hold a "chart" key. The weekly build reads no chart.
    sources: dict[str, bool]
    # The time of the Sleeper fetch of this week's transactions.json. The page shows it and the history keeps it.
    fetched: datetime | None = None


class VerifyFile(BaseModel):
    """The content of verify.json. A version 1 file has no build record."""

    build: BuildRecord | None = None
    chapters: dict[str, list[VerifyResult]]


class DropPlay(BaseModel):
    game_id: str
    play_id: str
    air_yards: float
    # None when nflverse has no field position for the play. Such a drop is never in the end zone.
    yardline_100: float | None


class NflverseWeek(BaseModel):
    # sources says which of the four files gave data, so a chapter can say what it lacks.
    sources: dict[str, bool]
    gsis: dict[str, str]
    # None means the source gave no data for the week. An empty dict means no player matched.
    drops: dict[str, list[DropPlay]] | None
    injuries: dict[str, dict[int, str]] | None
    # The usage of the last `USAGE_SAVED_WEEKS` weeks by Sleeper ID, QB, RB, WR, and TE only. None in an
    # extract with no usage field, or when the play by play has no row for the week.
    usage: dict[str, list[UsageWeek]] | None = None
    # The offense counts of each week of the season by Sleeper team code. None as for the usage.
    environment: dict[str, list[TeamWeek]] | None = None
    # The expected points from ffopportunity. None in an extract with no expected field, or when the file is missing.
    expected: ExpectedPoints | None = None
    # The away and home Sleeper team codes of each NFL game of week N+1. None in an extract with no such field, or
    # when the schedule file is missing or has no game that week.
    next_games: list[tuple[str, str]] | None = None
