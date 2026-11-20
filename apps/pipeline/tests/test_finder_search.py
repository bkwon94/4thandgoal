"""
Tests for the Finder search: the partner reads (the Spares tree), the Value offers, and the shortlist that Jev narrows.
They read the week 6 snapshot and use FakeJev, so no test calls TypeSafe.
"""
import logging
import re
import shutil
import threading
from concurrent.futures import ThreadPoolExecutor
from itertools import combinations

import httpx2
import pytest
from cpc import cpc_client
from fakes import FakeJev, no_news
from typesafe_sdk import RetryPolicy, TypeSafeClient

from analyzer.finder_pick import offer_sheet
from analyzer.finder_search import (
    SHORTLIST_KEEP,
    UNSURE,
    Anchor,
    Limit,
    ShortlistOffer,
    _out_with_no_return,
    gain_dropped,
    in_band,
    in_pool,
    offer_id,
    search,
    shortlist_answers,
    step_two_answers,
    varied,
)
from analyzer.jev_waves import (
    PACER,
    REQUEST_TOKENS,
    REQUESTS_PER_SECOND,
    TOKENS_PER_SECOND,
    JevWaves,
    Pacer,
    WaveRequest,
    estimated_tokens,
    plan_waves,
)
from analyzer.measures import is_handcuff, trade_handcuffs
from analyzer.spares_tree import pair_spares
from analyzer.trade import GivenPlayer, ProposedTrade, TradeSide
from analyzer.trade_jev import FACT_PREFIX
from analyzer.trade_news import NewsFeed
from league.jev import TypeSafeJev
from league.jev_port import JevError, NoulQuestion
from league.slow_sources import load_slow_sources
from league.snapshot import load_snapshot

CLIENT = cpc_client()
ASKER, PARTNER = 4, 12


@pytest.fixture
def snap(fixture_raw_dir, fixture_history_root, chart_week9, fixture_nflverse_dir, tmp_path):
    # The week 6 chart holds too few values for the Value screen, so the Finder tests read the week 9 trade values.
    cache = tmp_path / "nflverse"
    shutil.copytree(fixture_nflverse_dir, cache)
    slow = load_slow_sources(cache, 2026, 6, fixture_history_root)
    return load_snapshot(fixture_raw_dir, fixture_history_root, chart_week9, slow, client=CLIENT)


SHAPES = {"1-for-1", "2-for-1", "1-for-2", "3-for-1", "1-for-3", "3-for-2", "2-for-3"}


def _shape(trade):
    """The shape direction of a trade, by the players that the asker gives, then the players he gets."""
    return f"{len(trade.sides[0].player_ids)}-for-{len(trade.sides[1].player_ids)}"


def test_the_value_offers_hold_every_shape_in_both_directions(snap):
    found = search(ASKER, None, snap, FakeJev())
    assert {_shape(trade) for trade in found.offers} == SHAPES
    # Each other team gives some Value offer, because no partner filter stops a team.
    assert {trade.sides[1].roster_id for trade in found.offers} == {rid for rid in snap.rosters if rid != ASKER}


def _sums(snap, trade):
    """The trade value sum of the side of the asker, then of the side of the partner."""
    return [sum(snap.chart.values[pid] for pid in side.player_ids) for side in trade.sides]


def test_each_value_offer_is_inside_the_band_with_its_direction(snap):
    found = search(ASKER, None, snap, FakeJev())
    assert len(found.offers) > 1000
    for trade in found.offers:
        gives, gets = _sums(snap, trade)
        counts = [len(side.player_ids) for side in trade.sides]
        if counts[0] == counts[1]:
            # A 1-for-1 stays within 10% either way.
            assert max(gives, gets) / min(gives, gets) <= 1.1 + 1e-9, (trade, gives, gets)
        else:
            # The side that gets more players gets 100% to 125% of the sum of the other side.
            more, less = (gives, gets) if counts[0] > counts[1] else (gets, gives)
            assert 1.0 <= more / less <= 1.25 + 1e-9, (trade, gives, gets)


def test_the_band_holds_its_edges_and_its_direction():
    # Matthew Golden and Kyren Williams for Amon-Ra St. Brown sit at 125% of the week 11 chart (decision 15).
    assert in_band([40.5, 27.0], [54.0])
    assert not in_band([40.5, 27.5], [54.0])
    # The side that gets more players must get more value, never less.
    assert in_band([54.0], [40.5, 27.0])
    assert not in_band([30.0, 20.0], [54.0])
    # A 1-for-1 within 10% either way.
    assert in_band([11.0], [10.0]) and in_band([10.0], [11.0])
    assert not in_band([11.5], [10.0]) and not in_band([10.0], [11.5])
    # The floor of 5 on a side of 2 or 3, and none on a side of one.
    assert not in_band([4.5, 50.0], [50.0])
    assert in_band([5.0, 45.0], [45.0])
    assert in_band([4.5], [4.5])


def test_no_filler_and_no_player_without_a_chart_value_enters_a_value_offer(snap):
    found = search(ASKER, None, snap, FakeJev())
    # The fixture has pool players with no chart value, and players under 5, so each rule has something to keep out.
    none = {pid for rid, roster in snap.rosters.items() for pid in roster
            if in_pool(snap, pid, rid) and pid not in snap.chart.values}
    low = {pid for pid, value in snap.chart.values.items() if value < 5}
    assert none and any(pid in low for pid in snap.rosters[ASKER])
    for trade in found.offers:
        for side in trade.sides:
            assert not set(side.player_ids) & none
            if len(side.player_ids) > 1:
                assert all(snap.chart.values[pid] >= 5 for pid in side.player_ids), trade


def _fair_requests(jev):
    """The fair requests of step 1: each offer of the state lists its sides with their chart sums."""
    return [r for r in jev.requests if any("sides" in line for line in r.state.get("offers", {}).values())]


