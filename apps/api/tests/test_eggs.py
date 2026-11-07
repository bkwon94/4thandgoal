"""
Tests for the eggs routes of the API at the route seam, through the FastAPI test client with a temp SQLite file.
The rosters come from the recorded week 6 Sleeper data, so no test needs the network.
"""
import dataclasses
import json
import os
import shutil
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest
from cpc import cpc_client
from fastapi.testclient import TestClient

from analyzer.ratelimit import RateLimiter
from cornerstone_api.app import create_app
from cornerstone_api.settings import Settings
from cornerstone_api.sources import Sources
from cornerstone_api.value_models import VALUE_MODELS
from eggs.values import EggsValues
from league.provider.sleeper import load_raw

ET = ZoneInfo("America/New_York")
NOW = datetime(2026, 10, 19, 12, 0, tzinfo=ET)
PASSPHRASE = "cornerstone-test"
KEY = "commissioner-test"
PASS = {"X-League-Passphrase": PASSPHRASE}
COMMISSIONER = {"X-Commissioner-Key": KEY}
BASE = "/clients/cpc/eggs"
# The test egg T1 of the acceptance tests: a 3-tap on the Luck cell of Lil Fridge, in the light theme.
T1 = {"page": "/midseason/2026/", "target": "luck-3", "action": "tap3", "conditions": {"theme": "light"},
      "letter": "C"}
CHECK = {"page": "/midseason/2026/", "target": "luck-3", "action": "tap3", "conditions": {"theme": "light"}}
LIL_FRIDGE = 3
BO_GIRDS = 6


def _no_network(*args, **kwargs):
    raise AssertionError("network call")


@pytest.fixture
def repo(tmp_path, fixture_history_root, fixture_nflverse_dir):
    """A repo with the week 6 history and a fresh nflverse cache, as the teams route of the analyzer reads them."""
    shutil.copytree(fixture_history_root, tmp_path / "data" / "2026" / "history")
    shutil.copytree(fixture_nflverse_dir, tmp_path / "data" / "cache" / "nflverse")
    for cached in (tmp_path / "data" / "cache" / "nflverse").iterdir():
        os.utime(cached)
    return tmp_path


@pytest.fixture
def settings(repo):
    return Settings(passphrases={"cpc": PASSPHRASE}, repo=repo, result_cache_dir=repo / "results",
                    commissioner_keys={"cpc": KEY}, eggs_dir=repo / "eggs",
                    rate_limit_per_minute=600)


@pytest.fixture
def api(settings, fixture_raw_dir):
    client = cpc_client(at=settings.repo, models=VALUE_MODELS)
    sources = Sources(client, fetch_sleeper=lambda league_id: (load_raw(fixture_raw_dir), NOW),
                      fetch_nflverse=_no_network, fetch_history_week=_no_network, read_chart=_no_network,
                      clock=lambda: NOW)
    return TestClient(create_app(settings, [client], sources={"cpc": sources}))


def _drop(api, *eggs, week=9):
    """Put test eggs with a fixed letter in the store, so a check and a claim test know the letter of each egg.

    The drop route gives each egg its letter by the letter rule. tests/test_egg_drop.py tests the route.
    """
    dropped = api.app.state.hunts["cpc"].store.drop(week, list(eggs), NOW)
    return {"eggs": [{"id": egg.id, "letter": egg.letter} for egg in dropped]}


def test_the_check_of_a_dropped_egg_gives_its_letter_and_a_claim_token(api):
    _drop(api, T1)
    body = api.post(f"{BASE}/check", json=CHECK).json()
    assert body["match"] is True
    assert body["letter"] == "C"
    assert body["token"]


def test_a_check_in_the_wrong_theme_is_no_match_with_no_letter_and_no_token(api):
    _drop(api, T1)
    body = api.post(f"{BASE}/check", json={**CHECK, "conditions": {"theme": "dark"}}).json()
    assert body == {"match": False}


