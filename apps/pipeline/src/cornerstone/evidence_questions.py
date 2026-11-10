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


def sentences(text: str) -> list[str]:
    """The sentences of a text: a split after a full stop, a question mark, or a bang, before a capital or a quote."""
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z`\"])", text.strip())
    return [part.strip() for part in parts if part.strip()]


def then_facts(then_line: str) -> list[str]:
    """The sentences of a Then line, each one fact for question (a).

    A sentence that starts with "If" is a condition that a test may not meet, so it is no fact to show.
    """
    return [part for part in sentences(then_line) if not re.match(r"If\b", part)]


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

# Question (b): code first looks for a video or timed frames among the files, and then asks nothing. Jev judges only
# whether the Then line asks for motion and whether a text log holds animation values, because a draft that asked
# Jev whether the files record change over time read any timed log line, such as a request time, as motion.
ASKS_MOTION = "Does the Then line of `test` describe something that moves or animates on the screen over time?"
ASKS_MOTION_YES = (
    "The Then line names a change a person sees as it happens, such as a pulse, a spring, a crack, a slide, or a fade in."
)
ASKS_MOTION_NO = (
    "The Then line names only what one still moment can show, such as text, a color, a faded look, a count, or a layout."
)
LOGS_MOTION = (
    "Does a file in `evidence.text_files` log animation values, such as opacity, scale, a transform, "
    "or a stroke offset, at more than one moment of one animation?"
)
LOGS_MOTION_YES = (
    "A log lists the value of one animated property at two or more times, such as \"scale 0.29 at 527 ms, 1 at 1351 ms\"."
)
LOGS_MOTION_NO = (
    "The logs hold only end states, counts, request times, or one computed style, "
    "with no value of an animated property over time."
)
# A timed frame names its time in ms anywhere in the file name, such as frame-400ms-375-dark.png.
FRAME_NAME = re.compile(r"\d+ms[-_.].*\.(png|jpe?g)$", re.IGNORECASE)


def records_motion(state: dict) -> bool:
    """True when the files hold a video, or two or more shots that name their time in ms."""
    evidence = state["evidence"]
    frames = sum(1 for name in evidence["file_names"] if FRAME_NAME.search(name))
    return bool(evidence["video_files"]) or frames >= 2


def _motion_nouls(state: dict) -> dict[str, NoulQuestion]:
    if records_motion(state):
        return {}
    return {"b_asks_motion": NoulQuestion(instructions=ASKS_MOTION, yes=ASKS_MOTION_YES, no=ASKS_MOTION_NO),
            "b_logs_motion": NoulQuestion(instructions=LOGS_MOTION, yes=LOGS_MOTION_YES, no=LOGS_MOTION_NO)}


def _motion_flag(answers: dict[str, float], state: dict) -> tuple[float, str]:
    """The flag is p(the test asks for motion) times p(no log holds animation values). A video or frames give 0."""
    if not answers:
        return 0.0, ""
    probability = answers["b_asks_motion"] * (1 - answers["b_logs_motion"])
    return probability, (
        f"The Then line may ask for motion (at {answers['b_asks_motion']:.2f}), and the files hold no video, no timed "
        f"frames, and no log of animation values (a log at {answers['b_logs_motion']:.2f}).")


MOTION = Question(key="b", name="motion", cut=0.7, in_flow=True, nouls=_motion_nouls, flag=_motion_flag)

# Question (c): one Noul per shot, scoped to the text that the Then line names. A draft that asked about any text of
# the page was mostly right about the image, but it flagged a design ellipsis or a fixed bar over text that the test
# does not name, and the Judge does not fail a test for that.
THEN_TEXT_CUT = (
    "In the screenshot `evidence.screenshots[\"{path}\"]`, is the text that the Then line of `test` names "
    "cut off or too big for its space?"
)
THEN_TEXT_CUT_YES = (
    "A word or a line of the text that the Then line names stops at the edge of its box or the screen, "
    "ends in \"...\" so its full text does not show, runs out of its box, or sits under a bar so a person cannot read it."
)
THEN_TEXT_CUT_NO = (
    "The text that the Then line names shows in full inside its box, or the shot does not hold that text. "
    "Other text of the page may end in \"...\" or sit under a bar."
)


