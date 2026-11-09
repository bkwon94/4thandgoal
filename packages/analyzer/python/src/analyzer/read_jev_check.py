"""
The Jev checks of one read of the Advisor: is each Bullet faithful to its fact, and does a news Bullet state a report
as a sure fact. One request holds both. The checks only log, so no answer and no failure ever blocks a read.
"""
import logging
from collections.abc import Sequence
from typing import Protocol

from analyzer.trade_jev import NO_AT, YES_AT
from analyzer.trade_news import FACT_PREFIX as NEWS_PREFIX
from league.jev_port import Jev, JevError, NoulQuestion
from league.models import Fact

log = logging.getLogger(__name__)

# All question text of the checks lives here. Each Bullet and its fact go into their own question, so no question
# looks up an index in a list.
FAITHFUL = {
    "question": "Does every claim in `bullet` follow from `fact`?",
    "yes": "Each number, name, rank, comparison, and cause in the bullet is stated by the fact. Advice or an opinion "
           "that adds no factual claim is fine.",
    "no": "The bullet states a number, name, rank, comparison, or cause that the fact does not state, or that the "
          "fact contradicts."}
# The question reads true for the bad case, so a yes is a rumor stated as done.
RUMOR = {
    "question": "Does `bullet` state the news report in `fact` as a sure fact?",
    "yes": "The bullet says a reported trade, talk, or role change is done or certain, such as \"the Colts trade "
           "him to Denver\".",
    "no": "The bullet presents the news as a report, such as \"he is reported as a fit in Denver\", or it states "
          "only what already happened in a game."}
STATE = {"context": "An advisor wrote each bullet about one fantasy football trade. Each bullet cites one fact."}


class _Bullet(Protocol):
    @property
    def text(self) -> str: ...

    @property
    def fact_id(self) -> str: ...


class _Side(Protocol):
    """One side of the output of the Advisor. The checks sit a layer below the Advisor, so they name only its shape."""

    @property
    def roster_id(self) -> int: ...

    @property
    def bullets(self) -> Sequence[_Bullet]: ...


def _word(p: float) -> str:
    return "yes" if p > YES_AT else "no" if p < NO_AT else "unsure"


def read_jev_questions(sides: Sequence[_Side], facts: dict[str, Fact]) -> dict[str, NoulQuestion]:
    """The questions by key: "faithful.<roster id>.<n>" for each Bullet, and "rumor.<roster id>.<n>" for each Bullet
    that cites a NEWS fact. A Bullet whose fact is not on the sheet gets no question."""
    questions = {}
    for side in sides:
        for n, bullet in enumerate(side.bullets, start=1):
            if bullet.fact_id not in facts:
                continue
            where = f"{side.roster_id}.{n}"
            pair = {"bullet": bullet.text, "fact": facts[bullet.fact_id].text}
            questions[f"faithful.{where}"] = NoulQuestion(
                {"question": FAITHFUL["question"], **pair}, FAITHFUL["yes"], FAITHFUL["no"])
            if bullet.fact_id.startswith(NEWS_PREFIX):
                questions[f"rumor.{where}"] = NoulQuestion(
                    {"question": RUMOR["question"], **pair}, RUMOR["yes"], RUMOR["no"])
    return questions


def log_read_jev_checks(sides: Sequence[_Side], facts: dict[str, Fact], jev: Jev) -> None:
    """One Jev request with both checks of the read, and one log line of every answer. It never raises."""
    questions = read_jev_questions(sides, facts)
    if not questions:
        return
    # Log only: a failed request leaves the read as it is. The port raises JevError for every failure.
    try:
        response = jev.ask(STATE, questions)
    except JevError as error:
        log.warning("The Jev checks of the read failed, so they log no answer: %s", error)
        return
    answers = " ".join(f"{key}={p:.2g} {_word(p)}" for key, p in response.nouls.items())
    log.info("Jev checks of the read, log only: model=%s input_tokens=%s %s", response.model, response.input_tokens,
             answers)
