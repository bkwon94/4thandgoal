"""
The base of the package values model of each package, and the package values of league under [values.league].
Each package defines one model on this base, and "make schema" exports it to values.schema.json beside the model.
"""
from typing import ClassVar

from pydantic import BaseModel, ConfigDict


class PackageValues(BaseModel):
    """The base of the package values of one package. An unknown key fails, so a typo never passes as a default."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    # The package name, the key of its table [values.<package>] in client.toml.
    package: ClassVar[str]


class LeagueValues(PackageValues):
    """The package values of league. The default is no chart, and then each chart value is 0."""

    package: ClassVar[str] = "league"

    chart: str | None = None
