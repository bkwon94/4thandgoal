"""
Tests for the roster grade and the slot ranks of the managers file.
They feed the score known parts, and they read the grade of each entry on the fixture snapshot of week 6.
The grade reads the projections ahead, so some tests build projections that put a player above or below the line.
Other tests change the saved points or the chart values of one roster and read its parts against the league.
"""
from datetime import date

import pytest
from cpc import cpc_client

from league.history import load_history
from league.models import ChartValues, History, PastWeek
from league.parse import parse_week
from league.provider.sleeper import load_raw
from league.season_inputs import SeasonInputs
from league.snapshot import week_snapshot
from managers.entries import managers
from managers.grade import (
    GradeParts,
    SlotRank,
    _league_reads,
    depth_word,
    grade_letter,
    grade_read,
    grade_score,
    position_ranks,
    projected_values,
    roster_grades,
    roster_parts,
    season_points_per_game,
)
from managers.tunables import GRADE_WEIGHTS

CLIENT = cpc_client()


def _ahead(raw):
    return {entry.week: entry.projections for entry in raw.projections_ahead or []}


def _entries(raw_dir, root, with_snapshot=True):
    raw = load_raw(raw_dir)
    snapshot = week_snapshot(raw, root, 6, client=CLIENT) if with_snapshot else None
    inputs = SeasonInputs(history=load_history(root, raw, week=6), snapshot=snapshot, projections_ahead=_ahead(raw))
    return managers(inputs, parse_week(raw).teams)


def _snapshot(raw_dir, root):
    return week_snapshot(load_raw(raw_dir), root, 6, client=CLIENT)


def _depth(grade, position):
    return next(slot.depth for slot in grade.slots if slot.position == position)


def _history(raw_dir, root):
    return load_history(root, load_raw(raw_dir), week=6)


def _past(week, points, positions):
    return PastWeek(week=week, scores={}, pairs=[], points=points, projections={}, stats={}, moves=[],
                    positions=positions)


def _roster_ahead(snapshot, roster_id, points=10.0):
    """Projections ahead for the players of one roster only, so each of them ranks inside a small pool."""
    return {week: {pid: points for pid in snapshot.rosters[roster_id]} for week in (7, 8)}


@pytest.mark.parametrize("score, letter", [
    (100, "A"), (70, "A"), (69.99, "B"), (55, "B"), (54.99, "C"), (40, "C"),
    (39.99, "D"), (0, "D"),
])
def test_each_band_at_its_edge(score, letter):
    assert grade_letter(score) == letter


def test_the_score_is_the_weighted_sum_of_the_parts():
    assert grade_score(GradeParts(projection=1, production=1, trade_value=1, depth=1)) == 100
    assert grade_score(GradeParts(projection=0, production=0, trade_value=0, depth=0)) == 0
    assert grade_score(GradeParts(projection=1, production=0, trade_value=0, depth=0)) == GRADE_WEIGHTS["projection"]
    assert grade_score(GradeParts(projection=0, production=0.5, trade_value=0, depth=0)) == (
        GRADE_WEIGHTS["production"] / 2)
    assert grade_score(GradeParts(projection=0, production=0, trade_value=1, depth=0)) == GRADE_WEIGHTS["trade_value"]
    assert grade_score(GradeParts(projection=0, production=0, trade_value=0, depth=1)) == GRADE_WEIGHTS["depth"]


def test_the_score_reads_the_weights_45_30_10_15():
    assert grade_score(GradeParts(projection=1, production=0, trade_value=0, depth=0)) == 45
    assert grade_score(GradeParts(projection=0, production=1, trade_value=0, depth=0)) == 30
    assert grade_score(GradeParts(projection=0, production=0, trade_value=1, depth=0)) == 10
    assert grade_score(GradeParts(projection=0, production=0, trade_value=0, depth=1)) == 15
    assert grade_score(GradeParts(projection=0.5, production=0.5, trade_value=0.5, depth=0.5)) == 50


@pytest.mark.parametrize("parts, letter", [
    # Every part in full gives 100, an A. There is no A+: a report card tops out at A.
    (GradeParts(projection=1, production=1, trade_value=1, depth=1), "A"),
    # Projection, trade value, and depth in full give 70, the edge of A.
    (GradeParts(projection=1, production=0, trade_value=1, depth=1), "A"),
    # Projection and trade value in full give 55, the edge of B.
    (GradeParts(projection=1, production=0, trade_value=1, depth=0), "B"),
    # Production, trade value, and depth in full give 55. Projection at 0 still reaches B.
    (GradeParts(projection=0, production=1, trade_value=1, depth=1), "B"),
    # Production and trade value in full give 40, the edge of C.
    (GradeParts(projection=0, production=1, trade_value=1, depth=0), "C"),
    # Production in full gives 30. Trade value a hair under full gives 39.99, under the edge of C.
    (GradeParts(projection=0, production=1, trade_value=0.999, depth=0), "D"),
])
def test_a_score_at_a_band_edge_from_known_parts_reads_that_band(parts, letter):
    assert grade_letter(grade_score(parts)) == letter


