"""
Tests for the Finder search: the partner filter, the targets, the offers, and the shortlist that Jev narrows.
They read the week 6 snapshot and use FakeJev, so no test calls TypeSafe.
"""
import shutil

import pytest
from cpc import cpc_client
from fakes import FakeJev

from analyzer.adjusters import is_handcuff, trade_handcuffs
from analyzer.finder import _out_with_no_return
from analyzer.finder_search import SHORTLIST_KEEP, TARGET_MAX, offer_id, search
from analyzer.jev_waves import REQUESTS_PER_SECOND, JevWaves, WaveRequest, plan_waves
from league.jev_port import JevError, NoulQuestion
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


def _filter_requests(jev):
    return [r for r in jev.requests if set(r.questions) == {"partner_has", "partner_spares", "asker_has", "asker_spares"}]


def test_with_no_partner_the_partner_filter_asks_four_questions_of_every_other_team(snap):
    jev = FakeJev()
    found = search(ASKER, None, snap, jev)
    others = sorted(rid for rid in snap.rosters if rid != ASKER)
    assert len(others) == 11
    asked = sorted(r.state["teams"]["partner"]["roster_id"] for r in _filter_requests(jev))
    assert asked == others
    assert sorted(read.roster_id for read in found.partners) == others
    assert all(read.passed for read in found.partners)


def _target_requests(jev):
    return [r for r in jev.requests if r.questions and all("." in key and "|" not in key for key in r.questions)]


def test_a_picked_partner_keeps_the_filter_and_every_offer_to_that_partner(snap):
    jev = FakeJev()
    found = search(ASKER, PARTNER, snap, jev)
    assert [r.state["teams"]["partner"]["roster_id"] for r in _filter_requests(jev)] == [PARTNER]
    assert found.offers and found.shortlist
    for trade in found.offers + [offer.trade for offer in found.shortlist]:
        assert [side.roster_id for side in trade.sides] == [ASKER, PARTNER]


def test_only_a_partner_with_four_yes_answers_gets_the_full_search(snap):
    stopped = 7

    def answer(key, question, state):
        # One no of the four stops the partner. "Unsure" is not a yes either.
        if key == "asker_spares" and state["teams"]["partner"]["roster_id"] == stopped:
            return 0.5
        return 0.9

    jev = FakeJev(answer=answer)
    found = search(ASKER, None, snap, jev)
    read = next(read for read in found.partners if read.roster_id == stopped)
    assert not read.passed and read.answers["asker_spares"] == 0.5
    assert stopped not in found.targets
    assert all(trade.sides[1].roster_id != stopped for trade in found.offers)
    assert stopped not in [r.state["teams"]["partner"]["roster_id"] for r in _target_requests(jev)]


def test_the_targets_need_p_06_and_keep_at_most_four_per_side_the_highest_first(snap):
    rated = {}

    def answer(key, question, state):
        if "." in key and "|" not in key:
            # A spread of answers by player id, from 0.3 to 0.9, so some players fall under 0.6.
            p = 0.3 + (int(key.partition(".")[2]) % 7) / 10
            rated[key] = p
            return p
        return 0.9

    found = search(ASKER, PARTNER, snap, FakeJev(answer=answer))
    for owner, side in ((ASKER, "asker"), (PARTNER, "partner")):
        picked = found.targets[PARTNER][side]
        assert 0 < len(picked) <= TARGET_MAX
        ps = {key.partition(".")[2]: p for key, p in rated.items() if key.startswith(f"{owner}.")}
        assert all(ps[pid] >= 0.6 for pid in picked)
        # No player left out rates above a picked one.
        assert all(ps[pid] <= min(ps[p] for p in picked) for pid in ps if pid not in picked)
    targets = set(found.targets[PARTNER]["asker"]) | set(found.targets[PARTNER]["partner"])
    assert all(set(trade.player_ids) <= targets for trade in found.offers)


def test_no_offer_breaks_a_hard_rule_and_every_offer_is_small(snap):
    found = search(ASKER, None, snap, FakeJev())
    assert len(found.offers) > 0
    for trade in found.offers:
        for side in trade.sides:
            for pid in side.player_ids:
                player = snap.players[pid]
                assert player.position not in ("K", "DEF")
                assert not _out_with_no_return(snap, pid)
                assert not is_handcuff(snap, pid, side.roster_id)
        assert trade_handcuffs(trade, snap) == []
        counts = sorted(len(side.player_ids) for side in trade.sides)
        # 1-for-1, 2-for-1, or 1-for-2, and never 2-for-2 or larger.
        assert counts in ([1, 1], [1, 2])
    # The fixture rosters hold kickers and defenses, so the rule has something to keep out.
    assert any(snap.players[pid].position in ("K", "DEF") for roster in snap.rosters.values() for pid in roster)


def test_the_shortlist_keeps_the_ten_offers_with_the_highest_product_of_fair_and_need(snap):
    def answer(key, question, state):
        number, _, kind = key.partition("|")
        if not kind:
            return 0.9
        n = int(number)
        if kind == "fair":
            return 0.99 - 0.001 * n
        # The first offer is fair but fills no need of the asker, so the product drops it.
        return 0.1 if n == 0 and kind == f"need.{ASKER}" else 0.9

    found = search(ASKER, PARTNER, snap, FakeJev(answer=answer))
    assert len(found.offers) > SHORTLIST_KEEP
    assert [offer.offer_id for offer in found.shortlist] == [offer_id(t) for t in found.offers[1:SHORTLIST_KEEP + 1]]
    top = found.shortlist[0]
    assert top.score == pytest.approx(top.fair * top.needs[ASKER] * top.needs[PARTNER])
    assert set(top.needs) == {ASKER, PARTNER}


def test_a_failed_jev_request_drops_the_partner_and_never_raises(snap):
    found = search(ASKER, None, snap, FakeJev(error=JevError("429 Too Many Requests")))
    assert all(read.failed and not read.passed for read in found.partners)
    assert found.offers == [] and found.shortlist == []


def _tiny(n):
    return {str(i): WaveRequest({"n": i}, {"q": NoulQuestion("Is it?", "yes", "no")}) for i in range(n)}


def test_the_waves_keep_each_second_under_80_requests():
    waves = plan_waves(_tiny(200))
    assert [len(wave) for wave in waves] == [REQUESTS_PER_SECOND, REQUESTS_PER_SECOND, 40]


def test_the_waves_keep_each_second_under_100000_tokens():
    # About 40,000 characters of state is about 13,000 tokens by the high guess, so 7 fit in one second.
    big = {str(i): WaveRequest({"text": "x" * 40_000}, {}) for i in range(20)}
    waves = plan_waves(big)
    assert len(waves) == 3
    assert all(len(wave) <= 7 for wave in waves)


def test_the_next_wave_waits_one_second_after_the_start_of_the_last():
    now = [0.0]
    slept = []

    def sleep(seconds):
        slept.append(seconds)
        now[0] += seconds

    jev = FakeJev()
    pacer = JevWaves(jev, clock=lambda: now[0], sleep=sleep)
    answers = pacer.ask(_tiny(170), "test")
    assert len(answers) == 170 and all(answer is not None for answer in answers.values())
    assert len(jev.requests) == 170
    assert slept == [1.0, 1.0]
    # A second call shares the budget, so it waits too.
    pacer.ask(_tiny(1), "test")
    assert slept == [1.0, 1.0, 1.0]
