"""
Tests for the personal Topics of the front door at the route seam: the FastAPI test client with FakeJev, a function
model of Pydantic AI in place of Claude, and the recorded week 6 and week 9 Sleeper data with the chart of week 6.
"""
import dataclasses
import json
import os
import shutil
from collections.abc import AsyncIterator
from datetime import datetime
from pathlib import Path

import pytest
import test_api
from fakes import FakeJev
from fastapi.testclient import TestClient
from pydantic_ai.messages import ModelMessage, ModelRequest, UserPromptPart
from pydantic_ai.models.function import AgentInfo, FunctionModel
from test_api import CLIENT, HEADERS, _cpc, _here

from cornerstone_api.app import create_app
from cornerstone_api.personal_topics import LIVE_CACHE_SECONDS, TRENDING_CACHE_SECONDS, LiveCache
from cornerstone_api.personal_wording import FACT_MEANINGS, INSTRUCTIONS
from cornerstone_api.settings import Settings
from cornerstone_api.waiver_targets import TOP_BY_ADDS, TOP_BY_REST_PER_POSITION, TOP_BY_WEEK_PER_POSITION
from league.jev_port import JevError, NoulQuestion
from league.numbers import ordinal
from league.provider.raw import RawTrending
from league.provider.sleeper import load_raw

repo = test_api.repo
settings = test_api.settings
sources = test_api.sources

PERSONAL = "/clients/cpc/personal"
LIL_FRIDGE = 3
BO_GIRDS = 6
# The words that site copy never holds (decision 08 and the copy rules of the spec).
INNER_NAMES = ("jev", "advisor", "finder", "rival", "brian")
# The recorded data of the cpc build of week 9, fetched on the Tuesday after the games: the rosters, the players file
# with its injury report, the projections ahead, the trending adds, and the history of weeks 1 to 9.
CPC_2026 = Path(__file__).resolve().parents[3] / "clients" / "cpc" / "data" / "2026"
WEEK_9_RAW = CPC_2026 / "week-09" / "raw"
# The nflverse files of the week 9 build: the id map of 2026-11-03, the injury report of 2026-11-05, and the newest
# scrape of the depth chart on 2026-11-10, the morning of the build.
FIXTURES = Path(__file__).resolve().parents[2] / "pipeline" / "tests" / "fixtures"
NFLVERSE_WEEK_9 = (FIXTURES / "nflverse-2026-11-03", FIXTURES / "nflverse-2026-11-05", FIXTURES / "nflverse-2026-11-10")
RETURNS_2026 = Path(__file__).resolve().parents[3] / "data" / "nfl" / "2026" / "returns.json"
# Wednesday of week 10, after the cutoff, so the trade week is 10 and the stats run through week 9.
WEEK_10_NOW = datetime(2026, 11, 11, 12, 0, tzinfo=test_api.ET)
WEEK_9_FETCHED = datetime(2026, 11, 10, 8, 0, tzinfo=test_api.ET)
# The free agents that Brian saw on the weak list of the published week 9 file.
WEAK_ADDS = ("Drew Sample", "Camden Brown", "Van Jefferson")
COREY_KINER = "Corey Kiner"


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
        if "kept_players" in facts:
            kept = facts["kept_players"]
            text = (f"{kept[0]['name']} is the best add." if kept
                    else "No free agent beats your starters this week.")
        else:
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
    # The text waits for its check, then comes whole before "checked" (H10).
    texts = [i for i, kind in enumerate(kinds) if kind.startswith("text-")]
    assert checks[0][0] < min(texts) and max(texts) < checks[1][0]
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
    # The failed first text never leaves the API: each text part comes after the fix part, before "checked" (H10).
    texts = [i for i, kind in enumerate(kinds) if kind.startswith("text-")]
    assert kinds.index("data-fix") < min(texts)
    assert kinds.count("text-start") == 1
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
    assert not any(c["type"].startswith("text-") for c in chunks)
    [miss] = [c["data"] for c in chunks if c["type"] == "data-miss"]
    assert miss["closest"] == ["stack_up", "waiver_targets", "trade_ideas"]
    _ask(api, "weak_spots")
    assert writer.calls == 4


