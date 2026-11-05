"""
The package values of week, under [values.week] of client.toml.
"make schema" in packages/week/python exports the model to values.schema.json beside this file.
"""
from typing import ClassVar

from league.values import PackageValues


class WeekValues(PackageValues):
    """The package values of week. It has none yet."""

    package: ClassVar[str] = "week"
