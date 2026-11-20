"""
Tests for the fair cache of decision 19: the fair state names no asker, a press reads the answers that another press or
the warm-up stored, a moved player gives new keys only for his offers, and the warm-up waits while a press is live.
"""
import shutil
import zlib
from contextlib import ExitStack

import pytest
from cpc import cpc_client
from fakes import FakeJev

from analyzer.fair_cache import FairCache
from analyzer.finder_search import fair_requests, offer_id, search, value_offers, warm_fair
from analyzer.jev_waves import PACER, JevWaves, Pacer
from league.slow_sources import load_slow_sources
from league.snapshot import load_snapshot

CLIENT = cpc_client()
TEAM_A, TEAM_B = 4, 12


@pytest.fixture
def snap(fixture_raw_dir, fixture_history_root, chart_week9, fixture_nflverse_dir, tmp_path):
    # The week 6 chart holds too few values for the Value screen, so the tests read the week 9 trade values.
    cache = tmp_path / "nflverse"
    shutil.copytree(fixture_nflverse_dir, cache)
    slow = load_slow_sources(cache, 2026, 6, fixture_history_root)
    return load_snapshot(fixture_raw_dir, fixture_history_root, chart_week9, slow, client=CLIENT)


def test_the_fair_state_names_no_asker_so_a_press_of_either_team_sends_the_same_state(snap):
    # A real Jev run on 2026-11-20 moved the mean of the two side orders by 0.047 on average when the labels `asker`
    # and `partner` swapped, against 0.018 between two runs of the same request. So the fair state names no asker.
    offers = value_offers(TEAM_A, TEAM_B, snap)[:20]
    # The same offers as a press of team B builds them: the side of team B first.
    flipped = [trade.model_copy(update={"asker": TEAM_B, "sides": list(reversed(trade.sides))}) for trade in offers]
    for order, other in (("asker", "partner"), ("partner", "asker")):
        [from_a] = fair_requests(snap, TEAM_A, TEAM_B, offers, order)
        [from_b] = fair_requests(snap, TEAM_B, TEAM_A, flipped, other)
        assert from_a.state == from_b.state
        assert from_a.questions == from_b.questions
        assert from_a.state["teams"] == [snap.teams[TEAM_A].name, snap.teams[TEAM_B].name]


def test_the_fair_state_holds_only_the_team_names_and_the_players_chart_values_and_sums_of_each_side(snap):
    # The key holds only the chart week and the players of each side, so the state holds no lineup (decision 19).
    offers = value_offers(TEAM_A, TEAM_B, snap)[:20]
    [request] = fair_requests(snap, TEAM_A, TEAM_B, offers, "asker")
    assert set(request.state) == {"teams", "offers"}
    for line in request.state["offers"].values():
        assert set(line) == {"sides"}
        for side in line["sides"]:
            assert set(side) == {"team", "gives", "chart_sum"}
            assert all(set(player) == {"name", "chart_value"} for player in side["gives"])


def test_an_injury_and_a_roster_move_outside_the_offers_leave_the_fair_request_the_same(snap):
    offers = value_offers(TEAM_A, TEAM_B, snap)[:20]
    in_offers = {pid for trade in offers for side in trade.sides for pid in side.player_ids}
    benched = next(pid for pid in snap.rosters[TEAM_A] if pid not in in_offers)
    added = next(pid for rid, roster in snap.rosters.items() if rid not in (TEAM_A, TEAM_B) for pid in roster)
    players = {**snap.players, benched: snap.players[benched].model_copy(update={"injury_status": "Out"})}
    rosters = {rid: list(roster) for rid, roster in snap.rosters.items()}
    rosters[TEAM_B].append(added)
    changed = snap.model_copy(update={"players": players, "rosters": rosters})
    for order in ("asker", "partner"):
        assert fair_requests(changed, TEAM_A, TEAM_B, offers, order) == fair_requests(snap, TEAM_A, TEAM_B, offers,
                                                                                     order)


def _fair_questions(jev) -> int:
    """The count of fair questions that the Jev got: each fair request lists the sides of its offers."""
    return sum(len(r.questions) for r in jev.requests
               if any("sides" in line for line in r.state.get("offers", {}).values()))


def _by_words(key, question, state):
    """A fair answer from the words of the question, so each side order of each offer gets its own answer, and the same
    words get the same answer. Each answer is above NO_AT. Each other question gets a clear yes."""
    if not key.endswith("|fair"):
        return 0.9
    return 0.4 + zlib.crc32(question.instructions.split(": ", 1)[1].encode()) % 50 / 100


def _flipped(oid: str) -> str:
    """The id of the same offer from a press of the other team: the side of that team first."""
    return "-".join(reversed(oid.split("-")))


