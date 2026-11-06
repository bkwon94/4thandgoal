"""
The raw provider shapes: one pydantic model per raw file, at the HTTP call.
The protocol and the Sleeper adapter both read them, so the protocol does not depend on the adapter.
"""
from pydantic import BaseModel, ConfigDict


# The raw Sleeper shapes. The field names are the Sleeper names, so a reader sees the same key as in the file.
# Each model holds only the fields the code reads. A field the code does not read stays as an extra, because the
# raw files are saved as Sleeper sends them and a dump must give the file back.
class _Raw(BaseModel):
    model_config = ConfigDict(extra="allow")


class RawState(_Raw):
    """The NFL state: the season and the week that Sleeper shows."""
    season: str
    display_week: int
    season_start_date: str


class RawLeagueSettings(_Raw):
    """The settings object of league.json: the scored week, the reserve slots, the waiver budget, and the sizes."""
    last_scored_leg: int
    reserve_slots: int
    waiver_budget: int
    # The sizes of the League settings. A saved file of an old test or fixture can lack them, so each is optional, and
    # the map into the League settings stops on a missing one.
    num_teams: int | None = None
    playoff_teams: int | None = None
    playoff_week_start: int | None = None
    # 1 when the league scores a median game each week, else 0.
    league_average_match: int = 0


class RawLeague(_Raw):
    """The league from league.json: the lineup slots, the settings, and the scoring."""
    roster_positions: list[str]
    settings: RawLeagueSettings
    scoring_settings: dict[str, float]


class UserMetadata(_Raw):
    # A user who set no team name or avatar has no such key.
    team_name: str | None = None
    avatar: str | None = None


class RawUser(_Raw):
    """One user of the league from users.json."""
    user_id: str
    display_name: str
    avatar: str | None = None
    metadata: UserMetadata | None = None


class RosterSettings(_Raw):
    """The settings object of one roster in rosters.json: the record, the points, and the waiver state."""
    fpts: int
    # Sleeper leaves out the decimal part of a roster with no points.
    fpts_decimal: int = 0
    wins: int
    losses: int
    waiver_budget_used: int
    waiver_position: int


class RawRoster(_Raw):
    """One roster of the league from rosters.json."""
    roster_id: int
    owner_id: str
    # A roster with no players has None in rosters.json.
    players: list[str] | None
    settings: RosterSettings


class RawMatchup(_Raw):
    """One roster in one week. Two rows with the same matchup_id are a pair. A bye has matchup_id None."""
    roster_id: int
    matchup_id: int | None
    points: float
    # A saved past week can lack the lineup lists, so the parse of a past week reads them as empty.
    players: list[str] | None = None
    starters: list[str] | None = None
    players_points: dict[str, float] | None = None


class TransactionSettings(_Raw):
    waiver_bid: int | None = None


class RawTransaction(_Raw):
    """One move of one week from transactions.json: a waiver claim, a free agent pickup, or a trade."""
    transaction_id: str
    type: str
    status: str
    leg: int
    # Milliseconds since the epoch.
    created: int
    roster_ids: list[int]
    adds: dict[str, int] | None
    drops: dict[str, int] | None
    settings: TransactionSettings | None = None
    # The DraftPick domain model checks each pick, so the raw pick stays a dict.
    draft_picks: list[dict] | None = None


class RawProjection(_Raw):
    """One player's projection row for one week."""
    player_id: str
    stats: dict[str, float]


class RawStatPlayer(_Raw):
    position: str | None = None


class RawStatLine(_Raw):
    """One player's stat line for one week. A player whose game has not started has no game id yet."""
    player_id: str
    stats: dict[str, float]
    team: str | None = None
    game_id: str | None = None
    player: RawStatPlayer | None = None


class RawTrending(_Raw):
    """One row of trending.json: the adds of one player across all Sleeper leagues in the last day."""
    player_id: str
    count: int


class SchedulePair(_Raw):
    """One roster in one future week of schedule.json, with only the keys of its pair."""
    roster_id: int
    matchup_id: int | None


class RawScheduleWeek(_Raw):
    """One future week of schedule.json."""
    week: int
    matchups: list[SchedulePair]


class RawAheadWeek(_Raw):
    """The half-PPR projection of each player in one week ahead, by player id."""
    week: int
    projections: dict[str, float]


class RawBracketMatch(_Raw):
    """One match of the winners bracket from bracket.json. A dump must give back the file, so the extras stay."""
    r: int
    m: int


class RawPastWeek(_Raw):
    """The raw files of one past week that the history keeps."""
    # A test or a caller sets a field with a plain list, so an assignment goes through the model too.
    model_config = ConfigDict(extra="allow", validate_assignment=True)

    matchups: list[RawMatchup]
    transactions: list[RawTransaction]
    # A failed live stats fetch gives None, so the snapshot can name the stats stale.
    stats: list[RawStatLine] | None
    projections: list[RawProjection]

    def file_json(self, name: str) -> object:
        """The JSON of the raw file `name`, in the shape Sleeper sent it."""
        # exclude_unset keeps a default out of the dump, so a key that the file lacks stays absent.
        return self.model_dump(mode="json", exclude_unset=True, include={name})[name]


class RawWeek(RawPastWeek):
    """The whole raw set of one week: one field per raw file.

    The schedule, the projections ahead, and the trending file can be absent. An absent one leaves its field None.
    """
    state: RawState
    league: RawLeague
    users: list[RawUser]
    rosters: list[RawRoster]
    matchups_next: list[RawMatchup]
    # The players file has about 5 MB of entries in many shapes. Each reader takes the keys it needs.
    players: dict[str, dict]
    bracket: list[RawBracketMatch]
    schedule: list[RawScheduleWeek] | None = None
    projections_ahead: list[RawAheadWeek] | None = None
    trending: list[RawTrending] | None = None


class RawDraftSettings(_Raw):
    """The settings object of draft.json. An auction has a budget, and a snake has none."""
    teams: int
    rounds: int
    budget: int | None = None


class RawPickMetadata(_Raw):
    """The metadata of one pick in picks.json: the player at the time of the draft and, in an auction, the price."""
    first_name: str
    last_name: str
    position: str
    # The price in dollars as a string. Only an auction pick has it.
    amount: str | None = None


class RawDraftPick(_Raw):
    """One pick of picks.json. The roster id is the drafter, and in an auction the pick number is the order of sale."""
    pick_no: int
    round: int
    roster_id: int
    player_id: str
    metadata: RawPickMetadata


class RawDraft(_Raw):
    """The draft of a season: the type and the settings of draft.json, and the picks of picks.json."""
    type: str
    settings: RawDraftSettings
    picks: list[RawDraftPick]
