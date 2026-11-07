"""
Tests for the drop route of the eggs, its letter rule, and the drop step of the publish, with a temp SQLite file.
The rosters come from the recorded week 6 Sleeper data, so no test needs the network.
"""
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import httpx
import pytest
from cornerstone.egg_drop import run_egg_drop
from cpc import cpc_client
from fastapi.testclient import TestClient

from cornerstone_api.app import create_app
from cornerstone_api.settings import Settings
from cornerstone_api.sources import Sources
from cornerstone_api.value_models import VALUE_MODELS
from eggs.keys import API_URL
from league.provider.sleeper import load_raw

ET = ZoneInfo("America/New_York")
NOW = datetime(2026, 10, 19, 12, 0, tzinfo=ET)
PASSPHRASE = "cornerstone-test"
KEY = "commissioner-test"
COMMISSIONER = {"X-Commissioner-Key": KEY}
BASE = "/clients/cpc/eggs"
LIL_FRIDGE = 3


def _no_network(*args, **kwargs):
    raise AssertionError("network call")


@pytest.fixture
def settings(tmp_path, fixture_history_root, fixture_nflverse_dir):
    shutil.copytree(fixture_history_root, tmp_path / "data" / "2026" / "history")
    shutil.copytree(fixture_nflverse_dir, tmp_path / "data" / "cache" / "nflverse")
    for cached in (tmp_path / "data" / "cache" / "nflverse").iterdir():
        os.utime(cached)
    return Settings(passphrases={"cpc": PASSPHRASE}, repo=tmp_path, result_cache_dir=tmp_path / "results",
                    commissioner_keys={"cpc": KEY}, eggs_dir=tmp_path / "eggs")


@pytest.fixture
def api(settings, fixture_raw_dir):
    client = cpc_client(at=settings.repo, models=VALUE_MODELS)
    sources = Sources(client, fetch_sleeper=lambda league_id: (load_raw(fixture_raw_dir), NOW),
                      fetch_nflverse=_no_network, fetch_history_week=_no_network, read_chart=_no_network,
                      clock=lambda: NOW)
    return TestClient(create_app(settings, [client], sources={"cpc": sources}))


def _spots(count: int) -> list[dict]:
    """`count` test eggs, each on its own target of the midseason page. No spot is real."""
    return [{"page": "/midseason/2026/", "target": f"test-{index}", "action": "tap3", "conditions": {}}
            for index in range(count)]


def _letters(api, week=9, count=6) -> list[str]:
    response = api.post(f"{BASE}/drop", json={"week": week, "eggs": _spots(count)}, headers=COMMISSIONER)
    assert response.status_code == 200, response.text
    return [egg["letter"] for egg in response.json()["eggs"]]


def test_the_first_drop_of_an_empty_store_holds_a_c_d_e_g_and_l(api):
    assert _letters(api) == ["A", "C", "D", "E", "G", "L"]


def test_the_drop_refuses_a_letter_in_the_body(api):
    eggs = [{**spot, "letter": "C"} for spot in _spots(1)]
    response = api.post(f"{BASE}/drop", json={"week": 9, "eggs": eggs}, headers=COMMISSIONER)
    assert response.status_code == 422


def _hold(api, roster_id: int, word: str, letters: str, week: int = 1) -> None:
    """Give the roster a claim of each letter in the egg word, on test eggs of an old week outside the hunt."""
    store = api.app.state.hunts["cpc"].store
    eggs = store.drop(week, [{"page": "/test/", "target": f"held-{week}-{index}", "action": "tap2", "conditions": {},
                              "letter": letter} for index, letter in enumerate(letters)], NOW)
    for egg in eggs:
        store.claim(egg.id, roster_id, word, None, NOW)


def test_a_letter_that_one_manager_no_longer_needs_falls_behind_the_letters_that_every_manager_needs(api):
    _hold(api, LIL_FRIDGE, "LANSDALE", "AA", week=1)
    _hold(api, LIL_FRIDGE, "EAGLES", "A", week=2)
    assert _letters(api) == ["C", "D", "E", "G", "L", "N"]