def test_a_check_of_another_target_or_action_is_no_match(api):
    _drop(api, T1)
    assert api.post(f"{BASE}/check", json={**CHECK, "target": "luck-12"}).json() == {"match": False}
    assert api.post(f"{BASE}/check", json={**CHECK, "action": "tap2"}).json() == {"match": False}


def _claim(api, token, roster_id=LIL_FRIDGE, word="CORNERSTONE", headers=PASS):
    return api.post(f"{BASE}/claim", json={"token": token, "roster_id": roster_id, "word": word}, headers=headers)


def _token(api):
    return api.post(f"{BASE}/check", json=CHECK).json()["token"]


def test_a_claim_puts_the_letter_of_the_manager_into_the_egg_word_on_the_board(api):
    _drop(api, T1)
    response = _claim(api, _token(api))
    assert response.status_code == 200
    assert response.json()["letters"] == {"CORNERSTONE": ["C"], "LANSDALE": [], "EAGLES": []}
    board = api.get(f"{BASE}/board").json()
    cornerstone = next(word for word in board["words"] if word["word"] == "CORNERSTONE")
    lil_fridge = next(manager for manager in cornerstone["managers"] if manager["roster_id"] == LIL_FRIDGE)
    assert lil_fridge["team"] == "Lil Fridge"
    assert lil_fridge["letters"] == ["C"]
    assert board["counts"] == {"left": 0, "found": 1, "to_drop": 53}
    assert board["latest"][0] | {"claimed_at": None} == {
        "roster_id": LIL_FRIDGE, "team": "Lil Fridge", "letter": "C", "word": "CORNERSTONE", "claimed_at": None}


def test_the_claim_needs_the_passphrase(api):
    _drop(api, T1)
    token = _token(api)
    assert _claim(api, token, headers={}).status_code == 401
    assert _claim(api, token, headers={"X-League-Passphrase": "wrong"}).status_code == 401
    # The token stays good, because the guard stops the claim before the route takes it.
    assert _claim(api, token).status_code == 200


def test_a_token_is_good_for_one_claim(api):
    _drop(api, T1)
    token = _token(api)
    assert _claim(api, token).status_code == 200
    assert _claim(api, token, roster_id=12).status_code == 410


def test_a_check_of_a_claimed_egg_says_another_manager_claimed_first(api):
    _drop(api, T1)
    _claim(api, _token(api))
    body = api.post(f"{BASE}/check", json=CHECK).json()
    assert body == {"match": True, "claimed": True, "letter": "C"}


def test_a_second_claim_of_one_egg_answers_that_another_manager_claimed_first(api):
    _drop(api, T1)
    first, second = _token(api), _token(api)
    assert _claim(api, first).status_code == 200
    response = _claim(api, second, roster_id=12)
    assert response.status_code == 409
    assert response.json()["detail"] == "Another manager claimed first."


def test_the_drop_needs_the_commissioner_key_and_not_the_passphrase(api):
    for headers in ({}, PASS, {"X-Commissioner-Key": "wrong"}):
        response = api.post(f"{BASE}/drop", json={"week": 9, "eggs": [CHECK]}, headers=headers)
        assert response.status_code == 401
    assert api.get(f"{BASE}/board").json()["counts"] == {"left": 0, "found": 0, "to_drop": 54}


def test_the_undo_needs_the_commissioner_key_and_sets_the_egg_live_again(api, settings):
    egg_id = _drop(api, T1)["eggs"][0]["id"]
    _claim(api, _token(api))
    assert api.post(f"{BASE}/undo", json={"egg_id": egg_id}, headers=PASS).status_code == 401
    assert api.post(f"{BASE}/undo", json={"egg_id": egg_id}, headers=COMMISSIONER).status_code == 200
    assert api.get(f"{BASE}/board").json()["counts"]["left"] == 1
    assert _claim(api, _token(api), roster_id=12).status_code == 200


def test_the_check_and_the_board_need_no_key(api):
    assert api.get(f"{BASE}/board").status_code == 200
    assert api.post(f"{BASE}/check", json=CHECK).status_code == 200


