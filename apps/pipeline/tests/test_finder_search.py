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
    in_band,
    in_pool,
    offer_id,
    search,
    shortlist_answers,
    varied,
)
from analyzer.jev_waves import (
    PACER,
    REQUEST_TOKENS,
    REQUESTS_PER_SECOND,
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
    _, lines = _shortlist_merged(jev)
    # The shortlist reads every Value offer but the one that dropped.
    assert len(lines) == len(found.offers) - 1
    assert {offer.offer_id for offer in found.shortlist + found.dropped} <= {offer_id(t) for t in found.offers[1:]}


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


def _best_ids(shortlist):
    """The ids of the best offers: for each player of the asker and for each partner, the offer with the highest score.
    A tie goes to the lower offer id."""
    best: dict[tuple[str, object], ShortlistOffer] = {}
    for offer in sorted(shortlist, key=lambda offer: (-offer.score, offer.offer_id)):
        keys = [("player", pid) for pid in offer.trade.sides[0].player_ids]
        keys += [("partner", side.roster_id) for side in offer.trade.sides[1:]]
        for key in keys:
            best.setdefault(key, offer)
    return {offer.offer_id for offer in best.values()}


def _assert_varied(found):
    """AT-43: the best offer of each player of the asker and the best offer of each partner come before a second form
    of any trade. The best offers come by score, and so do the other offers.

    The best offers lead the list, so a list with any other offer holds every best offer, and the best of the list is
    the best of the search."""
    best = _best_ids(found.shortlist)
    flags = [offer.offer_id in best for offer in found.shortlist]
    assert flags == sorted(flags, reverse=True), [offer.offer_id for offer in found.shortlist]
    for group in (found.shortlist[:sum(flags)], found.shortlist[sum(flags):]):
        scores = [offer.score for offer in group]
        assert scores == sorted(scores, reverse=True)


def _offer(gives: str, partner: int, gets: str, score: float) -> ShortlistOffer:
    trade = ProposedTrade(season=2026, asker=6, sides=[
        TradeSide(roster_id=6, gives=[GivenPlayer(player_id=gives, to=partner)]),
        TradeSide(roster_id=partner, gives=[GivenPlayer(player_id=gets, to=6)])])
    return ShortlistOffer(offer_id=offer_id(trade), trade=trade, fair=score, needs={6: 1.0, partner: 1.0},
                          score=score)


def test_the_best_offer_of_each_player_and_each_partner_comes_before_a_second_form():
    # The rated offers of press 3 of AT-41 (evidence/AT-43/shortlist.txt). Bo Girds is roster 6. McBride is 8130,
    # Flowers 9997, and Golden 12501. Partner 11 gives Prescott 3294 or Stroud 9758, partner 7 gives Mahomes 4046 or
    # Goff 3163, and partner 3 gives Williams 11560.
    offers = [_offer("8130", 11, "3294", 0.442), _offer("9997", 7, "4046", 0.256), _offer("12501", 11, "3294", 0.343),
              _offer("8130", 3, "11560", 0.130), _offer("12501", 11, "9758", 0.281), _offer("9997", 11, "3294", 0.265),
              _offer("8130", 11, "9758", 0.252), _offer("9997", 11, "9758", 0.208), _offer("9997", 7, "3163", 0.204),
              _offer("12501", 7, "4046", 0.181)]
    shortlist = varied(offers, SHORTLIST_KEEP)
    # The best of McBride, of Golden, and of partner 11, then the best of Flowers (0.265), of partner 7, and of
    # partner 3. Then the other forms by score.
    assert [offer.score for offer in shortlist] == [0.442, 0.343, 0.265, 0.256, 0.130,
                                                    0.281, 0.252, 0.208, 0.204, 0.181]


def test_a_list_with_more_best_offers_than_it_keeps_holds_only_best_offers_by_score():
    offers = [_offer(f"p{n}", 20 + n, f"g{n}", 0.1 + 0.01 * n) for n in range(12)]
    offers += [_offer("p11", 20, "g99", 0.9)]
    shortlist = varied(offers, SHORTLIST_KEEP)
    # 0.9 is the best of p11 and of partner 20, so it leads. The other 11 best offers fill the list by score.
    assert [offer.score for offer in shortlist] == pytest.approx([0.9] + [0.1 + 0.01 * n for n in range(11, 2, -1)])


def test_the_shortlist_holds_the_best_offer_for_each_player_of_the_asker_before_more_forms(snap):
    found = search(ASKER, PARTNER, snap, FakeJev(answer=_rising_fair))
    assert len(found.offers) > SHORTLIST_KEEP
    assert len(found.shortlist) == SHORTLIST_KEEP
    _assert_varied(found)
    givers = {pid for trade in found.offers for pid in trade.sides[0].player_ids}
    # The top offer by the product still leads, and each player the asker gives has an offer on the list.
    assert found.shortlist[0].offer_id == offer_id(found.offers[0])
    assert givers <= {pid for offer in found.shortlist for pid in offer.trade.sides[0].player_ids}
    top = found.shortlist[0]
    assert top.score == pytest.approx(top.fair * top.needs[ASKER] * top.needs[PARTNER])
    assert set(top.needs) == {ASKER, PARTNER}


def test_the_shortlist_holds_an_offer_for_each_partner_before_more_forms(snap):
    found = search(ASKER, None, snap, FakeJev(answer=_rising_fair))
    _assert_varied(found)
    partners = {trade.sides[1].roster_id for trade in found.offers}
    assert len(partners) >= 2
    # The search has more best offers than the list keeps, so the list holds only best offers, one per partner at most
    # unless an offer is also the best of a player.
    best = _best_ids([ShortlistOffer(offer_id=offer_id(trade), trade=trade, fair=0.0, needs={}, score=0.0)
                      for trade in found.offers])
    assert len(best) > SHORTLIST_KEEP
    assert len({offer.trade.sides[1].roster_id for offer in found.shortlist}) >= 5


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
    for n in range(len(found.offers)):
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


def test_the_gain_state_holds_the_lineup_points_of_each_side_before_and_after_each_offer(snap):
    jev = FakeJev()
    found = search(ASKER, PARTNER, snap, jev)
    _, offers = _shortlist_merged(jev)
    assert len(offers) == len(found.offers)
    for n, trade in enumerate(found.offers):
        lines = offers[str(n)]["lineup_points"]
        for rid in (ASKER, PARTNER):
            [line] = [line for line in lines if line.startswith(snap.teams[rid].name + " ")]
            before, after, change = (float(x) for x in re.findall(r"\d+\.\d", line))
            # The fact states the change in words, so Jev compares no numbers itself.
            assert abs(before - after) == pytest.approx(change, abs=0.11)
            word = "gains" if after > before else "loses" if after < before else "keeps"
            assert word in line, line


class _ShortlistFails(FakeJev):
    def ask(self, state, questions):
        if any("|" in key for key in questions):
            raise JevError("timeout")
        return super().ask(state, questions)


def test_a_failed_shortlist_request_keeps_its_offers_as_unsure_and_never_reads_as_a_no(snap, caplog):
    with caplog.at_level(logging.INFO, logger="analyzer.finder_search"):
        found = search(ASKER, PARTNER, snap, _ShortlistFails())
    assert found.offers and found.shortlist and found.dropped == []
    assert len(found.shortlist) == min(len(found.offers), SHORTLIST_KEEP)
    for offer in found.shortlist:
        assert offer.failed
        assert offer.fair == UNSURE and set(offer.needs.values()) == {UNSURE} and set(offer.gains.values()) == {UNSURE}
    assert any("Finder shortlist with" in line and "failed request" in line for line in caplog.messages)


def test_the_pick_sheet_of_an_offer_with_a_failed_shortlist_request_states_no_jev_answer(snap):
    failed = search(ASKER, PARTNER, snap, _ShortlistFails()).shortlist[0]
    sheet = offer_sheet(failed, snap, NewsFeed(fetch=no_news))
    # The call never answered, so the pick never reads "unsure" for it.
    assert sheet and not any(key.startswith(FACT_PREFIX) for key in sheet)
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
        assert nouls == {"fair": 0.8, f"need.{ASKER}": 0.8, f"need.{PARTNER}": 0.8,
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
    # About 26,000 characters of state is about 13,000 tokens by the high guess, so 7 fit in one second.
    big = {str(i): WaveRequest({"text": "x" * 26_000}, {}) for i in range(20)}
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
    # About 20,000 characters of state is about 10,000 tokens by the high guess, so 30 requests are about 300,000.
    press = {str(i): WaveRequest({"text": "x" * 20_000}, {}) for i in range(30)}
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
