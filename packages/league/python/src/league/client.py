"""
The client: the values of clients/<slug>/client.toml with their check and exported JSON Schema, and the League settings.
The CLI and the API entry build the Client once with load_client and pass it down, so no module reads a global.
"""
import json
import tomllib
from collections.abc import Callable
from pathlib import Path
from typing import Literal, Self
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator

from league.league_settings import LeagueSettings
from league.paths import client_dir, league_file, nfl_dir

# The exported schema of the model. "make schema" writes it, and a rule test fails when it is stale.
CLIENT_SCHEMA = Path(__file__).parent / "client.schema.json"
CLIENT_FILE = "client.toml"

# The packages a client chooses. league, facts, and design are in every client, so the list never names them.
PackageName = Literal["week", "rankings", "managers", "waiver", "analyzer"]


class ClientError(ValueError):
    """A client file that is missing or breaks a rule. The message names the file and the bad value."""


class _Strict(BaseModel):
    # An unknown key fails, so a typo never passes as a default.
    model_config = ConfigDict(extra="forbid", frozen=True)


class Season(_Strict):
    """The provider and the league id of one season. The provider gives the league a new id each season."""
    provider: Literal["sleeper"]
    league_id: str


class LeagueValues(_Strict):
    """The package values of league. The default is no chart, and then each chart value is 0."""
    chart: str | None = None


class WeekValues(_Strict):
    """The package values of week. It has none yet."""


class RankingsValues(_Strict):
    """The package values of rankings. It has none yet."""


class ManagersValues(_Strict):
    """The package values of managers. It has none yet."""


class WaiverValues(_Strict):
    """The package values of waiver. It has none yet."""


class AnalyzerValues(_Strict):
    """The package values of analyzer. The finder is off by default."""
    finder: bool = False


class PackageValues(_Strict):
    """The [values.<package>] tables. A client sets only the values that differ from the defaults."""
    league: LeagueValues = Field(default_factory=LeagueValues)
    week: WeekValues = Field(default_factory=WeekValues)
    rankings: RankingsValues = Field(default_factory=RankingsValues)
    managers: ManagersValues = Field(default_factory=ManagersValues)
    waiver: WaiverValues = Field(default_factory=WaiverValues)
    analyzer: AnalyzerValues = Field(default_factory=AnalyzerValues)


class MenuItem(_Strict):
    """One menu item: the home page or one package of the list, with an optional label."""
    page: Literal["home"] | None = None
    package: PackageName | None = None
    label: str | None = None

    @model_validator(mode="after")
    def _one_target(self) -> Self:
        if (self.page is None) == (self.package is None):
            raise ValueError("A menu item names one of page or package.")
        return self


class Menu(_Strict):
    """The menu layout and its items. With no items, the menu takes the package list in its order."""
    layout: Literal["hamburger", "bar", "tabs"] = "hamburger"
    items: list[MenuItem] | None = None


class ClientValues(_Strict):
    """The values of one client. The seasons, the timezone, and the package list are required."""
    packages: list[PackageName]
    # The IANA name of the league timezone. The trade cutoffs, the fetch times, and the daily limits read it.
    timezone: str
    # The code of the usage count. With none, the site loads no count script.
    usage_code: str | None = None
    seasons: dict[int, Season] = Field(min_length=1)
    values: PackageValues = Field(default_factory=PackageValues)
    menu: Menu = Field(default_factory=Menu)

    @field_validator("timezone")
    @classmethod
    def _known_timezone(cls, name: str) -> str:
        try:
            ZoneInfo(name)
        except (ZoneInfoNotFoundError, ValueError):
            raise ValueError(f"{name} is not an IANA timezone name.") from None
        return name

    @model_validator(mode="after")
    def _menu_names_taken_packages(self) -> Self:
        for item in self.menu.items or []:
            if item.package is not None and item.package not in self.packages:
                raise ValueError(f"The menu item for {item.package} names a package that is not in the package list.")
        return self

    @property
    def menu_items(self) -> list[MenuItem]:
        """The items of the menu, or one item per package of the list when the menu sets none."""
        if self.menu.items is not None:
            return self.menu.items
        return [MenuItem(package=name) for name in self.packages]

    @property
    def latest_season(self) -> int:
        return max(self.seasons)

    @classmethod
    def from_toml_text(cls, text: str, path: Path) -> "ClientValues":
        """The values of the TOML text of `path`. A bad file raises ClientError with the file and each bad value."""
        try:
            data = tomllib.loads(text)
        except tomllib.TOMLDecodeError as err:
            raise ClientError(f"{path} is not valid TOML: {err}") from None
        try:
            return cls.model_validate(data)
        except ValidationError as err:
            raise ClientError(f"{path} breaks a rule:\n" + "\n".join(_lines(err))) from None


