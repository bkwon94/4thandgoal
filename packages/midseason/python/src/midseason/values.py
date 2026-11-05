"""
The package values of midseason, under [values.midseason] of client.toml.
"make schema" in packages/midseason/python exports the model to values.schema.json beside this file.
"""
from typing import ClassVar, Literal

from league.values import PackageValues

# The heat of the roast of the report. PRD, "The prose and the roast".
Roast = Literal["off", "warm", "hot"]


class MidseasonValues(PackageValues):
    """The package values of midseason: the heat of the roast. "off" drops the roast lines, "warm" softens each
    roast, and "hot" has no limit on heat for football decisions."""

    package: ClassVar[str] = "midseason"

    roast: Roast = "hot"