def test_the_guard_keeps_the_last_letter_that_the_leader_of_an_egg_word_needs(api):
    # Lil Fridge leads EAGLES and needs only an E, and E is still a letter that every manager needs.
    _hold(api, LIL_FRIDGE, "EAGLES", "EAGLS")
    assert "E" not in _letters(api)


def test_an_egg_word_with_a_winner_takes_no_more_letters(api):
    # G sits only in EAGLES, so with EAGLES won, no manager needs a G.
    _hold(api, LIL_FRIDGE, "EAGLES", "EAGLES")
    assert _letters(api) == ["A", "C", "D", "E", "L", "N"]


def test_no_letter_repeats_in_one_drop(api):
    letters = _letters(api, count=11)
    assert len(set(letters)) == 11


def test_a_drop_larger_than_the_letters_to_pick_drops_fewer_eggs_and_repeats_no_letter(api):
    # The three egg words hold 11 letters, so a drop of 12 eggs drops the first 11, each with its own letter.
    response = api.post(f"{BASE}/drop", json={"week": 9, "eggs": _spots(12)}, headers=COMMISSIONER)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["dropped"] == 11
    assert [egg["target"] for egg in body["eggs"]] == [f"test-{index}" for index in range(11)]
    assert len({egg["letter"] for egg in body["eggs"]}) == 11


@pytest.mark.parametrize("conditions", [
    {"clock": "11pm-midnight"}, {"clock": "25:00-26:00"}, {"clock": "23:00"}, {"clock": 2300},
    {"weekday": "thursday"}, {"weekday": "xyz"}, {"weekday": 3},
])
def test_the_drop_refuses_a_bad_clock_window_or_weekday_and_drops_nothing(api, conditions):
    eggs = [{**_spots(1)[0], "conditions": conditions}]
    response = api.post(f"{BASE}/drop", json={"week": 9, "eggs": eggs}, headers=COMMISSIONER)
    assert response.status_code == 422
    assert api.app.state.hunts["cpc"].store.eggs() == []


def test_the_drop_takes_a_good_clock_window_and_weekday(api):
    eggs = [{**_spots(1)[0], "conditions": {"clock": "23:00-00:00", "weekday": "Thu"}}]
    response = api.post(f"{BASE}/drop", json={"week": 9, "eggs": eggs}, headers=COMMISSIONER)
    assert response.status_code == 200, response.text


def test_a_second_drop_of_one_week_adds_nothing_and_answers_with_the_eggs_there(api):
    first = api.post(f"{BASE}/drop", json={"week": 9, "eggs": _spots(1)}, headers=COMMISSIONER).json()
    second = api.post(f"{BASE}/drop", json={"week": 9, "eggs": _spots(2)}, headers=COMMISSIONER).json()
    assert first["dropped"] == 1
    assert second["dropped"] == 0
    assert second["eggs"] == first["eggs"]


# A temp egg file of week 8 with six test spots, four of them confirmed. No spot is real.
EGG_FILE = """
[[eggs]]
week = 7
page = "/week/2026/7/"
target = "test-old"
action = "tap2"
conditions = {}
reason = "A test spot of an old week."
confirmed = true
""" + "".join(f"""
[[eggs]]
week = 8
page = "/week/2026/8/"
target = "test-{index}"
action = "tap3"
conditions = {{ theme = "light" }}
reason = "Test spot {index}."
confirmed = {"true" if index < 4 else "false"}
""" for index in range(6))


def _egg_file(tmp_path: Path, text: str = EGG_FILE) -> Path:
    path = tmp_path / "cpc-eggs" / "2026.toml"
    path.parent.mkdir(parents=True)
    path.write_text(text, encoding="utf-8")
    return path


def _egg_lines(eggs) -> list[str]:
    return [f"Egg {egg.id}  letter {egg.letter}  {egg.page}  {egg.target}" for egg in eggs]


def _board_left(api) -> int:
    return api.get(f"{BASE}/board").json()["counts"]["left"]


