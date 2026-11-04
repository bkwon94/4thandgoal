"""
Builds the fact sheet and the bundle that the writer and the page read.
The fact sheet is the only input the writer sees, so each fact carries every number as the page shows it.
"""
# The package re-exports only the names that callers outside the sheet use. Outside the sheet package, a module
# imports only cornerstone.sheet or cornerstone.sheet.base. A chapter name that a caller needs goes in this file.
# The test test_no_module_outside_the_sheet_imports_a_chapter_module in tests/test_layers.py holds the rule.
from cornerstone.sheet.assemble import build_bundle, read_bundle, write_bundle
from cornerstone.sheet.base import (
    Context,
    check_week_is_buildable,
    odds_inputs,
    projected_totals,
    week_dates,
    week_odds,
)
from cornerstone.sheet.next_week import storyline_facts
from cornerstone.sheet.rankings import odds_facts, power_facts, rank_why_facts, rankings_chapter, swing_facts
from cornerstone.sheet.standings import standings_facts

__all__ = [
    "Context", "build_bundle", "check_week_is_buildable", "odds_facts", "odds_inputs", "power_facts", "projected_totals",
    "rank_why_facts", "rankings_chapter", "read_bundle", "standings_facts", "storyline_facts", "swing_facts",
    "week_dates", "week_odds", "write_bundle",
]
