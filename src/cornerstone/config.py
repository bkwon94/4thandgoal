"""
The league config: the one object that names the league, its provider, its owner, and its timezone.
The CLI and the API entry build it once with cornerstone_config and pass it down, so no module reads a global.
"""
from pathlib import Path
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict


class LeagueConfig(BaseModel):
    """The identity of one league. A second league gets a second literal, not a second set of constants."""

    model_config = ConfigDict(frozen=True)

    slug: str
    display_name: str
    # The name of the provider the league data comes from.
    provider: str
    # The provider gives the league a new id each season, so the id is per season.
    league_ids: dict[int, str]
    # The provider username of the owner. The parse flags the owner's team with it.
    owner_username: str
    # The IANA name of the league timezone. The trade cutoffs, the fetch times, and the daily limits read it.
    timezone: str
    prompts_dir: Path

    @property
    def tz(self) -> ZoneInfo:
        return ZoneInfo(self.timezone)

    def league_id(self, season: int) -> str:
        """The provider league id of `season`. A season with no id stops the fetch with a plain message."""
        if season not in self.league_ids:
            raise ValueError(f"No league id for season {season}. Add it to the league config.")
        return self.league_ids[season]

    @property
    def current_league_id(self) -> str:
        """The league id of the latest season. A live fetch uses it, because it learns the season from the reply."""
        return self.league_ids[max(self.league_ids)]


def cornerstone_config() -> LeagueConfig:
    """The config of the Cornerstone league."""
    return LeagueConfig(
        slug="cornerstone",
        display_name="Cornerstone League",
        provider="sleeper",
        league_ids={2026: "1386167364424318976"},
        owner_username="bkwon",
        timezone="America/New_York",
        prompts_dir=Path(__file__).parent / "prompts",
    )