def _first_team(state, key):
    """The name of the team that the fair request of `key` names first."""
    return state["offers"][key.partition("|")[0]]["sides"][0]["team"]


def _fair_pairs(snap, pairs):
    """A Jev that answers the fair Noul of offer n with pairs[n]: the answer with the asker named first, then the
    answer with the partner named first. Each other question gets a clear yes."""
    asker = snap.teams[ASKER].name

    def answer(key, question, state):
        n, _, kind = key.partition("|")
        if kind == "fair" and "sides" in state["offers"][n] and int(n) in pairs:
            first, second = pairs[int(n)]
            return first if _first_team(state, key) == asker else second
        return 0.9
    return answer


def test_the_fair_step_drops_a_clear_no_on_the_mean_of_both_side_orders(snap):
    # Offer 0 reads 0.2 and 0.3, a mean of 0.25, so it drops. Offer 1 reads 0.1 and 0.6, a mean of 0.35, so it stays,
    # though one order alone is a clear no.
    jev = FakeJev(answer=_fair_pairs(snap, {0: (0.2, 0.3), 1: (0.1, 0.6)}))
    found = search(ASKER, PARTNER, snap, jev)
    dropped, kept = offer_id(found.offers[0]), offer_id(found.offers[1])
    assert found.fair_means[dropped] == pytest.approx(0.25) and found.fair_means[kept] == pytest.approx(0.35)
    assert found.unfair == [dropped]
    # Step 2 never reads the offer that dropped, and it reads the one that stayed only as the best of its group.
    assert dropped not in found.step_two and set(found.step_two) <= {offer_id(t) for t in found.offers[1:]}
    assert {offer.offer_id for offer in found.shortlist + found.dropped} <= set(found.step_two)


def _scattered_fair(key, question, state):
    """A fair answer that differs from offer to offer in no order, so the best of a group is not its first offer. Every
    answer is above NO_AT, so step 1 drops nothing. Each other question gets a clear yes."""
    n, _, kind = key.partition("|")
    return 0.31 + (int(n) * 7919 % 61) / 100 if kind == "fair" else 0.9


def test_step_two_gets_the_three_best_offers_of_each_partner_and_shape_direction(snap):
    jev = FakeJev(answer=_scattered_fair)
    found = search(ASKER, None, snap, jev)
    groups: dict[tuple[int, str], list[str]] = {}
    for trade in found.offers:
        groups.setdefault((trade.sides[1].roster_id, _shape(trade)), []).append(offer_id(trade))
    assert len(groups) > 11 and any(len(group) > 3 for group in groups.values())
    # Up to three offers per partner and shape direction, at most 11 partners times 7 shape directions times 3.
    assert len(found.step_two) == sum(min(3, len(group)) for group in groups.values()) <= 231
    chosen = set(found.step_two)
    for group in groups.values():
        picked = [oid for oid in group if oid in chosen]
        rest = [oid for oid in group if oid not in chosen]
        # The highest fair means of the group. A tie goes to the lower offer id.
        assert all(found.fair_means[oid] >= found.fair_means[other] for oid in picked for other in rest)
    # Step 2 asks about these offers and no other.
    # Each partner numbers its own offers from 0, so the count sums the offers of each request.
    assert sum(len(r.state["offers"]) for r in _shortlist_requests(jev)) == len(found.step_two)


def test_step_two_asks_the_need_and_the_gain_of_each_side_and_no_fair_question(snap):
    jev = FakeJev()
    found = search(ASKER, PARTNER, snap, jev)
    questions, _ = _shortlist_merged(jev)
    shapes = [_shape(t) for t in found.offers]
    assert len(found.step_two) == sum(min(3, shapes.count(s)) for s in set(shapes))
    assert set(questions) == {f"{n}|{kind}.{rid}" for n in range(len(found.step_two))
                              for kind in ("need", "gain") for rid in (ASKER, PARTNER)}


def test_the_score_of_an_offer_is_its_fair_mean(snap):
    found = search(ASKER, None, snap, FakeJev(answer=_scattered_fair))
    for offer in found.shortlist:
        assert offer.score == offer.fair == found.fair_means[offer.offer_id]


def test_each_fair_request_holds_the_chart_value_of_each_player_and_the_chart_sum_of_each_side(snap):
    jev = FakeJev()
    found = search(ASKER, PARTNER, snap, jev)
    requests = _fair_requests(jev)
    names = {snap.teams[ASKER].name, snap.teams[PARTNER].name}
    firsts = set()
    for request in requests:
        for team in request.state["teams"].values():
            assert all("chart_value" in player for player in team["players"])
        for key, question in request.questions.items():
            n = key.partition("|")[0]
            assert key.endswith("|fair")
            assert question.instructions.startswith(f"Is the trade in `offers.{n}` close to fair by chart value: ")
            assert question.yes == ("Each team gives about as much chart value as it gets, by the sums in "
                                    f"`offers.{n}.sides`.")
            assert question.no == f"One team gives a clearly larger chart sum in `offers.{n}.sides` than it gets back."
            sides = request.state["offers"][n]["sides"]
            assert {side["team"] for side in sides} == names
            for side in sides:
                assert side["chart_sum"] == pytest.approx(sum(player["chart_value"] for player in side["gives"]))
            firsts.add(sides[0]["team"])
            # The question names the teams in the order of the sides.
            assert question.instructions.index(sides[0]["team"]) < question.instructions.index(sides[1]["team"])
    # Each offer is asked once in each side order.
    assert firsts == names
    assert sum(len(r.questions) for r in requests) == 2 * len(found.offers)


def test_the_stream_reports_the_count_of_value_offers_and_the_count_checked_for_fairness(snap):
    lines = []
    found = search(ASKER, None, snap, FakeJev(), stage=lambda line, live=False: lines.append((line, live)))
    count = f"{len(found.offers):,}"
    assert ("Matching trade value", True) in lines
    assert (f"Matched {count} trades by trade value", False) in lines
    assert (f"Checking {count} trades for fairness", True) in lines
    assert (f"Checked {count} trades for fairness", False) in lines


