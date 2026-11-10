"""
The Finder pick: one sheet per shortlist offer, then one Advisor call that picks up to 3 offers, each with a headline
and 2 to 3 Bullets. A pick that fails a guard retries once. After two failed calls, the shortlist stands with fact lines.
"""
import logging

from pydantic import BaseModel

from analyzer.advisor import (
    Bullet,
    Lean,
    ReadBullet,
    TextGuard,
    bullet_failures,
    inner_word_failures,
    measured_sheet,
    read_bullets,
    side_lines,
    system_prompt,
)
from analyzer.finder_search import Shortlist, ShortlistOffer
from analyzer.trade_jev import jev_answer_facts, trade_jev_questions
from analyzer.trade_news import NewsFeed
from facts.writer import ClaudeCall, call_with_retry, finder_pick_call
from league.models import Fact
from league.snapshot import Snapshot

log = logging.getLogger(__name__)

PROMPT_FILE = "finder_pick.md"
MAX_PICKS = 3
MIN_BULLETS, MAX_BULLETS = 2, 3
# The line of a press whose search kept no offer. No Claude call runs, so code writes it.
NO_OFFER = "The search found no trade that works for both teams."
# The Leans of a trade that the asker sends. A pick reads as one of them, so the analyzer read of a pick agrees.
SEND_LEANS = ("Send it", "Lean yes", "Gut call")
# The text of a fact that an earlier offer of the message gave in full. The id stays, so a Bullet may cite it.
SAME_FACT = "(the same text as in an earlier offer)"


class PickOut(BaseModel):
    """One pick as the Advisor gives it: the offer id of the shortlist, the Lean of the trade if the asker graded it
    alone, a headline, and 2 to 3 Bullets. The Lean stays out of the document, because the card shows no Lean."""

    offer_id: str
    lean: Lean
    headline: str
    bullets: list[Bullet]


class FinderPickOut(BaseModel):
    """The structured output of the pick call: up to 3 picks, or no pick and a plain line that says why."""

    picks: list[PickOut]
    none_line: str | None


class FinderPick(BaseModel):
    """One trade of the finder document: its shortlist offer, and the headline and the Bullets of the Advisor.

    After a fallback, the headline is None, no Bullet stands, and the fact lines hold plain facts of the offer.
    """

    offer: ShortlistOffer
    headline: str | None
    bullets: list[ReadBullet]
    fact_lines: list[str]


class FinderPicks(BaseModel):
    """What a Finder press gives: the picks, the plain line when no pick stands, and whether the call fell back."""

    picks: list[FinderPick]
    none_line: str | None
    fallback: bool


def offer_sheet(offer: ShortlistOffer, snapshot: Snapshot, news: NewsFeed) -> dict[str, Fact]:
    """The facts of one shortlist offer by id: the measured facts of its trade, with the news of its players only,
    then the Jev answers of the shortlist as JEV facts, so the pick makes no new Jev call."""
    trade = offer.trade
    nouls = {"fair": offer.fair, **{f"need.{rid}": p for rid, p in offer.needs.items()}}
    questions = trade_jev_questions(trade, snapshot)
    return {**measured_sheet(trade, snapshot, news),
            **jev_answer_facts(trade, snapshot, questions, {key: p for key, p in nouls.items() if key in questions})}


def build_pick_prompt(shortlist: Shortlist, snapshot: Snapshot, sheets: dict[str, dict[str, Fact]],
                      feedback: str | None) -> tuple[str, str]:
    """The system prompt and the user message of the pick call: each offer with its sides and its own facts."""
    lines = [f"The asker: roster {shortlist.asker}, {snapshot.teams[shortlist.asker].name}.", ""]
    # One player or one team sits on many offers, so a fact text that an earlier offer gave is not sent again. This
    # keeps the message, and the cost and the time of the call, near those of one read.
    given: set[tuple[str, str]] = set()
    for offer in shortlist.shortlist:
        lines += [f"Offer {offer.offer_id}", *side_lines(offer.trade, snapshot), "Facts:"]
        for fid, f in sheets[offer.offer_id].items():
            lines.append(f"- {fid}: {SAME_FACT if (fid, f.text) in given else f.text}")
            given.add((fid, f.text))
        lines.append("")
    if feedback is not None:
        lines += ["Feedback from the last attempt:", feedback, "Give the whole response again."]
    return system_prompt(snapshot, PROMPT_FILE), "\n".join(lines).rstrip()


