"""
Tests for the Finder search: the partner filter (the Spares tree), the targets, the offers, and the shortlist that Jev narrows.
They read the week 6 snapshot and use FakeJev, so no test calls TypeSafe.
"""
import logging
import re
import shutil

import pytest
from cpc import cpc_client
from fakes import FakeJev, no_news

from analyzer.finder_pick import offer_sheet
from analyzer.finder_search import (
    SHORTLIST_KEEP,
    TARGET_MAX,
    UNSURE,
    WIDER_MAX,
    Anchor,
    Limit,
    ShortlistOffer,
    _out_with_no_return,
    in_pool,
    offer_id,
    search,
    varied,
)
from analyzer.jev_waves import REQUESTS_PER_SECOND, JevWaves, WaveRequest, plan_waves
from analyzer.measures import is_handcuff, trade_handcuffs
from analyzer.spares_tree import pair_spares
from analyzer.trade import GivenPlayer, ProposedTrade, TradeSide
from analyzer.trade_jev import FACT_PREFIX, TRADE_POSITIONS, weak_slot_rows
from analyzer.trade_news import NewsFeed
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


def _target_requests(jev):
    return [r for r in jev.requests if r.questions and all("." in key and "|" not in key for key in r.questions)]


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
    assert len(found.shortlist) >= 2 and not found.wider
    for trade in found.offers + [offer.trade for offer in found.shortlist]:
        assert [side.roster_id for side in trade.sides] == [ASKER, PARTNER]


def _both_sides(snap):
    """The other teams whose pair with the asker lists a player on each side, in roster order."""
    return [rid for rid in sorted(snap.rosters) if rid != ASKER
            and all(pair_spares(snap, ASKER, rid).values())]


def test_a_clear_no_for_each_player_of_one_side_stops_the_partner_and_unsure_passes(snap):
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
    assert unsure in found.targets
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


def test_the_target_step_logs_every_player_that_jev_is_asked_about_with_his_answer(snap, caplog):
    # A low answer for each target question, so no player is picked and the log still lists each one (AT-11).
    def answer(key, question, state):
        return 0.3 if "." in key and "|" not in key else 0.9

    jev = FakeJev(answer=answer)
    with caplog.at_level(logging.INFO, logger="analyzer.finder_search"):
        search(ASKER, PARTNER, snap, jev)
    asked = [key for r in _target_requests(jev) for key in r.questions]
    lines = [r.getMessage() for r in caplog.records if r.getMessage().startswith("Finder target questions")]
    assert asked and len(lines) == 1
    for key in asked:
        assert f"{snap.players[key.partition('.')[2]].name}=0.30" in lines[0]


def test_the_target_step_logs_the_players_of_a_failed_request_too(snap, caplog):
    def answer(key, question, state):
        # The target request fails, as a failed TypeSafe call does. The other requests answer yes.
        if "." in key and "|" not in key:
            raise JevError("429 Too Many Requests")
        return 0.9

    jev = FakeJev(answer=answer)
    with caplog.at_level(logging.INFO, logger="analyzer.finder_search"):
        search(ASKER, PARTNER, snap, jev)
    asked = [key for r in _target_requests(jev) for key in r.questions]
    lines = [r.getMessage() for r in caplog.records if r.getMessage().startswith("Finder target questions")]
    assert asked and len(lines) == 1 and "failed request" in lines[0]
    for key in asked:
        assert snap.players[key.partition(".")[2]].name in lines[0]


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
    # The best offer of each partner is a best offer, and the best offers of this search fit on the list.
    assert {offer.trade.sides[1].roster_id for offer in found.shortlist} == partners


def test_a_failed_jev_request_on_every_step_never_raises_and_never_hides_a_partner(snap):
    found = search(ASKER, None, snap, FakeJev(error=JevError("429 Too Many Requests")))
    # A failed call is an error, never a stop: each pair with a question is marked failed, and each goes on.
    assert all(read.passed for read in found.partners)
    assert all(read.failed for read in found.partners if any(pair_spares(snap, ASKER, read.roster_id).values()))
    # The targets fail too, so the wider pass builds the ideas, and the failed shortlist keeps them as unsure.
    assert found.wider and found.offers and found.shortlist
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


def test_a_failed_spares_tree_request_lets_the_partner_go_on_to_the_targets_and_logs(snap, caplog):
    failed = _partner_with_spares(snap)
    jev = _SparesTreeFails(failed)
    with caplog.at_level(logging.INFO, logger="analyzer.finder_search"):
        found = search(ASKER, None, snap, jev)
    read = next(read for read in found.partners if read.roster_id == failed)
    assert read.failed and read.passed
    assert failed in found.targets
    assert failed in [r.state["teams"]["partner"]["roster_id"] for r in _target_requests(jev)]
    assert any("Spares tree of" in line and snap.teams[failed].name in line and "failed request" in line
               for line in caplog.messages)


