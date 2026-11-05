"""
The shape of midseason.json and its writer: the week of the report, the takeover end week, and the acts with their
chapters. The pipeline owns the shape (ADR 0011), and the site side of the package reads it with its own schema.
"""
import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

from league.files import write_bytes_atomic
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


# Each chapter has its own model with a fixed key. A later chapter joins this union, with the key as the
# discriminator, so the site reads each chapter by its key.
Chapter = StateChapter


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


def midseason_report(season: int, week: int, state: LeagueState) -> MidseasonReport:
    """The report of `week` from the facts of each chapter. Act I holds the state of the league."""
    return MidseasonReport(
        season=season,
        week=week,
        takeover_end_week=week + TAKEOVER_WEEKS,
        acts=[Act(key="how-we-got-here", title="How we got here", chapters=[StateChapter(facts=state)])],
    )


def write_midseason(report: MidseasonReport, build: Path) -> Path:
    """Write midseason.json into the season folder of the build folder `build`. It never writes to published/."""
    out = build / str(report.season) / MIDSEASON_FILE
    out.parent.mkdir(parents=True, exist_ok=True)
    body = json.dumps(report.model_dump(mode="json"), ensure_ascii=False, indent=2) + "\n"
    write_bytes_atomic(out, body.encode("utf-8"))
    return out