def test_the_check_reads_the_fact_meanings_of_the_instructions(settings, sources):
    # H17: the check reads what `hole`, `can_play_now`, and `weak_starting_slots` mean, from the same dict as Claude.
    writer = Writer()
    checks = Checks([True])
    api = _api(settings, sources, FakeJev(answer=checks.answer), writer)
    _ask(api, "weak_spots")
    assert checks.states[0]["tool_results"]["meanings"] == FACT_MEANINGS
    assert {"hole", "can_play_now", "weak_starting_slots"} <= set(FACT_MEANINGS)
    assert all(meaning in INSTRUCTIONS for meaning in FACT_MEANINGS.values())


def test_a_failed_check_logs_each_failed_sentence_with_its_noul(settings, sources, caplog):
    # H17: the log shows which sentence failed and how sure the check was.
    writer = Writer()
    api = _api(settings, sources, FakeJev(answer=Checks([False, True]).answer), writer)
    with caplog.at_level("INFO", logger="cornerstone_api.claude_stream"):
        _ask(api, "weak_spots")
    [line] = [r.getMessage() for r in caplog.records if "failed the check" in r.getMessage()]
    assert "0.10" in line and "Your weakest spot is" in line


TYPED = "how can i improve my roster"


def _prompt(messages: list[ModelMessage]) -> str:
    return next(part.content for m in messages if isinstance(m, ModelRequest) for part in m.parts
                if isinstance(part, UserPromptPart) and isinstance(part.content, str))


def test_a_typed_question_reaches_the_prompt_and_the_check_of_its_personal_topic(settings, sources):
    # H17: a typed question that routes to weak spots gets an Answer to that question, checked against that question.
    writer = Writer()
    checks = Checks([True])
    api = _api(settings, sources, FakeJev(answer=checks.answer), writer)
    _ask(api, "weak_spots", question=TYPED)
    assert TYPED in _prompt(writer.requests[0])
    assert checks.states[0]["manager_question"] == TYPED


def test_a_tap_reads_no_typed_question_and_checks_against_the_topic_name(settings, sources):
    writer = Writer()
    checks = Checks([True])
    api = _api(settings, sources, FakeJev(answer=checks.answer), writer)
    _ask(api, "weak_spots")
    assert "The manager asks" not in _prompt(writer.requests[0])
    assert checks.states[0]["manager_question"].startswith("Weak spots of ")


def test_a_typed_question_reads_no_kept_answer_and_keeps_none(settings, sources):
    # A tap keeps its Answer. A typed question never reads it and never replaces it, so each typed question gets its own.
    writer = Writer()
    api = _api(settings, sources, FakeJev(answer=Checks([True]).answer), writer)
    _ask(api, "weak_spots")
    _ask(api, "weak_spots", question=TYPED)
    _ask(api, "weak_spots", question="where am i weak")
    assert writer.calls == 3
    _ask(api, "weak_spots")
    assert writer.calls == 3


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


def _prompt(messages: list[ModelMessage]) -> str:
    return next(part.content for m in messages if isinstance(m, ModelRequest) for part in m.parts
                if isinstance(part, UserPromptPart) and isinstance(part.content, str))


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
    # A starter who cannot play now, such as a player on IR, is a hole too.
    for s in starters:
        below = s["projected_rank_at_position"] is None or s["projected_rank_at_position"] > s["starter_line"]
        assert s["hole"] == (s["player"] is None or below or not s["can_play_now"])


def test_each_weak_starting_slot_of_weak_spots_is_a_row(settings, sources):
    # H17: a row names the slot, the player, his position, and his rank, so the check reads no "QB50" string.
    writer = Writer()
    api = _api(settings, sources, FakeJev(answer=Checks([True]).answer), writer)
    weak = []
    for roster_id in range(1, 13):
        _ask(api, "weak_spots", roster_id=roster_id)
        weak += _facts(writer.requests[-1])["weak_starting_slots"]
    assert any(row["player"] for row in weak)
    assert all(set(row) == {"slot", "player", "position", "projected_rank_at_position", "can_play_now"}
               for row in weak)


