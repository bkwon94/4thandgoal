"""
The live matchup card of Your next matchup: the lineup by projection of each side for the live Sleeper week, as Start or
sit reads it, and the win odds from the gap of the two totals. The rest of the Topic still comes from topics.json.
"""
import json
import math
from collections.abc import AsyncIterator
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict
from pydantic_ai.ui.vercel_ai.response_types import BaseChunk, DoneChunk, FinishChunk, StartChunk

from analyzer.routes import ServedClient
from cornerstone_api.ask import ClientAsker
from cornerstone_api.claude_stream import adapter, data
from cornerstone_api.personal_topics import AGENT, load_week
from cornerstone_api.start_sit import LiveWeek
from cornerstone_api.week_lineup import WeekLineup, week_lineup
from league.matchup_card import MatchupBlock, MatchupPlayer, MatchupTeam, matchup_slots, starting_slots

router = APIRouter()

NEXT_MATCHUP = "next_matchup"
# The season file of the sim, with the league spread in its parameters.
SIM_FILE = "sim.json"


class NextMatchupRequest(BaseModel):
    """The body of the live card: the roster id of the team that the Answer is about. useChat adds its own fields, and
    the route reads none of them."""

    model_config = ConfigDict(extra="ignore")

    roster_id: int


def win_odds(you: float, them: float, spread: float) -> float:
    """The chance that the score of Your team beats the score of the other team, from 0 to 1.

    Each score is a normal around its projected total with the league spread as its standard deviation, so the gap of
    the two scores is a normal around the gap of the totals with the spread times the square root of 2.
    """
    if spread <= 0:
        return 0.5 if you == them else float(you > them)
    return 0.5 * (1 + math.erf((you - them) / (2 * spread)))


def league_spread(folder: Path, season: int) -> float | None:
    """The league spread of the published sim.json of the season, or None when the season has no sim yet."""
    path = folder / "published" / str(season) / SIM_FILE
    if not path.exists():
        return None
    return float(json.loads(path.read_text(encoding="utf-8"))["parameters"]["spread"])


def _side(lineup: WeekLineup) -> list[tuple[str, MatchupPlayer]]:
    # A starter with no projection row counts 0, as he does in the total of the lineup.
    return [(row.slot, MatchupPlayer(name=row.player.name, position=row.player.position, nfl_team=row.player.nfl_team,
                                     points=round(row.player.projection or 0.0, 1)))
            for row in lineup.rows if row.player is not None]


def opponent(week: LiveWeek, roster_id: int) -> int | None:
    """The roster that meets `roster_id` in the live week: the other roster of its Sleeper matchup, or None."""
    mine = next((m for m in week.raw.matchups if m.roster_id == roster_id), None)
    if mine is None or mine.matchup_id is None:
        return None
    return next((m.roster_id for m in week.raw.matchups
                 if m.matchup_id == mine.matchup_id and m.roster_id != roster_id), None)


def matchup_card(week: LiveWeek, roster_id: int, spread: float | None) -> MatchupBlock | None:
    """The live card of the next game of `roster_id`, or None when the team has no game in the live week.

    Each side is the lineup by projection of Start or sit, so a bye, an OUT player, or a Swap moves the totals and the
    odds. The odds are None when the season has no sim spread yet.
    """
    other = opponent(week, roster_id)
    if other is None:
        return None
    mine, theirs = (week_lineup(week.raw, rid, week.kickoffs, week.now) for rid in (roster_id, other))
    you = MatchupTeam(roster_id=roster_id, name=week.team_name(roster_id), score=round(mine.total, 1))
    them = MatchupTeam(roster_id=other, name=week.team_name(other), score=round(theirs.total, 1))
    return MatchupBlock(
        final=False, you=you, them=them,
        odds=None if spread is None else round(win_odds(you.score, them.score, spread), 3),
        slots=matchup_slots(starting_slots(week.raw.league.roster_positions), _side(mine), _side(theirs)),
        read_at=week.now.isoformat())


async def _stream(card: MatchupBlock | None) -> AsyncIterator[BaseChunk]:
    yield StartChunk()
    if card is not None:
        yield data("block", card.model_dump(mode="json"))
    yield FinishChunk(finish_reason="stop")
    yield DoneChunk()


@router.post("/next-matchup")
async def next_matchup(body: NextMatchupRequest, asker: ClientAsker, served: ServedClient) -> StreamingResponse:
    """The stream of the live card of Your next matchup: one data block from code, with no Claude call. A team with no
    game in the live week gets a stream with no block, so the site keeps the card of topics.json."""
    week = await load_week(served, asker.season)
    if body.roster_id not in week.rosters:
        raise HTTPException(status_code=422, detail="Pick your team again.")
    spread = league_spread(served.sources.client.folder, asker.season)
    card = matchup_card(week, body.roster_id, spread)
    return adapter(AGENT, "").streaming_response(_stream(card))
