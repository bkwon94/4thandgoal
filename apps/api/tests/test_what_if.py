"""
Tests for the What-if route of the API at the HTTP seam, through the FastAPI test client and a real uvicorn server.
The route reads a real CPC 2026 week 10 sim file of the sim step of the build, so no test needs the network.
"""
import gzip
import json
import logging
import os
import shutil
import socket
import threading
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import httpx
import pytest
import uvicorn
from cpc import cpc_client
from fastapi.testclient import TestClient

from analyzer.ratelimit import RateLimiter
from cornerstone_api.app import create_app
from cornerstone_api.settings import Settings
from cornerstone_api.sources import Sources
from cornerstone_api.value_models import VALUE_MODELS
from cornerstone_api.what_if import WHAT_IFS_PER_MINUTE
from league.provider.sleeper import load_raw

ET = ZoneInfo("America/New_York")
NOW = datetime(2026, 11, 17, 12, 0, tzinfo=ET)
PASSPHRASE = "cornerstone-test"
PASS = {"X-League-Passphrase": PASSPHRASE}
# The week file of the sim step of the build for CPC 2026 week 10, from `make sim CLIENT=cpc WEEK=10` of the pipeline.
# tests/test_sim.py of the pipeline checks that a fresh sim step writes the same file.
WEEK_10_SIM = Path(__file__).parent / "fixtures" / "sim" / "cpc-week-10-sim.json"
WHAT_IF = "/clients/cpc/sim/what-if"
BO_GIRDS = 6
KEYS = {"schema_version", "season", "week", "runs", "effective_runs", "you", "set", "teams", "sample",
        "sample_weights", "page", "board"}
WIN_ABOVE_WEEK_11 = {"week": 11, "game": "win", "median": "above"}


def _no_network(*args, **kwargs):
    raise AssertionError("network call")


@pytest.fixture
def repo(tmp_path, fixture_history_root, fixture_nflverse_dir):
    """A client folder with the published week 10 sim file, and the week 6 history and nflverse cache that the teams
    route of the analyzer reads."""
    shutil.copytree(fixture_history_root, tmp_path / "data" / "2026" / "history")
    shutil.copytree(fixture_nflverse_dir, tmp_path / "data" / "cache" / "nflverse")
    for cached in (tmp_path / "data" / "cache" / "nflverse").iterdir():
        os.utime(cached)
    week_10 = tmp_path / "published" / "2026" / "week-10"
    week_10.mkdir(parents=True)
    shutil.copy(WEEK_10_SIM, week_10 / "sim.json")
    return tmp_path


def _app(repo: Path, fetch_sleeper):
    """The app of the CPC client in `repo`, with `fetch_sleeper` as its one Sleeper fetch and no other network."""
    settings = Settings(passphrases={"cpc": PASSPHRASE}, repo=repo, result_cache_dir=repo / "results",
                        commissioner_keys={"cpc": "key"}, eggs_dir=repo / "eggs", ask_dir=repo / "ask",
                        rate_limit_per_minute=600)
    client = cpc_client(at=repo, models=VALUE_MODELS)
    sources = Sources(client, fetch_sleeper=fetch_sleeper, fetch_nflverse=_no_network,
                      fetch_history_week=_no_network, read_chart=_no_network, clock=lambda: NOW)
    return create_app(settings, [client], sources={"cpc": sources})


@pytest.fixture
def app(repo, fixture_raw_dir):
    """The app with the recorded week 6 Sleeper data, so the teams route of the analyzer answers."""
    return _app(repo, lambda league_id: (load_raw(fixture_raw_dir), NOW))


@pytest.fixture
def api(app):
    return TestClient(app)


def test_a_what_if_with_one_set_result_and_no_passphrase_answers_each_key_of_the_spec(api):
    response = api.post(WHAT_IF, json={"you": BO_GIRDS, "set": [WIN_ABOVE_WEEK_11]})
    assert response.status_code == 200
    body = response.json()
    assert set(body) == KEYS
    assert (body["season"], body["week"], body["runs"], body["you"]) == (2026, 10, 10_000, BO_GIRDS)
    assert body["set"] == [WIN_ABOVE_WEEK_11]
    assert body["effective_runs"] < body["runs"]
    assert len(body["teams"]) == 12 and len(body["sample"]) == len(body["sample_weights"]) == 200
    assert body["page"]["you"] == BO_GIRDS