def _qbs_on_ir(fixture_raw_dir: Path, tmp_path: Path, roster_id: int) -> Path:
    """A copy of the recorded raw week with each QB of `roster_id` on IR, as Sleeper gives a player on IR."""
    raw = tmp_path / "raw-qbs-on-ir"
    shutil.copytree(fixture_raw_dir, raw)
    rosters = json.loads((raw / "rosters.json").read_text())
    players = json.loads((raw / "players.json").read_text())
    roster = next(each for each in rosters if each["roster_id"] == roster_id)
    for pid in roster["players"]:
        if players[pid].get("position") == "QB":
            players[pid] = {**players[pid], "injury_status": "IR", "status": "Inactive"}
    (raw / "players.json").write_text(json.dumps(players))
    return raw


def test_weak_spots_read_a_starter_on_ir_as_out_now_as_trade_ideas_do(settings, sources, fixture_raw_dir, tmp_path):
    # H12: Bo Girds has every QB on IR, so the lineup now has an empty QB slot. Weak spots names it the weakest
    # spot and a hole, as the weak starting slots of `/find` do, though the roster grade still ranks the QB.
    raw = _qbs_on_ir(fixture_raw_dir, tmp_path, BO_GIRDS)
    on_ir = dataclasses.replace(sources, fetch_sleeper=lambda league_id: (load_raw(raw), test_api.FETCHED))
    writer = Writer()
    api = _api(settings, on_ir, FakeJev(answer=Checks([True]).answer), writer)
    block = _block(_chunks(_ask(api, "weak_spots", roster_id=BO_GIRDS)))
    facts = _facts(writer.requests[0])
    assert {"slot": "QB", "player": None, "position": None, "projected_rank_at_position": None,
            "can_play_now": True} in facts["weak_starting_slots"]
    [qb] = [s for s in facts["starters"] if s["slot"] == "QB"]
    assert qb["can_play_now"] is False and qb["hole"] is True
    stats = {stat["label"]: stat["value"] for stat in block["stats"]}
    assert stats["Weakest spot"] == "QB"
    assert int(stats["Holes"]) >= 1
    assert block["rows"][0]["label"] == "QB"
    assert "hole" in block["rows"][0]["note"]


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
    writer = Writer()
    api = _api(settings, sources, FakeJev(answer=Checks([True]).answer), writer)
    for topic in ("weak_spots", "stack_up", "waiver_targets"):
        block = json.dumps(_block(_chunks(_ask(api, topic)))).lower()
        assert not any(name in block for name in INNER_NAMES)


def _caps(api: TestClient):
    asker = api.app.state.askers["cpc"]
    return asker.caps, asker.clock()


def test_past_the_team_cap_a_personal_topic_makes_no_claude_call_and_gives_the_cap_line(settings, sources):
    # AT-37 for a personal Topic: the store holds 25 Answers of Lil Fridge today, so no Claude call runs. The block
    # from code still shows, and the cap line comes with 3 closest Topics, as for the other Topics.
    writer = Writer()
    api = _api(settings, sources, FakeJev(answer=Checks([True]).answer), writer)
    caps, now = _caps(api)
    for _ in range(25):
        caps.record(LIL_FRIDGE, 0.01, now, counts=True)
    chunks = _chunks(_ask(api, "weak_spots"))
    assert writer.calls == 0
    [cap] = [c["data"] for c in chunks if c["type"] == "data-cap"]
    assert cap["cap"] == "team" and cap["line"] == "That's 25 questions today. Ask again tomorrow."
    assert cap["closest"] == ["stack_up", "waiver_targets", "trade_ideas"]
    assert not any(c["type"] == "text-delta" for c in chunks)
    assert not any(c["type"] == "data-check" for c in chunks)
    assert caps.answers_today(LIL_FRIDGE, now) == 25


