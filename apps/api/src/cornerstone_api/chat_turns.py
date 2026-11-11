"""
The turns of the Thread that each typed question carries: the plain question and the shown answer of each earlier turn.
The router reads them in the Jev state, and Claude reads them as earlier messages, with a cache mark on the last turn.
"""
from typing import Annotated, Any

from pydantic import AfterValidator, BaseModel, BeforeValidator, ConfigDict, Field
from pydantic_ai.messages import CachePoint, ModelMessage, ModelRequest, ModelResponse, TextPart, UserPromptPart

# The hard limit of the turns of one question: about 8,000 tokens, at about 4 characters per token. A follow-up such as
# "cant choose mine" needs only the last few turns, and a long Thread must not make each question cost more. The
# oldest turns drop first, so the newest context always stays.
TURNS_MAX_CHARS = 32_000
# The question of a turn is a typed question or a Topic name, so it has the cap of a typed question.
TURN_QUESTION_MAX = 300
# The shown answer of a turn is 1 to 4 short sentences. A longer text is not a shown answer, so the API answers 422.
TURN_ANSWER_MAX = 2_000
# A guard on the parse only: a list past this count loses its oldest turns before each turn is read.
TURNS_COUNT_MAX = 100

# The words that tell Jev how to read the turns. The route state adds them only when a question carries turns.
JEV_TURNS_CONTEXT = ("`earlier_turns` holds the earlier questions of this manager's chat and the answers that the site "
                     "showed, oldest first. Read `manager_question` as the next question of that chat: a short "
                     "follow-up such as 'what about him' or 'not mine' asks what the whole question would ask.")
# The line that tells Claude how to read the turns. A run adds it to its instructions only when a question carries turns.
CLAUDE_TURNS_LINE = ("The earlier messages are this manager's chat so far, oldest first, for context only. Read the "
                     "new question as the next message of that chat. Take no fact from an earlier answer.")


class Turn(BaseModel):
    """One earlier turn of the Thread: the question, and the final answer text that the manager saw. A turn holds plain
    text only, so no data block, tool result, or step line reaches the router or Claude."""

    model_config = ConfigDict(extra="forbid")

    question: str = Field(min_length=1, max_length=TURN_QUESTION_MAX)
    answer: str = Field(min_length=1, max_length=TURN_ANSWER_MAX)


def _newest_count(value: Any) -> Any:
    """The newest TURNS_COUNT_MAX items of a raw list, so a huge list costs no parse of each turn."""
    return value[-TURNS_COUNT_MAX:] if isinstance(value, list) else value


def cut(turns: list[Turn]) -> list[Turn]:
    """The newest turns that fit in TURNS_MAX_CHARS, oldest first. The oldest turns drop first."""
    kept: list[Turn] = []
    size = 0
    for turn in reversed(turns):
        size += len(turn.question) + len(turn.answer)
        if size > TURNS_MAX_CHARS:
            break
        kept.append(turn)
    return kept[::-1]


# The turns field of a request body. The API cuts a longer list from the oldest end, and never answers 422 for it.
Turns = Annotated[list[Turn], BeforeValidator(_newest_count), AfterValidator(cut)]


def with_turns(state: dict, turns: list[Turn]) -> dict:
    """The Jev state of a route with the turns added. With no turns, the state stays as it was."""
    if not turns:
        return state
    return {**state, "context": f"{state['context']} {JEV_TURNS_CONTEXT}",
            "earlier_turns": [turn.model_dump() for turn in turns]}


def turn_messages(turns: list[Turn]) -> list[ModelMessage]:
    """The turns as earlier messages of Claude: each question as a user message and each answer as a model message.

    The last message holds only a cache mark. Pydantic AI puts the Anthropic cache_control on the block before it, the
    last answer, so the next question of the Thread reads the whole chat from the cache.
    """
    if not turns:
        return []
    messages: list[ModelMessage] = []
    for turn in turns:
        messages.append(ModelRequest(parts=[UserPromptPart(turn.question)]))
        messages.append(ModelResponse(parts=[TextPart(turn.answer)]))
    messages.append(ModelRequest(parts=[UserPromptPart([CachePoint()])]))
    return messages


def turns_instructions(instructions: str, turns: list[Turn]) -> str:
    """The instructions of a run, with the line about the turns when the question carries some."""
    return f"{instructions}\n{CLAUDE_TURNS_LINE}" if turns else instructions