def _filter_requests(jev):
    return [r for r in jev.requests if r.questions and all(key.startswith("spare:") for key in r.questions)]


def test_with_no_partner_the_spares_tree_reads_every_other_team_on_both_sides(snap):
    jev = FakeJev()
    found = search(ASKER, None, snap, jev)
    others = sorted(rid for rid in snap.rosters if rid != ASKER)
    assert len(others) == 11
    assert sorted(read.roster_id for read in found.partners) == others
    # One request per pair with a listed player, with one question per listed player of both sides.
    for request in _filter_requests(jev):
        partner = request.state["teams"]["partner"]["roster_id"]
        spares = pair_spares(snap, ASKER, partner)
        assert set(request.questions) == {spare.key for side in spares.values() for spare in side}
    # Each answer is a clear yes, so a pair passes when each side lists a player.
    for read in found.partners:
        spares = pair_spares(snap, ASKER, read.roster_id)
        assert read.passed == bool(spares["partner"] and spares["asker"])
    assert sum(read.passed for read in found.partners) >= 6


def test_a_picked_partner_skips_the_partner_filter_and_keeps_every_offer_to_that_partner(snap, caplog):
    # Each Spares tree answer is a clear no, so a filter would stop the partner.
    def answer(key, question, state):
        return 0.1 if key.startswith("spare:") else 0.9

    jev = FakeJev(answer=answer)
    with caplog.at_level(logging.INFO, logger="analyzer.finder_search"):
        found = search(ASKER, PARTNER, snap, jev)
    assert _filter_requests(jev) == []
    assert not any("Partner filter" in r.getMessage() for r in caplog.records)
    assert [read.roster_id for read in found.partners if read.passed] == [PARTNER]
    assert len(found.shortlist) >= 2
    for trade in found.offers + [offer.trade for offer in found.shortlist]:
        assert [side.roster_id for side in trade.sides] == [ASKER, PARTNER]


def _both_sides(snap):
    """The other teams whose pair with the asker lists a player on each side, in roster order."""
    return [rid for rid in sorted(snap.rosters) if rid != ASKER
            and all(pair_spares(snap, ASKER, rid).values())]


def test_a_clear_no_for_each_player_of_one_side_marks_the_read_and_stops_no_partner(snap):
    stopped, unsure = _both_sides(snap)[:2]

    def answer(key, question, state):
        _, giver, _ = key.split(":") if key.startswith("spare:") else ("", "", "")
        # Each player of `stopped` reads a clear no. Each player of `unsure` reads unsure, which passes.
        if giver == str(stopped):
            return 0.2
        if giver == str(unsure):
            return 0.5
        return 0.9

    jev = FakeJev(answer=answer)
    found = search(ASKER, None, snap, jev)
    read = next(read for read in found.partners if read.roster_id == stopped)
    assert not read.passed and not read.failed
    assert next(read for read in found.partners if read.roster_id == unsure).passed
    # The Value screen is the one source of offers, so the partner of a clear no still gets Value offers (decision 15).
    partners = {trade.sides[1].roster_id for trade in found.offers}
    assert stopped in partners and unsure in partners


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
        # One of the 7 shape directions, and never 2-for-2 or 3-for-3.
        assert _shape(trade) in SHAPES
    # The fixture rosters hold kickers and defenses, so the rule has something to keep out.
    assert any(snap.players[pid].position in ("K", "DEF") for roster in snap.rosters.values() for pid in roster)


def _rising_fair(key, question, state):
    """The fair answer falls a little with each offer, so the first offers of each partner rate highest."""
    number, _, kind = key.partition("|")
    if not kind:
        return 0.9
    return 0.99 - 0.001 * int(number) if kind == "fair" else 0.9


def _tiers(offers):
    """The ids of the best offers of the three tiers of AT-43, by score: of each shape direction, of each partner not
    in an earlier tier, and of each player of the asker not in an earlier tier. A tie goes to the lower offer id."""
    ranked = sorted(offers, key=lambda offer: (-offer.score, offer.offer_id))
    keys = (lambda o: [_shape(o.trade)],
            lambda o: [side.roster_id for side in o.trade.sides[1:]],
            lambda o: list(o.trade.sides[0].player_ids))
    tiers, seen = [], set()
    for key_of in keys:
        best = {}
        for offer in ranked:
            for key in key_of(offer):
                best.setdefault(key, offer.offer_id)
        tier = {oid for oid in best.values() if oid not in seen}
        tiers.append(tier)
        seen |= tier
    return tiers


def _assert_varied(found):
    """AT-43: the best offer of each shape direction comes first, then the best of each partner, then the best of each
    player of the asker, before a second form of any trade. Each tier and the rest go by score, highest first."""
    tiers = _tiers(found.shortlist)
    place = [next((n for n, tier in enumerate(tiers) if offer.offer_id in tier), 3) for offer in found.shortlist]
    assert place == sorted(place), [offer.offer_id for offer in found.shortlist]
    for tier in range(4):
        scores = [offer.score for offer, at in zip(found.shortlist, place, strict=True) if at == tier]
        assert scores == sorted(scores, reverse=True)


def _offer(gives: list[str], partner: int, gets: list[str], score: float) -> ShortlistOffer:
    trade = ProposedTrade(season=2026, asker=6, sides=[
        TradeSide(roster_id=6, gives=[GivenPlayer(player_id=pid, to=partner) for pid in gives]),
        TradeSide(roster_id=partner, gives=[GivenPlayer(player_id=pid, to=6) for pid in gets])])
    return ShortlistOffer(offer_id=offer_id(trade), trade=trade, fair=score, needs={6: 1.0, partner: 1.0},
                          score=score)


