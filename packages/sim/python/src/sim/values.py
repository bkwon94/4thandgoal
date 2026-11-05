"""
The package values of sim, under [values.sim] of client.toml.
"make schema" in packages/sim/python exports the model to values.schema.json beside this file.
"""
from typing import ClassVar

from league.values import PackageValues


class SimValues(PackageValues):
    """The package values of sim. It has no values."""

    package: ClassVar[str] = "sim"
