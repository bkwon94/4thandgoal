"""
Builds the fact sheet and the bundle that the writer and the page read.
The fact sheet is the only input the writer sees, so each fact carries every number as the page shows it.
"""
# The package re-exports the names that callers use. A caller that needs a chapter function imports it from
# here, and a caller that needs only a base name imports cornerstone.sheet.base. Ticket 11 cuts the re-exports down.
from cornerstone.sheet.assemble import build_bundle, read_bundle, write_bundle
from cornerstone.sheet.base import (
    AWARD_TITLES,
    BYE_FACT_PREFIX,
    NUMBER_TOKEN,
    RANKINGS_CHAPTER,
    Context,
    Nums,
    _odds,
    _odds_inputs,
    check_week_is_buildable,
    fact,
    fmt,
    is_motw_recap,
    projected_totals,
    repeats_motw_headline,
    two_team_chapter,
    week_dates,
)
from cornerstone.sheet.next_week import storyline_facts
from cornerstone.sheet.rankings import odds_facts, power_facts, rank_why_facts, rankings_chapter, swing_facts
from cornerstone.sheet.standings import standings_facts
from cornerstone.sheet.trades import grade_input_facts, trade_facts

__all__ = [
    "AWARD_TITLES", "BYE_FACT_PREFIX", "NUMBER_TOKEN", "RANKINGS_CHAPTER", "Context", "Nums", "_odds", "_odds_inputs",
    "build_bundle", "check_week_is_buildable", "fact", "fmt", "grade_input_facts", "is_motw_recap", "odds_facts",
    "power_facts", "projected_totals", "rank_why_facts", "rankings_chapter", "read_bundle", "repeats_motw_headline",
    "standings_facts", "storyline_facts", "swing_facts", "trade_facts", "two_team_chapter", "week_dates",
    "write_bundle",
]