@pytest.mark.parametrize("spares, hole, word", [
    (2, False, "stacked"),
    (3, False, "stacked"),
    (1, False, "deep"),
    (0, False, "fine"),
    (0, True, "thin"),
    # A hole wins over depth: a slot no one above the line fills reads thin.
    (2, True, "thin"),
])
def test_each_depth_word(spares, hole, word):
    assert depth_word(spares, hole) == word


def test_each_entry_carries_the_letter_and_the_slot_ranks_in_order(fixture_raw_dir, fixture_history_root):
    entries = _entries(fixture_raw_dir, fixture_history_root)
    for entry in entries:
        assert entry.grade.letter in {"A", "B", "C", "D"}
        assert [slot.position for slot in entry.grade.slots] == ["QB", "RB", "WR", "TE"]
        assert all(slot.depth in {"deep", "fine", "thin"} for slot in entry.grade.slots)


def test_the_slot_ranks_place_each_team_once_per_position(fixture_raw_dir, fixture_history_root):
    entries = _entries(fixture_raw_dir, fixture_history_root)
    for index, position in enumerate(["QB", "RB", "WR", "TE"]):
        ranks = sorted(entry.grade.slots[index].rank for entry in entries)
        assert ranks == list(range(1, 13)), position


def test_the_file_carries_the_letter_and_never_the_score(fixture_raw_dir, fixture_history_root):
    entry = _entries(fixture_raw_dir, fixture_history_root)[0]
    grade = entry.model_dump(mode="json")["grade"]
    assert set(grade) == {"letter", "slots", "parts", "read"}
    assert set(grade["slots"][0]) == {"position", "rank", "depth"}
    assert set(grade["parts"][0]) == {"key", "rank"}


def test_each_entry_carries_the_part_ranks_in_the_order_of_the_weights(fixture_raw_dir, fixture_history_root):
    for entry in _entries(fixture_raw_dir, fixture_history_root):
        assert [part.key for part in entry.grade.parts] == list(GRADE_WEIGHTS)
        assert list(GRADE_WEIGHTS) == ["projection", "production", "trade_value", "depth"]


def test_the_part_ranks_place_each_roster_once_per_part(fixture_raw_dir, fixture_history_root):
    entries = _entries(fixture_raw_dir, fixture_history_root)
    for index, key in enumerate(GRADE_WEIGHTS):
        ranks = sorted(entry.grade.parts[index].rank for entry in entries)
        assert ranks == list(range(1, 13)), key


def test_a_roster_that_leads_a_part_ranks_1_on_it(fixture_raw_dir, fixture_history_root):
    snapshot = _snapshot(fixture_raw_dir, fixture_history_root)
    ahead, history = _ahead(load_raw(fixture_raw_dir)), _history(fixture_raw_dir, fixture_history_root)
    # Roster 5 alone has chart value, so it leads the trade value part.
    chart = ChartValues(week=6, date=date(2026, 10, 14), values={pid: 50.0 for pid in snapshot.rosters[5]})
    inputs = SeasonInputs(snapshot=snapshot, projections_ahead=ahead, history=history, chart=chart)
    grades = roster_grades(inputs)
    parts = roster_parts(inputs)
    assert {part.key: part.rank for part in grades[5].parts}["trade_value"] == 1
    for key in GRADE_WEIGHTS:
        leader = max(parts, key=lambda rid: (getattr(parts[rid], key), -rid))
        assert {part.key: part.rank for part in grades[leader].parts}[key] == 1, key


def test_the_grade_is_null_without_a_snapshot(fixture_raw_dir, fixture_history_root):
    entries = _entries(fixture_raw_dir, fixture_history_root, with_snapshot=False)
    assert all(entry.grade is None for entry in entries)
    assert entries[0].model_dump(mode="json")["grade"] is None


def test_the_value_is_the_mean_over_the_weeks_ahead_with_a_missing_week_as_0():
    values = projected_values({7: {"a": 10.0, "b": 4.0}, 8: {"a": 20.0}}, CLIENT)
    assert values == {"a": 15.0, "b": 2.0}


