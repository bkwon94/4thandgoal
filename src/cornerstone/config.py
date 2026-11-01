"""
The league config: the one object that names the league, its provider, its owner, and its timezone.
The CLI and the API entry build it once with cornerstone_config and pass it down, so no module reads a global.
"""
from pathlib import Path
from typing import Literal
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict


class LeagueConfig(BaseModel):
    """The identity of one league. A second league gets a second literal, not a second set of constants."""

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
    # Nothing reads it yet. Pipeline ticket 15 threads it into load_prompt for the writer, the verifier, the analysis,
    # the finder reasons, and the research.
    prompts_dir: Path

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
    )