def test_a_press_of_team_b_reads_the_answers_that_a_press_of_team_a_stored(snap):
    cache = FairCache()
    found_a = search(TEAM_A, TEAM_B, snap, FakeJev(answer=_by_words), fair_cache=cache)
    # A second Jev that says no to each fair question, so an answer asked again would show.
    later = FakeJev(answer=lambda key, question, state: 0.05 if key.endswith("|fair") else 0.9)
    found_b = search(TEAM_B, TEAM_A, snap, later, fair_cache=cache)
    assert found_a.offers and _fair_questions(later) == 0
    assert {_flipped(offer_id(trade)) for trade in found_a.offers} == {offer_id(trade) for trade in found_b.offers}
    assert len(set(found_a.fair_means.values())) > 10
    assert {_flipped(oid): mean for oid, mean in found_a.fair_means.items()} == found_b.fair_means


def test_a_press_drops_the_answers_of_its_client_from_an_old_chart_week_and_keeps_those_of_another_client(snap):
    # A client that the worker never warms, such as norcal, gets each answer from a press, so a press keeps the cache
    # small too.
    cache = FairCache()
    other = ("norcal", snap.season, snap.as_of.chart_week, ("1",), ("2",))
    cache.put(other, 0.5)
    search(TEAM_A, TEAM_B, snap, FakeJev(), fair_cache=cache)
    old_week = len(cache) - 1
    assert old_week > 0
    next_week = snap.model_copy(update={"as_of": snap.as_of.model_copy(update={"chart_week": 10})})
    search(TEAM_A, TEAM_B, next_week, FakeJev(), fair_cache=cache)
    assert len(cache) == old_week + 1
    assert other in cache


def _asked_offers(jev) -> list[list[str]]:
    """The player names of each offer that a fair question of the Jev asked about."""
    return [[player["name"] for side in line["sides"] for player in side["gives"]]
            for r in jev.requests for line in r.state.get("offers", {}).values() if "sides" in line]


def test_the_warm_up_asks_each_fair_question_of_every_team_pair_once(snap):
    cache = FairCache()
    keys, asked = warm_fair(snap, cache, JevWaves(FakeJev()))
    # 12 teams make 66 pairs, and each offer has two side orders.
    pairs = [(a, b) for a in sorted(snap.rosters) for b in sorted(snap.rosters) if a < b]
    assert len(pairs) == 66
    assert keys == 2 * sum(len(value_offers(a, b, snap)) for a, b in pairs) > 1000
    assert asked == keys == len(cache)
    # A second warm-up of the same rosters asks nothing.
    again = FakeJev()
    assert warm_fair(snap, cache, JevWaves(again)) == (keys, 0) and again.requests == []
    # A new chart week gives new keys for each offer, and the answers of the old week leave the cache.
    next_week = snap.model_copy(update={"as_of": snap.as_of.model_copy(update={"chart_week": 10})})
    assert warm_fair(next_week, cache, JevWaves(FakeJev())) == (keys, keys) and len(cache) == keys


def test_a_moved_player_gives_new_keys_only_for_the_offers_that_hold_him(snap):
    cache = FairCache()
    warm_fair(snap, cache, JevWaves(FakeJev()))
    # A wide receiver of team A with a chart value moves to team B. A wide receiver is never a handcuff, so the move
    # changes no other offer.
    moved = next(pid for pid in snap.rosters[TEAM_A]
                 if snap.players[pid].position == "WR" and snap.chart.values.get(pid, 0) >= 5)
    rosters = {rid: list(roster) for rid, roster in snap.rosters.items()}
    rosters[TEAM_A].remove(moved)
    rosters[TEAM_B].append(moved)
    jev = FakeJev()
    _, asked = warm_fair(snap.model_copy(update={"rosters": rosters}), cache, JevWaves(jev))
    name = snap.players[moved].name
    offers = _asked_offers(jev)
    assert asked == len(offers) > 0
    assert all(name in players for players in offers)


def test_the_warm_up_sends_no_request_while_a_press_is_live(snap):
    now = [0.0]
    jev = FakeJev()
    press = ExitStack()
    # The count of requests sent at each sleep of the warm-up, with the time of the clock.
    seen: list[tuple[float, int]] = []

    def sleep(seconds):
        seen.append((now[0], len(jev.requests)))
        now[0] += seconds
        # The press ends after the warm-up waits three times.
        if len(seen) == 3:
            press.close()

    pacer = Pacer(clock=lambda: now[0], sleep=sleep)
    press.enter_context(pacer.press())
    keys, asked = warm_fair(snap, FairCache(), JevWaves(jev, pacer=pacer, background=True))
    assert seen[:3] == [(0.0, 0), (1.0, 0), (2.0, 0)]
    assert asked == keys and len(jev.requests) > 0


def test_a_press_is_live_on_the_pacer_while_it_asks_jev(snap):
    live: list[bool] = []

    def answer(key, question, state):
        live.append(PACER.live)
        return 0.9

    search(TEAM_A, TEAM_B, snap, FakeJev(answer=answer))
    assert live and all(live)
    assert not PACER.live