def test_a_what_if_with_no_set_result_gives_the_page_of_bo_girds_in_the_week_file(api):
    body = api.post(WHAT_IF, json={"you": BO_GIRDS}).json()
    file = json.loads(WEEK_10_SIM.read_text(encoding="utf-8"))
    assert body["page"] == file["pages"][str(BO_GIRDS)]
    assert body["teams"] == file["teams"]
    assert body["board"] == [{key: row[key] for key in ("roster_id", "goals")} for row in file["board"]]
    assert body["sample"] == file["sample"]
    assert body["effective_runs"] == body["runs"] == 10_000


def test_two_equal_what_ifs_give_the_finish_lists_the_week_plans_the_score_to_beat_and_the_board_twice(api):
    # AT-20, on the week 10 file of the tests: a win and a median win for Bo Girds in week 11, twice.
    call = {"you": BO_GIRDS, "set": [WIN_ABOVE_WEEK_11]}
    first, second = (api.post(WHAT_IF, json=call).json() for _ in range(2))
    assert first == second
    page = first["page"]
    plans = [path["plan"] for finish in page["finishes"]["spot"] for path in finish["paths"]]
    assert plans and all(plan["weeks"] for plan in plans)
    assert [s["week"] for s in page["score_to_beat"]] == [11, 12, 13, 14]
    assert len(first["board"]) == 12
    file = json.loads(WEEK_10_SIM.read_text(encoding="utf-8"))
    board = {row["roster_id"]: row["goals"]["spot"]["odds"] for row in first["board"]}
    assert board[BO_GIRDS] == page["goals"]["spot"]["odds"] == first["teams"][str(BO_GIRDS)]["playoff"]
    assert board != {row["roster_id"]: row["goals"]["spot"]["odds"] for row in file["board"]}
    print("AT-20 board spot odds", board, "plans of the spot", len(plans))


def test_the_what_if_reads_the_latest_published_week(api, repo):
    # An older week file with another week number: the route reads only week 10, the latest.
    week_9 = repo / "published" / "2026" / "week-09"
    week_9.mkdir()
    (week_9 / "sim.json").write_text("not a sim file", encoding="utf-8")
    assert api.post(WHAT_IF, json={"you": BO_GIRDS}).json()["week"] == 10


def test_the_what_if_answers_with_each_sleeper_request_blocked_and_makes_none(repo, monkeypatch, caplog):
    tried: list[str] = []
    real = socket.getaddrinfo

    def blocked(host, *args, **kwargs):
        tried.append(str(host))
        if "sleeper" in str(host):
            raise OSError(f"blocked: {host}")
        return real(host, *args, **kwargs)

    monkeypatch.setattr(socket, "getaddrinfo", blocked)
    caplog.set_level(logging.INFO)
    response = TestClient(_app(repo, _no_network)).post(WHAT_IF, json={"you": BO_GIRDS, "set": [WIN_ABOVE_WEEK_11]})
    print("AT-16 status", response.status_code, "hosts tried", tried)
    print("AT-16 log", [r.getMessage() for r in caplog.records])
    assert response.status_code == 200
    assert not [host for host in tried if "sleeper" in host]
    assert not [r for r in caplog.records if "sleeper" in r.getMessage().lower()]


