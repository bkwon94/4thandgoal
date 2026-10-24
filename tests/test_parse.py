"""
Tests for the parse of raw Sleeper data into domain models.
They use the recorded week 6 data.
"""
from datetime import date

from cornerstone.parse import parse_week
from cornerstone.sleeper import load_raw


def test_parse_week_teams_and_matchups(fixture_raw_dir):
    wk = parse_week(load_raw(fixture_raw_dir))
    assert wk.week == 6 and wk.last_scored_week == 6
    assert len(wk.teams) == 12 and len(wk.matchups) == 6
    bo = next(t for t in wk.teams.values() if t.name == "Bo Girds")
    assert bo.is_brian and (bo.wins, bo.losses) == (8, 4)
    assert bo.avatar_url.endswith(".jpg")
    lamb = next(t for t in wk.teams.values() if t.name == "behold the lamb")
    assert lamb.avatar_url.startswith("https://sleepercdn.com/avatars/thumbs/")


def test_parse_week_lines_have_projection(fixture_raw_dir):
    wk = parse_week(load_raw(fixture_raw_dir))
    m = next(m for m in wk.matchups if m.matchup_id == 4)
    shough = next(line for s in (m.a, m.b) for line in s.lines if line.name == "Tyler Shough")
    assert shough.started and shough.points == 26.96 and shough.projection == 17.06


def test_unknown_player_falls_back_to_id(fixture_raw_dir):
    raw = load_raw(fixture_raw_dir)
    raw["players"].pop("8183")  # Brock Purdy
    wk = parse_week(raw)
    lines = [line for m in wk.matchups for s in (m.a, m.b) for line in s.lines]
    purdy = next(line for line in lines if line.player_id == "8183")
    assert purdy.name == "8183" and purdy.position == "?"


def test_week_argument_overrides_display_week(fixture_raw_dir):
    raw = load_raw(fixture_raw_dir)
    assert parse_week(raw, week=5).week == 5


def test_defense_name_and_slot(fixture_raw_dir):
    wk = parse_week(load_raw(fixture_raw_dir))
    lines = [line for m in wk.matchups for s in (m.a, m.b) for line in s.lines]
    tb = next(line for line in lines if line.player_id == "TB")
    assert tb.name == "Tampa Bay Buccaneers" and tb.position == "DEF"
    assert tb.started and tb.slot == "DEF"
    bench = next(line for line in lines if not line.started)
    assert bench.slot is None
    assert all(line.season_avg is None for line in lines)


def test_moves_are_complete_only(fixture_raw_dir):
    raw = load_raw(fixture_raw_dir)
    wk = parse_week(raw)
    expected = sum(
        len(t["adds"]) for t in raw["transactions"]
        if t["status"] == "complete" and t["adds"]
    )
    assert expected > 0 and len(wk.moves) == expected
    assert {m.kind for m in wk.moves} <= {"waiver", "free_agent", "trade"}
    assert all(m.week == 6 for m in wk.moves)


def test_next_matchups_and_season_start(fixture_raw_dir):
    wk = parse_week(load_raw(fixture_raw_dir))
    assert len(wk.next_matchups) == 6
    assert all(a < b for a, b in wk.next_matchups)
    assert wk.season_start == date(2026, 9, 9)


def test_empty_starter_slot_makes_no_line(fixture_raw_dir):
    raw = load_raw(fixture_raw_dir)
    entry = raw["matchups"][0]
    entry["starters"][1] = "0"
    entry["players"].append("0")
    wk = parse_week(raw)
    lines = [line for m in wk.matchups for s in (m.a, m.b) for line in s.lines]
    assert not any(line.player_id == "0" or line.name == "0" for line in lines)
    third = next(line for line in lines if line.player_id == entry["starters"][2])
    assert third.slot == raw["league"]["roster_positions"][2]


def test_next_matchups_keep_pairs_only(fixture_raw_dir):
    raw = load_raw(fixture_raw_dir)
    raw["matchups_next"] = [
        {"matchup_id": 1, "roster_id": 1},
        {"matchup_id": 1, "roster_id": 2},
        {"matchup_id": 2, "roster_id": 3},
        {"matchup_id": None, "roster_id": 4},
    ]
    assert parse_week(raw).next_matchups == [(1, 2)]


def test_trade_with_null_draft_picks_parses():
    from cornerstone.parse import parse_trades
    trade = {"type": "trade", "status": "complete", "transaction_id": "1", "created": 1791542003405,
             "roster_ids": [2, 6], "adds": {"11610": 6}, "drops": {"11610": 2}, "draft_picks": None}
    assert parse_trades([trade])[0].draft_picks == []


def test_schedule_pairs_per_week(fixture_raw_dir):
    wk = parse_week(load_raw(fixture_raw_dir))
    assert sorted(wk.schedule) == list(range(8, 15))
    assert all(len(pairs) == 6 for pairs in wk.schedule.values())
    assert all(a < b for pairs in wk.schedule.values() for a, b in pairs)


def test_week_without_schedule_parses(fixture_raw_dir):
    raw = load_raw(fixture_raw_dir)
    raw.pop("schedule")
    assert parse_week(raw).schedule == {}


def test_projections_ahead_per_week(fixture_raw_dir):
    wk = parse_week(load_raw(fixture_raw_dir))
    assert sorted(wk.projections_ahead) == list(range(7, 15))
    assert all(isinstance(pts, float) for week in wk.projections_ahead.values() for pts in week.values())


def test_week_without_projections_ahead_parses(fixture_raw_dir):
    raw = load_raw(fixture_raw_dir)
    raw.pop("projections_ahead")
    assert parse_week(raw).projections_ahead == {}


def test_roster_positions_are_the_league_slots(fixture_raw_dir):
    raw = load_raw(fixture_raw_dir)
    assert parse_week(raw).roster_positions == raw["league"]["roster_positions"]
