"""
Tests for the personal Topics of the front door at the route seam: the FastAPI test client with FakeJev, a function
model of Pydantic AI in place of Claude, and the recorded week 6 Sleeper data with the chart of week 6.
"""
import dataclasses
import json
import shutil
from collections.abc import AsyncIterator
from pathlib import Path

import test_api
from fakes import FakeJev
from fastapi.testclient import TestClient
from pydantic_ai.messages import ModelMessage, ModelRequest, UserPromptPart
from pydantic_ai.models.function import AgentInfo, FunctionModel
from test_api import CLIENT, HEADERS, _cpc, _here

from cornerstone_api.app import create_app
from league.jev_port import JevError, NoulQuestion
from league.numbers import ordinal
from league.provider.sleeper import load_raw

repo = test_api.repo
settings = test_api.settings
sources = test_api.sources

PERSONAL = "/clients/cpc/personal"
LIL_FRIDGE = 3
BO_GIRDS = 6
# The words that site copy never holds (decision 08 and the copy rules of the spec).
INNER_NAMES = ("jev", "advisor", "finder", "rival", "brian")
# The real waiver file of the latest published week of cpc.
PUBLISHED_WAIVER = Path(__file__).resolve().parents[3] / "clients" / "cpc" / "published" / "2026" / "week-08" / "waiver.json"


class Checks:
    """The Jev answers of the check of each text, in order: True passes every sentence, False fails the first."""

    def __init__(self, passes: list[bool]):
        self.passes = passes
        self.states: list[dict] = []

    def answer(self, key: str, question: NoulQuestion, state: dict) -> float:
        if key == "sentence_0":
            self.states.append(state)
        ok = self.passes[min(len(self.states), len(self.passes)) - 1]
        return 0.95 if ok or key != "sentence_0" else 0.1


def _facts(messages: list[ModelMessage]) -> dict:
    prompts = [part.content for m in messages if isinstance(m, ModelRequest) for part in m.parts
               if isinstance(part, UserPromptPart) and isinstance(part.content, str)]
    return json.loads(prompts[0].split("Facts:\n", 1)[1])


class Writer:
    """A stand-in for Claude: it writes one sentence from the facts of the prompt, word by word, and counts its calls."""

    def __init__(self):
        self.calls = 0
        self.requests: list[list[ModelMessage]] = []

    async def stream(self, messages: list[ModelMessage], info: AgentInfo) -> AsyncIterator[str]:
        self.calls += 1
        self.requests.append(messages)
        facts = _facts(messages)
        worst = max(facts["slot_ranks"], key=lambda slot: slot["rank"])
        text = f"Your weakest spot is {worst['position']}, which ranks {ordinal(worst['rank'])} of 12."
        for word in text.split(" "):
            yield word + " "

    def model(self) -> FunctionModel:
        return FunctionModel(stream_function=self.stream)


def _api(settings, sources, jev: FakeJev, writer: Writer) -> TestClient:
    app = create_app(settings, [CLIENT], sources=_cpc(_here(sources, settings)), jev=jev)
    app.state.personal_model = writer.model()
    return TestClient(app)


def _chunks(response) -> list[dict]:
    lines = [line.removeprefix("data: ") for line in response.text.splitlines() if line.startswith("data: ")]
    return [json.loads(line) for line in lines if line != "[DONE]"]


def _text(chunks: list[dict]) -> str:
    return "".join(c["delta"] for c in chunks if c["type"] == "text-delta").strip()


def _ask(api: TestClient, topic: str, roster_id: int = LIL_FRIDGE, **extra):
    return api.post(PERSONAL, json={"topic": topic, "roster_id": roster_id, **extra}, headers=HEADERS)


def test_a_tap_on_weak_spots_streams_the_data_block_before_the_text_then_the_check(settings, sources):
    # AT-18 and AT-20: the block from code first, then the words of Claude, then "checking" and "checked".
    writer = Writer()
    api = _api(settings, sources, FakeJev(answer=Checks([True]).answer), writer)
    response = _ask(api, "weak_spots")
    assert response.status_code == 200
    assert response.headers["x-vercel-ai-ui-message-stream"] == "v1"
    chunks = _chunks(response)
    kinds = [c["type"] for c in chunks]
    block_at = kinds.index("data-block")
    first_text = kinds.index("text-delta")
    assert block_at < first_text
    [block] = [c["data"] for c in chunks if c["type"] == "data-block"]
    assert block["topic"] == "weak_spots" and block["team"] == LIL_FRIDGE
    worst = block["rows"][0]
    assert block["fact"] == f"{worst['label']} ranks {worst['value']}"
    assert _text(chunks) == f"Your weakest spot is {worst['label']}, which ranks {worst['value'].replace(' of ', ' of ')}."
    checks = [(i, c["data"]["state"]) for i, c in enumerate(chunks) if c["type"] == "data-check"]
    assert [state for _, state in checks] == ["checking", "checked"]
    assert checks[0][0] > max(i for i, kind in enumerate(kinds) if kind == "text-delta")
    assert kinds[-1] == "finish"
    assert writer.calls == 1


