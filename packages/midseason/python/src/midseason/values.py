"""
The package values of midseason, under [values.midseason] of client.toml.
"make schema" in packages/midseason/python exports the model to values.schema.json beside this file.
"""
from typing import ClassVar

from league.values import PackageValues


class MidseasonValues(PackageValues):
    """The package values of midseason. It has no values."""

    package: ClassVar[str] = "midseason"
