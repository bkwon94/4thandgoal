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
from cornerstone_api.personal_topics import LIVE_CACHE_SECONDS, LiveCache
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
# The real waiver file of cpc week 9. Its add buckets hold players with a rest of season projection of 0.
WEEK_9_WAIVER = PUBLISHED_WAIVER.parents[1] / "week-09" / "waiver.json"


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


def _publish_waiver(settings, source: Path = PUBLISHED_WAIVER) -> dict:
    folder = settings.repo / "published" / "2026" / "week-06"
    folder.mkdir(parents=True)
    shutil.copy(source, folder / "waiver.json")
    return json.loads(source.read_text())


def _prompt(messages: list[ModelMessage]) -> str:
    return next(part.content for m in messages if isinstance(m, ModelRequest) for part in m.parts
                if isinstance(part, UserPromptPart) and isinstance(part.content, str))


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


def test_waiver_targets_drop_each_player_with_no_rest_of_season_projection(settings, sources):
    board = _publish_waiver(settings, WEEK_9_WAIVER)
    writer = Writer()
    api = _api(settings, sources, FakeJev(answer=Checks([True]).answer), writer)
    _ask(api, "waiver_targets")
    listed = {player["name"] for player in _facts(writer.requests[0])["waiver_list"]}
    zero = {player["name"] for key, bucket in board["buckets"].items() if key != "drops" for player in bucket
            if not player.get("ros_projection")}
    assert zero, "the week 9 file holds players with a rest of season projection of 0"
    assert listed and not listed & zero


def test_waiver_targets_put_the_trending_bucket_first_and_give_no_bid(settings, sources):
    board = _publish_waiver(settings, WEEK_9_WAIVER)
    writer = Writer()
    api = _api(settings, sources, FakeJev(answer=Checks([True]).answer), writer)
    block = _block(_chunks(_ask(api, "waiver_targets")))
    listed = _facts(writer.requests[0])["waiver_list"]
    buckets = [player["bucket"] for player in listed]
    trending = sum(1 for bucket in buckets if bucket == "trending")
    assert board["buckets"]["trending"] and buckets[:trending] == ["trending"] * trending
    assert all("bid" not in player for player in listed)
    assert all("$" not in row["value"] for row in block["rows"])
    assert "Quote no FAAB bid" in _prompt(writer.requests[0])


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
    # A starter who cannot play now, such as a player on IR, is a hole too.
    for s in starters:
        below = s["projected_rank_at_position"] is None or s["projected_rank_at_position"] > s["starter_line"]
        assert s["hole"] == (s["player"] is None or below or not s["can_play_now"])


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
    assert "QB: empty" in facts["weak_starting_slots"]
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
    _publish_waiver(settings)
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
