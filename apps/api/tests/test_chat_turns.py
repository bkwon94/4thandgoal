"""
Tests for the turns of the Thread that each typed question carries: the cut past the limit, the Jev state of the route,
and the earlier messages of Claude with the cache mark, for the free answer and a personal Topic typed as a question.
"""
import json
from collections.abc import AsyncIterator

import pytest
import test_api
import test_free_answer as free
from fakes import FakeJev
from fastapi.testclient import TestClient
from pydantic import ValidationError
from pydantic_ai.messages import CachePoint, ModelMessage, ModelRequest, ModelResponse, TextPart, UserPromptPart
from pydantic_ai.models.function import AgentInfo, FunctionModel
from test_api import CLIENT, HEADERS, _cpc, _here

from cornerstone_api.app import create_app
from cornerstone_api.ask import AskRequest
from cornerstone_api.chat_turns import (
    TURN_ANSWER_MAX,
    TURNS_MAX_CHARS,
    Turn,
    turn_messages,
)

repo = test_api.repo
settings = test_api.settings
sources = test_api.sources

ASK = "/clients/cpc/ask"
PERSONAL = "/clients/cpc/personal"
FIRST = {"question": "who has the best roster", "answer": "Bo Girds has the best roster, with a grade of 91."}
SECOND = {"question": "how about the worst", "answer": "Lil Fridge has the worst roster, with a grade of 60."}


def _body(**extra) -> dict:
    return {"question": "highest scoring team this season", "roster_id": free.LIL_FRIDGE, "week": 8, **extra}


def _long_turn(index: int, size: int) -> dict:
    return {"question": f"question {index}", "answer": "x" * size}


def test_turns_under_the_limit_stay_in_order_oldest_first():
    body = AskRequest.model_validate(_body(turns=[FIRST, SECOND]))
    assert [turn.question for turn in body.turns] == [FIRST["question"], SECOND["question"]]


def test_turns_past_the_limit_drop_the_oldest_first():
    # Each turn holds about a third of the limit, so the four turns hold more than the limit and the oldest drop.
    size = TURNS_MAX_CHARS // 3 - 20
    turns = [_long_turn(i, min(size, TURN_ANSWER_MAX)) for i in range(40)]
    body = AskRequest.model_validate(_body(turns=turns))
    kept = sum(len(turn.question) + len(turn.answer) for turn in body.turns)
    assert kept <= TURNS_MAX_CHARS
    assert body.turns[-1].question == "question 39"
    assert [turn.question for turn in body.turns] == [f"question {i}" for i in range(40 - len(body.turns), 40)]


def test_a_turn_past_its_length_cap_or_with_another_field_is_rejected():
    with pytest.raises(ValidationError):
        AskRequest.model_validate(_body(turns=[_long_turn(0, TURN_ANSWER_MAX + 1)]))
    with pytest.raises(ValidationError):
        AskRequest.model_validate(_body(turns=[{**FIRST, "block": {"rows": []}}]))
    with pytest.raises(ValidationError):
        AskRequest.model_validate(_body(turns=[{"question": "", "answer": "x"}]))


def test_no_turns_give_no_earlier_messages():
    assert turn_messages([]) == []


def test_the_earlier_messages_alternate_and_end_with_a_cache_mark_on_the_last_turn():
    messages = turn_messages([Turn(**FIRST), Turn(**SECOND)])
    content = lambda message: [part.content for part in message.parts]
    assert [type(m) for m in messages[:4]] == [ModelRequest, ModelResponse, ModelRequest, ModelResponse]
    assert [content(m) for m in messages[:4]] == [[FIRST["question"]], [FIRST["answer"]], [SECOND["question"]],
                                                  [SECOND["answer"]]]
    # A request with only a cache mark puts the Anthropic cache_control on the last block before it: the last answer.
    last = messages[-1]
    assert isinstance(last, ModelRequest)
    [part] = last.parts
    assert isinstance(part, UserPromptPart) and isinstance(part.content, list)
    assert all(isinstance(item, CachePoint) for item in part.content)
    assert len(messages) == 5


def test_the_route_puts_the_turns_in_the_jev_state_oldest_first(repo, fixture_raw_dir):
    jev = FakeJev(answer=free.Checks([True]).answer, choose=free._choice)
    api = free._api(repo, fixture_raw_dir, jev, free.Script("standings", {}, free._leader).model())
    response = api.post(ASK, json=_body(turns=[FIRST, SECOND]), headers=free.PASS)
    assert response.status_code == 200
    state = jev.requests[0].state
    assert state["earlier_turns"] == [FIRST, SECOND]
    assert "earlier_turns" in state["context"]
    assert state["manager_question"] == "highest scoring team this season"


def test_the_route_with_no_turns_keeps_the_state_as_before(repo, fixture_raw_dir):
    jev = FakeJev(answer=free.Checks([True]).answer, choose=free._choice)
    api = free._api(repo, fixture_raw_dir, jev, free.Script("standings", {}, free._leader).model())
    api.post(ASK, json=_body(), headers=free.PASS)
    state = jev.requests[0].state
    assert "earlier_turns" not in state
    assert "earlier_turns" not in state["context"]


