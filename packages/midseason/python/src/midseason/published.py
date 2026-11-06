"""
The shape of midseason.json and its writer: the week of the report, the takeover end week, the acts with their
chapters, and the report tile. The pipeline owns the shape (ADR 0011), and the site side of the package reads it with
its own schema.
"""
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel, Field

from league.files import write_bytes_atomic
from league.models import Blurb
from midseason.arcs import Arcs, ArcsChapter
from midseason.draft import DraftValue
from midseason.injury import InjuryChapter, InjuryToll
from midseason.lineups import LineupChapter, LineupChoices
from midseason.look_ahead import LOOK_AHEAD, LookAhead, LookAheadChapter
from midseason.luck import LuckChapter, ScheduleLuck
from midseason.opener import OPENER, Opener, ReportTile, TitleRace, report_tile
from midseason.records import RecordBook, RecordsChapter
from midseason.spread import Headline
from midseason.state import LeagueState
from midseason.top10 import PositionTop10, Top10Chapter
from midseason.trades import TradeFacts
from midseason.waivers import WaiverFacts

# The season file has its own version, so a change to one file never breaks the reader of another.
MIDSEASON_SCHEMA_VERSION = 1
MIDSEASON_FILE = "midseason.json"
# The home page shows the takeover through the week of the report, then the report tile. PRD, "The takeover".
TAKEOVER_WEEKS = 0


class StateChapter(BaseModel):
    """The state of the league, the first chapter of Act I."""
    key: Literal["state"] = "state"
    title: str = "The State of the League"
    facts: LeagueState
    # The blurb of the writer. Brian may edit its sentences in the draft before the publish.
    blurb: Blurb | None = None


class DraftChapter(BaseModel):
    """The draft steals and busts, the first chapter of Act II."""
    key: Literal["draft"] = "draft"
    title: str = "Draft Steals and Busts"
    facts: DraftValue
    blurb: Blurb | None = None


class WaiversChapter(BaseModel):
    """Waiver hits and misses, in Act II: the top hits, the top misses, the top outbid claims, and the streamers."""
    key: Literal["waivers"] = "waivers"
    title: str = "Waiver Hits and Misses"
    facts: WaiverFacts
    blurb: Blurb | None = None


class TradesChapter(BaseModel):
    """The trade report card, in Act II: every trade with its Trade result."""
    key: Literal["trades"] = "trades"
    title: str = "The Trade Report Card"
    facts: TradeFacts
    blurb: Blurb | None = None


class QuickHitsChapter(BaseModel):
    """Quick hits, the last chapter of Act II: the lineup choices and the injury toll in one block. Each part keeps
    its own facts and prose block, so the writer writes each part as before. GLOSSARY.md, "Quick hits"."""
    key: Literal["quick-hits"] = "quick-hits"
    title: str = "Quick Hits"
    chapters: list[Annotated[LineupChapter | InjuryChapter, Field(discriminator="key")]]


# Each chapter has its own model with a fixed key. A later chapter joins this union, with the key as the
# discriminator, so the site reads each chapter by its key.
Chapter = Annotated[StateChapter | ArcsChapter | LuckChapter | Top10Chapter | DraftChapter | WaiversChapter
                    | TradesChapter | RecordsChapter | QuickHitsChapter | LookAheadChapter,
                    Field(discriminator="key")]


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
    # The top of the report, the title race. The takeover of the home page shows it too.
    opener: Opener
    acts: list[Act]
    # The one big fact of the home tile, which the home page shows after the takeover ends.
    tile: ReportTile
    # Every headline of each team after the spread rule: the arcs, the awards, and the callouts.
    headlines: list[Headline]


def midseason_report(
    season: int, week: int, state: LeagueState, blurbs: Mapping[str, Blurb], *, arcs: Arcs, luck: ScheduleLuck,
    injuries: InjuryToll, top10: PositionTop10, draft: DraftValue, waivers: WaiverFacts, trades: TradeFacts,
    lineups: LineupChoices, records: RecordBook, race: TitleRace, look: LookAhead,
    headlines: list[Headline],
) -> MidseasonReport:
    """The report of `week` from the facts of each chapter and the blurbs by prose block key. The opener is the title
    race. The acts follow the lean acts of decision 14. Act I holds the state of the league, the arcs, Schedule luck,
    and Position top 10. Act II holds the draft, the waivers, the trades, the record book with the awards, and last
    Quick hits, with the lineup choices and the injury toll. Act III holds the look ahead, and the site ends it on the
    sim."""
    act_one: list[Chapter] = [
        StateChapter(facts=state, blurb=blurbs.get("state")),
        ArcsChapter(facts=arcs, blurb=blurbs.get("arcs")),
        LuckChapter(facts=luck, blurb=blurbs.get("luck")),
        Top10Chapter(facts=top10, blurb=blurbs.get("top10")),
    ]
    act_two: list[Chapter] = [
        DraftChapter(facts=draft, blurb=blurbs.get("draft")),
        WaiversChapter(facts=waivers, blurb=blurbs.get("waivers")),
        TradesChapter(facts=trades, blurb=blurbs.get("trades")),
        RecordsChapter(facts=records, blurb=blurbs.get("records")),
        QuickHitsChapter(chapters=[
            LineupChapter(facts=lineups, blurb=blurbs.get("lineup")),
            InjuryChapter(facts=injuries, blurb=blurbs.get("injuries")),
        ]),
    ]
    act_three: list[Chapter] = [
        LookAheadChapter(facts=look, blurb=blurbs.get(LOOK_AHEAD)),
    ]
    return MidseasonReport(
        season=season,
        week=week,
        takeover_end_week=week + TAKEOVER_WEEKS,
        opener=Opener(facts=race, blurb=blurbs.get(OPENER)),
        acts=[Act(key="how-we-got-here", title="How We Got Here", chapters=act_one),
              Act(key="the-moves", title="The Moves", chapters=act_two),
              Act(key="what-comes-next", title="What Comes Next", chapters=act_three)],
        tile=report_tile(race),
        headlines=headlines,
    )


# A chapter with its own prose block: each chapter of an act but Quick hits, and each part of Quick hits.
ProseChapter = (StateChapter | ArcsChapter | LuckChapter | InjuryChapter | Top10Chapter | DraftChapter
                | WaiversChapter | TradesChapter | LineupChapter | RecordsChapter | LookAheadChapter)


def prose_chapters(report: MidseasonReport) -> list[ProseChapter]:
    """Each chapter with its own prose block, in page order. The parts of Quick hits stand in for Quick hits, which
    has no prose of its own."""
    return [part for act in report.acts for chapter in act.chapters
            for part in (chapter.chapters if isinstance(chapter, QuickHitsChapter) else [chapter])]


def report_blurbs(report: MidseasonReport) -> list[Blurb]:
    """Every blurb of the report in page order: the opener's blurb, then each chapter's."""
    blurbs = [report.opener.blurb, *(chapter.blurb for chapter in prose_chapters(report))]
    return [blurb for blurb in blurbs if blurb is not None]


def read_midseason(season_build: Path) -> MidseasonReport:
    return MidseasonReport.model_validate_json((season_build / MIDSEASON_FILE).read_text(encoding="utf-8"))


def write_midseason(report: MidseasonReport, build: Path) -> Path:
    """Write midseason.json into the season folder of the build folder `build`. It never writes to published/."""
    out = build / str(report.season) / MIDSEASON_FILE
    out.parent.mkdir(parents=True, exist_ok=True)
    body = json.dumps(report.model_dump(mode="json"), ensure_ascii=False, indent=2) + "\n"
    write_bytes_atomic(out, body.encode("utf-8"))
    return out