def _gain_of_first_offer(p: float, side: int):
    """A Jev that gives `p` to the gain Noul of `side` on offer 0. Each other question gets the answer of
    `_rising_fair`, so offer 0 leads the list when it stays."""
    def answer(key, question, state):
        return p if key == f"0|gain.{side}" else _rising_fair(key, question, state)
    return answer


def _shortlist_requests(jev):
    return [r for r in jev.requests if r.questions and all("|" in key for key in r.questions)]


def test_the_shortlist_asks_one_gain_noul_per_side_of_each_offer(snap):
    jev = FakeJev()
    found = search(ASKER, PARTNER, snap, jev)
    [request] = _shortlist_requests(jev)
    for n in range(len(found.offers)):
        for rid in (ASKER, PARTNER):
            question = request.questions[f"{n}|gain.{rid}"]
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
    [request] = _shortlist_requests(jev)
    offers = request.state["offers"]
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


def _last_pool_player(snap, roster_id):
    """The pool player of the roster with the last id in string order. A tie of the FakeJev answers breaks by the id, so
    he is never one of the top targets on his own."""
    return max(pid for pid in snap.rosters[roster_id] if in_pool(snap, pid, roster_id))


def test_an_anchor_that_the_asker_gives_is_in_each_offer_on_the_asker_side(snap):
    anchor = _last_pool_player(snap, ASKER)
    found = search(ASKER, None, snap, FakeJev(), anchor=Anchor(player_id=anchor, side="gives"))
    assert found.offers and found.shortlist
    for trade in found.offers + [offer.trade for offer in found.shortlist]:
        assert trade.sides[0].roster_id == ASKER and anchor in trade.sides[0].player_ids
        assert all(anchor not in side.player_ids for side in trade.sides[1:])
    # Each target list of the asker side stays at most TARGET_MAX, with the anchor in it.
    assert all(anchor in sides["asker"] and len(sides["asker"]) <= TARGET_MAX for sides in found.targets.values())


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
    assert sorted(found.targets) == others
    jev = FakeJev(answer=answer)
    found = search(ASKER, None, snap, jev)
    assert len(_filter_requests(jev)) == sum(any(pair_spares(snap, ASKER, rid).values()) for rid in others)
    # No partner passed, so no target question asks. The wider pass gives the ideas that the pick weighs.
    assert not any(read.passed for read in found.partners) and found.targets == {}
    assert _target_requests(jev) == [] and found.wider


def test_an_anchored_search_asks_if_each_player_coming_back_would_take_the_place_of_the_anchor(snap):
    anchor = _last_pool_player(snap, ASKER)
    name = snap.players[anchor].name
    jev = FakeJev()
    search(ASKER, PARTNER, snap, jev, anchor=Anchor(player_id=anchor, side="gives"))
    [request] = _target_requests(jev)
    for key, question in request.questions.items():
        owner = int(key.partition(".")[0])
        # A player of the partner would come to the asker, so his question names the anchor he would replace.
        assert (f"take the place of {name}" in question.instructions) == (owner == PARTNER), key
    # A gets anchor turns it around: each player of the asker would go to the partner in his place.
    other = _last_pool_player(snap, PARTNER)
    jev = FakeJev()
    search(ASKER, PARTNER, snap, jev, anchor=Anchor(player_id=other, side="gets"))
    [request] = _target_requests(jev)
    other_name = snap.players[other].name
    assert all((f"take the place of {other_name}" in q.instructions) == key.startswith(f"{ASKER}.")
               for key, q in request.questions.items())
    # The plain search keeps the plain target question.
    jev = FakeJev()
    search(ASKER, PARTNER, snap, jev)
    assert not any("take the place of" in q.instructions for r in _target_requests(jev) for q in r.questions.values())

def _no_target(key, question, state):
    """Each target question reads no, so the normal search builds no offer. Each other question reads yes."""
    return 0.3 if "." in key and "|" not in key else 0.9


def _weak_positions(snap, roster_id):
    """The positions of the weak slots of a roster: the position of the weak starter, or of the empty slot."""
    return {row["position"] or row["slot"].rstrip("0123456789") for row in weak_slot_rows(snap, roster_id)}


