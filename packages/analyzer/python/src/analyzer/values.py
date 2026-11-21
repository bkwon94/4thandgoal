"""
The package values of analyzer, under [values.analyzer] of client.toml.
"make schema" in packages/analyzer/python exports the model to values.schema.json beside this file.
"""
from typing import Annotated, ClassVar

from pydantic import AwareDatetime, WithJsonSchema

from league.values import PackageValues

# The schema of the Lock: a string with a UTC offset. The site build checks it with ajv, which knows no date-time format,
# so the pattern asks for the offset and pydantic checks the rest.
LOCK_SCHEMA = {
    "anyOf": [{"type": "string", "pattern": r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(Z|[+-]\d{2}:\d{2})$"}, {"type": "null"}],
    "default": None,
}


class AnalyzerValues(PackageValues):
    """The package values of analyzer. The finder is off by default, and a client has no Lock by default."""

    package: ClassVar[str] = "analyzer"

    finder: bool = False
    # The Lock: the time when Sleeper closes trades for the season. With one, the site shows Deadline week until one day
    # after it. With none, the client has no Deadline week.
    lock: Annotated[AwareDatetime | None, WithJsonSchema(LOCK_SCHEMA)] = None