def test_the_board_names_no_page_no_target_no_action_and_no_condition(api):
    _drop(api, T1, {**T1, "target": "luck-12", "letter": "A"})
    _claim(api, _token(api))
    text = api.get(f"{BASE}/board").text
    for word in ("/midseason/2026/", "luck-3", "luck-12", "tap3", "theme", "light", "page", "target", "action"):
        assert word not in text


def test_the_board_lists_the_eleven_managers_who_hunt_and_never_the_commissioner(api):
    board = api.get(f"{BASE}/board").json()
    assert len(board["managers"]) == 11
    assert BO_GIRDS not in [manager["roster_id"] for manager in board["managers"]]
    assert all(len(word["managers"]) == 11 for word in board["words"])
    assert [(word["word"], word["prize"]) for word in board["words"]] == [
        ("CORNERSTONE", 50), ("LANSDALE", 30), ("EAGLES", 20)]


def test_the_board_shows_each_slot_of_the_hunt_by_week(api):
    _drop(api, T1, {**T1, "target": "luck-12", "letter": "A"})
    _claim(api, _token(api))
    weeks = api.get(f"{BASE}/board").json()["weeks"]
    assert [week["week"] for week in weeks] == list(range(9, 18))
    assert weeks[0]["slots"] == ["found", "out", "future", "future", "future", "future"]
    assert all(week["slots"] == ["future"] * 6 for week in weeks[1:])


def test_the_board_names_the_week_the_time_and_the_count_of_the_last_drop(api):
    assert api.get(f"{BASE}/board").json()["last_drop"] is None
    _drop(api, T1, {**T1, "target": "luck-12", "letter": "A"})
    tuesday = datetime(2026, 10, 27, 9, 30, tzinfo=ET)
    api.app.state.hunts["cpc"].clock = lambda: tuesday
    _drop(api, *[_letter_egg(letter, f"luck-{index}") for index, letter in enumerate("ACDEGL")], week=10)
    assert api.get(f"{BASE}/board").json()["last_drop"] == {
        "week": 10, "count": 6, "dropped_at": tuesday.isoformat()}


def test_the_store_is_one_sqlite_file_of_the_client_with_the_eggs_and_the_claims_tables(api, settings):
    _drop(api, T1)
    with sqlite3.connect(settings.eggs_dir / "cpc.sqlite") as db:
        tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
        claims = [row[1] for row in db.execute("PRAGMA table_info(claims)")]
        eggs = [row[1] for row in db.execute("PRAGMA table_info(eggs)")]
    assert tables == {"eggs", "claims"}
    assert eggs == ["id", "week", "page", "target", "action", "conditions", "letter", "dropped_at"]
    assert claims == ["egg_id", "roster_id", "word", "claimed_at", "browser", "undone_at"]


def test_the_claims_table_keeps_an_undone_claim_with_its_undo_time(api, settings):
    egg_id = _drop(api, T1)["eggs"][0]["id"]
    _claim(api, _token(api))
    api.post(f"{BASE}/undo", json={"egg_id": egg_id}, headers=COMMISSIONER)
    _claim(api, _token(api), roster_id=12)
    with sqlite3.connect(settings.eggs_dir / "cpc.sqlite") as db:
        rows = db.execute("SELECT roster_id, undone_at IS NOT NULL FROM claims ORDER BY rowid").fetchall()
    assert rows == [(LIL_FRIDGE, 1), (12, 0)]


def test_a_client_without_the_eggs_package_has_no_eggs_routes(settings, fixture_raw_dir):
    client = cpc_client(at=settings.repo, models=VALUE_MODELS)
    without = client.model_copy(update={"values": client.values.model_copy(
        update={"packages": [name for name in client.values.packages if name != "eggs"]})})
    api = TestClient(create_app(settings, [without]))
    assert api.get(f"{BASE}/board").status_code == 404
    assert api.post(f"{BASE}/check", json=CHECK).status_code == 404


def test_the_app_refuses_a_client_of_the_eggs_package_with_no_commissioner_key(settings):
    client = cpc_client(at=settings.repo, models=VALUE_MODELS)
    with pytest.raises(ValueError, match="CORNERSTONE_COMMISSIONER_KEY_CPC"):
        create_app(dataclasses.replace(settings, commissioner_keys={}), [client])