def test_the_route_cuts_a_long_list_from_the_oldest_end(repo, fixture_raw_dir):
    jev = FakeJev(answer=free.Checks([True]).answer, choose=free._choice)
    api = free._api(repo, fixture_raw_dir, jev, free.Script("standings", {}, free._leader).model())
    turns = [_long_turn(i, TURN_ANSWER_MAX) for i in range(40)]
    assert api.post(ASK, json=_body(turns=turns), headers=free.PASS).status_code == 200
    sent = jev.requests[0].state["earlier_turns"]
    assert sum(len(turn["question"]) + len(turn["answer"]) for turn in sent) <= TURNS_MAX_CHARS
    assert sent[-1]["question"] == "question 39"
    assert len(sent) < 40


def test_a_free_answer_reads_the_turns_as_earlier_messages_and_the_check_never_sees_them(repo, fixture_raw_dir):
    checks = free.Checks([True])
    script = free.Script("standings", {}, free._leader)
    api = free._api(repo, fixture_raw_dir, FakeJev(answer=checks.answer, choose=free._choice), script.model())
    api.post(ASK, json=_body(turns=[FIRST]), headers=free.PASS)
    response = free._free(api, "highest scoring team this season", turns=[FIRST])
    assert response.status_code == 200
    first = script.requests[0]
    assert free._prompts(first) == [FIRST["question"], "highest scoring team this season"]
    texts = [part.content for m in first if isinstance(m, ModelResponse) for part in m.parts
             if isinstance(part, TextPart)]
    assert texts == [FIRST["answer"]]
    marks = [item for m in first if isinstance(m, ModelRequest) for part in m.parts if isinstance(part, UserPromptPart)
             and isinstance(part.content, list) for item in part.content if isinstance(item, CachePoint)]
    assert len(marks) == 1
    # The check judges each claim against the tool results only. The turns are context, never a source of a claim.
    assert "earlier_turns" not in checks.seen[0]
    assert FIRST["answer"] not in json.dumps(checks.seen[0])


def test_a_free_answer_with_turns_never_reads_the_kept_answer_of_the_same_question_with_no_turns(repo,
                                                                                               fixture_raw_dir):
    script = free.Script("standings", {}, free._leader)
    api = free._api(repo, fixture_raw_dir, FakeJev(answer=free.Checks([True, True]).answer, choose=free._choice),
                    script.model())
    free._ask(api, "highest scoring team this season")
    api.post(ASK, json=_body(turns=[FIRST]), headers=free.PASS)
    free._free(api, "highest scoring team this season", turns=[FIRST])
    # Two Claude runs of two requests each: the tool call, then the text.
    assert len(script.requests) == 4


class TurnWriter:
    """A stand-in for Claude on a personal Topic: it keeps the messages of each request and writes one plain line."""

    def __init__(self):
        self.requests: list[list[ModelMessage]] = []

    async def stream(self, messages: list[ModelMessage], info: AgentInfo) -> AsyncIterator[str]:
        self.requests.append(messages)
        for word in ["Your", "team", "has", "a", "hole", "at", "one", "slot."]:
            yield word + " "

    def model(self) -> FunctionModel:
        return FunctionModel(stream_function=self.stream)


def _personal_api(settings, sources, writer: TurnWriter) -> TestClient:
    app = create_app(settings, [CLIENT], sources=_cpc(_here(sources, settings)), jev=FakeJev(yes=0.95))
    app.state.personal_model = writer.model()
    return TestClient(app)


def test_a_typed_personal_topic_reads_the_turns_and_a_tap_reads_none(settings, sources):
    writer = TurnWriter()
    api = _personal_api(settings, sources, writer)
    tapped = api.post(PERSONAL, json={"topic": "weak_spots", "roster_id": free.LIL_FRIDGE}, headers=HEADERS)
    assert tapped.status_code == 200
    typed = api.post(PERSONAL, json={"topic": "weak_spots", "roster_id": free.LIL_FRIDGE, "turns": [FIRST]},
                     headers=HEADERS)
    assert typed.status_code == 200
    # The tap writes the kept Answer. The typed question with turns reads it not, so Claude reads the turns.
    assert len(writer.requests) == 2
    assert not any(isinstance(m, ModelResponse) for m in writer.requests[0])
    typed_texts = [part.content for m in writer.requests[1] if isinstance(m, ModelResponse) for part in m.parts
                   if isinstance(part, TextPart)]
    assert typed_texts == [FIRST["answer"]]
    # The kept Answer of the tap stays as it was, so the next tap shows it with no Claude call (AT-8).
    again = api.post(PERSONAL, json={"topic": "weak_spots", "roster_id": free.LIL_FRIDGE}, headers=HEADERS)
    assert again.status_code == 200
    assert len(writer.requests) == 2
    key = lambda response: [c["data"]["key"] for c in free._chunks(response) if c["type"] == "data-key"]
    assert key(typed) == key(tapped) == key(again)
