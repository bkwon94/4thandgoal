"""
Builds the fact sheet and the bundle that the writer and the page read.
The fact sheet is the only input the writer sees, so each fact carries every number as the page shows it.
"""
# The package re-exports only the names that callers outside the sheet use. Outside the sheet package, a module
# imports only week.sheet or week.sheet.base. A chapter name that a caller needs goes in this file.
# The test test_no_module_outside_the_sheet_imports_a_chapter_module in tests/test_layers.py holds the rule.
from week.sheet.assemble import build_bundle, read_bundle, write_bundle
from week.sheet.base import (
    Context,
    check_week_is_buildable,
    projected_totals,
    week_dates,
)
from week.sheet.next_week import storyline_facts
from week.sheet.port import ChapterSource
from week.sheet.standings import standings_facts

__all__ = [
    "ChapterSource", "Context", "build_bundle", "check_week_is_buildable", "projected_totals", "read_bundle",
    "standings_facts", "storyline_facts", "week_dates", "write_bundle",
]