def test_varied_puts_the_best_of_each_shape_then_partner_then_player_first_and_the_rest_by_fair_mean():
    offers = [_offer(["p1"], 11, ["a"], 0.9), _offer(["p2"], 7, ["b"], 0.8),
              _offer(["p1", "p3"], 11, ["c"], 0.7), _offer(["p2"], 3, ["d", "e"], 0.6),
              _offer(["p4"], 3, ["f"], 0.5), _offer(["p2", "p3"], 7, ["g"], 0.4),
              _offer(["p1"], 9, ["h"], 0.3), _offer(["p5"], 11, ["i"], 0.2), _offer(["p4"], 11, ["j"], 0.1)]
    shortlist = varied(offers, SHORTLIST_KEEP)
    # The best of 1-for-1 (0.9), of 2-for-1 (0.7), and of 1-for-2 (0.6). Then the best of partner 7 (0.8) and of
    # partner 9 (0.3), because partners 11 and 3 are on the list. Then the best of p4 (0.5) and of p5 (0.2). Then the
    # rest by the fair mean: 0.4, then 0.1.
    assert [offer.score for offer in shortlist] == [0.9, 0.7, 0.6, 0.8, 0.3, 0.5, 0.2, 0.4, 0.1]
    assert [offer.score for offer in varied(offers, 4)] == [0.9, 0.7, 0.6, 0.8]


def test_a_list_with_more_best_offers_than_it_keeps_holds_only_best_offers_by_score():
    offers = [_offer([f"p{n}"], 20 + n, [f"g{n}"], 0.1 + 0.01 * n) for n in range(12)]
    offers += [_offer(["p11"], 20, ["g99"], 0.9)]
    shortlist = varied(offers, SHORTLIST_KEEP)
    # 0.9 is the best 1-for-1, so it leads. The other 11 partners are best offers, and they fill the list by score.
    assert [offer.score for offer in shortlist] == pytest.approx([0.9] + [0.1 + 0.01 * n for n in range(11, 2, -1)])


def test_the_shortlist_of_one_partner_holds_the_best_offer_of_each_shape_direction_first(snap):
    found = search(ASKER, PARTNER, snap, FakeJev(answer=_scattered_fair))
    assert len(found.shortlist) == min(SHORTLIST_KEEP, len(found.step_two))
    _assert_varied(found)
    shapes = {_shape(trade) for trade in found.offers}
    assert {_shape(offer.trade) for offer in found.shortlist[:len(shapes)]} == shapes


def test_the_shortlist_of_every_partner_holds_each_shape_then_more_partners_before_more_forms(snap):
    found = search(ASKER, None, snap, FakeJev(answer=_scattered_fair))
    assert len(found.shortlist) == SHORTLIST_KEEP
    _assert_varied(found)
    shapes = {_shape(trade) for trade in found.offers}
    assert len(shapes) == 7
    assert {_shape(offer.trade) for offer in found.shortlist[:7]} == shapes
    # The three places after the shapes go to the best offers of three more partners, by the fair mean of step 2.
    by_id = {offer_id(trade): trade for trade in found.offers}
    top: dict[int, str] = {}
    for oid in sorted(found.step_two, key=lambda oid: (-found.fair_means[oid], oid)):
        top.setdefault(by_id[oid].sides[1].roster_id, oid)
    later = found.shortlist[7:]
    assert all(offer.offer_id == top[offer.trade.sides[1].roster_id] for offer in later)
    assert len({offer.trade.sides[1].roster_id for offer in later}) == 3


def _spares_press(snap, spare_answer: float):
    """A press of every partner where each listed player of a partner gets `spare_answer`. An offer that brings the
    asker a listed player reads 0.95 on fair, and every other offer 0.5, so the shortlist holds such offers."""
    listed = {spare.player_id: spare for rid in snap.rosters if rid != ASKER
              for spare in pair_spares(snap, ASKER, rid)["partner"]}
    names = {snap.players[pid].name for pid in listed}

    def answer(key, question, state):
        n, _, kind = key.partition("|")
        if key.startswith("spare:"):
            return spare_answer if key.split(":")[1] != str(ASKER) else 0.9
        if kind == "fair":
            gets = next(side for side in state["offers"][n]["sides"] if side["team"] != snap.teams[ASKER].name)
            return 0.95 if {player["name"] for player in gets["gives"]} & names else 0.5
        return 0.9
    return listed, search(ASKER, None, snap, FakeJev(answer=answer))


def test_a_spares_tree_yes_is_a_pick_sheet_fact_and_changes_no_count_and_no_order(snap):
    listed, yes = _spares_press(snap, 0.9)
    _, no = _spares_press(snap, 0.1)
    # The Spares tree builds no offer, drops no offer, and changes no order (decision 16).
    assert [offer_id(t) for t in yes.offers] == [offer_id(t) for t in no.offers]
    assert yes.step_two == no.step_two
    assert [o.offer_id for o in yes.shortlist] == [o.offer_id for o in no.shortlist]
    with_spares = [offer for offer in yes.shortlist if offer.spares]
    assert with_spares and not any(offer.spares for offer in no.shortlist)
    asker = snap.teams[ASKER].name
    for offer in with_spares:
        partner = snap.teams[offer.trade.sides[1].roster_id].name
        texts = [fact.text for fact in offer_sheet(offer, snap, NewsFeed(fetch=no_news)).values()]
        for pid, slot in offer.spares.items():
            assert pid in offer.trade.sides[1].player_ids and slot == listed[pid].slot
            name = snap.players[pid].name
            assert f"For {asker}, {name} fills the weak slot {slot}, and {partner} can spare him." in texts
    for offer in no.shortlist:
        texts = [fact.text for fact in offer_sheet(offer, snap, NewsFeed(fetch=no_news)).values()]
        assert not any("can spare him" in text for text in texts)


