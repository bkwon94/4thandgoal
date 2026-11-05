"""
The package values of waiver, under [values.waiver] of client.toml.
"make schema" in packages/waiver/python exports the model to values.schema.json beside this file.
"""
from typing import ClassVar

from league.values import PackageValues


class WaiverValues(PackageValues):
    """The package values of waiver. It has no values."""

    package: ClassVar[str] = "waiver"