def _lines(err: ValidationError) -> list[str]:
    """One plain line per broken rule: the key path and the reason, with no pydantic text."""
    out = []
    for error in err.errors():
        where = ".".join(str(part) for part in error["loc"])
        reason = error["msg"].removeprefix("Value error, ")
        if error["type"] == "extra_forbidden":
            reason = "is not a known key"
        elif error["type"] == "missing":
            reason = "is required"
        out.append(f"- {where}: {reason}" if where else f"- {reason}")
    return out


def read_client_values(folder: Path) -> ClientValues:
    """The checked values of the client folder `folder`. A missing or bad file raises ClientError."""
    path = folder / CLIENT_FILE
    if not path.is_file():
        raise ClientError(f"No {CLIENT_FILE} for the client {folder.name} at {path}.")
    return ClientValues.from_toml_text(path.read_text(encoding="utf-8"), path)


def client_schema() -> dict:
    """The JSON Schema of the client values, as the site build reads it."""
    return ClientValues.model_json_schema()


def _schema_text() -> str:
    return json.dumps(client_schema(), indent=2) + "\n"


def write_schema_file(path: Path = CLIENT_SCHEMA) -> Path:
    """Write the exported JSON Schema of the client values."""
    path.write_text(_schema_text(), encoding="utf-8")
    return path


def check_schema_file(path: Path = CLIENT_SCHEMA) -> None:
    """Raise ClientError when the schema file at `path` differs from the model, so a stale export fails the check."""
    if not path.is_file() or path.read_text(encoding="utf-8") != _schema_text():
        raise ClientError(f"The schema file {path} is stale. Run make schema in packages/league/python and commit the file.")


class Client(BaseModel):
    """One league and its site: the folder of the client, its values, and the League settings of the season of the
    run. GLOSSARY.md, "Client". The sizes come from the provider, so a typed size never disagrees with the league.
    """

    model_config = ConfigDict(frozen=True)

    # The short name of the client in code, in paths, and in logs.
    slug: str
    # The client folder clients/<slug>, which holds client.toml, prompts/, and data/.
    folder: Path
    # The shared NFL data folder data/nfl, outside each client: the caches and the Returns file.
    nfl_dir: Path
    values: ClientValues
    settings: LeagueSettings

    @property
    def tz(self) -> ZoneInfo:
        """The league timezone as a ZoneInfo, so a caller can make an aware datetime with it."""
        return ZoneInfo(self.values.timezone)

    @property
    def chart(self) -> str | None:
        """The trade value chart of the client, the package value `chart` of league. None is no chart."""
        return self.values.values.league.chart

    @property
    def voice_dir(self) -> Path:
        """The prompts folder of the client. Its tone.md and vocabulary.md replace the default voice."""
        return self.folder / "prompts"

    def league_id(self, season: int) -> str:
        """The provider league id of `season`. A season with no id stops the fetch with a plain message."""
        if season not in self.values.seasons:
            raise ValueError(f"No league id for season {season}. Add [seasons.{season}] to {self.folder / CLIENT_FILE}.")
        return self.values.seasons[season].league_id

    @property
    def current_league_id(self) -> str:
        """The league id of the latest season. A live fetch uses it, because it learns the season from the reply."""
        return self.values.seasons[self.values.latest_season].league_id


# The provider fetch of the League settings: the league id and the cache file of the season.
SettingsFetch = Callable[[str, Path], LeagueSettings]


def load_client(root: Path, slug: str, season: int, fetch_settings: SettingsFetch) -> Client:
    """The client `slug` under the repo root `root`, with the League settings of `season`.

    A missing or bad client.toml, or a season the file does not name, raises ClientError.
    """
    folder = client_dir(root, slug)
    values = read_client_values(folder)
    if season not in values.seasons:
        raise ClientError(f"{folder / CLIENT_FILE} has no [seasons.{season}].")
    settings = fetch_settings(values.seasons[season].league_id, league_file(folder, season))
    return Client(slug=slug, folder=folder, nfl_dir=nfl_dir(root), values=values, settings=settings)
