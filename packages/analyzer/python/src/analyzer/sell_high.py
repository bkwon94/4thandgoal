"""
The sell high pick of the Advisor: one sheet of a roster side by side, then one Claude call that picks up to 3 players
to sell, each with a headline and 2 to 4 Bullets. The guards and the Jev checks of the read of one trade run on it.
"""
import logging

from pydantic import BaseModel, Field

from analyzer.advisor import (
    Bullet,
    ReadBullet,
    TextGuard,
    bullet_failures,
    inner_word_failures,
    read_bullets,
    system_prompt,
)
from analyzer.read_jev_check import log_read_jev_checks
from analyzer.sell_facts import sell_sheet, sheet_players
from analyzer.stage import Stage, quiet
from analyzer.trade_news import FACT_PREFIX as NEWS_PREFIX
from analyzer.trade_news import NewsFeed, news_facts
from facts.writer import ClaudeCall, call_with_retry, sell_high_call
from league.jev_port import Jev
from league.models import Fact
from league.snapshot import Snapshot

log = logging.getLogger(__name__)

PROMPT_FILE = "sell_high.md"
MAX_PICKS = 3
MIN_BULLETS, MAX_BULLETS = 2, 4


class SellPickOut(BaseModel):
    """One pick as the Advisor gives it: the player id of the sheet, a headline that says why, and 2 to 4 Bullets."""

    player_id: str
    headline: str
    # The count sits in the description, so the model reads it in the schema. The guard checks it and retries.
    bullets: list[Bullet] = Field(description=f"{MIN_BULLETS} to {MAX_BULLETS} Bullets")


class SellHighOut(BaseModel):
    """The structured output of the sell high call: up to 3 picks, or no pick and a plain line that says why."""

    # The count is a description only, as with the Bullets: the guard checks it.
    picks: list[SellPickOut] = Field(description=f"Up to {MAX_PICKS} picks, best first")
    none_line: str | None


class SellPick(BaseModel):
    """One player to sell as the page shows him: his id, the headline, and the Bullets with the text of each fact."""

    player_id: str
    headline: str
    bullets: list[ReadBullet]


class SellHigh(BaseModel):
    """What a sell high press gives: the roster, the picks, and the plain line when no pick stands."""

    roster_id: int
    picks: list[SellPick]
    none_line: str | None


class SellHighFailed(Exception):
    """The Advisor gave no pick that passed the guards in two calls. The API answers with an honest error."""


class _PickSide(BaseModel):
    """The Bullets of every pick in the shape of a side, for the Jev checks. The Bullets advise Your team."""

    roster_id: int
    bullets: list[Bullet]


def sell_high_sheet(snapshot: Snapshot, roster_id: int, news: NewsFeed) -> dict[str, Fact]:
    """The facts the Advisor reads by id: the side-by-side facts of the roster, then the news of its players."""
    return {**sell_sheet(snapshot, roster_id), **news_facts(sheet_players(snapshot, roster_id), snapshot, news)}


def _owner(fid: str) -> str | None:
    """The player id that a fact of the sheet is about, or None for a fact of the whole sheet such as the week."""
    if fid.startswith(NEWS_PREFIX):
        return fid.removeprefix(NEWS_PREFIX).split(".")[0]
    head, _, _ = fid.partition(".")
    return head if head.isdigit() else None


def build_sell_prompt(snapshot: Snapshot, roster_id: int, facts: dict[str, Fact],
                      feedback: str | None) -> tuple[str, str]:
    """The system prompt and the user message of the sell high call: the week facts, then each player with his own
    facts, so each player's reads sit side by side."""
    lines = [f"Your team: roster {roster_id}, {snapshot.teams[roster_id].name}.", "", "Facts of the week:"]
    lines += [f"- {fid}: {f.text}" for fid, f in facts.items() if _owner(fid) is None]
    for pid in sheet_players(snapshot, roster_id):
        player = snapshot.players[pid]
        lines += ["", f"Player {pid}: {player.name} ({player.position}, {player.nfl_team or 'no NFL team'})",
                  *(f"- {fid}: {f.text}" for fid, f in facts.items() if _owner(fid) == pid)]
    if feedback is not None:
        lines += ["", "Feedback from the last attempt:", feedback, "Give the whole response again."]
    return system_prompt(snapshot, PROMPT_FILE), "\n".join(lines)


def check_sells(out: SellHighOut, snapshot: Snapshot, roster_id: int, facts: dict[str, Fact]) -> list[str]:
    """Every guard the picks break. An empty list means the picks stand.

    A pick names a player of the sheet once. Each Bullet cites a fact of the sheet and passes the guards of the read
    of one trade. The headline holds only the names and the numbers of the facts its Bullets cite.
    """
    if not out.picks:
        if not (out.none_line or "").strip():
            return ["a response with no pick needs a none_line in plain words"]
        return inner_word_failures("none_line", out.none_line or "")
    if len(out.picks) > MAX_PICKS:
        return [f"the response has {len(out.picks)} picks; the most is {MAX_PICKS}"]
    players = sheet_players(snapshot, roster_id)
    allowed = {snapshot.teams[roster_id].name} | {snapshot.players[pid].name for pid in players}
    guard = TextGuard(None, snapshot, facts, allowed=allowed)
    failures, seen = [], set()
    for number, pick in enumerate(out.picks, start=1):
        label = f"pick {number}"
        if pick.player_id not in players:
            failures.append(f"{label}: player {pick.player_id} is not a player of the sheet")
            continue
        if pick.player_id in seen:
            failures.append(f"{label}: player {pick.player_id} is picked twice")
        seen.add(pick.player_id)
        bullet_fails, cited = bullet_failures(label, pick.bullets, facts, guard, least=MIN_BULLETS, most=MAX_BULLETS)
        failures += bullet_fails + guard.text_failures(f"{label} headline", pick.headline, cited)
    return failures


def pick_sells(roster_id: int, snapshot: Snapshot, *, jev: Jev, news: NewsFeed, call: ClaudeCall = sell_high_call,
               stage: Stage = quiet) -> SellHigh:
    """The players of the roster that the Advisor would sell, with why. A failed guard retries once with the
    failures as feedback. Raises SellHighFailed after two failed calls, a failed API call included.

    `stage` gets one plain line after the sheet, one after the guards pass, and one with the count of the picks.
    """
    facts = sell_high_sheet(snapshot, roster_id, news)
    count = len(sheet_players(snapshot, roster_id))
    stage(f"Lined up your {count} players" if count != 1 else "Lined up your one player")
    out = call_with_retry(
        call, lambda feedback: build_sell_prompt(snapshot, roster_id, facts, feedback), SellHighOut,
        lambda out: check_sells(out, snapshot, roster_id, facts), subject="sell high pick", log_label="sell high",
        logger=log)
    if out is None:
        raise SellHighFailed("The Advisor gave no sell high pick that passed the guards in two calls.")
    stage("Checked each number of the picks")
    # The Jev checks run on every Bullet in one request, as on the read of one trade. They only log, so no answer and
    # no failure ever blocks a pick.
    log_read_jev_checks([_PickSide(roster_id=roster_id, bullets=[b for pick in out.picks for b in pick.bullets])],
                        facts, jev)
    picks = [SellPick(player_id=pick.player_id, headline=pick.headline, bullets=read_bullets(pick.bullets, facts))
             for pick in out.picks]
    if not picks:
        stage("Found no player to sell")
    else:
        stage(f"Picked {len(picks)} players to sell" if len(picks) > 1 else "Picked one player to sell")
    return SellHigh(roster_id=roster_id, picks=picks, none_line=None if picks else out.none_line)
