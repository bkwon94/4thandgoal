"""
The package values of rankings, under [values.rankings] of client.toml.
"make schema" in packages/rankings/python exports the model to values.schema.json beside this file.
"""
from typing import ClassVar

from league.values import PackageValues


class RankingsValues(PackageValues):
    """The package values of rankings. It has no values."""

    package: ClassVar[str] = "rankings"