def _cut_text_nouls(state: dict) -> dict[str, NoulQuestion]:
    return {f"c_shot_{i}": NoulQuestion(instructions=THEN_TEXT_CUT.format(path=path), yes=THEN_TEXT_CUT_YES,
                                        no=THEN_TEXT_CUT_NO)
            for i, path in enumerate(state["evidence"]["screenshots"])}


def _cut_text_flag(answers: dict[str, float], state: dict) -> tuple[float, str]:
    """The flag is the highest answer over the shots, and the reason names that shot. No shot gives 0."""
    if not answers:
        return 0.0, ""
    key = max(answers, key=lambda each: answers[each])
    path = list(state["evidence"]["screenshots"])[int(key.removeprefix("c_shot_"))]
    return answers[key], f"The shot `{path}` may show the text of the Then line cut off or too big for its space."


CUT_TEXT = Question(key="c", name="cut-off text", cut=0.9, in_flow=True, nouls=_cut_text_nouls, flag=_cut_text_flag)

# Question (d): two Nouls per sentence of the Observation. The first asks if the files show it. The second asks if it
# reports a result that the Then line asks for, because a draft with the first Noul alone flagged true but harmless
# gaps, such as a note on a first run or a commit.
OBS_SHOWN = "Do the files in `evidence` show this statement of `agent_observation`: \"{sentence}\"?"
OBS_SHOWN_YES = (
    "A text file or a screenshot holds the statement with the same values, "
    "or the statement is only background, such as a reason, a commit, or a design note."
)
OBS_SHOWN_NO = "No file holds the statement, or a file gives a different value for a number or a quoted text in it."
OBS_RELEVANT = (
    "Does this statement of `agent_observation` report a result that the Then line of `test` asks for: \"{sentence}\"?"
)
OBS_RELEVANT_YES = "The statement gives an outcome, a value, or a screen state that one fact of the Then line depends on."
OBS_RELEVANT_NO = (
    "The statement is about how the agent ran the test, a first try, a path or a port, a commit, "
    "or the evidence of another test."
)


def observation_sentences(state: dict) -> list[str]:
    """The sentences of the Observation that (d) asks about.

    A sentence that names another test, such as AT-18 or evidence/AT-9/, is about files that the state does not hold,
    so code drops it.
    """
    own = state["test"]["id"]
    return [part for part in sentences(state["agent_observation"])
            if all(named == own for named in re.findall(r"AT-\d+", part))]


def _observation_nouls(state: dict) -> dict[str, NoulQuestion]:
    nouls: dict[str, NoulQuestion] = {}
    for i, sentence in enumerate(observation_sentences(state)):
        nouls[f"d_shown_{i}"] = NoulQuestion(instructions=OBS_SHOWN.format(sentence=sentence), yes=OBS_SHOWN_YES,
                                             no=OBS_SHOWN_NO)
        nouls[f"d_rel_{i}"] = NoulQuestion(instructions=OBS_RELEVANT.format(sentence=sentence), yes=OBS_RELEVANT_YES,
                                           no=OBS_RELEVANT_NO)
    return nouls


def _observation_flag(answers: dict[str, float], state: dict) -> tuple[float, str]:
    """The flag is the highest p(it reports a result) times p(no file shows it) over the sentences of the Observation."""
    if not answers:
        return 0.0, ""
    parts = observation_sentences(state)
    scores = {i: answers[f"d_rel_{i}"] * (1 - answers[f"d_shown_{i}"]) for i in range(len(parts))}
    worst = max(scores, key=lambda each: scores[each])
    return scores[worst], (
        f"No file may show this sentence of the Observation: \"{parts[worst]}\" "
        f"(shown at {answers[f'd_shown_{worst}']:.2f}, a result of the Then line at {answers[f'd_rel_{worst}']:.2f}).")


OBSERVATION = Question(key="d", name="the Observation", cut=0.7, in_flow=True, nouls=_observation_nouls,
                       flag=_observation_flag)

# Every question of the module, in the order that FLAGS.md lists them.
QUESTIONS: tuple[Question, ...] = (FACTS, MOTION, CUT_TEXT, OBSERVATION)


def in_flow() -> tuple[Question, ...]:
    """The questions that `evidence-flags` asks: each one with the in-flow mark."""
    return tuple(question for question in QUESTIONS if question.in_flow)