def test_the_start_needs_the_commissioner_key_of_each_client_of_the_eggs_package(monkeypatch, tmp_path):
    monkeypatch.setenv("CORNERSTONE_PASSPHRASE_CPC", PASSPHRASE)
    monkeypatch.delenv("CORNERSTONE_COMMISSIONER_KEY_CPC", raising=False)
    with pytest.raises(RuntimeError, match="CORNERSTONE_COMMISSIONER_KEY_CPC"):
        Settings.from_env(["cpc"], ["cpc"])
    monkeypatch.setenv("CORNERSTONE_COMMISSIONER_KEY_CPC", KEY)
    monkeypatch.setenv("CORNERSTONE_EGGS_DIR", str(tmp_path / "eggs"))
    settings = Settings.from_env(["cpc"], ["cpc"])
    assert settings.commissioner_keys == {"cpc": KEY}
    assert settings.eggs_dir == tmp_path / "eggs"
    assert KEY not in repr(settings)


def test_the_cpc_client_takes_the_eggs_package_and_the_roster_of_the_commissioner():
    client = cpc_client(models=VALUE_MODELS)
    assert "eggs" in client.values.packages
    assert client.values.package(EggsValues).commissioner == BO_GIRDS


# The board fixture of the site tests. The board is the seam between the API and the site, so the API test holds the
# fixture to the real answer, and the site tests render from it.
BOARD_FIXTURE = Path(__file__).resolve().parents[3] / "packages" / "eggs" / "site" / "lib" / "fixtures" / "board.json"


def test_the_board_answer_keeps_the_shape_of_the_site_fixture(api):
    api.app.state.hunts["cpc"].clock = lambda: NOW
    _drop(api, T1, {**T1, "target": "luck-12", "letter": "A"})
    _claim(api, _token(api))
    assert api.get(f"{BASE}/board").json() == json.loads(BOARD_FIXTURE.read_text(encoding="utf-8"))


def _letter_egg(letter, target):
    """A test egg with its own target, so each letter has its own egg."""
    return {**T1, "target": target, "letter": letter}


def _claim_egg(api, egg, roster_id=LIL_FRIDGE, word="CORNERSTONE"):
    """Check the egg at its spot and claim it, as a manager does."""
    token = api.post(f"{BASE}/check", json={**CHECK, "target": egg["target"]}).json()["token"]
    return _claim(api, token, roster_id=roster_id, word=word)


def test_two_claims_of_one_egg_at_once_give_one_winner(api):
    _drop(api, T1)
    tokens = [_token(api), _token(api)]
    with ThreadPoolExecutor(2) as pool:
        statuses = sorted(pool.map(lambda args: _claim(api, *args).status_code,
                                   [(tokens[0], LIL_FRIDGE), (tokens[1], 12)]))
    assert statuses == [200, 409]
    assert api.get(f"{BASE}/board").json()["counts"]["found"] == 1


def test_the_check_issues_its_token_under_the_lock_that_the_claim_holds(api, monkeypatch):
    # The issue rebuilds the map of live tokens that a claim pops, so a check and a claim must never run it at once.
    _drop(api, T1)
    hunt = api.app.state.hunts["cpc"]
    issue = hunt.tokens.issue
    held = []

    def watched(egg_id, now):
        held.append(hunt.lock.locked())
        return issue(egg_id, now)

    monkeypatch.setattr(hunt.tokens, "issue", watched)
    assert _claim(api, _token(api)).status_code == 200
    assert held == [True]


def test_the_claim_of_the_commissioner_is_refused_and_the_egg_stays_live(api):
    _drop(api, T1)
    token = _token(api)
    response = _claim(api, token, roster_id=BO_GIRDS)
    assert response.status_code == 422
    assert api.get(f"{BASE}/board").json()["counts"]["left"] == 1
    # The refusal keeps the token good.
    assert _claim(api, token).status_code == 200


