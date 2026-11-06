"""
The shape of midseason.json and its writer: the week of the report, the takeover end week, and the acts with their
chapters. The pipeline owns the shape (ADR 0011), and the site side of the package reads it with its own schema.
"""
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel, Field

from league.files import write_bytes_atomic
from league.models import Blurb
from midseason.draft import DraftValue
from midseason.prose import ROAST_SUFFIX
from midseason.state import LeagueState

# The season file has its own version, so a change to one file never breaks the reader of another.
MIDSEASON_SCHEMA_VERSION = 1
MIDSEASON_FILE = "midseason.json"
# The home page shows the takeover through the week after the report, then the report tile. PRD, "The takeover".
TAKEOVER_WEEKS = 1


class StateChapter(BaseModel):
    """The state of the league, the first chapter of Act I."""
    key: Literal["state"] = "state"
    title: str = "The state of the league"
    facts: LeagueState
    # The blurb of the writer. Brian may edit its sentences in the draft before the publish.
    blurb: Blurb | None = None
    # The roast blurb. None when the roast setting of the client is off.
    roast: Blurb | None = None


class DraftChapter(BaseModel):
    """The draft steals and busts, the first chapter of Act II."""
    key: Literal["draft"] = "draft"
    title: str = "Draft steals and busts"
    facts: DraftValue
    blurb: Blurb | None = None
    roast: Blurb | None = None


# Each chapter has its own model with a fixed key. A later chapter joins this union, with the key as the
# discriminator, so the site reads each chapter by its key.
Chapter = Annotated[StateChapter | DraftChapter, Field(discriminator="key")]


class Act(BaseModel):
    """One of the three acts of the report, each opened by a dark title page. GLOSSARY.md, "Act"."""
    key: Literal["how-we-got-here", "the-moves", "what-comes-next"]
    title: str
    chapters: list[Chapter]


class MidseasonReport(BaseModel):
    """The whole of midseason.json."""
    schema_version: int = MIDSEASON_SCHEMA_VERSION
    season: int
    # The last week that the report counts.
    week: int
    # The last published week that still shows the takeover on the home page.
    takeover_end_week: int
    acts: list[Act]


def midseason_report(
    season: int, week: int, state: LeagueState, blurbs: Mapping[str, Blurb], *, draft: DraftValue | None = None,
) -> MidseasonReport:
    """The report of `week` from the facts of each chapter and the blurbs by prose block key. Act I holds the state
    of the league. Act II holds the draft steals and busts when the build has the draft."""
    state_chapter = StateChapter(facts=state, blurb=blurbs.get("state"), roast=blurbs.get("state" + ROAST_SUFFIX))
    acts = [Act(key="how-we-got-here", title="How we got here", chapters=[state_chapter])]
    if draft is not None:
        draft_chapter = DraftChapter(facts=draft, blurb=blurbs.get("draft"), roast=blurbs.get("draft" + ROAST_SUFFIX))
        acts.append(Act(key="the-moves", title="The moves", chapters=[draft_chapter]))
    return MidseasonReport(season=season, week=week, takeover_end_week=week + TAKEOVER_WEEKS, acts=acts)


def report_blurbs(report: MidseasonReport) -> list[Blurb]:
    """Every blurb of the report in page order: each chapter's blurb, then its roast."""
    return [blurb for act in report.acts for chapter in act.chapters
            for blurb in (chapter.blurb, chapter.roast) if blurb is not None]


def read_midseason(season_build: Path) -> MidseasonReport:
    return MidseasonReport.model_validate_json((season_build / MIDSEASON_FILE).read_text(encoding="utf-8"))


def write_midseason(report: MidseasonReport, build: Path) -> Path:
    """Write midseason.json into the season folder of the build folder `build`. It never writes to published/."""
    out = build / str(report.season) / MIDSEASON_FILE
    out.parent.mkdir(parents=True, exist_ok=True)
    body = json.dumps(report.model_dump(mode="json"), ensure_ascii=False, indent=2) + "\n"
    write_bytes_atomic(out, body.encode("utf-8"))
    return out