def check_picks(out: FinderPickOut, shortlist: Shortlist, snapshot: Snapshot,
                sheets: dict[str, dict[str, Fact]]) -> list[str]:
    """Every guard the picks break. An empty list means the picks stand."""
    if not out.picks:
        if not (out.none_line or "").strip():
            return ["a response with no pick needs a none_line in plain words"]
        return inner_word_failures("none_line", out.none_line or "")
    if len(out.picks) > MAX_PICKS:
        return [f"the response has {len(out.picks)} picks; the most is {MAX_PICKS}"]
    offers = {offer.offer_id: offer for offer in shortlist.shortlist}
    failures, seen = [], set()
    for number, pick in enumerate(out.picks, start=1):
        label = f"pick {number}"
        if pick.offer_id not in offers:
            failures.append(f"{label}: offer {pick.offer_id} is not on the shortlist")
            continue
        if pick.offer_id in seen:
            failures.append(f"{label}: offer {pick.offer_id} is picked twice")
        seen.add(pick.offer_id)
        if pick.lean not in SEND_LEANS:
            failures.append(f"{label}: its Lean is {pick.lean}; pick only an offer you would read as "
                            f"{', '.join(SEND_LEANS[:-1])}, or {SEND_LEANS[-1]}")
        sheet = sheets[pick.offer_id]
        guard = TextGuard(offers[pick.offer_id].trade, snapshot, sheet)
        pick_failures, cited = bullet_failures(label, pick.bullets, sheet, guard,
                                               sheet=f"the sheet of offer {pick.offer_id}", least=MIN_BULLETS,
                                               most=MAX_BULLETS)
        failures += pick_failures
        failures += guard.text_failures(f"{label} headline", pick.headline, cited)
    return failures


def _fact_lines(offer: ShortlistOffer, sheet: dict[str, Fact]) -> list[str]:
    """The plain facts of a fallback offer: the points per game of each traded player, in the order of the sides."""
    return [sheet[f"{pid}.ppg"].text for side in offer.trade.sides for pid in side.player_ids if f"{pid}.ppg" in sheet]


def pick_trades(shortlist: Shortlist, snapshot: Snapshot, *, news: NewsFeed,
                call: ClaudeCall = finder_pick_call) -> FinderPicks:
    """The picks of the Advisor from the shortlist. An empty shortlist makes no call and gives the NO_OFFER line.

    A failed guard retries once with the failures as feedback. After two failed calls, a failed API call included,
    each shortlist offer stands with its fact lines and the fallback flag.
    """
    if not shortlist.shortlist:
        return FinderPicks(picks=[], none_line=NO_OFFER, fallback=False)
    sheets = {offer.offer_id: offer_sheet(offer, snapshot, news) for offer in shortlist.shortlist}
    out = call_with_retry(
        call, lambda feedback: build_pick_prompt(shortlist, snapshot, sheets, feedback), FinderPickOut,
        lambda out: check_picks(out, shortlist, snapshot, sheets), subject="finder pick", log_label="finder pick",
        logger=log)
    if out is None:
        # A code answer never takes the place of advice, so the shortlist shows plain facts with no headline.
        return FinderPicks(picks=[FinderPick(offer=offer, headline=None, bullets=[],
                                             fact_lines=_fact_lines(offer, sheets[offer.offer_id]))
                                  for offer in shortlist.shortlist], none_line=None, fallback=True)
    offers = {offer.offer_id: offer for offer in shortlist.shortlist}
    picks = [FinderPick(offer=offers[pick.offer_id], headline=pick.headline, fact_lines=[],
                        bullets=read_bullets(pick.bullets, sheets[pick.offer_id])) for pick in out.picks]
    return FinderPicks(picks=picks, none_line=None if picks else out.none_line, fallback=False)
