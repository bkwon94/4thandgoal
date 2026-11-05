"""
The League settings: the sizes of one season of a league that the provider gives, and the sizes that derive from them.
The provider adapter maps its own settings into this model, so no other module reads a provider field name.
"""
import math
from collections import Counter
from functools import cached_property

from pydantic import BaseModel, ConfigDict

# The positions with a line, a strength rank, and a star rank. K and DEF have none, so their slots are never holes.
RANKED_POSITIONS = ("QB", "RB", "WR", "TE")
# A FLEX slot takes a RB, a WR, or a TE. In practice it takes about one back or one receiver, so each FLEX slot
# counts half a RB slot and half a WR slot.
FLEX_SLOT = "FLEX"
FLEX_SHARE = {"RB": 0.5, "WR": 0.5}
# The positions a FLEX slot takes. A league that starts a TE only through a FLEX slot still starts a TE.
FLEX_POSITIONS = ("RB", "WR", "TE")
# Every position the sizes know, in lineup order. The position lists of a league keep this order.
LINEUP_POSITIONS = (*RANKED_POSITIONS, "K", "DEF")
# The slots that are no starter slot.
BENCH_SLOTS = frozenset({"BN", "IR", "TAXI"})
# The starter slots the sizes know. Another slot, such as SUPER_FLEX, stops the build with a plain message.
KNOWN_SLOTS = frozenset({*RANKED_POSITIONS, FLEX_SLOT, "K", "DEF"})
# The reception points of each points key of a projection. Each key uses 4-point passing touchdowns.
POINTS_KEYS = {0.0: "pts_std", 0.5: "pts_half_ppr", 1.0: "pts_ppr"}
# The points key of a parse with no League settings, such as a test of the CPC fixtures, which score half PPR.
# Each build and each live fetch passes the points key of its League settings.
DEFAULT_POINTS_KEY = POINTS_KEYS[0.5]


def playoff_rounds(playoff_spots: int) -> int:
    """The rounds of the playoff bracket. The bracket has one round per week, and each round halves the field."""
    return math.ceil(math.log2(playoff_spots)) if playoff_spots > 1 else 0


def bracket_byes(playoff_spots: int) -> int:
    """The count of top seeds that get a bye: the gap from the playoff spots to the next full bracket.
    Six spots fill a bracket of eight, so seeds 1 and 2 get a bye."""
    return 2 ** playoff_rounds(playoff_spots) - playoff_spots


def star_ranks(team_count: int, roster_slots: tuple[str, ...]) -> dict[str, int]:
    """The top count of each position on the chart that is a star: the top half of the starter tier, flex aside.
    GLOSSARY.md, "Star". A position with no slot has no stars."""
    counts = Counter(roster_slots)
    return {p: team_count * counts[p] // 2 for p in RANKED_POSITIONS if counts[p]}


class LeagueSettings(BaseModel):
    """The settings of one season: the team count, the playoff spots, the roster slots, the weeks of the regular
    season, the reception points, and the median game. GLOSSARY.md, "League settings".
    """

    model_config = ConfigDict(frozen=True)

    # The count of teams in the league. The parse stops when the roster count of a league file differs.
    team_count: int
    # The count of playoff spots. The league ranks by wins, then by points for.
    playoff_spots: int
    # The count of top seeds that get a bye. The adapter derives it with bracket_byes.
    bye_count: int
    # The star count of each position on the chart. The adapter derives it with star_ranks.
    star_rank_by_position: dict[str, int]
    # The starter slots of a lineup, in the provider order, with no bench slot.
    roster_slots: tuple[str, ...]
    # The last week of the regular season. The playoff bracket, not the round robin, decides later weeks.
    last_regular_week: int
    # The points for one reception: 0, 0.5, or 1.
    reception_points: float
    # True when the league scores a second game each week, against the median score. GLOSSARY.md, "Median game".
    median_game: bool

    def model_post_init(self, context: object) -> None:
        unknown = sorted(set(self.roster_slots) - KNOWN_SLOTS)
        if unknown:
            raise ValueError(f"The roster slot {', '.join(unknown)} is not one the sizes know. "
                             f"The known starter slots are {', '.join(sorted(KNOWN_SLOTS))}.")
        if self.reception_points not in POINTS_KEYS:
            raise ValueError(f"The league gives {self.reception_points} points per reception. "
                             "The projections know only 0, 0.5, and 1.")

    @property
    def points_key(self) -> str:
        """The projection key of the reception points: pts_std, pts_half_ppr, or pts_ppr."""
        return POINTS_KEYS[self.reception_points]

    @property
    def positions(self) -> tuple[str, ...]:
        """The positions the league starts, in lineup order: each position with a slot, through a FLEX slot too.

        They set the waiver pool and the leader boards, so a position the league never starts, such as K in CPC,
        is out of both.
        """
        slots = set(self.roster_slots)
        started = slots | (set(FLEX_POSITIONS) if FLEX_SLOT in slots else set())
        return tuple(position for position in LINEUP_POSITIONS if position in started)

    def _slots(self, position: str) -> float:
        """The starter slots of `position`, with its share of each FLEX slot."""
        counts = Counter(self.roster_slots)
        return counts[position] + FLEX_SHARE.get(position, 0) * counts[FLEX_SLOT]

    @property
    def _playoff_rounds(self) -> int:
        return playoff_rounds(self.playoff_spots)

    @property
    def last_season_week(self) -> int:
        """The last week of the fantasy season: the last regular week plus one week per playoff round. A waiver add
        plays the fantasy playoffs too, so his rest of season projection runs to this week."""
        return self.last_regular_week + self._playoff_rounds

    @property
    def return_by_week(self) -> int:
        """The last week of the regular season. When the side gets a player who is due back by this week, the trade
        is a return bet."""
        return self.last_regular_week

    # The settings are frozen, so the lines never change. The finder reads them for each player of each graded trade,
    # so they build once per settings object. cached_property writes to the instance dict, which a frozen model
    # allows, and no code may change the dict it returns.
    @cached_property
    def lines(self) -> dict[str, int]:
        """The line at each ranked position: the last position rank a starter can hold. GLOSSARY.md, "The line".

        A RB or WR line covers each starter slot, with its share of the FLEX slots. A QB or TE line covers one
        starter and one backup per team.
        """
        out = {}
        for position in RANKED_POSITIONS:
            per_team = self._slots(position) if position in FLEX_SHARE else 2 * self._slots(position)
            out[position] = int(self.team_count * per_team)
        return out

    @property
    def strength_rank(self) -> int:
        """The position rank a RB1, RB2, WR1, or WR2 starter must hold or beat to count. GLOSSARY.md, "Strength".
        It is the last back or receiver an average team starts at RB2 or WR2."""
        return self.team_count * int(min(Counter(self.roster_slots)[p] for p in ("RB", "WR")))

    @property
    def grade_spare_rank(self) -> dict[str, int]:
        """The rank of a spare at each position on the manager page. GLOSSARY.md, "Roster grade".

        The depth word of a position counts a spare only inside the league's starter count at the position, flex
        aside. Two spares read "stacked", one reads "deep", none reads "fine".
        """
        counts = Counter(self.roster_slots)
        return {p: counts[p] * self.team_count for p in RANKED_POSITIONS}

    @property
    def grade_strong_rank(self) -> int:
        """The slot rank that reads "strong" in the grade sentence: the top quarter, which rounds down."""
        return self.team_count // 4

    @property
    def grade_soft_rank(self) -> int:
        """The slot rank that reads "soft" in the grade sentence: the bottom quarter, which rounds down."""
        return self.team_count - self.team_count // 4 + 1