def test_a_search_with_no_offers_runs_one_wider_pass_with_no_more_jev_target_questions(snap):
    jev = FakeJev(answer=_no_target)
    found = search(ASKER, None, snap, jev)
    asked = len(_target_requests(jev))
    assert found.wider and found.offers and found.shortlist
    assert len(found.offers) <= WIDER_MAX
    # The wider pass asks no target question: the one target request of each partner is the normal one.
    assert asked == sum(read.passed for read in found.partners)
    need = _weak_positions(snap, ASKER) & set(TRADE_POSITIONS)
    assert need
    partners = [trade.sides[1].roster_id for trade in found.offers]
    # One 1-for-1 idea per partner at most, and each brings back a player at a weak slot of the asker.
    assert len(partners) == len(set(partners))
    for trade in found.offers:
        assert [len(side.player_ids) for side in trade.sides] == [1, 1]
        assert snap.players[trade.sides[1].player_ids[0]].position in need
        assert trade_handcuffs(trade, snap) == []
        for side in trade.sides:
            assert all(in_pool(snap, pid, side.roster_id) for pid in side.player_ids)


def test_a_search_with_offers_runs_no_wider_pass(snap):
    lines = []
    found = search(ASKER, None, snap, FakeJev(), stage=lambda line, live=False: lines.append((line, live)))
    assert found.offers and not found.wider
    assert not any("wider" in line for line, _ in lines)


def test_the_wider_pass_tells_the_manager_with_its_live_line_in_place_of_the_offers_line(snap):
    lines = []
    search(ASKER, None, snap, FakeJev(answer=_no_target), stage=lambda line, live=False: lines.append((line, live)))
    assert ("Found no players who fit", False) in lines
    wider = lines.index(("Looking wider for ideas", True))
    # The wider pass builds the offers, so the done line of the offers step ends it.
    assert lines[wider + 1][0].startswith("Built ") and lines[wider + 1][1] is False
    assert ("Building offers", True) not in lines


def test_the_wider_pass_of_an_anchor_that_the_asker_gives_holds_him_and_asks_for_his_position(snap):
    anchor = _last_pool_player(snap, ASKER)
    position = snap.players[anchor].position
    found = search(ASKER, None, snap, FakeJev(answer=_no_target), anchor=Anchor(player_id=anchor, side="gives"))
    assert found.wider and found.offers
    for trade in found.offers:
        assert trade.sides[0].player_ids == [anchor]
        assert snap.players[trade.sides[1].player_ids[0]].position == position


def test_the_wider_pass_of_an_anchor_that_the_asker_gets_holds_him(snap):
    anchor = _last_pool_player(snap, PARTNER)
    found = search(ASKER, None, snap, FakeJev(answer=_no_target), anchor=Anchor(player_id=anchor, side="gets"))
    assert found.wider and found.offers
    for trade in found.offers:
        assert [side.roster_id for side in trade.sides] == [ASKER, PARTNER]
        assert trade.sides[1].player_ids == [anchor]


def test_the_wider_pass_keeps_the_limit_of_the_manager(snap):
    kept = {snap.players[pid].position for pid in snap.rosters[ASKER] if in_pool(snap, pid, ASKER)} - {"QB"}
    limit = Limit(keep_positions=sorted(kept))
    found = search(ASKER, None, snap, FakeJev(answer=_no_target), limit=limit)
    assert found.wider and found.offers
    for trade in found.offers:
        assert all(snap.players[pid].position not in kept for pid in trade.sides[0].player_ids)


def test_the_wider_pass_keeps_a_partner_whose_spares_tree_request_failed(snap):
    # A failed request is never a no, so the wider pass weighs the partner as it weighs each other partner.
    failed = _partner_with_spares(snap)
    found = search(ASKER, None, snap, _SparesTreeFails(failed, answer=_no_target))
    assert next(read for read in found.partners if read.roster_id == failed).failed
    assert found.wider
    assert failed in {trade.sides[1].roster_id for trade in found.offers}


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


def test_a_full_wave_waits_until_the_last_second_has_room_for_its_requests():
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
    # A second call shares the budget. The last second holds 10 requests, so one more goes at once.
    pacer.ask(_tiny(1), "test")
    assert slept == [1.0, 1.0]


def test_small_waves_of_one_press_go_one_after_the_other_with_no_wait():
    # A press sends about 11 requests per wave, far under the 80 per second, so the targets and the shortlist never
    # wait for the rest of the second (decision 02).
    now = [0.0]
    slept = []
    pacer = JevWaves(FakeJev(), clock=lambda: now[0], sleep=lambda seconds: slept.append(seconds))
    for _ in range(3):
        pacer.ask(_tiny(11), "test")
    assert slept == []