def test_a_letter_into_an_egg_word_with_no_open_slot_for_it_is_refused(api):
    _drop(api, T1, _letter_egg("C", "luck-12"))
    assert _claim_egg(api, T1).status_code == 200
    response = _claim_egg(api, _letter_egg("C", "luck-12"))
    assert response.status_code == 422
    assert api.get(f"{BASE}/board").json()["counts"]["found"] == 1


def test_a_letter_that_is_not_in_the_egg_word_is_refused(api):
    _drop(api, {**T1, "letter": "Z"})
    assert _claim(api, _token(api)).status_code == 422


def test_a_letter_that_twice_in_the_egg_word_fills_two_slots_and_no_more(api):
    _drop(api, *[_letter_egg("R", f"luck-{n}") for n in (1, 2, 4)])
    assert _claim_egg(api, _letter_egg("R", "luck-1")).status_code == 200
    assert _claim_egg(api, _letter_egg("R", "luck-2")).status_code == 200
    assert _claim_egg(api, _letter_egg("R", "luck-4")).status_code == 422


def test_a_block_is_refused_when_the_letter_fits_an_egg_word_of_the_manager(api):
    _drop(api, T1)
    response = _claim(api, _token(api), word=None)
    assert response.status_code == 422
    assert api.get(f"{BASE}/board").json()["counts"]["found"] == 0


def test_a_block_counts_as_found_and_shows_nowhere_else(api):
    # Lil Fridge holds the one C of CORNERSTONE, and C is in neither LANSDALE nor EAGLES.
    _drop(api, T1, _letter_egg("C", "luck-12"))
    assert _claim_egg(api, T1).status_code == 200
    before = api.get(f"{BASE}/board").json()
    response = _claim_egg(api, _letter_egg("C", "luck-12"), word=None)
    assert response.status_code == 200
    after = api.get(f"{BASE}/board").json()
    assert after["counts"]["found"] == before["counts"]["found"] + 1
    assert after["words"] == before["words"]
    assert after["latest"] == before["latest"]


def _fill_eagles(api, roster_id, letters="EAGLS"):
    eggs = [_letter_egg(letter, f"luck-{n}") for n, letter in enumerate(letters, start=1)]
    _drop(api, *eggs)
    for egg in eggs:
        assert _claim_egg(api, egg, roster_id=roster_id, word="EAGLES").status_code == 200


def test_the_claim_that_fills_an_egg_word_names_the_winner_and_closes_the_word(api):
    # EAGLES holds two E, so Lil Fridge holds E, A, G, L, S, and the last E fills it.
    _fill_eagles(api, LIL_FRIDGE)
    spare = _letter_egg("E", "luck-12")
    _drop(api, spare, week=10)
    response = _claim_egg(api, spare, word="EAGLES")
    assert response.status_code == 200
    assert response.json()["winner"] == {"roster_id": LIL_FRIDGE, "word": "EAGLES"}
    words = {word["word"]: word for word in api.get(f"{BASE}/board").json()["words"]}
    assert words["EAGLES"]["winner"] == {"roster_id": LIL_FRIDGE, "team": "Lil Fridge"}
    assert words["CORNERSTONE"]["winner"] is None
    # Another manager now gets no letter into EAGLES.
    other = _letter_egg("A", "luck-13")
    _drop(api, other, week=11)
    assert _claim_egg(api, other, roster_id=12, word="EAGLES").status_code == 422


def test_the_undo_keeps_the_row_and_the_egg_goes_live_again(api, settings):
    egg_id = _drop(api, T1)["eggs"][0]["id"]
    _claim(api, _token(api))
    api.post(f"{BASE}/undo", json={"egg_id": egg_id}, headers=COMMISSIONER)
    with sqlite3.connect(next(settings.eggs_dir.iterdir())) as db:
        rows = db.execute("SELECT egg_id, undone_at FROM claims").fetchall()
    assert [row[0] for row in rows] == [egg_id]
    assert rows[0][1] is not None


