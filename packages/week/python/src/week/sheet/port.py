"""
The chapter port: a chapter that another package gives the week, with the facts it cites and the odds it computes.
The app passes the sources of the packages that the client takes, so a client with no rankings has no rankings chapter.
"""
from typing import TYPE_CHECKING, Protocol

from league.models import Chapter, Fact, OddsResult

if TYPE_CHECKING:
    from week.sheet.base import Context


class ChapterSource(Protocol):
    """One chapter of another package. The week calls each method once per build, in the order below.

    The week reads the odds too: the impact fact of each matchup and the Median Game chapter cite them. A source
    with no odds gives None, and a week with no source of odds gives no odds part.
    """

    def odds(self, c: "Context") -> OddsResult | None:
        """The odds after this week, or None. The context calls it after the projected totals."""
        ...

    def facts(self, c: "Context") -> list[Fact]:
        """The facts of the source. The sheet lists them after the facts of the week."""
        ...

    def chapter(self, c: "Context", facts: dict[str, Fact]) -> Chapter | None:
        """The chapter of the source, or None when the week gives it nothing to say. It goes after the week chapters."""
        ...
