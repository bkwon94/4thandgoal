"""
The league config: the one object that names the league, its provider, its owner, its timezone, and its sizes.
The CLI and the API entry build it once with cornerstone_config and pass it down, so no module reads a global.
"""
from pathlib import Path
from typing import Literal
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict


class LeagueConfig(BaseModel):
    """The identity and the sizes of one league. A second league gets a second literal, not a second set of constants.

    The sizes are the numbers that change with the team count or the league calendar. The tunables keep the
    algorithm settings, which stay the same for any league.
    """

    model_config = ConfigDict(frozen=True)

    # The short name of the league in code and in logs.
    slug: str
    # The name of the league that a person reads.
    display_name: str
    # The name of the provider the league data comes from. Sleeper is the one provider today.
    provider: Literal["sleeper"]
    # The provider gives the league a new id each season, so the id is per season.
    # The pairs are (season, league id). A frozen model still lets a caller change a dict in place, and pydantic
    # turns a read-only mapping back into a dict, so the field is a tuple.
    league_ids: tuple[tuple[int, str], ...]
    # The provider username of the owner. The parse flags the owner's team with it.
    owner_username: str
    # The IANA name of the league timezone. The trade cutoffs, the fetch times, and the daily limits read it.
    timezone: str
    # The folder of the prompt files that the writer and the verifier send to Claude.
    # Every prompt read takes this folder: the writer, the verifier, the analysis, the finder reasons, and the research.
    prompts_dir: Path

    # Standing: a contender holds a playoff spot by record, and a seller is far out of the last spot.
    # The count of playoff spots. The league ranks by wins, then by points for. The weekly facts read it too.
    playoff_spots: int
    # A seller has more than this many wins fewer than the team in the last playoff spot.
    # The league scores a median game each week, so each week gives two results, and two games are one week of
    # results.
    seller_gap: int
    # The last week of the regular season. When the side gets a player who is due back by this week,
    # the trade is a return bet.
    return_by_week: int
    # The count of top seeds that get a bye. The bracket gives seeds 1 and 2 a bye in week 15.
    bye_count: int
    # The season edges. The regular season ends at week 14. The playoff bracket, not the round robin, decides later
    # weeks.
    last_regular_week: int
    # The last week of the NFL fantasy season. A waiver add plays the fantasy playoffs too, so his rest of
    # season projection runs to this week.
    last_season_week: int
    # The line: the last position rank a starter can hold. GLOSSARY.md, "The line". A starting slot with a player
    # below the line is a hole. The league has 12 teams. Each starts 2 RB and 2 WR, and the 2 flex spots take about
    # one more of each, so 36 backs and 36 receivers start each week.
    line_rb_wr: int
    # Each of the 12 teams starts 1 QB and 1 TE. Rank 24 covers one starter and one backup per team.
    line_qb_te: int
    # Strength: the position rank a RB1, RB2, WR1, or WR2 starter must hold or beat to count. GLOSSARY.md, "Strength".
    # The 12 teams each start 2 RB and 2 WR, so rank 24 is the last back or receiver an average team starts at RB2
    # or WR2.
    strength_rank: int
    # Upside: a star is a player in the top of his position on the league's chart, by this count. GLOSSARY.md, "Star".
    # The counts are the starter tier of a 12-team one-QB league: 1 QB, 2 RB, 2 WR, and 1 TE per team, with the top
    # half of each tier. The chart is a one-QB chart and ranks QBs low, so an overall rank misses them. A position not
    # in the map has no stars.
    star_rank_by_position: dict[str, int]

    @property
    def lines(self) -> dict[str, int]:
        """The line at each ranked position. GLOSSARY.md, "The line".

        K and DEF have no line, so their slots are never holes.
        """
        return {"QB": self.line_qb_te, "RB": self.line_rb_wr, "WR": self.line_rb_wr, "TE": self.line_qb_te}

    @property
    def tz(self) -> ZoneInfo:
        """The league timezone as a ZoneInfo, so a caller can make an aware datetime with it."""
        return ZoneInfo(self.timezone)

    def league_id(self, season: int) -> str:
        """The provider league id of `season`. A season with no id stops the fetch with a plain message."""
        ids = dict(self.league_ids)
        if season not in ids:
            raise ValueError(f"No league id for season {season}. Add it to the league config.")
        return ids[season]

    @property
    def current_league_id(self) -> str:
        """The league id of the latest season. A live fetch uses it, because it learns the season from the reply."""
        return max(self.league_ids)[1]


def cornerstone_config() -> LeagueConfig:
    """The config of the Cornerstone league."""
    return LeagueConfig(
        slug="cornerstone",
        display_name="Cornerstone League",
        provider="sleeper",
        league_ids=((2026, "1386167364424318976"),),
        owner_username="bkwon",
        timezone="America/New_York",
        prompts_dir=Path(__file__).parent / "prompts",
        playoff_spots=6,
        seller_gap=2,
        return_by_week=14,
        bye_count=2,
        last_regular_week=14,
        last_season_week=17,
        line_rb_wr=36,
        line_qb_te=24,
        strength_rank=24,
        star_rank_by_position={"QB": 6, "RB": 12, "WR": 12, "TE": 6},
    )
