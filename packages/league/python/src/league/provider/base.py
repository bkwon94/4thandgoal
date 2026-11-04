"""
The Provider protocol: the six fetches that every league data service gives.
Each fetch returns the raw models or the League settings, so the rest of the pipeline never reads a provider field name.
"""
from datetime import datetime
from pathlib import Path
from typing import Protocol, runtime_checkable
from zoneinfo import ZoneInfo

from league.league_settings import LeagueSettings
from league.provider.raw import RawAheadWeek, RawPastWeek, RawWeek


# runtime_checkable lets a test check a fake with isinstance. It checks only that the six names exist.
# Each fetch takes the league id and not the client, because the provider sits under the client. Its one model import
# is the League settings, which the adapter maps into. The caller reads the id from the client. The last regular week
# and the last season week come the same way, as plain numbers from the League settings.
@runtime_checkable
class Provider(Protocol):
    def fetch_week(
            self, league_id: str, season: int, week: int, raw_dir: Path, players_cache: Path, tz: ZoneInfo,
            last_regular_week: int, last_season_week: int) -> RawWeek:
        """Save the raw files of `week` into `raw_dir` and give them back. The fetch time is in the timezone `tz`.

        The schedule runs to `last_regular_week`, and the projections ahead run to `last_season_week`.
        """
        ...

    def fetch_settings(self, league_id: str, cache: Path) -> LeagueSettings:
        """The League settings of the season of `league_id`. The league file at `cache` keeps them between runs."""
        ...

    def fetch_live(self, league_id: str, players_cache: Path) -> tuple[RawWeek, datetime]:
        """The raw data of the league now, and the aware time the rosters came back. It saves no weekly file."""
        ...

    def fetch_past_leg(self, league_id: str, season: int, week: int, out_dir: Path) -> RawPastWeek:
        """Save the history files of the past `week` into `out_dir` and give them back."""
        ...

    def fetch_players(self, players_cache: Path) -> dict[str, dict]:
        """The players file by player id. The cache file keeps it between fetches."""
        ...

    def fetch_projections(self, season: int, week: int, last_regular_week: int) -> list[RawAheadWeek]:
        """The projections of each week ahead of `week` that the trade grade reads, through `last_regular_week`."""
        ...
