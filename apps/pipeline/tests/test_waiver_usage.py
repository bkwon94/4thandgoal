"""
Tests for the usage and environment scores of the waiver board.
They feed hand-set usage and team counts at the engine seam and read the buckets and the facts.
"""
import re
from datetime import datetime
from zoneinfo import ZoneInfo

from cpc import cpc_client

from cornerstone.models import NflverseWeek, TeamWeek, UsageWeek
from cornerstone.provider.sleeper import load_raw
from cornerstone.waiver import waiver_board

CLIENT = cpc_client()

BUILT = datetime(2026, 10, 20, 21, 0, tzinfo=ZoneInfo("America/New_York"))


def _player(position, team="KC", name="Free Agent"):
    return {"position": position, "team": team, "status": "Active", "active": True, "full_name": name}


def _raw(fixture_raw_dir, players, per_week):
    """The week 6 raw with `players` added and a flat projection per week, weeks 7 to 17, for each ID in `per_week`."""
    raw = load_raw(fixture_raw_dir)
    raw.players = {**raw.players, **players}
    raw.projections_ahead = [{"week": w, "projections": dict(per_week)} for w in range(7, 18)]
    return raw


def _usage(week, snap_share, targets=0, carries=0, team="KC"):
    """One usage week. The target share and the carry share are four times the count, as on a team of 25 each."""
    return UsageWeek(week=week, team=team, snaps=snap_share, snap_share=snap_share, targets=targets,
                     target_share=4 * targets, carries=carries, carry_share=4 * carries, red_zone_touches=0)


def _team(plays=60, neutral_passes=30, rush_successes=10):
    """One game of a team with 40 neutral plays and 25 rushes."""
    return [TeamWeek(week=6, plays=plays, passes=plays - 25, rushes=25, rush_successes=rush_successes,
                     neutral_plays=40, neutral_passes=neutral_passes)]


def _nfl(usage, environment=None):
    return NflverseWeek(sources={}, gsis={}, drops=None, injuries=None, usage=usage,
                        environment=environment or {"KC": _team()})


def _best_adds(raw, nfl):
    return waiver_board(raw, 6, BUILT, nfl, client=CLIENT).buckets["best_adds"]


def test_a_rising_snap_share_outranks_a_higher_projection_with_flat_usage(fixture_raw_dir):
    players = {"80001": _player("WR", name="Riser"), "80002": _player("WR", name="Steady")}
    raw = _raw(fixture_raw_dir, players, {"80001": 5.0, "80002": 10.0})
    nfl = _nfl({"80001": [_usage(5, 48, targets=2), _usage(6, 71, targets=5)],
                "80002": [_usage(5, 70, targets=6), _usage(6, 70, targets=6)]})
    assert [p.player_id for p in _best_adds(raw, nfl)] == ["80001", "80002"]


def test_the_environment_ranks_passers_by_pace_and_neutral_passes_and_backs_by_rush_success(fixture_raw_dir):
    # FAST runs the most plays and passes the most. GRND runs fewer plays and wins the most runs.
    # SLOW runs the fewest plays. Every player has the same projection and no usage.
    environment = {"FAST": _team(plays=70, neutral_passes=26, rush_successes=8),
                   "GRND": _team(plays=65, neutral_passes=18, rush_successes=14),
                   "SLOW": _team(plays=60, neutral_passes=22, rush_successes=11)}
    players = {"80001": _player("WR", team="GRND"), "80002": _player("WR", team="FAST"),
               "80003": _player("RB", team="FAST"), "80004": _player("RB", team="GRND")}
    raw = _raw(fixture_raw_dir, players, {pid: 8.0 for pid in players})
    best = [p.player_id for p in _best_adds(raw, _nfl({}, environment))]
    assert best.index("80002") < best.index("80001")
    assert best.index("80004") < best.index("80003")


def test_a_player_carries_a_usage_fact_and_an_environment_fact_with_their_numbers(fixture_raw_dir):
    players = {"80001": _player("WR", name="Riser Guy"), "80002": _player("RB", name="Back Guy")}
    raw = _raw(fixture_raw_dir, players, {"80001": 5.0, "80002": 5.0})
    environment = {"KC": _team(plays=70, neutral_passes=26, rush_successes=11), "BUF": _team(plays=72)}
    nfl = _nfl({"80001": [_usage(5, 48, targets=2), _usage(6, 71, targets=5)],
                "80002": [_usage(5, 60, carries=12), _usage(6, 55, carries=9)]}, environment)
    facts = {p.player_id: [f.text for f in p.facts] for p in _best_adds(raw, nfl)}
    assert facts["80001"] == [
        "Riser Guy played 71% of snaps and took 5 targets last week, up from 48% and 2.",
        "KC runs the 2nd fastest offense and passes on 65% of neutral downs."]
    assert facts["80002"] == [
        "Back Guy played 55% of snaps and took 9 carries last week, down from 60% and 12.",
        "KC runs the 2nd fastest offense and succeeds on 44% of runs."]


def test_every_digit_of_a_fact_is_in_its_numbers(fixture_raw_dir):
    players = {f"8000{i}": _player(pos) for i, pos in enumerate(("QB", "RB", "WR", "TE"), start=1)}
    raw = _raw(fixture_raw_dir, players, {pid: 5.0 for pid in players})
    nfl = _nfl({pid: [_usage(5, 40, targets=3, carries=4), _usage(6, 40, targets=3, carries=4)] for pid in players})
    best = _best_adds(raw, nfl)
    assert len(best) == 4 and all(len(p.facts) == 2 for p in best)
    for fact in (f for p in best for f in p.facts):
        assert set(re.findall(r"\d+", fact.text)) <= set(fact.numbers), fact.text


def test_a_player_with_no_usage_rows_scores_0_and_has_no_usage_fact(fixture_raw_dir):
    # A rookie in week 1 or a player on a bye has no row for one of the two weeks.
    players = {"80001": _player("WR"), "80002": _player("WR"), "80003": _player("WR")}
    raw = _raw(fixture_raw_dir, players, {pid: 5.0 for pid in players})
    best = {p.player_id: p for p in _best_adds(raw, _nfl({"80002": [_usage(6, 71, targets=5)]}))}
    for pid in players:
        assert best[pid].scores.usage == 0
        assert [f.id for f in best[pid].facts] == [f"W.env.{pid}"]
    assert _best_adds(raw, None)[0].facts == []


def test_the_usage_score_reads_the_last_2_of_the_4_saved_weeks(fixture_raw_dir):
    # The snap share falls from week 3 to week 6, but it rises from week 5 to week 6.
    raw = _raw(fixture_raw_dir, {"80001": _player("WR", name="Riser Guy")}, {"80001": 5.0})
    rows = [_usage(3, 90, targets=6), _usage(4, 80, targets=6), _usage(5, 40, targets=2), _usage(6, 60, targets=4)]
    player = _best_adds(raw, _nfl({"80001": rows}))[0]
    assert player.scores.usage == 1.0
    assert player.facts[0].text == "Riser Guy played 60% of snaps and took 4 targets last week, up from 40% and 2."