def test_the_value_stops_at_the_last_regular_week():
    last = CLIENT.settings.last_regular_week
    ahead = {last - 1: {"a": 10.0}, last: {"a": 20.0}, last + 1: {"a": 90.0}}
    assert projected_values(ahead, CLIENT) == {"a": 15.0}


def test_a_player_with_a_cold_month_and_a_high_projection_ahead_ranks_high(fixture_raw_dir, fixture_history_root):
    snapshot = _snapshot(fixture_raw_dir, fixture_history_root)
    rostered = [pid for roster in snapshot.rosters.values() for pid in roster if snapshot.players[pid].position == "WR"]
    # The coldest wide receiver on a roster by the analyzer's points per game over the last weeks.
    cold = min(rostered, key=lambda pid: (snapshot.lineup_value(pid), pid))
    ahead = _ahead(load_raw(fixture_raw_dir))
    ahead = {week: {**projections, cold: 99.0} for week, projections in ahead.items()}
    positions = {pid: player.position for pid, player in snapshot.players.items()}
    assert position_ranks(projected_values(ahead, CLIENT), positions)[cold] == 1


def test_a_player_with_no_projection_ahead_has_no_rank():
    ranks = position_ranks(projected_values({7: {"a": 10.0}}, CLIENT), {"a": "QB", "b": "QB"})
    assert ranks == {"a": 1}


def test_a_starter_out_with_a_projection_ahead_is_no_hole(fixture_raw_dir, fixture_history_root):
    snapshot = _snapshot(fixture_raw_dir, fixture_history_root)
    # Roster 1 starts 10229 at WR with the status Out and no return week on file.
    assert snapshot.players["10229"].injury_status == "Out"
    history = _history(fixture_raw_dir, fixture_history_root)
    inputs = SeasonInputs(snapshot=snapshot, projections_ahead=_roster_ahead(snapshot, 1), history=history)
    grade = roster_grades(inputs)[1]
    assert _depth(grade, "WR") != "thin"
    assert all(slot.depth != "thin" for slot in grade.slots)


def test_a_starter_with_no_projection_ahead_is_a_hole(fixture_raw_dir, fixture_history_root):
    snapshot = _snapshot(fixture_raw_dir, fixture_history_root)
    ahead = _roster_ahead(snapshot, 1)
    # 8183 is the only QB of roster 1, so with no projection his slot is a hole.
    for projections in ahead.values():
        del projections["8183"]
    history = _history(fixture_raw_dir, fixture_history_root)
    inputs = SeasonInputs(snapshot=snapshot, projections_ahead=ahead, history=history)
    assert _depth(roster_grades(inputs)[1], "QB") == "thin"


def test_the_grade_is_null_without_projections_ahead(fixture_raw_dir, fixture_history_root):
    raw = load_raw(fixture_raw_dir)
    inputs = SeasonInputs(history=load_history(fixture_history_root, raw, week=6),
                          snapshot=week_snapshot(raw, fixture_history_root, 6, client=CLIENT))
    entries = managers(inputs, parse_week(raw).teams)
    assert all(entry.grade is None for entry in entries)


def test_the_season_points_per_game_count_the_weeks_with_a_stat_line():
    history = History(week=3, weeks={
        1: _past(1, {"a": 10.0, "b": 30.0}, {"a": "WR"}),
        2: _past(2, {"a": 20.0}, {"a": "WR"}),
        # A stat line with no points counts 0 in the sum and one week in the count.
        3: _past(3, {}, {"a": "WR"}),
    })
    assert season_points_per_game(history) == {"a": 10.0}


def test_a_player_with_no_stat_line_counts_0_points_per_game(fixture_raw_dir, fixture_history_root):
    history = _history(fixture_raw_dir, fixture_history_root)
    # b has points on a roster but no stat line in any week, so he has no points per game.
    history.weeks[1].points["b"] = 30.0
    assert "b" not in season_points_per_game(history)


def test_a_roster_that_scored_a_lot_but_projects_low_ranks_higher(fixture_raw_dir, fixture_history_root):
    snapshot = _snapshot(fixture_raw_dir, fixture_history_root)
    ahead = _ahead(load_raw(fixture_raw_dir))
    # Roster 1 projects low: each of its players projects 0.1 a week.
    ahead = {week: {**projections, **{pid: 0.1 for pid in snapshot.rosters[1]}} for week, projections in ahead.items()}
    before = roster_parts(SeasonInputs(snapshot=snapshot, projections_ahead=ahead,
                                       history=_history(fixture_raw_dir, fixture_history_root)))[1]
    history = _history(fixture_raw_dir, fixture_history_root)
    for past in history.weeks.values():
        for pid in snapshot.rosters[1]:
            past.points[pid] = 60.0
            past.positions[pid] = snapshot.players[pid].position
    after = roster_parts(SeasonInputs(snapshot=snapshot, projections_ahead=ahead, history=history))[1]
    assert after.production == 1.0
    assert after.projection == before.projection
    assert grade_score(after) > grade_score(before)


