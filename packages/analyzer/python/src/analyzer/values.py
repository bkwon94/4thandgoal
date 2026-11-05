"""
The package values of analyzer, under [values.analyzer] of client.toml.
"make schema" in packages/analyzer/python exports the model to values.schema.json beside this file.
"""
from typing import ClassVar

from league.values import PackageValues


class AnalyzerValues(PackageValues):
    """The package values of analyzer. The finder is off by default."""

    package: ClassVar[str] = "analyzer"

    finder: bool = False