def test_the_what_if_has_its_own_limit_and_the_other_routes_still_answer(api):
    # The shared limit of the analyzer is 10 a minute in the real app.
    api.app.state.limiter = RateLimiter(10)
    # A set result for a played week fails its check before the draw, so each call is cheap and still counts.
    bad = {"you": BO_GIRDS, "set": [{"week": 3, "game": "win", "median": "above"}]}
    statuses = [api.post(WHAT_IF, json=bad).status_code for _ in range(WHAT_IFS_PER_MINUTE + 1)]
    assert statuses[:WHAT_IFS_PER_MINUTE] == [422] * WHAT_IFS_PER_MINUTE
    assert statuses[-1] == 429
    blocked = api.post(WHAT_IF, json={"you": BO_GIRDS})
    print("AT-17 statuses", statuses, "then", blocked.status_code, "Retry-After", blocked.headers.get("Retry-After"))
    assert blocked.status_code == 429 and 0 < int(blocked.headers["Retry-After"]) <= 60
    health = api.get("/health")
    teams = api.get("/clients/cpc/teams", params={"season": 2026}, headers=PASS)
    print("AT-17 /health", health.status_code, "analyzer /teams", teams.status_code)
    assert health.status_code == 200 and teams.status_code == 200


def test_the_what_if_answer_is_gzip_and_under_60_kb(app):
    with TestClient(app) as api, api.stream("POST", WHAT_IF, json={"you": BO_GIRDS, "set": [WIN_ABOVE_WEEK_11]},
                                            headers={"Accept-Encoding": "gzip"}) as response:
        raw = b"".join(response.iter_raw())
    print("AT-18 Content-Encoding", response.headers.get("content-encoding"), "size", len(raw), "bytes")
    assert response.headers["content-encoding"] == "gzip"
    assert len(raw) < 60_000
    assert json.loads(gzip.decompress(raw))["week"] == 10


def test_a_set_result_for_a_played_week_answers_422_with_a_message_that_names_the_week(api):
    response = api.post(WHAT_IF, json={"you": BO_GIRDS, "set": [{"week": 3, "game": "win", "median": "above"}]})
    print("AT-20", response.status_code, response.json())
    assert response.status_code == 422
    assert "week 3" in response.json()["detail"]


def test_a_what_if_for_a_roster_not_in_the_league_answers_422(api):
    assert api.post(WHAT_IF, json={"you": 99}).status_code == 422


def test_no_route_reads_or_writes_an_announcement(app):
    paths = sorted(app.openapi()["paths"])
    print("AT-67 routes", paths)
    assert not [path for path in paths if "announce" in path.lower()]


def test_two_equal_what_ifs_run_the_sim_twice(api, caplog):
    caplog.set_level(logging.INFO, logger="cornerstone_api.what_if")
    body = {"you": BO_GIRDS, "set": [WIN_ABOVE_WEEK_11]}
    first, second = api.post(WHAT_IF, json=body), api.post(WHAT_IF, json=body)
    runs = [r.getMessage() for r in caplog.records if r.getMessage().startswith("What-if of cpc ran")]
    print("AT-68 log", runs)
    assert len(runs) == 2
    assert first.json() == second.json()


@pytest.fixture
def server(app):
    """The app on a real uvicorn server on a free local port, so a client can go away in the middle of a call."""
    live = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=0, log_level="warning"))
    thread = threading.Thread(target=live.run, daemon=True)
    thread.start()
    deadline = time.monotonic() + 10
    while not live.started and time.monotonic() < deadline:
        time.sleep(0.01)
    port = live.servers[0].sockets[0].getsockname()[1]
    yield f"http://127.0.0.1:{port}"
    live.should_exit = True
    thread.join(timeout=10)


def test_a_client_that_goes_away_after_100_ms_stops_the_sim_before_10000_runs(server, caplog):
    caplog.set_level(logging.INFO, logger="cornerstone_api.what_if")
    with pytest.raises(httpx.ReadTimeout):
        httpx.post(f"{server}{WHAT_IF}", json={"you": BO_GIRDS, "set": [WIN_ABOVE_WEEK_11]}, timeout=0.1)
    # The sim runs on in the server thread until its next stop check, so the test waits for the log line.
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        lines = [r.getMessage() for r in caplog.records if r.name == "cornerstone_api.what_if"]
        if lines:
            break
        time.sleep(0.05)
    print("AT-19 log", lines)
    assert len(lines) == 1 and "stopped after" in lines[0] and "the client went away" in lines[0]
    done = int(lines[0].split("stopped after ")[1].split(" of ")[0])
    assert 0 < done < 10_000
