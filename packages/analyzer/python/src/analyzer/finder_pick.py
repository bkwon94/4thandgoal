"""
The Finder pick: one sheet per shortlist offer, then one Advisor call that picks up to 5 offers and up to 3 near ideas.
A failed pick gets one repair call on its own sheet, and a stream gets each pick as soon as it stands.
"""
import contextvars
import logging
import re
import string
import threading
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Protocol, cast

from pydantic import BaseModel, Field, ValidationError
from pydantic_core import from_json

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
from analyzer.finder_search import Shortlist, ShortlistOffer, sheet_questions
from analyzer.read_jev_check import log_read_jev_checks
from analyzer.stage import Stage, quiet
from analyzer.team_facts import lineup_now_fact
from analyzer.trade_jev import jev_answer_facts, trade_jev_questions
from analyzer.trade_news import NewsFeed
from facts.names import last_name
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
# The most picks of one press. The Finder sparks varied ideas, so 5 picks show with up to 3 near ideas (decision 17).
MAX_PICKS = 5
# The most near ideas of one press. An idea is an idea, so a list with offers always shows at least one.
MAX_NEAR = 3
# Each pick has a Lean, a Case, and 2 to 4 Bullets.
MIN_BULLETS, MAX_BULLETS = 2, 4
# The line of a press whose search kept no offer. No Claude call runs, so code writes it. The Spares tree gives reasons,
# never a gate (decision 16), so no Spares tree answer picks this line.
NO_OFFER = "No team has a player who fits this ask, so no trade came up."
# The end of the line of a press with a Trade block whose search kept no offer. The line names the block players first.
NO_BLOCK_OFFER_END = "with the partner and the position you picked."
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


class StreamedCall(Protocol):
    """The Claude call of the pick with a stream: it gives `on_text` the JSON text of its answer as the text grows."""

    def __call__(self, system: str, user: str, output_model: type[BaseModel], *,
                 on_text: Callable[[str], None]) -> BaseModel: ...


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
    """The structured output of the pick call: up to 5 picks, up to 3 near ideas, with no pick a plain line that says
    why, and with fewer than 5 picks a plain line that says why it kept fewer."""

    # The count of picks comes first, so a stream reads it before the first pick, and the count line under the cards
    # shows the real count from the first card (AT-72). It is required, so the schema makes the model write it. No guard
    # checks it against the picks: the picks that stand are the truth.
    count: int = Field(description=f"How many picks you give, 0 to {MAX_PICKS}; write it first")
    # The count is a description only, as with the Bullets: the guard checks it.
    picks: list[PickOut] = Field(description=f"Up to {MAX_PICKS} picks")
    near: list[NearOut] = Field(description=f"Up to {MAX_NEAR} near ideas; at least 1 when there is no pick")
    none_line: str | None
    # The pick kept 3, 2, and 2 of 10 offers in three real presses, so it must say why it keeps fewer than 5. The line
    # only logs and rides in the document, so no guard checks it and no retry waits on it.
    short_line: str | None = Field(default=None, description=f"Why the pick keeps fewer than {MAX_PICKS}, else null")


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


# One pick that stands, sent to the caller as soon as it stands, in the order of the pick, with the most picks that the
# press can keep, so a stream can count the trades still to come. A stream sends it as a trade.
OnPick = Callable[[FinderPick, int], None]


def _drop(pick: FinderPick, most: int) -> None:
    """The default send of a pick: a press with no stream sends no pick before its end."""


# The word that the pick has no more trades, sent once, as soon as the streamed picks list closes and each of its picks
# stood or dropped. A stream sends it, so the site drops the count line when the pick keeps fewer than the most.
OnPicksEnd = Callable[[], None]


def _no_end() -> None:
    """The default word of the end: a press with no stream sends no word before its end."""


# The count of trades that the pick keeps, sent as soon as the streamed count closes, and again each time it changes:
# down when a pick drops, up when a pick stands past the count. A stream sends it, so the count line under the cards
# shows the real count from the first card (AT-72).
OnPicksCount = Callable[[int], None]


def _no_count(count: int) -> None:
    """The default send of the count: a press with no stream sends no count before its end."""


