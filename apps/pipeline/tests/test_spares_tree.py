"""
Tests for the Spares tree: the code list of the players a team can spare, and the decision that Jev answers feed.
They read the week 6 snapshot and use FakeJev with fixed answers, so no test calls TypeSafe.
"""
import shutil

import pytest
from cpc import cpc_client
from fakes import FakeJev

from analyzer.spares_tree import spare_list, spares_tree
from analyzer.trade_jev import TRADE_POSITIONS, weak_slot_rows
from league.jev_port import JevError
from league.lineup import above_the_line, cannot_play_now
from league.ranks import OUT_STATUSES
from league.slow_sources import load_slow_sources
from league.snapshot import load_snapshot

CLIENT = cpc_client()


@pytest.fixture
def snap(fixture_raw_dir, fixture_history_root, chart_week6, fixture_nflverse_dir, tmp_path):
    cache = tmp_path / "nflverse"
    shutil.copytree(fixture_nflverse_dir, cache)
    slow = load_slow_sources(cache, 2026, 6, fixture_history_root)
    return load_snapshot(fixture_raw_dir, fixture_history_root, chart_week6, slow, client=CLIENT)


def _weak_positions(snap, roster_id):
    return {row["position"] or row["slot"].rstrip("0123456789") for row in weak_slot_rows(snap, roster_id)}


def _can_cover(snap, pid):
    return (above_the_line(snap, pid) and not cannot_play_now(snap, pid)
            and snap.players[pid].injury_status not in OUT_STATUSES)


def test_each_listed_player_fits_a_weak_slot_and_has_a_backup_above_the_line_who_can_play_now(snap):
    pairs = [(giver, receiver) for giver in snap.rosters for receiver in snap.rosters if giver != receiver]
    listed_pairs = 0
    for giver, receiver in pairs:
        spares = spare_list(snap, giver, receiver)
        listed_pairs += bool(spares)
        for spare in spares:
            position = snap.players[spare.player_id].position
            assert spare.player_id in snap.rosters[giver]
            assert position in _weak_positions(snap, receiver)
            backups = [pid for pid in snap.rosters[giver] if pid != spare.player_id
                       and snap.players[pid].position == position and _can_cover(snap, pid)]
            assert backups, (giver, receiver, snap.players[spare.player_id].name)
    # The literal reading of decision 12 lists a player for most pairs, so the Finder is not starved.
    assert listed_pairs > len(pairs) // 2


def _receiver_with_weak_rb(snap):
    return next(rid for rid in sorted(snap.rosters) if "RB" in _weak_positions(snap, rid))


def _two_free_rbs(snap, receiver):
    """Two healthy RBs above the line who are on no roster of the pair test, so the test roster can hold them."""
    owned = set(snap.rosters[receiver])
    rbs = sorted(pid for pid, player in snap.players.items()
                 if player.position == "RB" and pid not in owned and _can_cover(snap, pid))
    return rbs[0], rbs[1]


def _test_roster(snap, giver, receiver, out: str | None = None):
    """The giver roster with its RBs swapped for two healthy RBs above the line. `out` is listed Out with no return."""
    first, second = _two_free_rbs(snap, receiver)
    others = {rid: [pid for pid in roster if pid not in (first, second)] for rid, roster in snap.rosters.items()}
    others[giver] = [pid for pid in others[giver] if snap.players[pid].position != "RB"] + [first, second]
    players = dict(snap.players)
    if out is not None:
        players[out] = players[out].model_copy(update={"injury_status": "Out"})
    return snap.model_copy(update={"rosters": others, "players": players}), first, second


def test_a_starter_whose_only_backup_is_out_is_not_listed(snap):
    receiver = _receiver_with_weak_rb(snap)
    giver = next(rid for rid in sorted(snap.rosters) if rid != receiver)
    healthy, first, second = _test_roster(snap, giver, receiver)
    listed = {spare.player_id for spare in spare_list(healthy, giver, receiver)}
    # Each RB has the other as a backup above the line who can play now, so both are listed.
    assert {first, second} <= listed
    hurt, first, second = _test_roster(snap, giver, receiver, out=second)
    listed = {spare.player_id for spare in spare_list(hurt, giver, receiver)}
    # The only backup of the first RB is Out, so he is no cover, and no RB of the giver is listed.
    assert first not in listed and second not in listed
    assert not any(hurt.players[pid].position == "RB" for pid in listed)