def test_a_failed_jev_request_on_every_step_never_raises_and_never_hides_a_partner(snap):
    found = search(ASKER, None, snap, FakeJev(error=JevError("429 Too Many Requests")))
    # A failed call is an error, never a stop: each pair with a question is marked failed, and each goes on.
    assert all(read.passed for read in found.partners)
    assert all(read.failed for read in found.partners if any(pair_spares(snap, ASKER, read.roster_id).values()))
    # The Value screen needs no Jev answer, so it builds the offers, and the failed shortlist keeps them as unsure.
    assert found.offers and found.shortlist
    assert all(offer.failed for offer in found.shortlist) and found.dropped == []


class _SparesTreeFails(FakeJev):
    """A Jev whose Spares tree request fails for one partner. Each other request answers as FakeJev does."""

    def __init__(self, partner: int, **kwargs):
        super().__init__(**kwargs)
        self.partner = partner

    def ask(self, state, questions):
        if (any(key.startswith("spare:") for key in questions)
                and state["teams"]["partner"]["roster_id"] == self.partner):
            super().ask(state, questions)
            raise JevError("429 Too Many Requests")
        return super().ask(state, questions)


def _partner_with_spares(snap):
    return next(rid for rid in sorted(snap.rosters) if rid != ASKER and any(pair_spares(snap, ASKER, rid).values()))


def test_a_failed_spares_tree_request_lets_the_partner_go_on_and_logs(snap, caplog):
    failed = _partner_with_spares(snap)
    jev = _SparesTreeFails(failed)
    with caplog.at_level(logging.INFO, logger="analyzer.finder_search"):
        found = search(ASKER, None, snap, jev)
    read = next(read for read in found.partners if read.roster_id == failed)
    assert read.failed and read.passed
    assert failed in {trade.sides[1].roster_id for trade in found.offers}
    assert any("Spares tree of" in line and snap.teams[failed].name in line and "failed request" in line
               for line in caplog.messages)


def _gain_of_first_offer(p: float, side: int):
    """A Jev that gives `p` to the gain Noul of `side` on offer 0. Each other question gets the answer of
    `_rising_fair`, so offer 0 leads the list when it stays."""
    def answer(key, question, state):
        return p if key == f"0|gain.{side}" else _rising_fair(key, question, state)
    return answer


def _shortlist_requests(jev):
    """The shortlist requests of a press: each asks the gain Noul of the sides of its offers."""
    return [r for r in jev.requests if r.questions and all("|" in key for key in r.questions)
            and any("|gain." in key for key in r.questions)]


def _shortlist_merged(jev):
    """The questions and the offer lines of every shortlist request of a press, merged by key. Each offer keeps its
    number in the whole list, so the parts of a split merge."""
    requests = _shortlist_requests(jev)
    return ({key: q for r in requests for key, q in r.questions.items()},
            {n: line for r in requests for n, line in r.state["offers"].items()})


def test_the_shortlist_asks_one_gain_noul_per_side_of_each_offer(snap):
    jev = FakeJev()
    found = search(ASKER, PARTNER, snap, jev)
    questions, _ = _shortlist_merged(jev)
    for n in range(len(found.step_two)):
        for rid in (ASKER, PARTNER):
            question = questions[f"{n}|gain.{rid}"]
            assert str(question.instructions).startswith(
                f"Does {snap.teams[rid].name} start a better lineup after this trade")


def test_a_clear_no_gain_drops_the_offer_and_keeps_its_answers(snap):
    first = None
    for side in (ASKER, PARTNER):
        found = search(ASKER, PARTNER, snap, FakeJev(answer=_gain_of_first_offer(0.29, side)))
        first = offer_id(found.offers[0])
        assert first not in {offer.offer_id for offer in found.shortlist}
        [dropped] = [offer for offer in found.dropped if offer.offer_id == first]
        assert dropped.gains[side] == pytest.approx(0.29)
    # With a clear yes everywhere, the same offer leads the list, so only the gain answer dropped it.
    found = search(ASKER, PARTNER, snap, FakeJev(answer=_rising_fair))
    assert found.shortlist[0].offer_id == first and found.dropped == []


def test_an_unsure_gain_keeps_the_offer(snap):
    found = search(ASKER, PARTNER, snap, FakeJev(answer=_gain_of_first_offer(0.3, ASKER)))
    kept = {offer.offer_id: offer for offer in found.shortlist}
    assert found.dropped == []
    assert kept[offer_id(found.offers[0])].gains[ASKER] == pytest.approx(0.3)


def test_a_gain_of_0_2_drops_the_offer_and_a_gain_of_0_5_keeps_it(snap):
    # AT-45 with fixed answers: 0.2 is a clear no, and 0.5 is unsure.
    first = offer_id(search(ASKER, PARTNER, snap, FakeJev(answer=_rising_fair)).offers[0])
    for side in (ASKER, PARTNER):
        found = search(ASKER, PARTNER, snap, FakeJev(answer=_gain_of_first_offer(0.2, side)))
        assert first in found.step_two
        assert first not in {offer.offer_id for offer in found.shortlist}
        assert [offer.offer_id for offer in found.dropped] == [first]
        found = search(ASKER, PARTNER, snap, FakeJev(answer=_gain_of_first_offer(0.5, side)))
        assert found.dropped == [] and first in {offer.offer_id for offer in found.shortlist}


def test_a_failed_step_two_call_of_one_offer_raises_an_error_and_never_reads_as_a_drop(snap):
    trade = search(ASKER, PARTNER, snap, FakeJev()).shortlist[0].trade
    with pytest.raises(JevError):
        step_two_answers(snap, trade, FakeJev(error=JevError("timeout")))
    answers = step_two_answers(snap, trade, FakeJev(answer=lambda key, q, state: 0.2 if "|gain." in key else 0.8))
    assert gain_dropped({rid: answers[f"gain.{rid}"] for rid in (ASKER, PARTNER)})
    assert not gain_dropped({ASKER: 0.5, PARTNER: 0.8})


