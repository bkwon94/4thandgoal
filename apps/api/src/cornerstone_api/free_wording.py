"""
All the wording of a free answer: the instructions of Claude, the line that asks for a rewrite, and the Jev check of
each sentence against the tool results. Change the check here and run the live check of the free answer.
"""
import re

from cornerstone_api.free_blocks import BLOCK_MEANING
from league.jev_port import NoulQuestion

INSTRUCTIONS = """\
You answer one question that a manager of a 12-team fantasy football league typed into the league site.
Read this season's league data with the tools, then answer in 1 to 3 short sentences of plain words.

Rules:
- Use only what the tool results say. Give the real numbers and the team names from them.
- State only facts from the tool results. Give no advice, no rating, and no opinion word, such as "decent", "good \
time to sell", or "can afford to move him". For a trade question, end with the facts. The site can offer the trade \
ideas under the answer.
- You can make at most 4 data tool calls. Ask for only what the question needs. show_block does not count.
- If the tools do not hold the answer, say what you could not find. Never guess.
- Never name a tool, a file, or a data source. Never write a heading, a table, or a list in the text.
- Text is the default. Pick a block by the shape of your answer, not by the words of the question. Call \
show_block once, after one short lead sentence:
  - The answer ranks 3 or more players or teams, best first: kind "list".
  - The answer sets 2 teams or 2 players side by side: kind "table".
  - The answer is about one NFL player: kind "player".
  - Any other answer, such as one fact, a score, a record, or one game, is text only.
  - The answer is the moves of a week: the "ready" block of moves_feed, by its `block_id`.
- A tool result with a `block_id` holds a ready block that code built from that data. To show it, call show_block \
with kind "ready" and that `block_id`, and copy nothing into it.
- A question about the top or best players or teams with no time, such as "my top players", means this season. The \
lead sentence then says "this season".
- With a block, the lead sentence says what the block shows, and the block holds the rest. Copy each value of the \
block from the tool results of your earlier calls. show_block reads no data.
- In a player block, take `can_play_now` and `status` from the tool results.
- Call the person who runs another team "the manager" of that team.
"""

REWRITE = """\
A check found that these sentences of your answer do not follow from the tool results:
{sentences}
Write the whole answer again, with the same rules. Remove each of these sentences, or restate it with only the exact \
numbers of the tool results. Add no new claim. Keep each other sentence as it is. If a failed sentence is a row of your block, call show_block again with that row \
fixed or removed.
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


# The marks of the text block that the site renders (decision 09): a bullet or a number at the head of a line, and bold
# or italic around words. The rules match `text-block.tsx` of the site. Every other mark stays, because the site shows
# it as plain text too.
LIST_MARK = re.compile(r"^[ \t]*(?:[-*+]|\d+[.)])[ \t]+", re.MULTILINE)
INLINE_MARK = re.compile(r"\*\*(?=\S)(.+?)(?<=\S)\*\*|__(?=\S)(.+?)(?<=\S)__|\*(?=\S)(.+?)(?<=\S)\*"
                         r"|(?<!\w)_(?=\S)(.+?)(?<=\S)_(?!\w)")


def plain_text(text: str) -> str:
    """`text` with the marks of the text block taken out, so the Jev check reads the plain sentences that the manager
    reads on the site."""
    unlisted = LIST_MARK.sub("", text)
    return INLINE_MARK.sub(lambda match: next(group for group in match.groups() if group is not None), unlisted)


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


def check_state(question: str, your_team: str, parts: list[str], tool_results: dict[str, object],
                has_block: bool = False) -> dict:
    """The state of one check: the question, the team of the manager who asks, so "your team" has its name, the whole
    answer so a pronoun has its subject, and each tool result by the name of its call. An answer with a block holds
    the meaning of its row sentences too, so the check reads a row as the manager does."""
    state = {"context": CHECK_CONTEXT, "manager_question": question, "manager_team": your_team, "answer": parts,
             "tool_results": tool_results}
    if has_block:
        state["block_rows"] = BLOCK_MEANING
    return state
