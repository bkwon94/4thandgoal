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
    shough = next(l for s in (m.a, m.b) for l in s.lines if l.name == "Tyler Shough")
    assert shough.started and shough.points == 26.96 and shough.projection == 17.06


def test_unknown_player_falls_back_to_id(fixture_raw_dir):
    raw = load_raw(fixture_raw_dir)
    raw["players"].pop("8183")  # Brock Purdy
    wk = parse_week(raw)
    lines = [l for m in wk.matchups for s in (m.a, m.b) for l in s.lines]
    purdy = next(l for l in lines if l.player_id == "8183")
    assert purdy.name == "8183" and purdy.position == "?"


def test_week_argument_overrides_display_week(fixture_raw_dir):
    raw = load_raw(fixture_raw_dir)
    assert parse_week(raw, week=5).week == 5


def test_defense_name_and_slot(fixture_raw_dir):
    wk = parse_week(load_raw(fixture_raw_dir))
    lines = [l for m in wk.matchups for s in (m.a, m.b) for l in s.lines]
    tb = next(l for l in lines if l.player_id == "TB")
    assert tb.name == "Tampa Bay Buccaneers" and tb.position == "DEF"
    assert tb.started and tb.slot == "DEF"
    bench = next(l for l in lines if not l.started)
    assert bench.slot is None
    assert all(l.season_avg is None for l in lines)


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
    lines = [l for m in wk.matchups for s in (m.a, m.b) for l in s.lines]
    assert not any(l.player_id == "0" or l.name == "0" for l in lines)
    third = next(l for l in lines if l.player_id == entry["starters"][2])
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