def test_a_kept_answer_still_comes_back_past_the_cap(settings, sources):
    # Story 48: a kept Answer costs nothing, so it works past a cap and records nothing.
    writer = Writer()
    api = _api(settings, sources, FakeJev(answer=Checks([True]).answer), writer)
    first = _text(_chunks(_ask(api, "weak_spots")))
    caps, now = _caps(api)
    caps.record(None, 25.00, now, counts=False)
    spent = caps.month_usd(now)
    again = _chunks(_ask(api, "weak_spots"))
    assert _text(again) == first
    assert not any(c["type"] == "data-cap" for c in again)
    assert caps.month_usd(now) == spent and caps.answers_today(LIL_FRIDGE, now) == 1


def test_one_checked_answer_counts_once_and_costs_the_league(settings, sources):
    # Decision 04: a checked Claude Answer is one Answer of the team, and its cost goes to the league month.
    writer = Writer()
    api = _api(settings, sources, FakeJev(answer=Checks([False, True]).answer), writer)
    _chunks(_ask(api, "weak_spots"))
    caps, now = _caps(api)
    assert writer.calls == 2
    assert caps.answers_today(LIL_FRIDGE, now) == 1
    assert caps.month_usd(now) > 0


def test_an_honest_miss_and_an_error_cost_the_league_but_do_not_count(settings, sources):
    class DownJev(FakeJev):
        def ask(self, state, questions):
            raise JevError("down")

    writer = Writer()
    api = _api(settings, sources, FakeJev(answer=Checks([False, False]).answer), writer)
    _chunks(_ask(api, "weak_spots"))
    caps, now = _caps(api)
    after_miss = caps.month_usd(now)
    assert after_miss > 0 and caps.answers_today(LIL_FRIDGE, now) == 0
    down = _api(settings, sources, DownJev(), writer)
    _chunks(_ask(down, "stack_up"))
    caps, now = _caps(down)
    assert caps.month_usd(now) > after_miss and caps.answers_today(LIL_FRIDGE, now) == 0


class Fetches:
    """The Sleeper fetch of the recorded data, with a count of its calls, so a test sees each live load."""

    def __init__(self, raw_dir: Path):
        self.raw_dir = raw_dir
        self.calls = 0

    def fetch(self, league_id: str):
        self.calls += 1
        return load_raw(self.raw_dir), test_api.FETCHED


def test_a_kept_answer_within_the_live_window_reads_no_sleeper_data(settings, sources, fixture_raw_dir):
    # AT-8: the tap on a kept Answer must not wait on a second live load, so the site shows no step line before it.
    fetches = Fetches(fixture_raw_dir)
    writer = Writer()
    api = _api(settings, dataclasses.replace(sources, fetch_sleeper=fetches.fetch),
               FakeJev(answer=Checks([True]).answer), writer)
    _ask(api, "weak_spots")
    loads = fetches.calls
    assert loads > 0
    tap = _chunks(_ask(api, "weak_spots"))
    assert fetches.calls == loads
    assert writer.calls == 1
    # A kept Answer sends no tool part, so the site has no step to show before the text.
    assert not any(c["type"].startswith("tool-") for c in tap)


def test_past_the_live_window_a_tap_loads_the_league_again(settings, sources, fixture_raw_dir):
    # A waiver claim or a trade must reach the key, so the cached league lasts only its window.
    fetches = Fetches(fixture_raw_dir)
    api = _api(settings, dataclasses.replace(sources, fetch_sleeper=fetches.fetch),
               FakeJev(answer=Checks([True]).answer), Writer())
    now = [0.0]
    api.app.state.live["cpc"] = LiveCache(LIVE_CACHE_SECONDS, clock=lambda: now[0])
    _ask(api, "weak_spots")
    loads = fetches.calls
    now[0] = LIVE_CACHE_SECONDS - 1
    _ask(api, "weak_spots")
    assert fetches.calls == loads
    now[0] = LIVE_CACHE_SECONDS
    _ask(api, "weak_spots")
    assert fetches.calls == 2 * loads