def test_the_drop_step_sends_only_the_confirmed_eggs_of_the_week_and_says_the_count(api, settings, tmp_path):
    client = cpc_client(at=settings.repo, models=VALUE_MODELS)
    before = _board_left(api)
    line = run_egg_drop(client, 8, _egg_file(tmp_path), api, KEY)
    eggs = api.app.state.hunts["cpc"].store.eggs(8)
    assert line.splitlines() == ["Dropped 4 eggs of week 8.", *_egg_lines(eggs)]
    assert _board_left(api) == before + 4
    assert [egg.target for egg in eggs] == ["test-0", "test-1", "test-2", "test-3"]
    assert all(egg.conditions == {"theme": "light"} for egg in eggs)


def test_a_week_with_no_confirmed_egg_drops_none_and_says_so(api, settings, tmp_path):
    client = cpc_client(at=settings.repo, models=VALUE_MODELS)
    path = _egg_file(tmp_path, EGG_FILE.replace("confirmed = true", "confirmed = false"))
    line = run_egg_drop(client, 8, path, api, KEY)
    assert line.startswith("No eggs dropped: week 8 has no confirmed egg")
    assert _board_left(api) == 0


def test_the_drop_step_warns_when_the_api_is_down_and_a_retry_drops_the_eggs(api, settings, tmp_path):
    client = cpc_client(at=settings.repo, models=VALUE_MODELS)
    path = _egg_file(tmp_path)
    # Nothing listens on port 9 of this machine, so the request fails at once with no network.
    with httpx.Client(base_url="http://127.0.0.1:9") as down:
        line = run_egg_drop(client, 8, path, down, KEY)
    assert line.startswith("WARNING: the egg drop of week 8 failed")
    assert "make egg-drop CLIENT=cpc WEEK=8" in line
    assert run_egg_drop(client, 8, path, api, KEY).startswith("Dropped 4 eggs of week 8.")


def test_the_drop_step_warns_when_the_api_refuses_the_key(api, settings, tmp_path):
    client = cpc_client(at=settings.repo, models=VALUE_MODELS)
    line = run_egg_drop(client, 8, _egg_file(tmp_path), api, "wrong")
    assert line.startswith("WARNING: the egg drop of week 8 failed")
    assert _board_left(api) == 0


def test_a_client_without_the_eggs_package_skips_the_drop(api, settings, tmp_path):
    client = cpc_client(at=settings.repo, models=VALUE_MODELS)
    without = client.model_copy(update={"values": client.values.model_copy(
        update={"packages": [name for name in client.values.packages if name != "eggs"]})})
    line = run_egg_drop(without, 8, _egg_file(tmp_path), api, KEY)
    assert line == "The client cpc has no eggs package, so no eggs dropped."
    assert _board_left(api) == 0


def test_the_egg_undo_and_the_egg_drop_default_to_the_same_live_api():
    pipeline = Path(__file__).resolve().parents[2] / "pipeline"
    env = {name: value for name, value in os.environ.items() if name != "CORNERSTONE_API_URL"}
    # "make -n" prints the curl line of the undo with the URL that the Makefile picks, and runs nothing else.
    # The "make" call runs the real Makefile, so the default of the Makefile is the one under test.
    dry = subprocess.run(["make", "-n", "egg-undo", "CLIENT=cpc", "EGG=1"], cwd=pipeline, env=env,
                         capture_output=True, text=True, check=True).stdout
    assert f'"{API_URL}/clients/cpc/eggs/undo"' in dry
    assert API_URL == "https://api.4thandgoal.app"


def test_a_repeat_drop_prints_the_eggs_that_already_dropped(api, settings, tmp_path):
    client = cpc_client(at=settings.repo, models=VALUE_MODELS)
    path = _egg_file(tmp_path)
    first = run_egg_drop(client, 8, path, api, KEY)
    again = run_egg_drop(client, 8, path, api, KEY)
    assert again.splitlines()[0] == "Week 8 already holds its eggs, so no eggs dropped."
    assert again.splitlines()[1:] == first.splitlines()[1:]
    assert len(again.splitlines()) == 5
