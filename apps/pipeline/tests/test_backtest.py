"""
Tests for the backtest of the Finder: the list of Spares tree stops and passes for Brian, and the check of each mark.
They read the week 6 snapshot and give fixed Jev answers through FakeJev, so no test calls TypeSafe.
"""
import json
import re
import shutil

import pytest
from cpc import cpc_client
from fakes import FakeJev

from analyzer.backtest import Mark, check_marks, list_lines, load_marks, run_spares
from analyzer.spares_tree import pair_spares
from league.jev_port import JevError
from league.slow_sources import load_slow_sources
from league.snapshot import load_snapshot

CLIENT = cpc_client()
ASKER, PARTNER = 4, 12


@pytest.fixture
def snap(fixture_raw_dir, fixture_history_root, chart_week6, fixture_nflverse_dir, tmp_path):
    cache = tmp_path / "nflverse"
    shutil.copytree(fixture_nflverse_dir, cache)
    slow = load_slow_sources(cache, 2026, 6, fixture_history_root)
    return load_snapshot(fixture_raw_dir, fixture_history_root, chart_week6, slow, client=CLIENT)


def _first_listed_side(snap):
    """The first giver and receiver whose side lists a player."""
    return next((giver, receiver) for giver in sorted(snap.rosters) for receiver in sorted(snap.rosters)
                if giver != receiver and pair_spares(snap, giver, receiver)["asker"])


def test_the_spares_run_reads_both_sides_of_every_pair_with_one_request_per_pair(snap):
    jev = FakeJev()
    outcomes = run_spares(snap, jev)
    teams = len(snap.rosters)
    assert len(outcomes) == teams * (teams - 1)
    assert len(jev.requests) <= teams * (teams - 1) // 2
    # Each answer is a clear yes, so a side stops only when it lists no player.
    assert all(outcome.stopped == (not outcome.spares) for outcome in outcomes)


def test_the_list_numbers_each_line_and_puts_every_jev_stop_first_with_its_answers(snap):
    giver, receiver = _first_listed_side(snap)
    no_side = {spare.key for spare in pair_spares(snap, giver, receiver)["asker"]}
    outcomes = run_spares(snap, FakeJev(answer=lambda key, q, state: 0.1 if key in no_side else 0.8))
    lines = list_lines(snap, outcomes, limit=12)
    numbered = [line for line in lines if re.match(r"\d+\. ", line)]
    assert [int(line.partition(".")[0]) for line in numbered] == list(range(1, len(numbered) + 1))
    assert len(numbered) == 12
    first = numbered[0]
    assert first.startswith(f"1. Stop: {snap.teams[giver].name} gives {snap.teams[receiver].name} no one.")
    assert "0.10" in first
    # Each pass names the answer that decided it, a yes or an unsure answer.
    assert all("0.80" in line for line in numbered[1:] if " Pass: " in line)
    # A side that lists no player stops by the count rule, with no Jev answer, so one plain line counts them.
    count = sum(not outcome.spares for outcome in outcomes)
    assert any(line.startswith(f"{count} sides list no player") for line in lines if not re.match(r"\d+\. ", line))


def _trade_mark(snap, expect="drop"):
    give = next(pid for pid in snap.rosters[ASKER] if snap.players[pid].position == "WR")
    get = next(pid for pid in snap.rosters[PARTNER] if snap.players[pid].position == "QB")
    return Mark(id=1, kind="trade", asker=snap.teams[ASKER].name, partner=snap.teams[PARTNER].name,
                asker_gives=[snap.players[give].name], asker_gets=[snap.players[get].name], expect=expect)


def test_a_trade_mark_is_right_when_a_clear_no_on_a_gain_drops_it(snap):
    mark = _trade_mark(snap)
    [result] = check_marks([mark], snap, FakeJev(answer=lambda key, q, state: 0.1 if key == f"0|gain.{ASKER}" else 0.9))
    assert result.got == "drop" and result.right
    assert "0.10" in result.why
    [result] = check_marks([mark], snap, FakeJev())
    assert result.got == "keep" and not result.right


def test_a_spares_mark_is_right_when_the_side_does_what_brian_marked(snap):
    giver, receiver = _first_listed_side(snap)
    mark = Mark(id=2, kind="spares", giver=snap.teams[giver].name, receiver=snap.teams[receiver].name, expect="stop")
    [result] = check_marks([mark], snap, FakeJev(yes=0.1))
    assert result.got == "stop" and result.right
    [result] = check_marks([mark], snap, FakeJev(yes=0.5))
    assert result.got == "pass" and not result.right


def test_a_failed_jev_call_is_an_error_and_never_a_right_mark(snap):
    results = check_marks([_trade_mark(snap, expect="keep")], snap, FakeJev(error=JevError("timeout")))
    assert [(result.got, result.right) for result in results] == [("error", False)]


def test_the_marks_file_loads_each_mark(tmp_path):
    path = tmp_path / "marks.json"
    path.write_text(json.dumps([
        {"id": 1, "kind": "trade", "asker": "A", "partner": "B", "asker_gives": ["X"], "asker_gets": ["Y"],
         "expect": "drop", "note": "the lineup of A gets worse"},
        {"id": 2, "kind": "spares", "giver": "A", "receiver": "B", "expect": "pass"}]))
    marks = load_marks(path)
    assert [(mark.id, mark.kind, mark.expect) for mark in marks] == [(1, "trade", "drop"), (2, "spares", "pass")]