def test_need_answers_of_0_1_on_both_sides_drop_no_offer(snap):
    # AT-59: need is a reason, never a gate. A gain of 0.8 on both sides keeps the offer.
    def answer(key, question, state):
        _, _, kind = key.partition("|")
        if kind.startswith("need."):
            return 0.1
        return 0.8 if kind.startswith("gain.") else _rising_fair(key, question, state)

    found = search(ASKER, PARTNER, snap, FakeJev(answer=answer))
    assert found.dropped == []
    assert len(found.shortlist) == min(SHORTLIST_KEEP, len(found.step_two))
    for offer in found.shortlist:
        assert list(offer.needs.values()) == pytest.approx([0.1, 0.1])
        assert offer.score == offer.fair


def test_the_gain_state_holds_the_lineup_points_of_each_side_before_and_after_each_offer(snap):
    jev = FakeJev()
    found = search(ASKER, PARTNER, snap, jev)
    _, offers = _shortlist_merged(jev)
    assert len(offers) == len(found.step_two)
    by_id = {offer_id(trade): trade for trade in found.offers}
    for n, trade in enumerate(by_id[oid] for oid in found.step_two):
        lines = offers[str(n)]["lineup_points"]
        for rid in (ASKER, PARTNER):
            [line] = [line for line in lines if line.startswith(snap.teams[rid].name + " ")]
            before, after, change = (float(x) for x in re.findall(r"\d+\.\d", line))
            # The fact states the change in words, so Jev compares no numbers itself.
            assert abs(before - after) == pytest.approx(change, abs=0.11)
            word = "gains" if after > before else "loses" if after < before else "keeps"
            assert word in line, line


class _ShortlistFails(FakeJev):
    """A Jev whose step 2 requests fail. The fair requests of step 1 answer as FakeJev does."""
    def ask(self, state, questions):
        if any("|gain." in key for key in questions):
            raise JevError("timeout")
        return super().ask(state, questions)


def test_a_failed_shortlist_request_keeps_its_offers_as_unsure_and_never_reads_as_a_no(snap, caplog):
    with caplog.at_level(logging.INFO, logger="analyzer.finder_search"):
        found = search(ASKER, PARTNER, snap, _ShortlistFails())
    assert found.offers and found.shortlist and found.dropped == []
    assert len(found.shortlist) == min(len(found.step_two), SHORTLIST_KEEP)
    for offer in found.shortlist:
        assert offer.failed and not offer.fair_failed
        # The fair mean of step 1 still stands. Each step 2 answer is unsure.
        assert offer.fair == found.fair_means[offer.offer_id]
        assert set(offer.needs.values()) == {UNSURE} and set(offer.gains.values()) == {UNSURE}
    assert any("Finder shortlist with" in line and "failed request" in line for line in caplog.messages)


def test_the_pick_sheet_of_an_offer_with_a_failed_shortlist_request_states_no_jev_answer(snap):
    failed = search(ASKER, PARTNER, snap, _ShortlistFails()).shortlist[0]
    sheet = offer_sheet(failed, snap, NewsFeed(fetch=no_news))
    # The step 2 call never answered, so the pick never reads "unsure" for a need. The fair mean of step 1 stands.
    assert sheet and [key for key in sheet if key.startswith(FACT_PREFIX)] == [f"{FACT_PREFIX}fair"]
    # With every call failed, the sheet states no Jev answer at all.
    none = search(ASKER, PARTNER, snap, FakeJev(error=JevError("timeout"))).shortlist[0]
    assert none.failed and none.fair_failed
    assert not any(key.startswith(FACT_PREFIX) for key in offer_sheet(none, snap, NewsFeed(fetch=no_news)))
    answered = search(ASKER, PARTNER, snap, FakeJev()).shortlist[0]
    assert any(key.startswith(FACT_PREFIX) for key in offer_sheet(answered, snap, NewsFeed(fetch=no_news)))


class _ContextLimitJev(FakeJev):
    """A FakeJev that fails a request above the 64k context of one TypeSafe request, as TypeSafe does."""
    def ask(self, state, questions):
        if estimated_tokens(WaveRequest(state, dict(questions))) >= REQUEST_TOKENS:
            raise JevError("the request is above the context of the model")
        return super().ask(state, questions)


def test_a_partner_of_1200_offers_splits_under_64k_and_no_offer_passes_as_unsure(snap):
    every = {rid: [pid for pid in snap.rosters[rid] if in_pool(snap, pid, rid)] for rid in (ASKER, PARTNER)}
    # Every 2-for-3 of the pools, with no Value screen, so one partner holds far more offers than one request fits.
    offers = [ProposedTrade(season=2026, asker=ASKER, sides=[
        TradeSide(roster_id=ASKER, gives=[GivenPlayer(player_id=pid, to=PARTNER) for pid in gives]),
        TradeSide(roster_id=PARTNER, gives=[GivenPlayer(player_id=pid, to=ASKER) for pid in gets])])
        for gives in combinations(every[ASKER], 2) for gets in combinations(every[PARTNER], 3)][:1200]
    assert len(offers) == 1200
    jev = _ContextLimitJev(yes=0.8)
    answers = shortlist_answers(snap, ASKER, {PARTNER: offers}, JevWaves(jev))
    assert len(jev.requests) >= 3
    assert all(estimated_tokens(WaveRequest(r.state, dict(r.questions))) < 64_000 for r in jev.requests)
    assert len(answers[PARTNER]) == 1200
    for nouls in answers[PARTNER]:
        assert nouls is not None
        assert nouls == {f"need.{ASKER}": 0.8, f"need.{PARTNER}": 0.8,
                         f"gain.{ASKER}": 0.8, f"gain.{PARTNER}": 0.8}


def test_the_fair_requests_of_a_press_split_under_64k_and_each_value_offer_gets_its_answer(snap):
    jev = _ContextLimitJev(yes=0.8)
    found = search(ASKER, None, snap, jev)
    fair = _fair_requests(jev)
    # More than one request per partner and side order, because some partner holds far more than 64k of offers.
    assert len(fair) > 2 * 11
    assert all(estimated_tokens(WaveRequest(r.state, dict(r.questions))) < 64_000 for r in fair)
    assert set(found.fair_means) == {offer_id(trade) for trade in found.offers}
    assert all(mean == pytest.approx(0.8) for mean in found.fair_means.values())