# The test egg T2 of the acceptance tests: the clock window 11 PM to midnight in the timezone of the client.
T2 = {**T1, "target": "award-top-score", "action": "hold1", "conditions": {"clock": "23:00-00:00"}, "letter": "A"}
T2_CHECK = {"page": "/midseason/2026/", "target": "award-top-score", "action": "hold1", "conditions": {}}


def test_a_clock_window_egg_matches_only_inside_the_window_in_the_timezone_of_the_client(api):
    _drop(api, T2)
    hunt = api.app.state.hunts["cpc"]
    hunt.clock = lambda: datetime(2026, 11, 10, 22, 59, tzinfo=ET)
    assert api.post(f"{BASE}/check", json=T2_CHECK).json() == {"match": False}
    hunt.clock = lambda: datetime(2026, 11, 10, 23, 30, tzinfo=ET)
    assert api.post(f"{BASE}/check", json=T2_CHECK).json()["letter"] == "A"
    # 23:30 in Los Angeles is 2:30 in New York, so the window of the client holds on the clock of the client.
    hunt.clock = lambda: datetime(2026, 11, 10, 23, 30, tzinfo=ZoneInfo("America/Los_Angeles"))
    assert api.post(f"{BASE}/check", json=T2_CHECK).json() == {"match": False}
    hunt.clock = lambda: datetime(2026, 11, 11, 0, 0, tzinfo=ET)
    assert api.post(f"{BASE}/check", json=T2_CHECK).json() == {"match": False}


def test_a_weekday_egg_matches_only_on_that_day_of_the_client(api):
    _drop(api, {**T2, "conditions": {"weekday": "thu"}})
    hunt = api.app.state.hunts["cpc"]
    hunt.clock = lambda: datetime(2026, 11, 12, 1, 0, tzinfo=ET)
    assert api.post(f"{BASE}/check", json=T2_CHECK).json()["match"] is True
    hunt.clock = lambda: datetime(2026, 11, 13, 1, 0, tzinfo=ET)
    assert api.post(f"{BASE}/check", json=T2_CHECK).json() == {"match": False}


TEEHEE = 12
# The test egg T3 of the acceptance tests: a long press of the sim champion trophy when the champion is Teehee.
T3 = {"page": "/midseason/2026/", "target": "sim-trophy", "action": "hold1", "conditions": {"sim_champion": TEEHEE},
      "letter": "D"}


def test_a_sim_egg_matches_only_when_the_replay_shows_its_champion(api):
    _drop(api, T3)
    check = {"page": "/midseason/2026/", "target": "sim-trophy", "action": "hold1"}
    assert api.post(f"{BASE}/check", json={**check, "conditions": {"sim_champion": LIL_FRIDGE}}).json() == {
        "match": False}
    assert api.post(f"{BASE}/check", json={**check, "conditions": {"sim_champion": TEEHEE}}).json()["letter"] == "D"


def _check(api, **body):
    return api.post(f"{BASE}/check", json={"page": "/midseason/2026/", "conditions": {}, **body}).json()


def test_an_open_state_egg_matches_when_the_listener_sends_that_state_among_the_open_states(api):
    _drop(api, {**T1, "target": "bench-3-9", "action": "tap2", "conditions": {"open": "show-all-bench"}})
    check = {"target": "bench-3-9", "action": "tap2"}
    assert _check(api, **check, conditions={"open": []}) == {"match": False}
    assert _check(api, **check, conditions={"open": ["show-all-draft"]}) == {"match": False}
    assert _check(api, **check, conditions={"open": ["show-all-draft", "show-all-bench"]})["match"] is True


def test_a_tap_combo_egg_matches_only_the_double_tap_with_its_trail(api):
    _drop(api, {**T1, "target": "award-top-score", "action": "tap2", "conditions": {"trail": ["heading-a", "heading-b"]}})
    check = {"target": "award-top-score", "action": "tap2"}
    assert _check(api, **check) == {"match": False}
    assert _check(api, **check, trail=["heading-b", "heading-a"]) == {"match": False}
    assert _check(api, **check, trail=["heading-a", "heading-b"])["match"] is True


