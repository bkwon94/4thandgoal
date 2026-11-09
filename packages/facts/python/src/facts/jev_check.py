"""
The Jev check of one blurb: one Noul per sentence, in one request, over every chapter fact and the vocabulary.
All Jev question text lives here, so a reader audits and edits it in one place. The check logs only.
"""
import re
from collections.abc import Sequence
from pathlib import Path

from facts.writer import load_prompt, with_terms
from league.jev_port import Jev, NoulQuestion
from league.models import Blurb, Chapter, FactSheet, JevAnswer, JevCheck

# The design `single_all_vocab` of research 01: one Noul per sentence, with the vocabulary as named fields.
# It gave the most blurbs that agree with Claude at an equal count of missed fails.
QUESTION = (
    "Does every claim in the sentence follow from `facts`, with each stat term read as `vocabulary` defines it?"
)
YES = (
    "Each number, name, rank, comparison, and cause in the sentence is stated by a fact. "
    "A joke or an opinion that adds no factual claim is fine."
)
NO = (
    "The sentence states a number, name, rank, comparison, cause, or consequence that no fact "
    "states, or that a fact contradicts."
)
# A term line of the vocabulary, such as "- **streak**: head-to-head results only".
TERM_LINE = re.compile(r"^- \*\*(.+?)\*\*: (.+)$", re.MULTILINE)


def _key(index: int) -> str:
    return f"sentence_{index}"


def jev_state(blurb: Blurb, chapter: Chapter, sheet: FactSheet, *, prompts_dir: Path,
              terms: Sequence[str] = ()) -> dict:
    """The state of one request. It holds what the Claude verifier reads: the chapter title, the whole blurb so a
    pronoun has its subject, every chapter fact and callback fact by ID, and each vocabulary term by name."""
    vocabulary = with_terms(load_prompt(prompts_dir, "vocabulary.md"), terms)
    fact_ids = [*chapter.fact_ids, *chapter.callback_ids]
    return {
        "chapter": chapter.title,
        "blurb": [s.text for s in blurb.sentences],
        "facts": {fid: sheet.facts[fid].text for fid in fact_ids if fid in sheet.facts},
        "vocabulary": dict(TERM_LINE.findall(vocabulary)),
    }


def jev_questions(blurb: Blurb) -> dict[str, NoulQuestion]:
    """One Noul per sentence. Each sentence goes into its own question, so no question looks up an index in a list."""
    return {
        _key(i): NoulQuestion(instructions={"question": QUESTION, "sentence": s.text}, yes=YES, no=NO)
        for i, s in enumerate(blurb.sentences)
    }


def jev_check(blurb: Blurb, chapter: Chapter, sheet: FactSheet, jev: Jev, *, prompts_dir: Path,
              terms: Sequence[str] = ()) -> JevCheck:
    """One Jev request for the blurb, with one Jev answer per sentence index. Raises JevError when the call fails."""
    state = jev_state(blurb, chapter, sheet, prompts_dir=prompts_dir, terms=terms)
    answers = jev.ask(state, jev_questions(blurb))
    return JevCheck(
        model=answers.model,
        answers=[JevAnswer(index=i, yes=answers.nouls[_key(i)]) for i in range(len(blurb.sentences))],
        input_tokens=answers.input_tokens,
    )