def _pair_with_spares_on_both_sides(snap):
    return next((asker, partner) for asker in sorted(snap.rosters) for partner in sorted(snap.rosters)
                if asker != partner and spare_list(snap, partner, asker) and spare_list(snap, asker, partner))


def _answer_side(giver, p):
    """Fixed Jev answers: `p` for each player that `giver` lists, a clear yes for each other player."""
    def answer(key, question, state):
        return p if key.startswith(f"spare:{giver}:") else 0.9
    return answer


def test_a_clear_no_for_each_listed_player_stops_the_side(snap):
    asker, partner = _pair_with_spares_on_both_sides(snap)
    read = spares_tree(snap, asker, partner, FakeJev(answer=_answer_side(partner, 0.2)))
    assert read.stopped == ["partner"] and not read.passed


def test_an_unsure_answer_passes(snap):
    asker, partner = _pair_with_spares_on_both_sides(snap)
    read = spares_tree(snap, asker, partner, FakeJev(answer=_answer_side(partner, 0.5)))
    assert read.stopped == [] and read.passed


def test_one_unsure_answer_among_clear_noes_passes_the_side(snap):
    asker, partner = _pair_with_spares_on_both_sides(snap)
    first = spare_list(snap, asker, partner)[0].player_id

    def answer(key, question, state):
        # The first player of the asker reads unsure, each other player of the asker a clear no.
        if key.startswith(f"spare:{asker}:"):
            return 0.5 if key == f"spare:{asker}:{first}" else 0.2
        return 0.9

    read = spares_tree(snap, asker, partner, FakeJev(answer=answer))
    assert read.stopped == [] and read.passed


def test_a_failed_jev_call_is_an_error_and_never_a_stop(snap):
    asker, partner = _pair_with_spares_on_both_sides(snap)
    with pytest.raises(JevError):
        spares_tree(snap, asker, partner, FakeJev(error=JevError("429 Too Many Requests")))


def test_a_side_that_lists_no_player_stops_with_no_question_for_it(snap):
    receiver = _receiver_with_weak_rb(snap)
    giver = next(rid for rid in sorted(snap.rosters) if rid != receiver)
    # The giver keeps only one RB and no other trade position, so he can spare no one.
    healthy, first, _ = _test_roster(snap, giver, receiver)
    rosters = {**healthy.rosters, giver: [first]}
    lone = healthy.model_copy(update={"rosters": rosters})
    assert spare_list(lone, giver, receiver) == []
    jev = FakeJev()
    read = spares_tree(lone, receiver, giver, jev)
    assert "partner" in read.stopped and not read.passed
    assert not any(key.startswith(f"spare:{giver}:") for r in jev.requests for key in r.questions)


def test_each_question_names_the_weak_starter_and_the_state_holds_the_chart_values(snap):
    asker, partner = _pair_with_spares_on_both_sides(snap)
    jev = FakeJev()
    spares_tree(snap, asker, partner, jev)
    [request] = jev.requests
    team = snap.teams[asker].name
    spare = spare_list(snap, partner, asker)[0]
    question = request.questions[f"spare:{partner}:{spare.player_id}"]
    assert question.instructions.startswith(f"Would {snap.players[spare.player_id].name} (")
    assert question.instructions.endswith(f" of {team} for the rest of the season?")
    assert spare.starter in question.instructions
    value = snap.chart.values.get(spare.player_id)
    chart_lines = request.state["chart"]
    assert any(snap.players[spare.player_id].name in line and (value is None or str(value) in line)
               for line in chart_lines)
    assert set(TRADE_POSITIONS) >= {snap.players[s.player_id].position for s in spare_list(snap, partner, asker)}
