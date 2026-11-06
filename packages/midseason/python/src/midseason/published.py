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
from midseason.arcs import Arcs, ArcsChapter
from midseason.draft import DraftValue
from midseason.injury import InjuryChapter, InjuryToll
from midseason.look_ahead import LOOK_AHEAD, LookAhead, LookAheadChapter
from midseason.luck import LuckChapter, ScheduleLuck
from midseason.opener import OPENER, Opener, TitleRace
from midseason.prose import ROAST_SUFFIX
from midseason.state import LeagueState
from midseason.top10 import PositionTop10, Top10Chapter
from midseason.trades import TradeFacts
from midseason.waivers import WaiverFacts
from midseason.watch import PlayersToWatch, WatchChapter

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


class WaiversChapter(BaseModel):
    """Waiver hits and misses, in Act II: the top hits, the top misses, the top outbid claims, and the streamers."""
    key: Literal["waivers"] = "waivers"
    title: str = "Waiver hits and misses"
    facts: WaiverFacts
    blurb: Blurb | None = None
    roast: Blurb | None = None


class TradesChapter(BaseModel):
    """The trade report card, in Act II: every trade with its Trade result."""
    key: Literal["trades"] = "trades"
    title: str = "The trade report card"
    facts: TradeFacts
    blurb: Blurb | None = None
    roast: Blurb | None = None


# Each chapter has its own model with a fixed key. A later chapter joins this union, with the key as the
# discriminator, so the site reads each chapter by its key.
Chapter = Annotated[StateChapter | ArcsChapter | LuckChapter | InjuryChapter | Top10Chapter | DraftChapter
                    | WaiversChapter | TradesChapter | LookAheadChapter | WatchChapter, Field(discriminator="key")]


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


def midseason_report(
    season: int, week: int, state: LeagueState, blurbs: Mapping[str, Blurb], *, arcs: Arcs, luck: ScheduleLuck,
    injuries: InjuryToll, top10: PositionTop10, draft: DraftValue, waivers: WaiverFacts, trades: TradeFacts,
    watch: PlayersToWatch, race: TitleRace, look: LookAhead,
) -> MidseasonReport:
    """The report of `week` from the facts of each chapter and the blurbs by prose block key. The opener is the title
    race. Act I holds the state of the league, the arcs, Schedule luck, the injury toll, and Position top 10. Act II
    holds the draft, the waivers, and the trades. Act III holds the look ahead and the players to watch."""
    act_one: list[Chapter] = [
        StateChapter(facts=state, blurb=blurbs.get("state"), roast=blurbs.get("state" + ROAST_SUFFIX)),
        ArcsChapter(facts=arcs, blurb=blurbs.get("arcs"), roast=blurbs.get("arcs" + ROAST_SUFFIX)),
        LuckChapter(facts=luck, blurb=blurbs.get("luck"), roast=blurbs.get("luck" + ROAST_SUFFIX)),
        InjuryChapter(facts=injuries, blurb=blurbs.get("injuries"), roast=blurbs.get("injuries" + ROAST_SUFFIX)),
        Top10Chapter(facts=top10, blurb=blurbs.get("top10"), roast=blurbs.get("top10" + ROAST_SUFFIX)),
    ]
    act_two: list[Chapter] = [
        DraftChapter(facts=draft, blurb=blurbs.get("draft"), roast=blurbs.get("draft" + ROAST_SUFFIX)),
        WaiversChapter(facts=waivers, blurb=blurbs.get("waivers"), roast=blurbs.get("waivers" + ROAST_SUFFIX)),
        TradesChapter(facts=trades, blurb=blurbs.get("trades"), roast=blurbs.get("trades" + ROAST_SUFFIX)),
    ]
    act_three: list[Chapter] = [
        LookAheadChapter(facts=look, blurb=blurbs.get(LOOK_AHEAD), roast=blurbs.get(LOOK_AHEAD + ROAST_SUFFIX)),
        WatchChapter(facts=watch, blurb=blurbs.get("watch"), roast=blurbs.get("watch" + ROAST_SUFFIX)),
    ]
    return MidseasonReport(
        season=season,
        week=week,
        takeover_end_week=week + TAKEOVER_WEEKS,
        opener=Opener(facts=race, blurb=blurbs.get(OPENER), roast=blurbs.get(OPENER + ROAST_SUFFIX)),
        acts=[Act(key="how-we-got-here", title="How we got here", chapters=act_one),
              Act(key="the-moves", title="The moves", chapters=act_two),
              Act(key="what-comes-next", title="What comes next", chapters=act_three)],
    )


def report_blurbs(report: MidseasonReport) -> list[Blurb]:
    """Every blurb of the report in page order: the opener's blurb and its roast, then each chapter's."""
    opener = [blurb for blurb in (report.opener.blurb, report.opener.roast) if blurb is not None]
    return opener + [blurb for act in report.acts for chapter in act.chapters
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
