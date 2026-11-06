"""
The client: the kernel keys of clients/<slug>/client.toml, the check of each [values.<package>] table, the exported
JSON Schemas, and the League settings. The CLI and the API entry build the Client once with load_client.
"""
import inspect
import json
import tomllib
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Annotated, Any, Literal, Self, TypeVar
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, ConfigDict, Field, ValidationError, WithJsonSchema, field_validator, model_validator

from league.league_settings import LeagueSettings
from league.paths import client_dir, league_file, nfl_dir
from league.values import LeagueValues, PackageValues

# The exported schema of the kernel keys. "make schema" writes it, and a rule test fails when it is stale.
CLIENT_SCHEMA = Path(__file__).parent / "client.schema.json"
# The exported schema of the package values of one package, beside the module of its model.
VALUES_SCHEMA = "values.schema.json"
CLIENT_FILE = "client.toml"

# The package values models that an app reads, one per package. The app builds the list, because league imports
# no core package. A table of a package with no model in the list is left to the check of the app that reads it.
ValueModels = Sequence[type[PackageValues]]
V = TypeVar("V", bound=PackageValues)

# The schema of the [values] tables in the kernel schema: one table per package. The site build checks each table
# with the schema of its package, and the name of each table with the package list.
TABLES_SCHEMA = {"type": "object", "additionalProperties": {"type": "object"}}

# The packages a client chooses. league, facts, and design are in every client, so the list never names them.
PackageName = Literal["week", "rankings", "managers", "waiver", "analyzer", "sim", "midseason"]
# Each package that needs another package, with the package it needs. The midseason report ends on the sim, and the
# app wires the two, so a client that takes midseason takes sim too.
PACKAGE_NEEDS: dict[PackageName, PackageName] = {"midseason": "sim"}


class ClientError(ValueError):
    """A client file that is missing or breaks a rule. The message names the file and the bad value."""


class _Strict(BaseModel):
    # An unknown key fails, so a typo never passes as a default.
    model_config = ConfigDict(extra="forbid", frozen=True)


class Season(_Strict):
    """The provider and the league id of one season. The provider gives the league a new id each season."""
    provider: Literal["sleeper"]
    league_id: str


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
    """The menu items. The look of the site owns the navigation, so a client sets no layout (ADR 0024).
    With no items, the site build puts the home page first, then the package list."""
    items: list[MenuItem] | None = None


class ClientValues(_Strict):
    """The values of one client. The seasons, the timezone, and the package list are required."""
    packages: list[PackageName]
    # The IANA name of the league timezone. The trade cutoffs, the fetch times, and the daily limits read it.
    timezone: str
    # The code of the usage count. With none, the site loads no count script.
    usage_code: str | None = None
    seasons: dict[int, Season] = Field(min_length=1)
    # The checked [values.<package>] tables by package name. from_toml_text checks each table with the model of its
    # package and fills this key, so the kernel check never reads a table.
    package_values: Annotated[dict[str, PackageValues], WithJsonSchema(TABLES_SCHEMA)] = Field(
        default_factory=dict, alias="values")
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

    @model_validator(mode="after")
    def _each_needed_package_is_taken(self) -> Self:
        for package, needed in PACKAGE_NEEDS.items():
            if package in self.packages and needed not in self.packages:
                raise ValueError(f"The {package} package needs the {needed} package. Add {needed} to the package list.")
        return self

    @property
    def latest_season(self) -> int:
        return max(self.seasons)

    def package(self, model: type[V]) -> V:
        """The checked package values of the package of `model`. A package off the list has none, so a KeyError."""
        values = self.package_values[model.package]
        assert isinstance(values, model)
        return values

    @classmethod
    def from_toml_text(cls, text: str, path: Path, models: ValueModels) -> "ClientValues":
        """The values of the TOML text of `path`, with each table checked by its model in `models`.

        A bad file raises ClientError with the file and each bad value.
        """
        try:
            data = tomllib.loads(text)
        except tomllib.TOMLDecodeError as err:
            raise ClientError(f"{path} is not valid TOML: {err}") from None
        tables = data.pop("values", {})
        try:
            kernel = cls.model_validate(data)
        except ValidationError as err:
            raise ClientError(f"{path} breaks a rule:\n" + "\n".join(_lines(err))) from None
        checked, lines = _check_tables(tables, kernel.packages, models)
        if lines:
            raise ClientError(f"{path} breaks a rule:\n" + "\n".join(lines))
        return kernel.model_copy(update={"package_values": checked})