def test_three_fair_requests_of_a_press_fit_in_one_second_of_the_token_budget(snap):
    jev = FakeJev(yes=0.8)
    search(ASKER, None, snap, jev)
    fair = _fair_requests(jev)
    assert all(3 * estimated_tokens(WaveRequest(r.state, dict(r.questions))) <= TOKENS_PER_SECOND for r in fair)
    # So each wave of step 1 holds three requests or more, not one, and the step takes a third of the seconds.
    waves = plan_waves({str(n): WaveRequest(r.state, dict(r.questions)) for n, r in enumerate(fair)})
    assert all(len(wave) >= 3 for wave in waves[:-1])


def _last_pool_player(snap, roster_id):
    """The pool player of the roster with a chart value and the last id in string order, so he can enter a Value
    offer."""
    return max(pid for pid in snap.rosters[roster_id] if in_pool(snap, pid, roster_id) and pid in snap.chart.values)


def test_an_anchor_that_the_asker_gives_is_in_each_offer_on_the_asker_side(snap):
    anchor = _last_pool_player(snap, ASKER)
    found = search(ASKER, None, snap, FakeJev(), anchor=Anchor(player_id=anchor, side="gives"))
    assert found.offers and found.shortlist
    for trade in found.offers + [offer.trade for offer in found.shortlist]:
        assert trade.sides[0].roster_id == ASKER and anchor in trade.sides[0].player_ids
        assert all(anchor not in side.player_ids for side in trade.sides[1:])


def test_an_anchor_that_the_asker_gets_keeps_the_search_to_his_roster_and_each_offer_holds_him(snap):
    anchor = _last_pool_player(snap, PARTNER)
    jev = FakeJev()
    found = search(ASKER, None, snap, jev, anchor=Anchor(player_id=anchor, side="gets"))
    # Only the roster of the anchor can give him, so the search reads that roster alone.
    assert [read.roster_id for read in found.partners] == [PARTNER]
    assert found.offers and found.shortlist
    for trade in found.offers + [offer.trade for offer in found.shortlist]:
        assert [side.roster_id for side in trade.sides] == [ASKER, PARTNER]
        assert anchor in trade.sides[1].player_ids



def test_an_anchored_search_skips_the_partner_filter_and_the_plain_search_keeps_it(snap):
    # Each filter question reads no here, so a filter would stop every partner.
    def answer(key, question, state):
        return 0.1 if key.startswith("spare:") else 0.9

    others = sorted(rid for rid in snap.rosters if rid != ASKER)
    anchor = _last_pool_player(snap, ASKER)
    jev = FakeJev(answer=answer)
    found = search(ASKER, None, snap, jev, anchor=Anchor(player_id=anchor, side="gives"))
    # The filter reads the weakest slots, and the anchor names the player the trade turns on, so no filter asks.
    assert _filter_requests(jev) == []
    assert [read.roster_id for read in found.partners if read.passed] == others
    jev = FakeJev(answer=answer)
    found = search(ASKER, None, snap, jev)
    assert len(_filter_requests(jev)) == sum(any(pair_spares(snap, ASKER, rid).values()) for rid in others)
    # No partner passed, and the Value screen still builds the offers that the pick weighs.
    assert not any(read.passed for read in found.partners) and found.offers


def test_an_aim_and_a_keep_of_the_limit_hold_on_every_value_offer(snap):
    found = search(ASKER, None, snap, FakeJev(), limit=Limit(aim_position="RB"))
    assert found.offers
    # Each Value offer brings the asker an RB.
    assert all(any(snap.players[pid].position == "RB" for pid in trade.sides[1].player_ids) for trade in found.offers)
    kept = _last_pool_player(snap, ASKER)
    found = search(ASKER, None, snap, FakeJev(), limit=Limit(keep_players=[kept], keep_positions=["WR"]))
    assert found.offers
    for trade in found.offers:
        assert kept not in trade.sides[0].player_ids
        assert all(snap.players[pid].position != "WR" for pid in trade.sides[0].player_ids)


class _FairFails(FakeJev):
    """A Jev whose fair requests of step 1 fail. Each other request answers as FakeJev does."""
    def ask(self, state, questions):
        if any("sides" in line for line in state.get("offers", {}).values()):
            raise JevError("timeout")
        return super().ask(state, questions)


def test_a_failed_fair_request_drops_no_offer(snap):
    found = search(ASKER, PARTNER, snap, _FairFails())
    assert found.offers and found.unfair == [] and found.fair_means == {}
    assert found.shortlist


def test_the_estimate_of_a_request_is_at_least_the_count_of_typesafe():
    # Three fair requests of Bo Girds and one partner on the live week 11 rosters, sent to TypeSafe on 2026-11-20: the
    # characters of each request, and the input tokens that TypeSafe counted for it. A request over 64k real tokens
    # fails with max_tokens_exceeded, so the split needs an estimate that never falls under the real count.
    for chars, counted in ((33_992, 14_609), (66_927, 28_297), (100_567, 42_321)):
        # The state "{}" and the quotes of the instructions are 4 characters.
        request = WaveRequest({}, {"q": NoulQuestion("x" * (chars - 4), "", "")})
        assert estimated_tokens(request) >= counted, (chars, estimated_tokens(request), counted)
        # A guess far over the count splits the requests smaller than they need to be, so each step sends more of them.
        assert estimated_tokens(request) <= counted * 1.05, (chars, estimated_tokens(request), counted)


def test_a_request_under_the_split_limit_is_one_that_typesafe_takes():
    # On 2026-11-20 TypeSafe took a fair request that it counted at 54,100 input tokens, and it refused the next larger
    # ones, about 54,600 and 56,500 tokens, with max_tokens_exceeded. Its own prompt fills the rest of the 64k context.
    # The estimate stays over the real count, so a request split under REQUEST_TOKENS is one that TypeSafe takes.
    assert REQUEST_TOKENS <= 54_100