@pytest.fixture
def week_9_repo(tmp_path, fixture_nflverse_dir) -> Path:
    """A repo with the history of weeks 1 to 9, the Returns file, and the nflverse files of the week 9 build. The live
    load saves week 9 into the history, so the history is a copy."""
    shutil.copytree(CPC_2026 / "history", tmp_path / "data" / "2026" / "history")
    shutil.copy(RETURNS_2026, tmp_path / "data" / "2026" / "returns.json")
    cache = tmp_path / "data" / "cache" / "nflverse"
    shutil.copytree(fixture_nflverse_dir, cache)
    for folder in NFLVERSE_WEEK_9:
        shutil.copytree(folder, cache, dirs_exist_ok=True)
    for cached in cache.iterdir():
        os.utime(cached)
    return tmp_path


def _week_9_trending() -> list[RawTrending]:
    return [RawTrending.model_validate(row) for row in json.loads((WEEK_9_RAW / "trending.json").read_text())]


@pytest.fixture
def week_9_raw():
    return load_raw(WEEK_9_RAW)


def _week_9_api(repo: Path, sources, jev: FakeJev, writer: Writer, raw=None) -> TestClient:
    """The app over the recorded week 9 data, in trade week 10. `raw` changes the Sleeper data, such as a roster."""
    week_9 = load_raw(WEEK_9_RAW) if raw is None else raw
    settings = Settings(passphrases={"cpc": test_api.PASSPHRASE}, repo=repo, result_cache_dir=repo / "results",
                        commissioner_keys={"cpc": "commissioner-test"})
    nine = dataclasses.replace(sources, fetch_sleeper=lambda league_id: (week_9, WEEK_9_FETCHED),
                               fetch_trending=_week_9_trending, clock=lambda: WEEK_10_NOW)
    return _api(settings, nine, jev, writer)


class Reads:
    """The Jev answers of the waiver read by player name: the add and the stash Noul of each player, 0.1 by default,
    and a pass of each claim check. Each waiver state it reads stays in `players` by name."""

    def __init__(self, add: dict[str, float] | None = None, stash: dict[str, float] | None = None):
        self.add = add or {}
        self.stash = stash or {}
        self.players: dict[str, dict] = {}
        self.need: dict | None = None

    def answer(self, key: str, question: NoulQuestion, state: dict) -> float:
        if "player" not in state:
            return 0.95
        name = state["player"]["name"]
        self.players[name] = state["player"]
        self.need = state["team"]
        return (self.add if key == "add" else self.stash).get(name, 0.1)


def _reads(jev: FakeJev) -> list:
    return [request for request in jev.requests if "player" in request.state]


def test_waiver_targets_read_each_free_agent_by_hard_rules_only_with_one_jev_request_each(week_9_repo, sources,
                                                                                          week_9_raw):
    reads = Reads()
    jev = FakeJev(answer=reads.answer)
    _ask(_week_9_api(week_9_repo, sources, jev, Writer()), "waiver_targets", roster_id=BO_GIRDS)
    rostered = {pid for roster in week_9_raw.rosters for pid in roster.players or []}
    names = {pid: (entry.get("full_name") or "") for pid, entry in week_9_raw.players.items()}
    read = _reads(jev)
    assert read and len(read) == len(reads.players)
    # One run stays under about 60 Jev requests: the cap of the candidates and the claim check.
    assert len(read) <= TOP_BY_ADDS + 4 * (TOP_BY_WEEK_PER_POSITION + TOP_BY_REST_PER_POSITION)
    assert len(jev.requests) <= 60
    rostered_names = {names[pid] for pid in rostered}
    for name, player in reads.players.items():
        assert name not in rostered_names
        assert player["position"] in ("QB", "RB", "WR", "TE")
        assert player["week_projection"] > 0 or player["rest_of_season_projection"] > 0
    # Each request asks the two Nouls of one player, with the need of the team in the state.
    assert all(set(request.questions) == {"add", "stash"} for request in read)
    assert reads.need is not None and reads.need["name"] == "Bo Girds"


