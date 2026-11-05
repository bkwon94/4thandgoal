"""
The package values of managers, under [values.managers] of client.toml.
"make schema" in packages/managers/python exports the model to values.schema.json beside this file.
"""
from typing import ClassVar

from league.values import PackageValues


class ManagersValues(PackageValues):
    """The package values of managers. It has none yet."""

    package: ClassVar[str] = "managers"