def test_a_second_ask_with_the_same_facts_returns_the_kept_answer_with_no_claude_call(settings, sources):
    # AT-29: the same facts give the same key, and the kept text comes back with its check and no Claude call.
    writer = Writer()
    checks = Checks([True])
    api = _api(settings, sources, FakeJev(answer=checks.answer), writer)
    first = _chunks(_ask(api, "weak_spots"))
    second = _chunks(_ask(api, "weak_spots"))
    assert writer.calls == 1
    assert len(checks.states) == 1
    assert _text(second) == _text(first)
    key = lambda chunks: [c["data"]["key"] for c in chunks if c["type"] == "data-key"]
    assert key(second) == key(first)
    assert [c["data"]["state"] for c in second if c["type"] == "data-check"] == ["checked"]
    assert [c["data"] for c in second if c["type"] == "data-block"] == [c["data"] for c in first
                                                                       if c["type"] == "data-block"]


def test_a_changed_roster_changes_the_key_and_claude_writes_a_fresh_answer(settings, sources, fixture_raw_dir,
                                                                          tmp_path):
    # Decision 11: a waiver claim or a trade changes the facts, so the kept Answer of the old roster stays unused.
    writer = Writer()
    api = _api(settings, sources, FakeJev(answer=Checks([True]).answer), writer)
    first = _chunks(_ask(api, "weak_spots"))
    raw = tmp_path / "raw-after-a-drop"
    shutil.copytree(fixture_raw_dir, raw)
    rosters = json.loads((raw / "rosters.json").read_text())
    mine = next(roster for roster in rosters if roster["roster_id"] == LIL_FRIDGE)
    mine["players"] = mine["players"][1:]
    (raw / "rosters.json").write_text(json.dumps(rosters))
    # A second app over the same store, as after a restart, reads the roster after the drop.
    changed = dataclasses.replace(sources, fetch_sleeper=lambda league_id: (load_raw(raw), test_api.FETCHED))
    api = _api(settings, changed, FakeJev(answer=Checks([True]).answer), writer)
    second = _chunks(_ask(api, "weak_spots"))
    key = lambda chunks: [c["data"]["key"] for c in chunks if c["type"] == "data-key"]
    assert key(second) != key(first)
    assert writer.calls == 2


def test_one_failed_claim_fades_the_text_and_streams_a_second_checked_text(settings, sources):
    # AT-21: the first text fails one claim, "fixing" and the fix part come, and the rewrite streams with "checked".
    writer = Writer()
    checks = Checks([False, True])
    api = _api(settings, sources, FakeJev(answer=checks.answer), writer)
    chunks = _chunks(_ask(api, "weak_spots"))
    states = [c["data"]["state"] for c in chunks if c["type"] == "data-check"]
    assert states == ["checking", "fixing", "checking", "checked"]
    kinds = [c["type"] for c in chunks]
    assert kinds.index("data-fix") < max(i for i, kind in enumerate(kinds) if kind == "text-delta")
    assert writer.calls == 2
    # The rewrite reads the failed sentence, so Claude knows what to fix.
    rewrite = [part.content for part in writer.requests[1][-1].parts if isinstance(part, UserPromptPart)]
    assert "do not follow from the facts" in rewrite[0]
    # The check reads the slice of the Topic as the evidence, and the team of the manager who asks.
    assert checks.states[0]["tool_results"]["team_facts"]["team"] == checks.states[0]["manager_team"]


def test_a_second_failed_claim_ends_with_the_honest_miss_and_keeps_nothing(settings, sources):
    # Story 29: a bad Answer never stays, so a second fail gives the closest Topics, and a repeat asks Claude again.
    writer = Writer()
    api = _api(settings, sources, FakeJev(answer=Checks([False, False, False]).answer), writer)
    chunks = _chunks(_ask(api, "weak_spots"))
    assert [c["data"]["state"] for c in chunks if c["type"] == "data-check"][-1] == "failed"
    [miss] = [c["data"] for c in chunks if c["type"] == "data-miss"]
    assert miss["closest"] == ["stack_up", "waiver_targets", "trade_ideas"]
    _ask(api, "weak_spots")
    assert writer.calls == 4


def test_a_failed_jev_check_ends_the_stream_with_an_error_and_keeps_nothing(settings, sources):
    class DownJev(FakeJev):
        def ask(self, state, questions):
            raise JevError("down")

    writer = Writer()
    api = _api(settings, sources, DownJev(), writer)
    chunks = _chunks(_ask(api, "weak_spots"))
    assert any(c["type"] == "error" for c in chunks)
    assert not any(c["type"] == "data-check" and c["data"]["state"] == "checked" for c in chunks)
    _ask(api, "weak_spots")
    assert writer.calls == 2


def _block(chunks: list[dict]) -> dict:
    [block] = [c["data"] for c in chunks if c["type"] == "data-block"]
    return block


