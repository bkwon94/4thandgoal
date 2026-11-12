"""
The NFL game card of a free answer (AT-19): the live cpc week 10 from Sleeper, the saved weeks 1 to 9 of cpc, and the
Sleeper DEF projections of weeks 10 and 11, recorded on 2026-11-12. The Bears have a bye in week 10.
"""
import json
from pathlib import Path

from cornerstone_api.free_game import nfl_game
from cornerstone_api.free_tools import SeasonData
from league.provider.sleeper import load_raw

TESTS = Path(__file__).parent
CPC_HISTORY = TESTS.parents[2] / "clients" / "cpc" / "data" / "2026" / "history"
RAW_WEEK_10 = TESTS / "fixtures" / "start-sit" / "cpc-week-10"
DEF_PROJECTIONS = TESTS / "fixtures" / "nfl-game"


def def_projections(season: int, week: int) -> list[dict]:
    """The recorded answer of the Sleeper projections of the DEF rows of `week`."""
    return json.loads((DEF_PROJECTIONS / f"sleeper-def-projections-week-{week}.json").read_text())


def _data() -> SeasonData:
    return SeasonData(season=2026, week=9, teams={}, history_root=CPC_HISTORY, points_key="pts_half_ppr",
                      median_game=True, fetch_raw=lambda: load_raw(RAW_WEEK_10),
                      fetch_def_projections=def_projections)


def _def_row(week: int, team: str) -> dict:
    return next(row for row in def_projections(2026, week) if row["player_id"] == team)


def test_the_bears_game_is_the_next_game_after_the_bye_and_its_margin_is_the_gap_of_the_two_def_projections():
    result = nfl_game(_data(), "Bears")
    block = result.pop("block")
    assert result["week"] == 11 and result["live_week"] == 10
    assert result["team"] == "Chicago Bears" and result["opponent"] == "New Orleans Saints"
    # Each team scores what the DEF projection of the other team allows.
    bears, saints = _def_row(11, "CHI"), _def_row(11, "NO")
    assert result["projected_points"] == {"Chicago Bears": saints["stats"]["pts_allow"],
                                          "New Orleans Saints": bears["stats"]["pts_allow"]}
    gap = saints["stats"]["pts_allow"] - bears["stats"]["pts_allow"]
    assert block["kind"] == "nfl_game" and block["margin"] == gap == result["expected_margin"]
    assert [side["code"] for side in block["sides"]] == ["CHI", "NO"]


def test_a_team_that_plays_in_the_live_week_gets_the_live_game_with_the_favorite_ahead():
    result = nfl_game(_data(), "green bay")
    packers, vikings = _def_row(10, "GB"), _def_row(10, "MIN")
    assert result["week"] == 10 and result["opponent"] == "Minnesota Vikings"
    margin = vikings["stats"]["pts_allow"] - packers["stats"]["pts_allow"]
    assert margin == 3.0 and result["block"]["margin"] == margin
    assert result["favorite"] == "Green Bay Packers"


def test_the_strip_holds_the_32_defenses_against_the_position_with_the_opponent_lit():
    block = nfl_game(_data(), "Bears", position="WR")["block"]
    strip = block["strip"]
    assert strip["position"] == "WR" and strip["lit"] == "NO"
    assert len(strip["defenses"]) == 32
    allowed = [row["allowed"] for row in strip["defenses"]]
    assert allowed == sorted(allowed)
    # The value of the Saints is the mean of `fan_pts_allow_wr` over their games of weeks 1 to 9.
    games = [row["stats"]["fan_pts_allow_wr"] for week in range(1, 10)
             for row in json.loads((CPC_HISTORY / f"week-{week:02d}" / "stats.json").read_text())
             if row["player_id"] == "NO" and row["stats"].get("gp")]
    saints = next(row for row in strip["defenses"] if row["team"] == "NO")
    assert saints["allowed"] == round(sum(games) / len(games), 1)


def test_no_position_reads_the_points_allowed_to_all_positions():
    strip = nfl_game(_data(), "Bears")["block"]["strip"]
    assert strip["position"] is None and len(strip["defenses"]) == 32


def test_the_pass_share_of_each_team_sits_against_the_league_mark():
    result = nfl_game(_data(), "Bears")
    weeks = [json.loads((CPC_HISTORY / f"week-{week:02d}" / "stats.json").read_text()) for week in range(1, 10)]

    def share(team: str | None) -> float:
        rows = [row["stats"] for rows in weeks for row in rows if team is None or row.get("team") == team]
        passes = sum(stats.get("pass_att", 0) for stats in rows)
        return round(passes / (passes + sum(stats.get("rush_att", 0) for stats in rows)), 3)

    passing = result["block"]["pass_share"]
    assert passing["league"] == share(None)
    assert [side["share"] for side in passing["sides"]] == [share("CHI"), share("NO")]
    assert result["pass_share"] == {"Chicago Bears": share("CHI"), "New Orleans Saints": share("NO"),
                                    "league": share(None)}


def test_a_name_of_no_nfl_team_says_so():
    assert nfl_game(_data(), "Bo Girds") == {"error": "No NFL team is named Bo Girds."}
