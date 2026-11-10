"""
The Evidence flag questions that Jev answers on one acceptance test: the wording, the criteria, the cuts, the
in-flow marks, and the bar. Every word that Jev reads as a question lives here. evidence_flags.py builds the state.
"""
import re
from collections.abc import Callable
from dataclasses import dataclass

from league.jev_port import NoulQuestion

# The bar of a question on the eval run: it catches at least half of the past gaps of its kind, and it flags 10% or
# fewer of the PASS tests. The in-flow mark of each question follows that run, and only a later ticket changes a cut.
BAR_HIT_RATE = 0.5
BAR_FALSE_FLAG_RATE = 0.10


@dataclass(frozen=True)
class Question:
    """One Evidence flag question: its key, its cut, its in-flow mark, its Nouls, and the code that makes its flag.

    `nouls` gives the Nouls of one test from its state, each key with the prefix `<key>_`. `flag` gives the flag
    probability and the reason from the answers of those Nouls. A flag probability at or above `cut` is a flag.
    """
    key: str
    name: str
    cut: float
    in_flow: bool
    nouls: Callable[[dict], dict[str, NoulQuestion]]
    flag: Callable[[dict[str, float], dict], tuple[float, str]]


# Question (a): one Noul for each sentence of the Then line, because each sentence is one fact.
FACT_SHOWN = "Do the files in `evidence` show this fact from the Then line of `test`: \"{fact}\"?"
FACT_SHOWN_YES = (
    "A file in `evidence.text_files` or a shot in `evidence.screenshots` shows the fact itself: "
    "the command output, the log line, the code, or the screen holds it for the case the test names."
)
FACT_SHOWN_NO = (
    "No file shows the fact. Only `agent_observation` says it, or the files show a different case or item, "
    "or a file shows only a test pass line such as \"1 passed\" with no detail of the fact."
)


def then_facts(then_line: str) -> list[str]:
    """The sentences of a Then line, each one fact for question (a).

    A sentence that starts with "If" is a condition that a test may not meet, so it is no fact to show.
    """
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z`\"])", then_line.strip())
    return [part.strip() for part in parts if part.strip() and not re.match(r"If\b", part.strip())]


def _fact_nouls(state: dict) -> dict[str, NoulQuestion]:
    return {f"a_fact_{i}": NoulQuestion(instructions=FACT_SHOWN.format(fact=fact), yes=FACT_SHOWN_YES,
                                        no=FACT_SHOWN_NO)
            for i, fact in enumerate(then_facts(state["test"]["then"]))}


def _fact_flag(answers: dict[str, float], state: dict) -> tuple[float, str]:
    """The flag is 1 minus the answer of the least-shown fact, and the reason names that fact."""
    if not answers:
        return 0.0, ""
    key = min(answers, key=lambda each: answers[each])
    fact = then_facts(state["test"]["then"])[int(key.removeprefix("a_fact_"))]
    return 1 - answers[key], f"No file may show this fact of the Then line: \"{fact}\" (shown at {answers[key]:.2f})."


FACTS = Question(key="a", name="the facts", cut=0.7, in_flow=True, nouls=_fact_nouls, flag=_fact_flag)

# Every question of the module, in the order that FLAGS.md lists them.
QUESTIONS: tuple[Question, ...] = (FACTS,)


def in_flow() -> tuple[Question, ...]:
    """The questions that `evidence-flags` asks: each one with the in-flow mark."""
    return tuple(question for question in QUESTIONS if question.in_flow)