def test_the_facts_of_a_free_agent_say_why_he_trends_from_the_depth_chart_and_the_sleeper_adds(week_9_repo, sources):
    # Corey Kiner is third on the chart of the Patriots, and both backs above him are out, so his role is open.
    reads = Reads()
    _ask(_week_9_api(week_9_repo, sources, FakeJev(answer=reads.answer), Writer()), "waiver_targets",
         roster_id=BO_GIRDS)
    kiner = reads.players[COREY_KINER]
    assert kiner["sleeper_adds_last_day"] > 0
    assert kiner["depth_chart_place"] == 3 and kiner["every_player_above_is_out"] is True
    assert all(above["out_now"] for above in kiner["players_above"])
    assert [week["week"] for week in kiner["last_weeks"]] == [7, 8, 9]
    assert {"points", "snap_share_percent", "targets", "carries"} <= set(next(
        week for week in kiner["last_weeks"] if week["played"]))


def test_the_team_need_names_the_empty_qb_slot_when_the_only_healthy_qb_leaves(week_9_repo, sources, week_9_raw):
    # Bo Girds holds Lamar Jackson on IR. Without Malik Willis, no QB can play now, so the QB slot is empty.
    mine = next(roster for roster in week_9_raw.rosters if roster.roster_id == BO_GIRDS)
    willis = next(pid for pid in mine.players or [] if week_9_raw.players[pid].get("full_name") == "Malik Willis")
    mine.players = [pid for pid in mine.players or [] if pid != willis]
    reads = Reads()
    _ask(_week_9_api(week_9_repo, sources, FakeJev(answer=reads.answer), Writer(), raw=week_9_raw),
         "waiver_targets", roster_id=BO_GIRDS)
    assert reads.need is not None
    assert "QB: empty" in reads.need["weak_starting_slots"]
    assert reads.need["weakest_starter_by_position"]["QB"] == {"slot": "QB", "player": None}
    qbs = [player for player in reads.players.values() if player["position"] == "QB"]
    assert qbs and all(player["empty_slots_he_fits"] == ["QB"] for player in qbs)


def test_the_answer_reads_the_kept_players_only_best_first_and_the_block_lists_them(week_9_repo, sources):
    reads = Reads(add={COREY_KINER: 0.92}, stash={"Kyler Murray": 0.81, "Drew Sample": 0.5})
    writer = Writer()
    chunks = _chunks(_ask(_week_9_api(week_9_repo, sources, FakeJev(answer=reads.answer), writer),
                          "waiver_targets", roster_id=BO_GIRDS))
    block = _block(chunks)
    assert [row["label"] for row in block["rows"]] == [COREY_KINER, "Kyler Murray"]
    assert block["fact"] == "2 free agents worth a claim"
    facts = _facts(writer.requests[0])
    assert set(facts) == {"team", "teams_in_league", "week", "team_need", "kept_players"}
    assert [(p["name"], p["kind"]) for p in facts["kept_players"]] == [(COREY_KINER, "add this week"),
                                                                     ("Kyler Murray", "stash for later weeks")]
    assert not any(name in json.dumps(facts) for name in WEAK_ADDS)
    assert "Quote no FAAB bid" in _prompt(writer.requests[0])
    assert all("$" not in row["value"] for row in block["rows"])


def test_with_no_player_above_the_yes_line_the_answer_says_no_free_agent_beats_the_starters(week_9_repo, sources):
    writer = Writer()
    chunks = _chunks(_ask(_week_9_api(week_9_repo, sources, FakeJev(answer=Reads().answer), writer),
                          "waiver_targets", roster_id=BO_GIRDS))
    block = _block(chunks)
    assert block["fact"] == "No free agent beats the starters this week"
    assert block["rows"] == []
    assert _facts(writer.requests[0])["kept_players"] == []
    assert "no free agent beats the starters" in _prompt(writer.requests[0])
    # It is a real Answer, checked and kept, not the honest miss.
    assert [c["data"]["state"] for c in chunks if c["type"] == "data-check"][-1] == "checked"