def test_a_roster_with_high_chart_values_ranks_higher(fixture_raw_dir, fixture_history_root):
    snapshot = _snapshot(fixture_raw_dir, fixture_history_root)
    ahead, history = _ahead(load_raw(fixture_raw_dir)), _history(fixture_raw_dir, fixture_history_root)
    chart = ChartValues(week=6, date=date(2026, 10, 14), values={pid: 50.0 for pid in snapshot.rosters[1]})
    before = roster_parts(SeasonInputs(snapshot=snapshot, projections_ahead=ahead, history=history))
    after = roster_parts(SeasonInputs(snapshot=snapshot, projections_ahead=ahead, history=history, chart=chart))
    assert after[1].trade_value == 1.0
    assert all(after[rid].trade_value == 0.0 for rid in after if rid != 1)
    assert grade_score(after[1]) > grade_score(before[1])


def _reads(raw_dir, root):
    snapshot = _snapshot(raw_dir, root)
    return _league_reads(SeasonInputs(snapshot=snapshot, projections_ahead=_ahead(load_raw(raw_dir)),
                                      history=_history(raw_dir, root)))


def test_the_depth_part_puts_the_lowest_depth_total_at_0_and_the_highest_at_1(fixture_raw_dir, fixture_history_root):
    reads = _reads(fixture_raw_dir, fixture_history_root)
    totals = {rid: read.depth_total() for rid, read, _ in reads}
    # The fixture rosters differ in depth, so the league read has a low end and a high end.
    assert min(totals.values()) < max(totals.values())
    depth = {rid: read.parts(league).depth for rid, read, league in reads}
    assert all(depth[rid] == 0.0 for rid in totals if totals[rid] == min(totals.values()))
    assert all(depth[rid] == 1.0 for rid in totals if totals[rid] == max(totals.values()))


def test_the_places_read_puts_the_lowest_places_total_at_0_and_the_highest_at_1(fixture_raw_dir,
                                                                                fixture_history_root):
    reads = _reads(fixture_raw_dir, fixture_history_root)
    totals = {rid: read.places_total() for rid, read, _ in reads}
    assert min(totals.values()) < max(totals.values())
    places = {rid: league.places for rid, _, league in reads}
    assert all(places[rid] == 0.0 for rid in totals if totals[rid] == min(totals.values()))
    assert all(places[rid] == 1.0 for rid in totals if totals[rid] == max(totals.values()))


def test_no_chart_gives_0_for_the_trade_value_part(fixture_raw_dir, fixture_history_root):
    snapshot = _snapshot(fixture_raw_dir, fixture_history_root)
    parts = roster_parts(SeasonInputs(snapshot=snapshot, projections_ahead=_ahead(load_raw(fixture_raw_dir)),
                                      history=_history(fixture_raw_dir, fixture_history_root)))
    assert all(part.trade_value == 0.0 for part in parts.values())


def _slot(position, rank, depth="fine"):
    return SlotRank(position=position, rank=rank, depth=depth)


@pytest.mark.parametrize("slots, read", [
    ([_slot("QB", 11), _slot("RB", 3), _slot("WR", 11), _slot("TE", 2)], "Strong at RB and TE. Soft at QB and WR."),
    ([_slot("QB", 1, "deep"), _slot("RB", 2), _slot("WR", 3), _slot("TE", 6)], "Strong at QB, RB, and WR. Deep at QB."),
    # A thin position is a hole, so it reads thin and never soft too.
    ([_slot("QB", 5), _slot("RB", 6), _slot("WR", 12, "thin"), _slot("TE", 7)], "Thin at WR."),
    # One star cannot make a position with a hole strong, so a thin position never reads strong either.
    ([_slot("QB", 5), _slot("RB", 6), _slot("WR", 3, "thin"), _slot("TE", 7)], "Thin at WR."),
    ([_slot("QB", 5), _slot("RB", 6, "stacked"), _slot("WR", 4), _slot("TE", 7)], "Deep at RB."),
    ([_slot("QB", 5), _slot("RB", 6), _slot("WR", 4), _slot("TE", 7)], "Middle of the league at every position."),
])
def test_the_grade_read_names_the_strong_deep_soft_and_thin_positions(slots, read):
    assert grade_read(slots, client=CLIENT) == read
