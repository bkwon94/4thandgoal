"""
The wire code of the week build: it gives the week package the chapter source of each package that the client takes.
Outside this folder, a module of the app imports the week build and the rankings chapter only from here.
"""
from cornerstone.sheet.rankings import (
    RANKINGS,
    odds_facts,
    odds_inputs,
    power_facts,
    rank_why_facts,
    rankings_chapter,
    swing_facts,
    week_odds,
)
from league.client import Client
from league.models import Bundle
from week import sheet as week_sheet
from week.sheet import (
    ChapterSource,
    Context,
    check_week_is_buildable,
    projected_totals,
    read_bundle,
    standings_facts,
    storyline_facts,
    week_dates,
    write_bundle,
)

# The chapter source of each package that gives the week a chapter, by package name. The rankings package gives
# its chapter and the odds. A client that omits a package gets no chapter from it.
CHAPTER_SOURCES: dict[str, ChapterSource] = {"rankings": RANKINGS}


def chapter_sources(client: Client) -> tuple[ChapterSource, ...]:
    """The chapter sources of the packages of `client`, in the order of its package list."""
    return tuple(CHAPTER_SOURCES[name] for name in client.values.packages if name in CHAPTER_SOURCES)


def build_bundle(*args, client: Client, **kwargs) -> Bundle:
    """The bundle of one week, with the chapters of the packages that `client` takes. See week.sheet.build_bundle."""
    return week_sheet.build_bundle(*args, client=client, sources=chapter_sources(client), **kwargs)


__all__ = [
    "CHAPTER_SOURCES", "Context", "build_bundle", "chapter_sources", "check_week_is_buildable", "odds_facts",
    "odds_inputs", "power_facts", "projected_totals", "rank_why_facts", "rankings_chapter", "read_bundle",
    "standings_facts", "storyline_facts", "swing_facts", "week_dates", "week_odds", "write_bundle",
]