def test_a_kept_waiver_answer_comes_back_with_its_block_and_no_jev_read(week_9_repo, sources):
    reads = Reads(add={COREY_KINER: 0.92})
    jev = FakeJev(answer=reads.answer)
    writer = Writer()
    api = _week_9_api(week_9_repo, sources, jev, writer)
    first = _chunks(_ask(api, "waiver_targets", roster_id=BO_GIRDS))
    # The first tap reads each free agent, and its block lists the player that the read kept.
    assert _reads(jev)
    assert [row["label"] for row in _block(first)["rows"]] == [COREY_KINER]
    asked = len(jev.requests)
    second = _chunks(_ask(api, "waiver_targets", roster_id=BO_GIRDS))
    assert len(jev.requests) == asked
    assert writer.calls == 1
    assert _block(second) == _block(first)
    assert _text(second) == _text(first)


def test_a_new_injury_of_a_free_agent_changes_the_waiver_key(week_9_repo, sources, week_9_raw):
    # AT-8: the key covers the facts of each candidate, so a new injury gives a fresh Answer.
    writer = Writer()
    jev = FakeJev(answer=Reads().answer)
    first = _chunks(_ask(_week_9_api(week_9_repo, sources, jev, writer), "waiver_targets", roster_id=BO_GIRDS))
    kiner = next(pid for pid, entry in week_9_raw.players.items() if entry.get("full_name") == COREY_KINER)
    week_9_raw.players[kiner] = {**week_9_raw.players[kiner], "injury_status": "Questionable"}
    second = _chunks(_ask(_week_9_api(week_9_repo, sources, jev, writer, raw=week_9_raw), "waiver_targets",
                          roster_id=BO_GIRDS))
    key = lambda chunks: [c["data"]["key"] for c in chunks if c["type"] == "data-key"]
    assert key(second) != key(first)


def test_a_failed_waiver_read_ends_with_an_error_and_no_claude_call(week_9_repo, sources):
    class DownReads(FakeJev):
        def ask(self, state, questions):
            if "player" in state:
                raise JevError("down")
            return super().ask(state, questions)

    writer = Writer()
    chunks = _chunks(_ask(_week_9_api(week_9_repo, sources, DownReads(), writer), "waiver_targets",
                          roster_id=BO_GIRDS))
    assert any(c["type"] == "error" for c in chunks)
    assert not any(c["type"] == "data-block" for c in chunks)
    assert writer.calls == 0


def test_past_the_team_cap_the_waiver_targets_make_no_jev_read(week_9_repo, sources):
    jev = FakeJev(answer=Reads().answer)
    writer = Writer()
    api = _week_9_api(week_9_repo, sources, jev, writer)
    caps, now = _caps(api)
    for _ in range(25):
        caps.record(BO_GIRDS, 0.01, now, counts=True)
    chunks = _chunks(_ask(api, "waiver_targets", roster_id=BO_GIRDS))
    assert not _reads(jev) and writer.calls == 0
    block = _block(chunks)
    assert block["rows"] == [] and block["fact"] == "Free agents for the QB slot"


def test_the_trending_list_serves_its_window_then_loads_again():
    now = [0.0]
    calls = []
    cache = LiveCache(LIVE_CACHE_SECONDS, clock=lambda: now[0])

    def fetch() -> list[RawTrending]:
        calls.append(now[0])
        return _week_9_trending()

    cache.trending(fetch)
    now[0] = TRENDING_CACHE_SECONDS - 1
    cache.trending(fetch)
    assert len(calls) == 1
    now[0] = TRENDING_CACHE_SECONDS
    cache.trending(fetch)
    assert len(calls) == 2