def test_how_you_stack_up_shows_the_four_parts_of_the_roster_grade_with_their_ranks(settings, sources):
    # The Topic reads the roster grade of the managers page, with no new formula: its letter, its four part ranks,
    # and its slot ranks. Claude gets the parts and the slots, and nothing else of the grade.
    writer = Writer()
    api = _api(settings, sources, FakeJev(answer=Checks([True]).answer), writer)
    block = _block(_chunks(_ask(api, "stack_up")))
    assert [row["label"] for row in block["rows"]] == ["Projection Ahead", "Season Production", "Trade Value",
                                                       "Depth And Holes"]
    assert all(row["value"].endswith(" of 12") for row in block["rows"])
    facts = _facts(writer.requests[0])
    assert set(facts) == {"team", "teams_in_league", "week", "grade", "part_ranks", "slot_ranks", "grade_read"}
    assert block["fact"].startswith(f"Grade {facts['grade']['letter']}")
    assert [part["rank"] for part in facts["part_ranks"]] == [int(row["value"][:-8].rstrip("stndrh"))
                                                              for row in block["rows"]]


def _publish_waiver(settings) -> dict:
    folder = settings.repo / "published" / "2026" / "week-06"
    folder.mkdir(parents=True)
    shutil.copy(PUBLISHED_WAIVER, folder / "waiver.json")
    return json.loads(PUBLISHED_WAIVER.read_text())


def test_waiver_targets_read_the_published_waiver_list_and_drop_each_rostered_player(settings, sources,
                                                                                   fixture_raw_dir):
    board = _publish_waiver(settings)
    writer = Writer()
    api = _api(settings, sources, FakeJev(answer=Checks([True]).answer), writer)
    block = _block(_chunks(_ask(api, "waiver_targets")))
    facts = _facts(writer.requests[0])
    rostered = {pid for roster in json.loads((fixture_raw_dir / "rosters.json").read_text())
                for pid in roster["players"] or []}
    on_board = {player["name"]: player["player_id"] for bucket in board["buckets"].values() for player in bucket}
    listed = [player["name"] for player in facts["waiver_list"]]
    assert listed, "the slice holds the free players of the board"
    assert all(on_board[name] not in rostered for name in listed)
    assert len(listed) < len(on_board) or not (set(on_board.values()) & rostered)
    assert [row["label"] for row in block["rows"]] == listed[:len(block["rows"])]
    assert set(facts) == {"team", "teams_in_league", "week", "slot_ranks", "starters", "waiver_list"}


def test_waiver_targets_with_no_published_waiver_list_say_so_in_the_block(settings, sources):
    writer = Writer()
    api = _api(settings, sources, FakeJev(answer=Checks([True]).answer), writer)
    block = _block(_chunks(_ask(api, "waiver_targets")))
    assert block["fact"] == "No waiver list this week"
    assert block["rows"] == []
    assert _facts(writer.requests[0])["waiver_list"] == []


def test_a_topic_about_another_team_reads_the_slice_of_that_team(settings, sources):
    writer = Writer()
    api = _api(settings, sources, FakeJev(answer=Checks([True]).answer), writer)
    block = _block(_chunks(_ask(api, "weak_spots", team=BO_GIRDS)))
    assert block["team"] == BO_GIRDS
    prompt = next(part.content for part in writer.requests[0][-1].parts if isinstance(part, UserPromptPart))
    facts = _facts(writer.requests[0])
    assert facts["team"] != "Lil Fridge"
    assert f"call this team {facts['team']}" in prompt


def test_weak_spots_name_each_hole_of_the_lineup_in_the_slice(settings, sources):
    writer = Writer()
    api = _api(settings, sources, FakeJev(answer=Checks([True]).answer), writer)
    _ask(api, "weak_spots")
    starters = _facts(writer.requests[0])["starters"]
    assert starters and all({"slot", "player", "position", "projected_rank_at_position", "starter_line", "hole"}
                            <= set(s) for s in starters)
    # A hole is a slot with no player, or a starter below the line of his position (GLOSSARY.md, "Hole").
    for s in starters:
        below = s["projected_rank_at_position"] is None or s["projected_rank_at_position"] > s["starter_line"]
        assert s["hole"] == (s["player"] is None or below)


def test_a_personal_topic_needs_the_passphrase(settings, sources):
    writer = Writer()
    api = _api(settings, sources, FakeJev(answer=Checks([True]).answer), writer)
    response = api.post(PERSONAL, json={"topic": "weak_spots", "roster_id": LIL_FRIDGE})
    assert response.status_code == 401
    assert writer.calls == 0


def test_a_team_that_is_not_in_the_league_is_422_with_no_claude_call(settings, sources):
    writer = Writer()
    api = _api(settings, sources, FakeJev(answer=Checks([True]).answer), writer)
    assert _ask(api, "weak_spots", roster_id=99).status_code == 422
    assert _ask(api, "weak_spots", team=99).status_code == 422
    assert _ask(api, "power_rankings").status_code == 422
    assert writer.calls == 0


def test_no_step_line_or_block_line_names_an_inner_tool(settings, sources):
    _publish_waiver(settings)
    writer = Writer()
    api = _api(settings, sources, FakeJev(answer=Checks([True]).answer), writer)
    for topic in ("weak_spots", "stack_up", "waiver_targets"):
        block = json.dumps(_block(_chunks(_ask(api, topic)))).lower()
        assert not any(name in block for name in INNER_NAMES)
