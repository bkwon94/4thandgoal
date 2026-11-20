"""
The Finder pick: one sheet per shortlist offer, then one Advisor call that picks up to 3 offers, each with a Lean, a
Case of at most 3 sentences, and 2 to 4 Bullets, and up to 3 near ideas, each with the reason it fell short. A failed
pick gets one repair call on its own sheet. With no pick and no near idea left, the shortlist stands with fact lines.
"""
import contextvars
import logging
import re
import string
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor

from pydantic import BaseModel, Field

from analyzer.advisor import (
    CONDITION,
    FIRST_SENTENCE,
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
from analyzer.team_facts import lineup_now_fact
from analyzer.trade_jev import jev_answer_facts, trade_jev_questions
from analyzer.trade_news import NewsFeed
from facts.tokens import Nums, fact
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
# The most near ideas of one press. An idea is an idea, so a list with offers always shows at least one.
MAX_NEAR = 3
MIN_BULLETS, MAX_BULLETS = 2, 4
# The lines of a press whose search kept no offer. No Claude call runs, so code writes them. NO_PARTNER is for a
# search where no team passed the partner filter, and NO_OFFER for a search where the teams that passed gave no offer.
NO_PARTNER = "No other team has a starter for your weak spots that it can spare, so no trade came up."
NO_OFFER = "No team has a player who fits this ask, so no trade came up."
# The line when each pick failed its repair and only near ideas stand, so the Advisor gave no none_line of its own.
NO_CLEAR_PICK = "No offer on the list is a clear win, so these are ideas to weigh."
# The Leans of a trade that the asker sends. A pick reads as one of them, so the analyzer read of a pick agrees.
SEND_LEANS = ("Send it", "Lean yes", "Gut call")
# The text of a fact that an earlier offer of the message gave in full. The id stays, so a Bullet may cite it.
SAME_FACT = "(the same text as in an earlier offer)"
# The most sentences of the Case of a pick. The card shows the Case under the Lean, so it stays short.
MAX_CASE_SENTENCES = 3
# The end of one sentence: a stop that a space or the end of the text follows, so "2.5" is no end.
SENTENCE_END = re.compile(r"[.!?](?=\s|$)")
# The short label of each offer in the pick prompt, in the order of the shortlist. An offer id is long, such as
# "4:7569-12:10236+8146", and the Advisor copied it wrong in 4 of 6 calls (decision 02). A label is one letter, and
# code maps it back to its offer.
LABELS = string.ascii_uppercase
# A job that runs after the Answer goes out, such as the log-only Jev checks.
Job = Callable[[], None]
Defer = Callable[[Job], None]


def run_now(job: Job) -> None:
    """The default Defer: it runs the job at once, for a caller with no Answer to send first."""
    job()


class PickOut(BaseModel):
    """One pick as the Advisor gives it: the label of the offer, the Lean of the trade if the asker graded it alone,
    the Case of at most 3 sentences with its condition first, and 2 to 4 Bullets."""

    label: str
    lean: Lean
    case: str = Field(description=f"At most {MAX_CASE_SENTENCES} sentences; the first holds the condition")
    # The counts sit in the description, so the model reads them in the schema. The API does not enforce an array
    # count above minItems 1, and a min_length or max_length here only moves the check into the SDK, so the guard
    # checks the count and retries.
    bullets: list[Bullet] = Field(description=f"{MIN_BULLETS} to {MAX_BULLETS} Bullets")


class NearOut(BaseModel):
    """One near idea as the Advisor gives it: the label of an offer that it would not send, the one reason it fell
    short for the asker, and the one fact that the reason rests on, so the reason gets the guards of a Bullet."""

    label: str
    reason: str
    fact_id: str


class FinderPickOut(BaseModel):
    """The structured output of the pick call: up to 3 picks, up to 3 near ideas, and with no pick a plain line that
    says why."""

    # The count is a description only, as with the Bullets: the guard checks it.
    picks: list[PickOut] = Field(description=f"Up to {MAX_PICKS} picks")
    near: list[NearOut] = Field(description=f"Up to {MAX_NEAR} near ideas; at least 1 when there is no pick")
    none_line: str | None


class FinderPick(BaseModel):
    """One trade of the finder document: its shortlist offer, and the Lean, the Case, and the Bullets of the Advisor.

    After a fallback, the Lean and the Case are None, no Bullet stands, and the fact lines hold plain facts of the offer.
    """

    offer: ShortlistOffer
    lean: Lean | None
    case: str | None
    bullets: list[ReadBullet]
    fact_lines: list[str]


class NearIdea(BaseModel):
    """One near idea of the finder document: its shortlist offer, and the reason of the Advisor that it fell short."""

    offer: ShortlistOffer
    reason: str


class _PickSide(BaseModel):
    """The Bullets of one pick in the shape of a side, for the Jev checks. The Bullets advise the asker."""

    roster_id: int
    bullets: list[Bullet]


class FinderPicks(BaseModel):
    """What a Finder press gives: the picks, the near ideas, the plain line when no pick stands, and whether the call
    fell back."""

    picks: list[FinderPick]
    near: list[NearIdea] = []
    none_line: str | None
    fallback: bool


def spare_facts(offer: ShortlistOffer, snapshot: Snapshot) -> dict[str, Fact]:
    """One fact by id for each player that the asker gets with a Spares tree "yes", such as "For Bo Girds, Patrick
    Mahomes fills the weak slot QB, and To Infinity and Bijan can spare him." It is a reason for the Case, never a gate
    (decision 16)."""
    asker = snapshot.teams[offer.trade.asker].name
    facts = {}
    for side in offer.trade.sides[1:]:
        partner = snapshot.teams[side.roster_id].name
        for pid in side.player_ids:
            if pid not in offer.spares:
                continue
            n = Nums()
            name = snapshot.players[pid].name
            # The slot goes through Nums, so the checker accepts a slot name with a digit, such as "RB2".
            text = f"For {asker}, {name} fills the weak slot {n.text(offer.spares[pid])}, and {partner} can spare him."
            facts[f"{pid}.spare"] = fact(f"{pid}.spare", text, n, [asker, partner], [name])
    return facts


def offer_sheet(offer: ShortlistOffer, snapshot: Snapshot, news: NewsFeed) -> dict[str, Fact]:
    """The facts of one shortlist offer by id: the measured facts of its trade, with the news of its players only,
    the lineup now of the asker, the Spares tree facts, then the Jev answers of the shortlist as JEV facts, so the
    pick makes no new Jev call. After a failed request the offer holds no Jev answer of that step, so the sheet states
    none, never "unsure"."""
    trade = offer.trade
    nouls = {} if offer.failed else {f"need.{rid}": p for rid, p in offer.needs.items()}
    if not offer.fair_failed:
        nouls["fair"] = offer.fair
    questions = trade_jev_questions(trade, snapshot)
    now = lineup_now_fact(snapshot, trade.asker)
    return {**measured_sheet(trade, snapshot, news), **({} if now is None else {now.id: now}),
            **spare_facts(offer, snapshot),
            **jev_answer_facts(trade, snapshot, questions, {key: p for key, p in nouls.items() if key in questions})}


def labeled(shortlist: Shortlist) -> dict[str, ShortlistOffer]:
    """Each shortlist offer by its label, A to J, in the order of the shortlist."""
    return dict(zip(LABELS, shortlist.shortlist, strict=False))


def label_of(text: str) -> str:
    """The label that the Advisor wrote, read plainly: "Offer B" and " b " are both "B"."""
    text = text.strip()
    if text.lower().startswith("offer "):
        text = text[len("offer "):]
    return text.strip().upper()


def build_pick_prompt(shortlist: Shortlist, snapshot: Snapshot, sheets: dict[str, dict[str, Fact]],
                      feedback: str | None) -> tuple[str, str]:
    """The system prompt and the user message of the pick call: each offer with its label, its sides, and its own
    facts."""
    lines = [f"The asker: roster {shortlist.asker}, {snapshot.teams[shortlist.asker].name}.", ""]
    # One player or one team sits on many offers, so a fact text that an earlier offer gave is not sent again. This
    # keeps the message, and the cost and the time of the call, near those of one read.
    given: set[tuple[str, str]] = set()
    for label, offer in labeled(shortlist).items():
        lines += [f"Offer {label}", *side_lines(offer.trade, snapshot), "Facts:"]
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
    if len(out.near) > MAX_NEAR:
        return [f"the response has {len(out.near)} near ideas; the most is {MAX_NEAR}"]
    if not out.picks:
        if not (out.none_line or "").strip():
            return ["a response with no pick needs a none_line in plain words"]
        # An idea is an idea: the shortlist has offers, so the asker always sees at least one.
        if not out.near:
            return ["a response with no pick needs at least one near idea, the offer that came closest"]
        return inner_word_failures("none_line", out.none_line or "")
    if len(out.picks) > MAX_PICKS:
        return [f"the response has {len(out.picks)} picks; the most is {MAX_PICKS}"]
    offers = labeled(shortlist)
    failures, seen = [], set()
    for number, pick in enumerate(out.picks, start=1):
        if label_of(pick.label) in seen:
            failures.append(f"pick {number}: offer {pick.label} is picked twice")
        seen.add(label_of(pick.label))
    # A pick of a label that is not on the shortlist has no sheet, so no repair can fix it. Such a pick drops when
    # another pick names a real offer, and only a response of such picks alone retries.
    if not any(label_of(pick.label) in offers for pick in out.picks):
        failures += [f"pick {number}: offer {pick.label} is not on the shortlist"
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
    case = pick.case.strip()
    first = FIRST_SENTENCE.match(case)
    if first is None or not CONDITION.search(first.group()):
        failures.append(f"{label} case: the first sentence must hold the condition, with 'if' or 'as long as'")
    sentences = len(SENTENCE_END.findall(case))
    if sentences > MAX_CASE_SENTENCES:
        failures.append(f"{label} case: it has {sentences} sentences; the most is {MAX_CASE_SENTENCES}")
    guard = TextGuard(offer.trade, snapshot, sheet)
    bullet_fails, cited = bullet_failures(label, pick.bullets, sheet, guard, sheet=f"the sheet of offer {pick.label}",
                                          least=MIN_BULLETS, most=MAX_BULLETS)
    return failures + bullet_fails + guard.text_failures(f"{label} case", pick.case, cited)


def check_picks(out: FinderPickOut, shortlist: Shortlist, snapshot: Snapshot,
                sheets: dict[str, dict[str, Fact]]) -> list[list[str]]:
    """The guards that each pick breaks, in the order of the picks. An empty list means that pick stands, so one bad
    pick never fails the picks that pass."""
    offers = labeled(shortlist)
    failures = []
    for number, pick in enumerate(out.picks, start=1):
        label = f"pick {number}"
        offer = offers.get(label_of(pick.label))
        if offer is None:
            failures.append([f"{label}: offer {pick.label} is not on the shortlist"])
            continue
        failures.append(pick_failures(label, pick, offer, snapshot, sheets[offer.offer_id]))
    return failures


def near_failures(label: str, near: NearOut, offer: ShortlistOffer, snapshot: Snapshot,
                  sheet: dict[str, Fact]) -> list[str]:
    """Every guard that one near idea breaks, on the sheet of its offer. Its reason is checked as one Bullet that cites
    its fact. An empty list means the near idea stands."""
    bullet = Bullet(text=near.reason, mark="against", fact_id=near.fact_id)
    failures, _ = bullet_failures(label, [bullet], sheet, TextGuard(offer.trade, snapshot, sheet),
                                  sheet=f"the sheet of offer {near.label}", least=1, most=1)
    # The reason is the one claim of the near idea, so its failures name the near idea alone.
    return [failure.replace(f"{label} bullet 1", label, 1) for failure in failures]


def standing_near(out: FinderPickOut, picked: set[str], shortlist: Shortlist, snapshot: Snapshot,
                  sheets: dict[str, dict[str, Fact]]) -> list[tuple[NearOut, ShortlistOffer]]:
    """The near ideas that stand, in their order, each with its offer. `picked` holds the offer ids of the picks. A
    near idea is no advice to send, so one that fails a guard gets no repair: it drops, and the log says why. A near
    idea of a picked offer, a repeat, or an offer off the list drops."""
    offers = labeled(shortlist)
    stand, seen = [], set(picked)
    for number, near in enumerate(out.near, start=1):
        label = f"near {number}"
        offer = offers.get(label_of(near.label))
        if offer is None:
            failures = [f"{label}: offer {near.label} is not on the shortlist"]
        elif offer.offer_id in seen:
            failures = [f"{label}: offer {near.label} is a pick or an earlier near idea"]
        else:
            failures = near_failures(label, near, offer, snapshot, sheets[offer.offer_id])
        if failures:
            # A failure can quote a trade value, so the log line masks every number after the label.
            log.warning("finder %s dropped: %s", label,
                        "; ".join(ANY_NUMBER.sub("#", fail.removeprefix(f"{label}: ")) for fail in failures))
            continue
        seen.add(offer.offer_id)
        stand.append((near, offer))
    return stand


def build_repair_prompt(label: str, offer: ShortlistOffer, asker: int, snapshot: Snapshot, sheet: dict[str, Fact],
                        pick: PickOut, failures: list[str]) -> tuple[str, str]:
    """The system prompt and the user message of the repair of one pick: its offer with its label, its one sheet with
    each fact in full, the pick that failed, and its failures. The other offers stay out, so the call is small."""
    lines = [f"The asker: roster {asker}, {snapshot.teams[asker].name}.", "",
             f"Offer {label}", *side_lines(offer.trade, snapshot), "Facts:",
             *(f"- {fid}: {f.text}" for fid, f in sheet.items()), "",
             "The pick that failed:", pick.model_dump_json(indent=2), "",
             f"Failures: {'; '.join(failures)}", "",
             f"Give the pick of offer {label} again, with each failure fixed."]
    return system_prompt(snapshot, REPAIR_PROMPT_FILE), "\n".join(lines)


def _repair(number: int, pick: PickOut, failures: list[str], label: str, offer: ShortlistOffer, asker: int,
            snapshot: Snapshot, sheet: dict[str, Fact], call: ClaudeCall) -> PickOut | None:
    """One repair call for one failed pick, with the same guards on its answer. The repaired pick, or None when the
    call fails or its answer fails a guard again. No code trims a Bullet or changes the text of a judgment."""
    where = f"pick {number}"
    try:
        fixed = call(*build_repair_prompt(label, offer, asker, snapshot, sheet, pick, failures), PickOut)
        # Any call, real or injected, can come back empty. That is a failed repair.
        if fixed is None:
            raise WriterError(f"no parsed output for the repair of {where}")
        if label_of(fixed.label) != label:
            again = [f"{where}: the repair must keep offer {label}; it gave {fixed.label}"]
        else:
            again = pick_failures(where, fixed, offer, snapshot, sheet)
    except CHECK_ERRORS as err:
        again = [str(err)]
    if again:
        # A failure can quote a trade value, so the log line masks every number, as the retry of a call does.
        log.warning("finder repair of %s failed: %s", where, ANY_NUMBER.sub("#", "; ".join(again)))
        return None
    log.info("finder repair of %s passed", where)
    return fixed


def _repair_picks(out: FinderPickOut, failures: list[list[str]], shortlist: Shortlist, snapshot: Snapshot,
                  sheets: dict[str, dict[str, Fact]], call: ClaudeCall) -> list[tuple[PickOut, ShortlistOffer]]:
    """The picks that stand, in the order of the picks, each with its offer: each pick that passed, and each failed
    pick that one repair call fixed. The repairs run at the same time, so the time of a press adds the longest repair
    only."""
    offers = labeled(shortlist)
    jobs = {}
    for number, (pick, fails) in enumerate(zip(out.picks, failures, strict=True), start=1):
        if fails:
            log.warning("finder pick %d failed: %s", number, ANY_NUMBER.sub("#", "; ".join(fails)))
        if fails and label_of(pick.label) in offers:
            jobs[number] = pick, fails
    repaired: dict[int, PickOut | None] = {}
    if jobs:
        with ThreadPoolExecutor(max_workers=len(jobs)) as pool:
            # Each repair runs in a copy of the context of the press, so the press meter counts its call.
            futures = {}
            for number, (pick, fails) in jobs.items():
                label = label_of(pick.label)
                offer = offers[label]
                futures[number] = pool.submit(contextvars.copy_context().run, _repair, number, pick, fails, label,
                                              offer, shortlist.asker, snapshot, sheets[offer.offer_id], call)
            repaired = {number: future.result() for number, future in futures.items()}
    stand = []
    for number, (pick, fails) in enumerate(zip(out.picks, failures, strict=True), start=1):
        fixed = repaired.get(number) if fails else pick
        if fixed is not None:
            stand.append((fixed, offers[label_of(pick.label)]))
    return stand


def _fact_lines(offer: ShortlistOffer, sheet: dict[str, Fact]) -> list[str]:
    """The plain facts of a fallback offer: the points per game of each traded player, in the order of the sides."""
    return [sheet[f"{pid}.ppg"].text for side in offer.trade.sides for pid in side.player_ids if f"{pid}.ppg" in sheet]


def offer_sheets(shortlist: Shortlist, snapshot: Snapshot, news: NewsFeed) -> dict[str, dict[str, Fact]]:
    """The sheet of each shortlist offer by offer id. The sheets build at the same time, because each one reads the
    news of its players, and one after the other they took 1 to 2 s of a press (decision 02)."""
    offers = shortlist.shortlist
    with ThreadPoolExecutor(max_workers=len(offers)) as pool:
        futures = [pool.submit(contextvars.copy_context().run, offer_sheet, offer, snapshot, news) for offer in offers]
        return {offer.offer_id: future.result() for offer, future in zip(offers, futures, strict=True)}


def _log_checks(stand: list[tuple[PickOut, ShortlistOffer]], near: list[tuple[NearOut, ShortlistOffer]], asker: int,
                sheets: dict[str, dict[str, Fact]], jev: Jev) -> None:
    """The Jev checks of each pick and of the reason of each near idea against its own sheet, as on the read of one
    trade. They only log, so no answer and no failure ever blocks a pick."""
    for pick, offer in stand:
        log_read_jev_checks([_PickSide(roster_id=asker, bullets=pick.bullets)], sheets[offer.offer_id], jev)
    for idea, offer in near:
        reason = Bullet(text=idea.reason, mark="against", fact_id=idea.fact_id)
        log_read_jev_checks([_PickSide(roster_id=asker, bullets=[reason])], sheets[offer.offer_id], jev)


def pick_trades(shortlist: Shortlist, snapshot: Snapshot, *, news: NewsFeed, jev: Jev,
                call: ClaudeCall = finder_pick_call, repair_call: ClaudeCall = finder_repair_call,
                stage: Stage = quiet, defer: Defer = run_now) -> FinderPicks:
    """The picks and the near ideas of the Advisor from the shortlist. An empty shortlist makes no call and gives the
    NO_PARTNER line when no team passed the partner filter, else the NO_OFFER line.

    One call picks the best 3 across every partner. Each offer has a label, A to J, in the prompt, and code maps the
    label back to its offer. A failure of the whole response retries the pick call once with the failures as feedback.
    A pick that fails its own guards gets one repair call on its own sheet, and a pick that fails again drops. So only a
    pick that reads Send it, Lean yes, or Gut call stands. A near idea that fails its guards drops with no repair. When
    no pick and no near idea stand, after two failed calls or after the repairs, each shortlist offer stands with its
    fact lines and the fallback flag.
    `stage` gets one live line before the call and one done line when the picks stand. The default drops them.
    `defer` gets the log-only Jev checks, so a route runs them after its Answer goes out. The default runs them now.
    """
    if not shortlist.shortlist:
        passed = any(read.passed for read in shortlist.partners)
        return FinderPicks(picks=[], none_line=NO_OFFER if passed else NO_PARTNER, fallback=False)
    most = min(MAX_PICKS, len(shortlist.shortlist))
    # A pick with no offer that stands sends no done line, so the site drops this live line with the Answer.
    stage(f"Picking the best {most}" if most > 1 else "Picking the best one", live=True)
    sheets = offer_sheets(shortlist, snapshot, news)
    out = call_with_retry(
        call, lambda feedback: build_pick_prompt(shortlist, snapshot, sheets, feedback), FinderPickOut,
        lambda out: response_failures(out, shortlist), subject="finder pick", log_label="finder pick", logger=log)
    stand = [] if out is None or not out.picks else _repair_picks(
        out, check_picks(out, shortlist, snapshot, sheets), shortlist, snapshot, sheets, repair_call)
    near = [] if out is None else standing_near(out, {offer.offer_id for _, offer in stand}, shortlist, snapshot,
                                                sheets)
    if not stand and not near:
        # A code answer never takes the place of advice, so the shortlist shows plain facts with no Lean and no Case.
        return FinderPicks(picks=[FinderPick(offer=offer, lean=None, case=None, bullets=[],
                                             fact_lines=_fact_lines(offer, sheets[offer.offer_id]))
                                  for offer in shortlist.shortlist], none_line=None, fallback=True)
    # The checks only log, so they wait until the Answer goes out and add no time to the press (decision 02).
    defer(lambda: _log_checks(stand, near, shortlist.asker, sheets, jev))
    if stand:
        stage(f"Picked the best {len(stand)}" if len(stand) > 1 else "Picked the best one")
    else:
        # No offer is a clear win, so the done line names the ideas that the pick weighed.
        stage(f"Kept {len(near)} ideas to weigh" if len(near) > 1 else "Kept one idea to weigh")
    picks = [FinderPick(offer=offer, lean=pick.lean, case=pick.case, fact_lines=[],
                        bullets=read_bullets(pick.bullets, sheets[offer.offer_id])) for pick, offer in stand]
    return FinderPicks(picks=picks, near=[NearIdea(offer=offer, reason=idea.reason) for idea, offer in near],
                       none_line=None if stand or out is None else out.none_line or NO_CLEAR_PICK, fallback=False)
