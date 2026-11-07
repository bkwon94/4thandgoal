"""
The package values of midseason, under [values.midseason] of client.toml.
"make schema" in packages/midseason/python exports the model to values.schema.json beside this file.
"""
from typing import ClassVar, Literal

from league.values import PackageValues

# The voice of the prose of the report, from the cleanest to the meanest. PRD, "The prose and the roast".
Roast = Literal["off", "warm", "hot", "savage"]


class MidseasonValues(PackageValues):
    """The package values of midseason: the voice of the prose of the report. "off" is a sharp, clean sports writer,
    "warm" a funny friend in the group chat, "hot" a mean columnist, and "savage" a full roast. Brian chose savage as
    the default."""

    package: ClassVar[str] = "midseason"

    roast: Roast = "savage"
