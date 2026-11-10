"""
The Finder pick: one sheet per shortlist offer, then one Advisor call that picks up to 3 offers, each with a headline
and 2 to 4 Bullets. A failed pick gets one repair call on its own sheet. With no pick left, the shortlist stands with
fact lines.
"""
import contextvars
import logging
from concurrent.futures import ThreadPoolExecutor

from pydantic import BaseModel, Field

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
from analyzer.read_jev_check import log_read_jev_checks
from analyzer.stage import Stage, quiet
from analyzer.trade_jev import jev_answer_facts, trade_jev_questions
from analyzer.trade_news import NewsFeed
from facts.writer import (
    ANY_NUMBER,
    CHECK_ERRORS,
    ClaudeCall,
    call_with_retry,
    finder_pick_call,
    finder_repair_call,
)
from league.claude_errors import WriterError
from league.jev_port import Jev
from league.models import Fact
from league.snapshot import Snapshot

log = logging.getLogger(__name__)

PROMPT_FILE = "finder_pick.md"
REPAIR_PROMPT_FILE = "finder_pick_repair.md"
MAX_PICKS = 3
MIN_BULLETS, MAX_BULLETS = 2, 4
# The line of a press whose search kept no offer. No Claude call runs, so code writes it.
NO_OFFER = "The search found no trade that works for both teams."
# The Leans of a trade that the asker sends. A pick reads as one of them, so the analyzer read of a pick agrees.
SEND_LEANS = ("Send it", "Lean yes", "Gut call")
# The text of a fact that an earlier offer of the message gave in full. The id stays, so a Bullet may cite it.
SAME_FACT = "(the same text as in an earlier offer)"


class PickOut(BaseModel):
    """One pick as the Advisor gives it: the offer id of the shortlist, the Lean of the trade if the asker graded it
    alone, a headline, and 2 to 4 Bullets. The Lean stays out of the document, because the card shows no Lean."""

    offer_id: str
    lean: Lean
    headline: str
    # The counts sit in the description, so the model reads them in the schema. The API does not enforce an array
    # count above minItems 1, and a min_length or max_length here only moves the check into the SDK, so the guard
    # checks the count and retries.
    bullets: list[Bullet] = Field(description=f"{MIN_BULLETS} to {MAX_BULLETS} Bullets")


class FinderPickOut(BaseModel):
    """The structured output of the pick call: up to 3 picks, or no pick and a plain line that says why."""

    # The count is a description only, as with the Bullets: the guard checks it.
    picks: list[PickOut] = Field(description=f"Up to {MAX_PICKS} picks")
    none_line: str | None


class FinderPick(BaseModel):
    """One trade of the finder document: its shortlist offer, and the headline and the Bullets of the Advisor.

    After a fallback, the headline is None, no Bullet stands, and the fact lines hold plain facts of the offer.
    """

    offer: ShortlistOffer
    headline: str | None
    bullets: list[ReadBullet]
    fact_lines: list[str]


class _PickSide(BaseModel):
    """The Bullets of one pick in the shape of a side, for the Jev checks. The Bullets advise the asker."""

    roster_id: int
    bullets: list[Bullet]


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


def response_failures(out: FinderPickOut, shortlist: Shortlist) -> list[str]:
    """The guards that the whole response breaks. A failure here retries the whole pick call, because no single pick
    is at fault. An empty list means each pick goes on to its own guards."""
    if not out.picks:
        if not (out.none_line or "").strip():
            return ["a response with no pick needs a none_line in plain words"]
        return inner_word_failures("none_line", out.none_line or "")
    if len(out.picks) > MAX_PICKS:
        return [f"the response has {len(out.picks)} picks; the most is {MAX_PICKS}"]
    offers = {offer.offer_id for offer in shortlist.shortlist}
    failures, seen = [], set()
    for number, pick in enumerate(out.picks, start=1):
        if pick.offer_id in seen:
            failures.append(f"pick {number}: offer {pick.offer_id} is picked twice")
        seen.add(pick.offer_id)
    # A pick of an offer that is not on the shortlist has no sheet, so no repair can fix it. Such a pick drops when
    # another pick names a real offer, and only a response of such picks alone retries.
    if not any(pick.offer_id in offers for pick in out.picks):
        failures += [f"pick {number}: offer {pick.offer_id} is not on the shortlist"
                     for number, pick in enumerate(out.picks, start=1)]
    return failures


