"""
All the wording of a free answer: the instructions of Claude, the line that asks for a rewrite, and the Jev check of
each sentence against the tool results. Change the check here and run the live check of the free answer.
"""
import re

from league.jev_port import NoulQuestion

INSTRUCTIONS = """\
You answer one question that a manager of a 12-team fantasy football league typed into the league site.
Read this season's league data with the tools, then answer in 1 to 3 short sentences of plain words.

Rules:
- Use only what the tool results say. Give the real numbers and the team names from them.
- You can make at most 4 tool calls. Ask for only what the question needs.
- If the tools do not hold the answer, say what you could not find. Never guess.
- Never name a tool, a file, or a data source. Never use a heading, a table, or a list.
- Call the person who runs another team "the manager" of that team.
"""

REWRITE = """\
A check found that these sentences of your answer do not follow from the tool results:
{sentences}
Write the whole answer again. Keep only what the tool results say, with the same rules.
"""


def run_instructions(season: int, week: int, your_team: str, named_team: str | None) -> str:
    """The facts of one question that code knows: the season, the latest week, Your team, and the team it names."""
    lines = [f"The season is {season}. The latest week with results is week {week}.",
             f"The manager who asks runs the team {your_team}. 'My team', 'me', and 'I' mean {your_team}."]
    if named_team is not None:
        lines.append(f"The question is about the team {named_team}.")
    return "\n".join(lines)


def rewrite_prompt(failed: list[str]) -> str:
    return REWRITE.format(sentences="\n".join(f"- {sentence}" for sentence in failed))


# One Noul per sentence, as the check of the weekly blurbs does, so each answer reads one claim.
CHECK_QUESTION = "Does every claim in the sentence follow from `tool_results`?"
CHECK_YES = ("Each number, name, rank, record, and comparison in the sentence is stated by `tool_results`, or follows "
             "from them by a plain reading. A sentence with no factual claim, such as one that says what the data "
             "does not hold, is fine.")
CHECK_NO = ("The sentence states a number, name, rank, record, or comparison that `tool_results` do not state, or "
            "that `tool_results` contradict.")
CHECK_CONTEXT = ("A fantasy football league site answered `manager_question` from the manager of `manager_team` with "
                 "`answer`. The answer read only `tool_results`, the data of this season.")

# The end of a sentence: a stop, a question mark, or a bang, then a space. A line break ends a sentence too.
SENTENCE_END = re.compile(r"(?<=[.!?])\s+|\n+")


def sentences(text: str) -> list[str]:
    """The sentences of an answer, in order, with no blank one."""
    return [part.strip() for part in SENTENCE_END.split(text) if part.strip()]


def sentence_key(index: int) -> str:
    return f"sentence_{index}"


def check_questions(parts: list[str]) -> dict[str, NoulQuestion]:
    """One Noul per sentence. Each sentence goes into its own question, so no question looks up an index in a list."""
    return {sentence_key(i): NoulQuestion(instructions={"question": CHECK_QUESTION, "sentence": part},
                                          yes=CHECK_YES, no=CHECK_NO)
            for i, part in enumerate(parts)}


def check_state(question: str, your_team: str, parts: list[str], tool_results: dict[str, object]) -> dict:
    """The state of one check: the question, the team of the manager who asks, so "your team" has its name, the whole
    answer so a pronoun has its subject, and each tool result by the name of its call."""
    return {"context": CHECK_CONTEXT, "manager_question": question, "manager_team": your_team, "answer": parts,
            "tool_results": tool_results}
