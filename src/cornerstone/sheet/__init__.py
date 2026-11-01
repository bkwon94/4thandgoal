"""
Builds the fact sheet and the bundle that the writer and the page read.
The fact sheet is the only input the writer sees, so each fact carries every number as the page shows it.
"""
# The package re-exports only the names that callers outside the sheet use. A caller that needs only a base
# name imports cornerstone.sheet.base, and a caller that needs one chapter imports that chapter module.
from cornerstone.sheet.assemble import build_bundle, read_bundle, write_bundle
from cornerstone.sheet.base import (
    NUMBER_TOKEN,
    RANKINGS_CHAPTER,
    Context,
    check_week_is_buildable,
    fmt,
    is_motw_recap,
    odds_inputs,
    projected_totals,
    week_dates,
    week_odds,
)
from cornerstone.sheet.next_week import storyline_facts
from cornerstone.sheet.rankings import odds_facts, power_facts, rank_why_facts, rankings_chapter, swing_facts
from cornerstone.sheet.standings import standings_facts
from cornerstone.sheet.trades import grade_input_facts, trade_facts

__all__ = [
    "NUMBER_TOKEN", "RANKINGS_CHAPTER", "Context", "build_bundle", "check_week_is_buildable", "fmt",
    "grade_input_facts", "is_motw_recap", "odds_facts", "odds_inputs", "power_facts", "projected_totals",
    "rank_why_facts", "rankings_chapter", "read_bundle", "standings_facts", "storyline_facts", "swing_facts",
    "trade_facts", "week_dates", "week_odds", "write_bundle",
]