def pick_failures(label: str, pick: PickOut, offer: ShortlistOffer, snapshot: Snapshot,
                  sheet: dict[str, Fact]) -> list[str]:
    """Every guard that one pick of a shortlist offer breaks, on the sheet of that offer. An empty list means the pick
    stands."""
    failures = []
    if pick.lean not in SEND_LEANS:
        failures.append(f"{label}: its Lean is {pick.lean}; pick only an offer you would read as "
                        f"{', '.join(SEND_LEANS[:-1])}, or {SEND_LEANS[-1]}")
    guard = TextGuard(offer.trade, snapshot, sheet)
    bullet_fails, cited = bullet_failures(label, pick.bullets, sheet, guard, sheet=f"the sheet of offer {offer.offer_id}",
                                          least=MIN_BULLETS, most=MAX_BULLETS)
    return failures + bullet_fails + guard.text_failures(f"{label} headline", pick.headline, cited)


def check_picks(out: FinderPickOut, shortlist: Shortlist, snapshot: Snapshot,
                sheets: dict[str, dict[str, Fact]]) -> list[list[str]]:
    """The guards that each pick breaks, in the order of the picks. An empty list means that pick stands, so one bad
    pick never fails the picks that pass."""
    offers = {offer.offer_id: offer for offer in shortlist.shortlist}
    failures = []
    for number, pick in enumerate(out.picks, start=1):
        label = f"pick {number}"
        if pick.offer_id not in offers:
            failures.append([f"{label}: offer {pick.offer_id} is not on the shortlist"])
            continue
        failures.append(pick_failures(label, pick, offers[pick.offer_id], snapshot, sheets[pick.offer_id]))
    return failures


def build_repair_prompt(offer: ShortlistOffer, asker: int, snapshot: Snapshot, sheet: dict[str, Fact],
                        pick: PickOut, failures: list[str]) -> tuple[str, str]:
    """The system prompt and the user message of the repair of one pick: its offer, its one sheet with each fact in
    full, the pick that failed, and its failures. The other offers stay out, so the call is small."""
    lines = [f"The asker: roster {asker}, {snapshot.teams[asker].name}.", "",
             f"Offer {offer.offer_id}", *side_lines(offer.trade, snapshot), "Facts:",
             *(f"- {fid}: {f.text}" for fid, f in sheet.items()), "",
             "The pick that failed:", pick.model_dump_json(indent=2), "",
             f"Failures: {'; '.join(failures)}", "",
             f"Give the pick of offer {offer.offer_id} again, with each failure fixed."]
    return system_prompt(snapshot, REPAIR_PROMPT_FILE), "\n".join(lines)


def _repair(label: str, pick: PickOut, failures: list[str], offer: ShortlistOffer, asker: int, snapshot: Snapshot,
            sheet: dict[str, Fact], call: ClaudeCall) -> PickOut | None:
    """One repair call for one failed pick, with the same guards on its answer. The repaired pick, or None when the
    call fails or its answer fails a guard again. No code trims a Bullet or changes the text of a judgment."""
    try:
        fixed = call(*build_repair_prompt(offer, asker, snapshot, sheet, pick, failures), PickOut)
        # Any call, real or injected, can come back empty. That is a failed repair.
        if fixed is None:
            raise WriterError(f"no parsed output for the repair of {label}")
        if fixed.offer_id != offer.offer_id:
            again = [f"{label}: the repair must keep offer {offer.offer_id}; it gave {fixed.offer_id}"]
        else:
            again = pick_failures(label, fixed, offer, snapshot, sheet)
    except CHECK_ERRORS as err:
        again = [str(err)]
    if again:
        # A failure can quote a trade value, so the log line masks every number, as the retry of a call does.
        log.warning("finder repair of %s failed: %s", label, ANY_NUMBER.sub("#", "; ".join(again)))
        return None
    log.info("finder repair of %s passed", label)
    return fixed