def test_a_selected_word_egg_matches_only_its_word_in_its_blurb(api):
    _drop(api, {**T1, "target": "blurb-luck", "action": "select", "conditions": {"word": "lucky"}})
    assert _check(api, target="blurb-luck", action="select", word="unlucky") == {"match": False}
    assert _check(api, target="blurb-other", action="select", word="lucky") == {"match": False}
    assert _check(api, target="blurb-luck", action="select", word="lucky")["match"] is True


def test_the_trade_key_the_scroll_and_the_404_page_each_hold_as_a_condition(api):
    trade = "3:4046,4881|12:6794"
    _drop(api,
          {**T1, "page": "/analyzer/", "target": "verdict-word", "action": "hold3", "conditions": {"trade": trade}},
          {**T1, "target": "page-end", "action": "tap4", "conditions": {"scrolled_end": True}},
          {**T1, "page": "/old-week/", "target": "not-found-hero", "action": "tap5", "conditions": {"not_found": True}})
    assert _check(api, page="/analyzer/", target="verdict-word", action="hold3",
                  conditions={"trade": "3:4046|12:6794"}) == {"match": False}
    assert _check(api, page="/analyzer/", target="verdict-word", action="hold3",
                  conditions={"trade": trade})["match"] is True
    assert _check(api, target="page-end", action="tap4") == {"match": False}
    assert _check(api, target="page-end", action="tap4", conditions={"scrolled_end": True})["match"] is True
    assert _check(api, page="/old-week/", target="not-found-hero", action="tap5") == {"match": False}
    assert _check(api, page="/old-week/", target="not-found-hero", action="tap5",
                  conditions={"not_found": True})["match"] is True


def test_the_check_has_its_own_limit_of_60_an_hour_and_the_other_routes_keep_theirs(api):
    _drop(api, T1)
    statuses = [api.post(f"{BASE}/check", json=CHECK).status_code for _ in range(61)]
    assert statuses[:60] == [200] * 60
    assert statuses[60] == 429
    blocked = api.post(f"{BASE}/check", json=CHECK)
    # The window is one hour, so the retry-after is close to one hour, and the site names it in minutes.
    assert 3500 < int(blocked.headers["Retry-After"]) <= 3600
    # The 60 checks spend nothing of the limit of 10 a minute of the other routes.
    assert api.get("/clients/cpc/teams", params={"season": 2026}, headers=PASS).status_code == 200
    assert api.get(f"{BASE}/board").status_code == 200


def test_the_check_limit_counts_each_address_apart(api):
    for _ in range(60):
        api.post(f"{BASE}/check", json=CHECK, headers={"Fly-Client-IP": "10.0.0.1"})
    assert api.post(f"{BASE}/check", json=CHECK, headers={"Fly-Client-IP": "10.0.0.1"}).status_code == 429
    assert api.post(f"{BASE}/check", json=CHECK, headers={"Fly-Client-IP": "10.0.0.2"}).status_code == 200


def test_the_board_has_its_own_limit_of_60_a_minute_and_spends_none_of_the_shared_limit(api):
    # The shared limit of the analyzer and the claim is 10 a minute in the real app.
    api.app.state.limiter = RateLimiter(10)
    statuses = [api.get(f"{BASE}/board").status_code for _ in range(61)]
    assert statuses[:60] == [200] * 60
    assert statuses[60] == 429
    assert 0 < int(api.get(f"{BASE}/board").headers["Retry-After"]) <= 60
    # The 60 board reads spend nothing of the limit of 10 a minute of the other routes.
    assert api.get("/clients/cpc/teams", params={"season": 2026}, headers=PASS).status_code == 200


def test_a_claim_of_an_egg_that_is_gone_says_to_find_the_egg_again(api, settings):
    _drop(api, T1)
    token = _token(api)
    with sqlite3.connect(settings.eggs_dir / "cpc.sqlite") as db:
        db.execute("DELETE FROM eggs")
    response = _claim(api, token)
    assert response.status_code == 410
    assert "Find the egg again" in response.json()["detail"]