def _check_tables(tables: Any, packages: list[PackageName], models: ValueModels) -> tuple[dict[str, PackageValues],
                                                                                          list[str]]:
    """The checked table of league and of each package of the list, and one plain line per broken rule.

    A package with no table takes the defaults of its model. A table of a package off the list fails.
    """
    if not isinstance(tables, dict):
        return {}, ["- values: is not a table"]
    taken = ["league", *packages]
    lines = [f"- values.{name}: names a package that is not in the package list" for name in tables if name not in taken]
    by_name = {model.package: model for model in models}
    checked: dict[str, PackageValues] = {}
    for name in taken:
        model = by_name.get(name)
        if model is None:
            continue
        table = tables.get(name, {})
        if not isinstance(table, dict):
            lines.append(f"- values.{name}: is not a table")
            continue
        try:
            checked[name] = model.model_validate(table)
        except ValidationError as err:
            lines.extend(_lines(err, ("values", name)))
    return checked, lines


def _lines(err: ValidationError, prefix: tuple[str, ...] = ()) -> list[str]:
    """One plain line per broken rule: the key path under `prefix` and the reason, with no pydantic text."""
    out = []
    for error in err.errors():
        where = ".".join(str(part) for part in (*prefix, *error["loc"]))
        reason = error["msg"].removeprefix("Value error, ")
        if error["type"] == "extra_forbidden":
            reason = "is not a known key"
        elif error["type"] == "missing":
            reason = "is required"
        out.append(f"- {where}: {reason}" if where else f"- {reason}")
    return out


def read_client_values(folder: Path, models: ValueModels) -> ClientValues:
    """The checked values of the client folder `folder`, each table by its model in `models`.

    A missing or bad file raises ClientError.
    """
    path = folder / CLIENT_FILE
    if not path.is_file():
        raise ClientError(f"No {CLIENT_FILE} for the client {folder.name} at {path}.")
    return ClientValues.from_toml_text(path.read_text(encoding="utf-8"), path, models)


# The model of an exported schema: the kernel keys, or the package values of one package.
SchemaModel = type[ClientValues] | type[PackageValues]


def schema_file(model: SchemaModel) -> Path:
    """The exported schema file of `model`: client.schema.json for the kernel keys, else values.schema.json beside it."""
    if model is ClientValues:
        return CLIENT_SCHEMA
    return Path(inspect.getfile(model)).parent / VALUES_SCHEMA


def _package_of(model: SchemaModel) -> str:
    return model.package if issubclass(model, PackageValues) else "league"


def _schema_text(model: SchemaModel) -> str:
    return json.dumps(model.model_json_schema(), indent=2) + "\n"


def write_schema_file(model: SchemaModel, path: Path | None = None) -> Path:
    """Write the exported JSON Schema of `model`, as the site build reads it."""
    path = path or schema_file(model)
    path.write_text(_schema_text(model), encoding="utf-8")
    return path


def check_schema_file(model: SchemaModel, path: Path | None = None) -> None:
    """Raise ClientError when the schema file of `model` differs from the model, so a stale export fails the check."""
    path = path or schema_file(model)
    if not path.is_file() or path.read_text(encoding="utf-8") != _schema_text(model):
        package = _package_of(model)
        raise ClientError(f"The schema file {path} of {package} is stale. Run make schema in packages/{package}/python "
                          "and commit the file.")


def check_schema_files(models: ValueModels) -> None:
    """Check the kernel schema and the schema of each model in `models`. The first stale file raises ClientError."""
    for model in (ClientValues, *models):
        check_schema_file(model)


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
        return self.values.package(LeagueValues).chart

    @property
    def voice_dir(self) -> Path:
        """The prompts folder of the client. Its tone.md and vocabulary.md replace the default voice."""
        return self.folder / "prompts"

    def league_id(self, season: int) -> str:
        """The provider league id of `season`. A season with no id stops the fetch with a plain message."""
        if season not in self.values.seasons:
            raise ClientError(f"No league id for season {season}. Add [seasons.{season}] to {self.folder / CLIENT_FILE}.")
        return self.values.seasons[season].league_id

    @property
    def current_league_id(self) -> str:
        """The league id of the latest season. A live fetch uses it, because it learns the season from the reply."""
        return self.values.seasons[self.values.latest_season].league_id


# The provider fetch of the League settings: the league id and the cache file of the season.
SettingsFetch = Callable[[str, Path], LeagueSettings]


def load_client(root: Path, slug: str, season: int | None, fetch_settings: SettingsFetch,
                models: ValueModels) -> Client:
    """The client `slug` under the repo root `root`, with the League settings of `season`. `models` checks the tables.

    A season of None takes the latest season of client.toml, so a caller reads the file one time.
    A missing or bad client.toml, or a season the file does not name, raises ClientError.
    """
    folder = client_dir(root, slug)
    values = read_client_values(folder, models)
    if season is None:
        season = values.latest_season
    if season not in values.seasons:
        raise ClientError(f"{folder / CLIENT_FILE} has no [seasons.{season}].")
    settings = fetch_settings(values.seasons[season].league_id, league_file(folder, season))
    return Client(slug=slug, folder=folder, nfl_dir=nfl_dir(root), values=values, settings=settings)