def _repair_picks(out: FinderPickOut, failures: list[list[str]], shortlist: Shortlist, snapshot: Snapshot,
                  sheets: dict[str, dict[str, Fact]], call: ClaudeCall) -> list[PickOut]:
    """The picks that stand, in the order of the picks: each pick that passed, and each failed pick that one repair
    call fixed. The repairs run at the same time, so the time of a press adds the longest repair only."""
    offers = {offer.offer_id: offer for offer in shortlist.shortlist}
    jobs = {}
    for number, (pick, fails) in enumerate(zip(out.picks, failures, strict=True), start=1):
        if fails:
            log.warning("finder pick %d failed: %s", number, ANY_NUMBER.sub("#", "; ".join(fails)))
        if fails and pick.offer_id in offers:
            jobs[number] = pick, fails
    repaired: dict[int, PickOut | None] = {}
    if jobs:
        with ThreadPoolExecutor(max_workers=len(jobs)) as pool:
            # Each repair runs in a copy of the context of the press, so the press meter counts its call.
            futures = {number: pool.submit(contextvars.copy_context().run, _repair, f"pick {number}", pick, fails,
                                           offers[pick.offer_id], shortlist.asker, snapshot, sheets[pick.offer_id],
                                           call)
                       for number, (pick, fails) in jobs.items()}
            repaired = {number: future.result() for number, future in futures.items()}
    stand = []
    for number, (pick, fails) in enumerate(zip(out.picks, failures, strict=True), start=1):
        fixed = repaired.get(number) if fails else pick
        if fixed is not None:
            stand.append(fixed)
    return stand


def _fact_lines(offer: ShortlistOffer, sheet: dict[str, Fact]) -> list[str]:
    """The plain facts of a fallback offer: the points per game of each traded player, in the order of the sides."""
    return [sheet[f"{pid}.ppg"].text for side in offer.trade.sides for pid in side.player_ids if f"{pid}.ppg" in sheet]


def pick_trades(shortlist: Shortlist, snapshot: Snapshot, *, news: NewsFeed, jev: Jev,
                call: ClaudeCall = finder_pick_call, repair_call: ClaudeCall = finder_repair_call,
                stage: Stage = quiet) -> FinderPicks:
    """The picks of the Advisor from the shortlist. An empty shortlist makes no call and gives the NO_OFFER line.

    A failure of the whole response retries the pick call once with the failures as feedback. A pick that fails its
    own guards gets one repair call on its own sheet, and a pick that fails again drops. When no pick stands, after
    two failed calls or after the repairs, each shortlist offer stands with its fact lines and the fallback flag.
    `stage` gets one plain line when the picks stand. The default drops it.
    """
    if not shortlist.shortlist:
        return FinderPicks(picks=[], none_line=NO_OFFER, fallback=False)
    sheets = {offer.offer_id: offer_sheet(offer, snapshot, news) for offer in shortlist.shortlist}
    out = call_with_retry(
        call, lambda feedback: build_pick_prompt(shortlist, snapshot, sheets, feedback), FinderPickOut,
        lambda out: response_failures(out, shortlist), subject="finder pick", log_label="finder pick", logger=log)
    if out is not None and not out.picks:
        return FinderPicks(picks=[], none_line=out.none_line, fallback=False)
    stand = [] if out is None else _repair_picks(out, check_picks(out, shortlist, snapshot, sheets), shortlist,
                                                 snapshot, sheets, repair_call)
    if not stand:
        # A code answer never takes the place of advice, so the shortlist shows plain facts with no headline.
        return FinderPicks(picks=[FinderPick(offer=offer, headline=None, bullets=[],
                                             fact_lines=_fact_lines(offer, sheets[offer.offer_id]))
                                  for offer in shortlist.shortlist], none_line=None, fallback=True)
    # The Jev checks run on each pick against its own sheet, as on the read of one trade. They only log, so no answer
    # and no failure ever blocks a pick.
    for pick in stand:
        log_read_jev_checks([_PickSide(roster_id=shortlist.asker, bullets=pick.bullets)], sheets[pick.offer_id], jev)
    stage(f"Picked the best {len(stand)}" if len(stand) > 1 else "Picked the best one")
    offers = {offer.offer_id: offer for offer in shortlist.shortlist}
    picks = [FinderPick(offer=offers[pick.offer_id], headline=pick.headline, fact_lines=[],
                        bullets=read_bullets(pick.bullets, sheets[pick.offer_id])) for pick in stand]
    return FinderPicks(picks=picks, none_line=None, fallback=False)