def _tiny(n):
    return {str(i): WaveRequest({"n": i}, {"q": NoulQuestion("Is it?", "yes", "no")}) for i in range(n)}


def test_the_waves_keep_each_second_under_80_requests():
    waves = plan_waves(_tiny(200))
    assert [len(wave) for wave in waves] == [REQUESTS_PER_SECOND, REQUESTS_PER_SECOND, 40]


def test_the_waves_keep_each_second_under_100000_tokens():
    # About 30,000 characters of state is about 13,000 tokens by the high guess, so 7 fit in one second.
    big = {str(i): WaveRequest({"text": "x" * 30_000}, {}) for i in range(20)}
    waves = plan_waves(big)
    assert len(waves) == 3
    assert all(len(wave) <= 7 for wave in waves)


def test_a_full_wave_waits_until_the_last_second_has_room_for_its_requests():
    now = [0.0]
    slept = []

    def sleep(seconds):
        slept.append(seconds)
        now[0] += seconds

    jev = FakeJev()
    pacer = JevWaves(jev, pacer=Pacer(clock=lambda: now[0], sleep=sleep))
    answers = pacer.ask(_tiny(170), "test")
    assert len(answers) == 170 and all(answer is not None for answer in answers.values())
    assert len(jev.requests) == 170
    assert slept == [1.0, 1.0]
    # A second call shares the budget. The last second holds 10 requests, so one more goes at once.
    pacer.ask(_tiny(1), "test")
    assert slept == [1.0, 1.0]


def test_small_waves_of_one_press_go_one_after_the_other_with_no_wait():
    # A press sends about 11 requests per wave, far under the 80 per second, so the Spares tree and the shortlist never
    # wait for the rest of the second (decision 02).
    now = [0.0]
    slept = []
    pacer = JevWaves(FakeJev(), pacer=Pacer(clock=lambda: now[0], sleep=lambda seconds: slept.append(seconds)))
    for _ in range(3):
        pacer.ask(_tiny(11), "test")
    assert slept == []


class _FixedClock:
    """A clock that moves only when every press waits, so no press sends while the clock of another runs ahead.

    A sleep of a press notes its wake time. When no press is awake, the clock jumps to the soonest wake time and wakes
    each press that waits for it. A press that ends calls `done`, so it no longer holds the clock.
    """
    def __init__(self, presses):
        self.now = 0.0
        self._awake = presses
        self._wakes: list[float] = []
        self._turn = threading.Condition()

    def __call__(self):
        with self._turn:
            return self.now

    def sleep(self, seconds):
        with self._turn:
            wake = self.now + seconds
            self._wakes.append(wake)
            self._awake -= 1
            self._advance()
            while self.now < wake:
                self._turn.wait()

    def done(self):
        with self._turn:
            self._awake -= 1
            self._advance()

    def _advance(self):
        if self._awake == 0 and self._wakes:
            self.now = min(self._wakes)
            woken = [wake for wake in self._wakes if wake <= self.now]
            self._wakes = [wake for wake in self._wakes if wake > self.now]
            self._awake += len(woken)
            self._turn.notify_all()


class _TimedJev(FakeJev):
    """A FakeJev that keeps the clock time and the estimated tokens of each request as it goes out."""
    def __init__(self, clock):
        super().__init__()
        self.clock = clock
        self.sent: list[tuple[float, int]] = []

    def ask(self, state, questions):
        with self._lock:
            self.sent.append((self.clock(), estimated_tokens(WaveRequest(state, dict(questions)))))
        return super().ask(state, questions)


def test_each_press_uses_the_one_pacer_of_the_process():
    assert JevWaves(FakeJev()).pacer is PACER and JevWaves(FakeJev()).pacer is PACER


def test_two_presses_at_once_share_one_pacer_and_hold_100000_tokens_or_fewer_in_each_second():
    clock = _FixedClock(presses=2)
    # The process has one pacer. The test gives the two presses one pacer of its own, so a fixed clock runs it.
    shared = Pacer(clock=clock, sleep=clock.sleep)
    jev = _TimedJev(clock)
    # About 23,000 characters of state is about 10,000 tokens by the high guess, so 30 requests are about 300,000.
    press = {str(i): WaveRequest({"text": "x" * 23_000}, {}) for i in range(30)}
    assert 299_000 < sum(estimated_tokens(request) for request in press.values()) < 301_000
    # Each press makes its own JevWaves, as the API does for each Finder press.
    def run(label):
        try:
            return JevWaves(jev, pacer=shared).ask(press, label)
        finally:
            clock.done()

    with ThreadPoolExecutor(max_workers=2) as pool:
        presses = [pool.submit(run, label) for label in ("first", "second")]
        assert all(len(done.result()) == 30 for done in presses)
    assert len(jev.sent) == 60
    for start, _ in jev.sent:
        held = sum(tokens for at, tokens in jev.sent if start <= at < start + 1.0)
        assert held <= 100_000, (start, held)


def test_no_jev_request_of_a_press_sends_the_long_context_header(snap):
    # The real TypeSafe adapter sends each request of a press to a transport that keeps its headers and fails it. The
    # press goes on after each failure, so its Spares tree and its shortlist each send their requests.
    sent = []

    def keep(request):
        sent.append(request.headers)
        return httpx2.Response(503)

    client = TypeSafeClient(api_key="test-key", transport=httpx2.MockTransport(keep),
                            retry=RetryPolicy(max_retries=0))
    found = search(ASKER, None, snap, TypeSafeJev(client))
    assert found.shortlist and all(offer.failed for offer in found.shortlist)
    assert len(sent) > 11
    assert not any("TypeSafe-Danger-Zone-Long-Context" in headers for headers in sent)