class FinderPicks(BaseModel):
    """What a Finder press gives: the picks, the near ideas, the plain line when no pick stands, and whether the call
    fell back."""

    picks: list[FinderPick]
    near: list[NearIdea] = []
    none_line: str | None
    fallback: bool
    # The plain line of the Advisor on why it kept fewer picks than it could, or None when it kept the most.
    short_line: str | None = None


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
    pick makes no new Jev call: the fair mean of step 1, and the need and the gain of each side of step 2. After a
    failed request the offer holds no Jev answer of that step, so the sheet states none, never "unsure"."""
    trade = offer.trade
    nouls = {} if offer.failed else {**{f"need.{rid}": p for rid, p in offer.needs.items()},
                                     **{f"gain.{rid}": p for rid, p in offer.gains.items()}}
    if not offer.fair_failed:
        nouls["fair"] = offer.fair
    # The need questions are those of one trade, and the fair and gain questions are those that the search asked.
    questions = {**trade_jev_questions(trade, snapshot), **sheet_questions(trade, snapshot)}
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


def no_block_offer_line(snapshot: Snapshot, trade_block: list[str]) -> str:
    """The line of a press whose search with a Trade block kept no offer, with the last name of each block player, such
    as "No fair trade sends Walker or Flowers with the partner and the position you picked." Code writes it, because no
    Claude call runs."""
    names = [last_name(snapshot.players[pid].name) or snapshot.players[pid].name for pid in trade_block]
    listed = " or ".join(names) if len(names) < 3 else f"{', '.join(names[:-1])}, or {names[-1]}"
    return f"No fair trade sends {listed} {NO_BLOCK_OFFER_END}"


def build_pick_prompt(shortlist: Shortlist, snapshot: Snapshot, sheets: dict[str, dict[str, Fact]],
                      feedback: str | None) -> tuple[str, str]:
    """The system prompt and the user message of the pick call: each offer with its label, its sides, and its own
    facts. With a Trade block, a line after the asker names the block players, so the pick can spread across them."""
    lines = [f"The asker: roster {shortlist.asker}, {snapshot.teams[shortlist.asker].name}."]
    if shortlist.trade_block:
        names = " and ".join(snapshot.players[pid].name for pid in shortlist.trade_block)
        lines.append(f"The Trade block: {names}.")
    lines.append("")
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


class _PickWatch:
    """The picks of one pick call, each checked as soon as the call has written it whole. A pick that passes stands at
    once, and a pick that fails gets its repair call at once, in a thread of `pool`, so the repairs run at the same
    time. Each pick that stands goes to `send` in the order of the pick, so a stream shows the first trade long before
    the call ends (decision 20).

    `sent` holds the offer id of each pick that went out. The attempts of one press share it, so a retried call never
    sends one trade twice. A closed watch sends nothing more, because the answer of its call failed.
    """

    def __init__(self, shortlist: Shortlist, snapshot: Snapshot, sheets: dict[str, dict[str, Fact]],
                 repair_call: ClaudeCall, pool: ThreadPoolExecutor, send: OnPick, sent: set[str], most: int,
                 end: OnPicksEnd = _no_end, count: OnPicksCount = _no_count) -> None:
        self._offers = labeled(shortlist)
        self._asker = shortlist.asker
        self._snapshot = snapshot
        self._sheets = sheets
        self._repair_call = repair_call
        self._pool = pool
        self._send = send
        self._sent = sent
        self._most = most
        self._end = end
        self._count = count
        # The count of picks that the call states, or None until the stream has closed it.
        self._stated: int | None = None
        # The count that went out last, so a send goes out only when the count changes.
        self._count_sent: int | None = None
        # The count of picks of this call that stood, in the order of the pick, whether this watch or an earlier attempt
        # sent its trade.
        self._stood = 0
        # True once the picks list of the call has closed, so no pick comes after the picks that the watch holds.
        self._ended = False
        self._end_sent = False
        self._picks: list[PickOut | None] = []
        self._results: list[Future[PickOut | None]] = []
        self._next = 0
        self._closed = False
        # A repair ends in its own thread, so its send and the send of the call thread take turns.
        self._lock = threading.Lock()

    def feed(self, text: str) -> None:
        """Read the JSON text of the call so far, and check each pick that it now holds whole. A pick is whole when the
        next pick starts, or when the picks list ends, which a key after "picks" shows."""
        try:
            partial = from_json(text, allow_partial=True)
        except ValueError:
            return
        if not isinstance(partial, dict) or not isinstance(partial.get("picks"), list):
            return
        keys = list(partial)
        # A value is whole when a later key starts. The count comes before the picks, so it is whole before any pick.
        if self._stated is None and "count" in keys and keys.index("count") < len(keys) - 1:
            stated = partial["count"]
            if isinstance(stated, int) and not isinstance(stated, bool):
                with self._lock:
                    self._stated = max(0, min(stated, self._most))
                    self._send_count()
        picks = partial["picks"]
        ended = keys.index("picks") < len(keys) - 1
        for index in range(len(self._picks), len(picks) if ended else len(picks) - 1):
            try:
                pick = PickOut.model_validate(picks[index])
            except ValidationError:
                # The whole answer fails its parse too, so the call fails and runs again.
                pick = None
            self._start(pick)
        if ended and not self._ended:
            self._ended = True
            self._flush()

    def _start(self, pick: PickOut | None) -> None:
        """Check one whole pick, and stand it, start its repair, or drop it."""
        number = len(self._picks) + 1
        label = None if pick is None else label_of(pick.label)
        offer = None if label is None else self._offers.get(label)
        earlier = {label_of(p.label) for p in self._picks if p is not None}
        future: Future[PickOut | None] = Future()
        if pick is None or label is None or offer is None or label in earlier or number > MAX_PICKS:
            # A pick off the list, a repeat, or a pick past the most has no repair. The response check drops it or
            # runs the call again.
            if pick is not None and offer is None:
                log.warning("finder pick %d failed: offer %s is not on the shortlist", number, pick.label)
            future.set_result(None)
        else:
            sheet = self._sheets[offer.offer_id]
            fails = pick_failures(f"pick {number}", pick, offer, self._snapshot, sheet)
            if fails:
                log.warning("finder pick %d failed: %s", number, ANY_NUMBER.sub("#", "; ".join(fails)))
                # The repair runs in a copy of the context of the press, so the press meter counts its call.
                future = self._pool.submit(contextvars.copy_context().run, _repair, number, pick, fails, label,
                                           offer, self._asker, self._snapshot, sheet, self._repair_call)
            else:
                future.set_result(pick)
        with self._lock:
            self._picks.append(pick)
            self._results.append(future)
        future.add_done_callback(lambda _: self._flush())

    def _total(self) -> int:
        """The count of trades that this call keeps: the stated count less each pick that dropped, and never less than
        the picks that stood. With no stated count, it is the most picks of the press. The caller holds the lock."""
        if self._stated is None:
            return self._most
        dropped = sum(1 for future in self._results
                      if future.done() and not future.cancelled() and future.result() is None)
        return max(self._stood, self._stated - dropped)

    def _send_count(self) -> None:
        """Send the count of trades when it differs from the count that went out last. The caller holds the lock."""
        if self._closed or self._stated is None:
            return
        total = self._total()
        if total != self._count_sent:
            self._count_sent = total
            self._count(total)

    def _flush(self) -> None:
        """Send each pick that stands, in the order of the pick, up to the first pick whose repair still runs."""
        with self._lock:
            # A pick that dropped lowers the count at once, even when an earlier repair still runs.
            self._send_count()
            while self._next < len(self._results) and self._results[self._next].done():
                # A closed watch reads no result, because close() cancels each repair that has not started.
                if self._closed:
                    self._next += 1
                    continue
                pick, fixed = self._picks[self._next], self._results[self._next].result()
                self._next += 1
                if pick is None or fixed is None:
                    continue
                offer = self._offers[label_of(pick.label)]
                self._stood += 1
                # A pick that stands past the stated count raises it before its trade goes out.
                self._send_count()
                if offer.offer_id not in self._sent:
                    self._sent.add(offer.offer_id)
                    self._send(_finder_pick(fixed, offer, self._sheets[offer.offer_id]), self._total())
            # The picks list has closed and each pick stood or dropped, so no trade of this call is still to come.
            if self._ended and self._next == len(self._results) and not self._closed and not self._end_sent:
                self._end_sent = True
                self._end()

    def close(self) -> None:
        """Send nothing more, because the answer of this call failed. Cancel each repair that has not started, so the
        press pays for no repair that it never uses. A repair that runs now ends in its pool, and its pick drops."""
        with self._lock:
            self._closed = True
            results = list(self._results)
        # The cancel runs outside the lock, because a cancel runs the done callback, and the callback takes the lock.
        for future in results:
            future.cancel()

    def finish(self, out: FinderPickOut) -> list[tuple[PickOut, ShortlistOffer]]:
        """Check each pick of the whole answer that the stream did not hold whole yet, wait for each repair, send each
        pick that is left, and give the picks that stand, in the order of the pick."""
        for pick in out.picks[len(self._picks):]:
            self._start(pick)
        # The whole answer is in, so its picks list has closed, even when the stream never showed the close.
        self._ended = True
        stand = []
        for pick, future in zip(self._picks, self._results, strict=True):
            fixed = future.result()
            if pick is not None and fixed is not None:
                stand.append((fixed, self._offers[label_of(pick.label)]))
        # A done callback of a repair can run after its result is ready, so this flush sends each pick before the end.
        self._flush()
        self.close()
        return stand


def _finder_pick(pick: PickOut, offer: ShortlistOffer, sheet: dict[str, Fact]) -> FinderPick:
    """One trade of the finder document from a pick that stands."""
    return FinderPick(offer=offer, lean=pick.lean, case=pick.case, fact_lines=[],
                      bullets=read_bullets(pick.bullets, sheet))


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
                stage: Stage = quiet, defer: Defer = run_now, on_pick: OnPick | None = None,
                on_picks_end: OnPicksEnd = _no_end, on_picks_count: OnPicksCount = _no_count) -> FinderPicks:
    """The picks and the near ideas of the Advisor from the shortlist. An empty shortlist makes no call and gives the
    NO_OFFER line, or with a Trade block the line that names the block players.

    One call picks the best 5 across every partner. Each offer has a label, A to J, in the prompt, and code maps the
    label back to its offer. A failure of the whole response retries the pick call once with the failures as feedback.
    A pick that fails its own guards gets one repair call on its own sheet, and a pick that fails again drops. So only a
    pick that reads Send it, Lean yes, or Gut call stands. A near idea that fails its guards drops with no repair. When
    no pick and no near idea stand, after two failed calls or after the repairs, each shortlist offer stands with its
    fact lines and the fallback flag.
    `stage` gets one live line before the call and one done line when the picks stand. The default drops them.
    `defer` gets the log-only Jev checks, so a route runs them after its Answer goes out. The default runs them now.
    With `on_pick`, the pick call streams, and each pick goes to `on_pick` as soon as it stands, with its guards passed
    or repaired, in the order of the pick, with the most picks of the press (decision 20). The `call` must then take `on_text`, as finder_pick_call does.
    With `on_pick`, `on_picks_end` gets one word when the pick has no more trades: as soon as the streamed picks list
    closes and each of its picks stood or dropped. A later attempt can still send a trade after it.
    With `on_pick`, `on_picks_count` gets the count of trades that the pick keeps, as soon as the streamed count closes,
    and again each time a drop or an extra pick changes it. Each trade carries the same count.
    The FinderPicks that the press gives stay the truth: a pick that went out from a failed answer is not in them.
    """
    if not shortlist.shortlist:
        # A search with a Trade block names its block players, so the asker knows which ask kept no trade.
        none_line = no_block_offer_line(snapshot, shortlist.trade_block) if shortlist.trade_block else NO_OFFER
        return FinderPicks(picks=[], none_line=none_line, fallback=False)
    most = min(MAX_PICKS, len(shortlist.shortlist))
    # A pick with no offer that stands sends no done line, so the site drops this live line with the Answer.
    stage(f"Picking the best {most}" if most > 1 else "Picking the best one", live=True)
    sheets = offer_sheets(shortlist, snapshot, news)
    sent: set[str] = set()
    watches: list[_PickWatch] = []
    # No `with` block holds the pool, because its exit waits for every repair, and a repair of a failed attempt is of
    # no use. The shutdown at the end waits for none: finish() already waited for each repair of the answer that stands.
    pool = ThreadPoolExecutor(max_workers=MAX_PICKS)
    try:
        def attempt(system: str, user: str, output_model: type[BaseModel]) -> BaseModel:
            watch = _PickWatch(shortlist, snapshot, sheets, repair_call, pool, on_pick or _drop, sent, most,
                               on_picks_end, on_picks_count)
            watches.append(watch)
            try:
                # Only a press that sends each pick streams the call, so a call with no stream keeps its plain shape.
                if on_pick is None:
                    return call(system, user, output_model)
                return cast(StreamedCall, call)(system, user, output_model, on_text=watch.feed)
            except BaseException:
                watch.close()
                raise

        def check(out: FinderPickOut) -> list[str]:
            failures = response_failures(out, shortlist)
            if failures:
                watches[-1].close()
            return failures

        out = call_with_retry(
            attempt, lambda feedback: build_pick_prompt(shortlist, snapshot, sheets, feedback), FinderPickOut,
            check, subject="finder pick", log_label="finder pick", logger=log)
        if out is None and watches:
            watches[-1].close()
        stand = [] if out is None or not out.picks else watches[-1].finish(out)
    finally:
        pool.shutdown(wait=False, cancel_futures=True)
    near = [] if out is None else standing_near(out, {offer.offer_id for _, offer in stand}, shortlist, snapshot,
                                                sheets)
    if not stand and not near:
        # With no pick and no near idea left, the shortlist stands with fact lines.
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
    picks = [_finder_pick(pick, offer, sheets[offer.offer_id]) for pick, offer in stand]
    short_line = None
    if stand and len(stand) < most and out is not None:
        short_line = out.short_line
        log.info("finder pick kept %d of %d: %s", len(stand), most, short_line or "no reason given")
    return FinderPicks(picks=picks, near=[NearIdea(offer=offer, reason=idea.reason) for idea, offer in near],
                       none_line=None if stand or out is None else out.none_line or NO_CLEAR_PICK, fallback=False,
                       short_line=short_line)
