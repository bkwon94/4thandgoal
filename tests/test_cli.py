"""
Tests for the cornerstone command line.
They run the real console script.
"""
import json
import subprocess
from pathlib import Path


def _no_nflverse(season, week, player_ids, players):
    raise AssertionError("no test downloads an nflverse file")


def test_help_lists_commands():
    out = subprocess.run(["uv", "run", "cornerstone", "--help"], capture_output=True, text=True)
    assert out.returncode == 0
    for cmd in ("build", "publish", "rewrite", "history"):
        assert cmd in out.stdout


def test_build_stops_when_week_is_not_final(tmp_path, fixture_raw_dir, monkeypatch, capsys):
    import shutil

    from cornerstone import cli

    def no_claude(*args, **kwargs):
        raise AssertionError("the gate must stop the build before any Claude call")

    monkeypatch.setattr(cli, "claude_call", no_claude)
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'stub'\n")
    shutil.copytree(fixture_raw_dir, tmp_path / "data" / "2026" / "week-07" / "raw")
    monkeypatch.chdir(tmp_path)

    code = cli.main(["build", "--season", "2026", "--week", "7", "--no-fetch"])

    assert code == 2
    assert "not final" in capsys.readouterr().out


def test_build_with_week_reads_saved_raw(tmp_path, fixture_raw_dir, monkeypatch, capsys):
    import shutil

    from cornerstone import cli, pipeline

    def no_fetch(*args, **kwargs):
        raise AssertionError("saved raw data must not be fetched again")

    def no_claude(*args, **kwargs):
        raise AssertionError("the gate must stop the build before any Claude call")

    monkeypatch.setattr(pipeline, "fetch_week", no_fetch)
    # The gate stops this build first. The patch keeps any later build off the network.
    monkeypatch.setattr(pipeline, "fetch_nflverse", lambda repo: _no_nflverse)
    monkeypatch.setattr(cli, "claude_call", no_claude)
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'stub'\n")
    shutil.copytree(fixture_raw_dir, tmp_path / "data" / "2026" / "week-07" / "raw")
    monkeypatch.chdir(tmp_path)

    code = cli.main(["build", "--week", "7", "--season", "2026"])

    assert code == 2
    assert "not final" in capsys.readouterr().out


def test_rewrite_without_facts_exits_plainly(tmp_path, monkeypatch, capsys):
    from cornerstone import cli

    def no_claude(*args, **kwargs):
        raise AssertionError("no Claude call expected")

    monkeypatch.setattr(cli, "claude_call", no_claude)
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'stub'\n")
    monkeypatch.chdir(tmp_path)

    code = cli.main(["rewrite", "--week", "6", "--season", "2026", "--chapter", "median"])

    out = capsys.readouterr().out
    assert code == 2
    assert out.startswith("Missing file ") and "facts.json" in out
    assert len(out.strip().splitlines()) == 1 and "Traceback" not in out


def test_sleeper_failure_exits_plainly(tmp_path, monkeypatch, capsys):
    import httpx

    from cornerstone import cli

    def down(*args, **kwargs):
        raise httpx.ConnectError("no route")

    monkeypatch.setattr(cli, "resolve_week", down)
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'stub'\n")
    monkeypatch.chdir(tmp_path)

    assert cli.main(["build"]) == 2
    assert "Sleeper request failed: no route" in capsys.readouterr().out


def test_missing_file_message_has_no_none_and_hint_fits_command(tmp_path, monkeypatch, capsys):
    from cornerstone import cli

    def no_name(*args, **kwargs):
        raise FileNotFoundError()

    monkeypatch.setattr(cli, "run_build", no_name)
    monkeypatch.setattr(cli, "run_rewrite", no_name)
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'stub'\n")
    monkeypatch.chdir(tmp_path)

    assert cli.main(["build", "--season", "2026", "--week", "7", "--no-fetch"]) == 2
    out = capsys.readouterr().out
    assert out == "Missing file. Run the build with --refetch.\n"

    assert cli.main(["rewrite", "--season", "2026", "--week", "7", "--chapter", "median"]) == 2
    out = capsys.readouterr().out
    assert out == "Missing file. Build the week first.\n"


def _chart_repo(tmp_path, fixture_raw_dir, monkeypatch):
    import shutil

    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'stub'\n")
    shutil.copytree(fixture_raw_dir, tmp_path / "data" / "2026" / "week-06" / "raw")
    monkeypatch.chdir(tmp_path)


def _pad_rows(value):
    from cornerstone.models import ChartRow

    # The name key drops digits, so each pad name spells its number in letters to stay unique.
    return [ChartRow(value=value, name="Pad " + "".join(chr(ord("a") + int(d)) for d in str(i)), position="TE")
            for i in range(100)]


def _save_chart(tmp_path, parsed):
    from cornerstone.chart import chart_dir

    charts = chart_dir(tmp_path)
    charts.mkdir(parents=True)
    # A saved parse means the command makes no fetch and no Claude call.
    (charts / "week-06.json").write_text(parsed.model_dump_json())


def _sleeper_state(season):
    return lambda: {"season": season, "season_start_date": "2026-09-09"}


def test_chart_without_saved_raw_data_prints_the_chart_and_skips_the_match(tmp_path, monkeypatch, capsys):
    from cornerstone import cli
    from cornerstone.models import ChartRead, ChartRow

    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'stub'\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cli, "fetch_state", _sleeper_state("2026"))
    _save_chart(tmp_path, ChartRead(week=6, date="2026-10-13",
                                    rows=[ChartRow(value=60.0, name="Some One", position="RB"), *_pad_rows(50.0)]))

    assert cli.main(["chart", "--season", "2026", "--week", "6"]) == 0
    out = capsys.readouterr().out
    assert "60.0  Some One  RB" in out
    assert "header week: pass" in out
    assert "No raw data for week 6, so no player match." in out
    assert "Matched" not in out


def test_chart_without_saved_raw_data_of_a_past_season_says_so(tmp_path, monkeypatch, capsys):
    from cornerstone import cli

    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'stub'\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cli, "fetch_state", _sleeper_state("2027"))

    assert cli.main(["chart", "--season", "2026", "--week", "6"]) == 2
    assert "No raw data" in capsys.readouterr().out


def test_chart_prints_the_table_and_every_guard_when_a_guard_fails(tmp_path, fixture_raw_dir, monkeypatch, capsys):
    from cornerstone import cli
    from cornerstone.models import ChartRead, ChartRow

    _chart_repo(tmp_path, fixture_raw_dir, monkeypatch)
    _save_chart(tmp_path, ChartRead(week=6, date="2026-10-13", rows=[ChartRow(value=60.0, name="Some One", position="RB")]))

    assert cli.main(["chart", "--season", "2026", "--week", "6"]) == 1
    out = capsys.readouterr().out
    assert "60.0  Some One  RB" in out
    assert "header week: pass" in out
    assert "at least 100 rows: FAIL" in out
    assert "no trade values were made" in out
    assert "Matched" not in out


def test_chart_prints_the_table_the_guards_and_the_matches(tmp_path, fixture_raw_dir, monkeypatch, capsys):
    from cornerstone import cli
    from cornerstone.models import ChartRead, ChartRow
    from cornerstone.parse import parse_week
    from cornerstone.sleeper import load_raw

    _chart_repo(tmp_path, fixture_raw_dir, monkeypatch)
    line = parse_week(load_raw(fixture_raw_dir)).matchups[0].a.lines[0]
    parsed = ChartRead(week=6, date="2026-10-13", rows=[
        ChartRow(value=60.0, name=line.name, position=line.position),
        ChartRow(value=50.0, name="Nobody Atall", position="RB"),
        *_pad_rows(50.0),
    ])
    _save_chart(tmp_path, parsed)

    assert cli.main(["chart", "--season", "2026", "--week", "6"]) == 0

    out = capsys.readouterr().out
    assert f"60.0  {line.name}  {line.position}" in out
    assert "header week: pass" in out
    assert "Matched 1 of 102 chart rows" in out


def _analyze_repo(tmp_path, fixture_raw_dir, fixture_history_root, monkeypatch):
    """A repo in tmp_path with the week 6 raw data and history, as the analyze command reads them."""
    import shutil

    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'stub'\n")
    shutil.copytree(fixture_raw_dir, tmp_path / "data" / "2026" / "week-06" / "raw")
    shutil.copytree(fixture_history_root, tmp_path / "data" / "2026" / "history")
    monkeypatch.chdir(tmp_path)


CHART_FIXTURE = str(Path(__file__).parent / "fixtures" / "charts" / "week-06.json")


def test_analyze_prints_the_breakdown_per_side_with_no_trade_value(
        tmp_path, fixture_raw_dir, fixture_history_root, monkeypatch, capsys):
    from cornerstone import cli

    _analyze_repo(tmp_path, fixture_raw_dir, fixture_history_root, monkeypatch)
    code = cli.main(["analyze", "--season", "2026", "--week", "6", "--chart", CHART_FIXTURE,
                     "--side", "4:7569", "--side", "12:10236,8146", "--asker", "4", "--no-claude"])

    out = capsys.readouterr().out
    assert code == 0
    assert "Nico Collins" in out and "Dalton Kincaid" in out and "Garrett Wilson" in out
    assert out.count("Start letter: C") == 2
    # Each side prints its adjusters in rubric order, after the start letter.
    assert out.count("Roster fit: ") == 2 and out.count("Standing: ") == 2
    assert out.index("Start letter") < out.index("Roster fit: ") < out.index("Standing: ")
    assert "(asked)" in out
    # Week 6 is the trade week, so the stats end at week 5.
    assert "Week 6 of 2026. Chart week 6. Stats through week 5." in out
    # The repo has no nflverse cache. The points allowed come from the history, so they are present.
    assert "Sources missing: schedules, depth charts, id map, injuries, expected points, player weeks." in out
    # The trade values 46.5, 31.5, and 27.5, their sum, and the ratio never print.
    for number in ("46.5", "31.5", "27.5", "59", "47.2", "1.0"):
        assert number not in out


def test_analyze_names_the_sources_it_has_from_the_cache(
        tmp_path, fixture_raw_dir, fixture_history_root, fixture_nflverse_dir, monkeypatch, capsys):
    import shutil

    from cornerstone import cli

    _analyze_repo(tmp_path, fixture_raw_dir, fixture_history_root, monkeypatch)
    shutil.copytree(fixture_nflverse_dir, tmp_path / "data" / "cache" / "nflverse")
    code = cli.main(["analyze", "--season", "2026", "--week", "6", "--chart", CHART_FIXTURE,
                     "--side", "4:7569", "--side", "12:10236,8146", "--asker", "4", "--no-claude"])

    assert code == 0
    assert ("Sources: schedules, depth charts, points allowed, injuries, expected points, player weeks.\n"
            in capsys.readouterr().out)


def test_analyze_names_the_one_source_the_cache_lacks(
        tmp_path, fixture_raw_dir, fixture_history_root, fixture_nflverse_dir, monkeypatch, capsys):
    import shutil

    from cornerstone import cli

    _analyze_repo(tmp_path, fixture_raw_dir, fixture_history_root, monkeypatch)
    cache = tmp_path / "data" / "cache" / "nflverse"
    shutil.copytree(fixture_nflverse_dir, cache)
    (cache / "ep_weekly_2026.csv").unlink()
    code = cli.main(["analyze", "--season", "2026", "--week", "6", "--chart", CHART_FIXTURE,
                     "--side", "4:7569", "--side", "12:10236,8146", "--asker", "4", "--no-claude"])

    assert code == 0
    assert "Sources missing: expected points.\n" in capsys.readouterr().out


def test_the_source_names_are_the_names_of_the_refreshed_sources():
    from cornerstone import cli
    from cornerstone.live import REFRESHED_SOURCES
    from cornerstone.snapshot import SLOW_SOURCES

    # The line names each slow source the snapshot can miss, by the key the snapshot gives it.
    assert set(cli._SOURCE_NAMES) == set(SLOW_SOURCES)
    # The line and the refresh name each nflverse file with the same words.
    assert {name for name, _ in REFRESHED_SOURCES} <= set(cli._SOURCE_NAMES.values())


def _set_back_the_jacobs_trade(tmp_path):
    """Rewrite the saved rosters to before the Josh Jacobs trade. The saved rosters show the league after it."""
    import json

    path = tmp_path / "data" / "2026" / "week-06" / "raw" / "rosters.json"
    rosters = json.loads(path.read_text())
    moves = {11: (["5850", "11834"], ["12490", "8146"]), 12: (["12490", "8146"], ["5850", "11834"])}
    for roster in rosters:
        if roster["roster_id"] in moves:
            out, back = moves[roster["roster_id"]]
            roster["players"] = [pid for pid in roster["players"] if pid not in out] + back
    path.write_text(json.dumps(rosters))


def test_analyze_prints_the_full_breakdown_and_the_verdict_for_the_josh_jacobs_trade(
        tmp_path, fixture_raw_dir, fixture_history_root, fixture_nflverse_dir, monkeypatch, capsys):
    import shutil

    from cornerstone import cli

    _analyze_repo(tmp_path, fixture_raw_dir, fixture_history_root, monkeypatch)
    shutil.copytree(fixture_nflverse_dir, tmp_path / "data" / "cache" / "nflverse")
    # The returns file has Jacobs back in week 7.
    shutil.copy(fixture_history_root.parent / "returns.json", tmp_path / "data" / "2026" / "returns.json")
    _set_back_the_jacobs_trade(tmp_path)
    code = cli.main(["analyze", "--season", "2026", "--week", "6", "--chart", CHART_FIXTURE,
                     "--side", "11:12490,8146", "--side", "12:5850,11834", "--asker", "12", "--no-claude"])

    out = capsys.readouterr().out
    assert code == 0
    assert "Week 6 of 2026. Chart week 6. Stats through week 5." in out
    # Each side ends with the schedule lean and the final letter, after the five adjusters with steps.
    assert out.count("  Schedule: even. ") == 2
    assert "  Final letter: B\n" in out and "  Final letter: D\n" in out
    assert out.index("Handcuff: ") < out.index("Schedule: ") < out.index("Final letter: ")
    # The fairness line follows the verdict, then one reason per side in the order of the sides.
    assert out.endswith(
        "\nVerdict for Amon-Ra Dawg Your Team: decline. The trade costs the asking side too much.\n"
        "Fairness: Lopsided: Amon-Ra Dawg Your Team gives more.\n"
        "  Unsolicited Dak Picks: It gets far more trade value than it gives.\n"
        "  Amon-Ra Dawg Your Team: The best lineup gains after the trade. "
        "Josh Jacobs is due back in week 7, so he counts for his projection ahead of 12.2 a game.\n")
    # The trade values 3.0, 27.5, 11.5, and 55.0, their sums, and the ratios never print.
    for number in ("27.5", "11.5", "55", "30.5", "66.5"):
        assert number not in out


def test_analyze_names_a_player_not_on_the_giving_roster(
        tmp_path, fixture_raw_dir, fixture_history_root, monkeypatch, capsys):
    from cornerstone import cli

    _analyze_repo(tmp_path, fixture_raw_dir, fixture_history_root, monkeypatch)
    code = cli.main(["analyze", "--season", "2026", "--week", "6", "--chart", CHART_FIXTURE,
                     "--side", "4:4034", "--side", "12:10236", "--asker", "4", "--no-claude"])

    assert code == 2
    assert "Christian McCaffrey is no longer on Pukancun on 3." in capsys.readouterr().out


def test_analyze_needs_exactly_two_sides(tmp_path, fixture_raw_dir, fixture_history_root, monkeypatch, capsys):
    from cornerstone import cli

    _analyze_repo(tmp_path, fixture_raw_dir, fixture_history_root, monkeypatch)
    code = cli.main(["analyze", "--season", "2026", "--week", "6", "--side", "4:7569", "--asker", "4", "--no-claude"])

    assert code == 2
    assert "exactly twice" in capsys.readouterr().out


def test_analyze_prints_one_plain_line_for_a_trade_that_breaks_a_model_rule(
        tmp_path, fixture_raw_dir, fixture_history_root, monkeypatch, capsys):
    from cornerstone import cli

    _analyze_repo(tmp_path, fixture_raw_dir, fixture_history_root, monkeypatch)
    code = cli.main(["analyze", "--season", "2026", "--week", "6", "--chart", CHART_FIXTURE,
                     "--side", "4:7569", "--side", "4:10236", "--asker", "4", "--no-claude"])

    out = capsys.readouterr().out
    assert code == 2
    assert out.strip() == "A proposed trade needs two different rosters"


def _live_analyze(tmp_path, fixture_raw_dir, fixture_history_root, fixture_nflverse_dir, chart_week6, monkeypatch,
                  fetch_history_week, unsaved_week=None):
    """Run analyze without --week. The live entry runs for real, with every fetch swapped for a fixture-backed one.

    An `unsaved_week` is removed from the history, so the live build must fetch it.
    """
    import shutil
    from datetime import datetime

    import pytest

    from cornerstone import cli, live
    from cornerstone.sleeper import load_raw

    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'stub'\n")
    shutil.copytree(fixture_history_root, tmp_path / "data" / "2026" / "history")
    if unsaved_week is not None:
        shutil.rmtree(tmp_path / "data" / "2026" / "history" / f"week-{unsaved_week:02d}")
    shutil.copytree(fixture_nflverse_dir, tmp_path / "data" / "cache" / "nflverse")
    for cached in (tmp_path / "data" / "cache" / "nflverse").iterdir():
        cached.touch()
    monkeypatch.chdir(tmp_path)
    fetched = datetime(2026, 10, 19, 9, 30, tzinfo=cli.EASTERN)
    real = live.live_snapshot
    monkeypatch.setattr(cli, "live_snapshot", lambda repo, season, **kw: real(
        repo, season, now=datetime(2026, 10, 19, 12, 0, tzinfo=cli.EASTERN),
        fetch_sleeper=lambda league_id, cache: (load_raw(fixture_raw_dir), fetched),
        fetch_nflverse=lambda url: pytest.fail(f"network call to {url}"),
        fetch_history_week=fetch_history_week,
        read_chart=lambda repo, start, week, lines: chart_week6))
    return cli.main(["analyze", "--season", "2026", "--side", "4:7569", "--side", "12:10236,8146",
                     "--asker", "4", "--no-claude"])


def _no_history_fetch(league_id, season, week, out_dir):
    raise AssertionError(f"network call for history week {week}")


def test_analyze_without_week_grades_the_live_snapshot_and_prints_the_as_of_line(
        tmp_path, fixture_raw_dir, fixture_history_root, fixture_nflverse_dir, chart_week6, monkeypatch, capsys):
    code = _live_analyze(tmp_path, fixture_raw_dir, fixture_history_root, fixture_nflverse_dir, chart_week6,
                         monkeypatch, _no_history_fetch)

    out = capsys.readouterr().out
    assert code == 0
    assert "Week 6 of 2026. Chart week 6. Stats through week 5. Rosters fetched 2026-10-19T09:30-04:00." in out
    assert "Refresh failed" not in out
    assert "Nico Collins" in out


def test_analyze_without_week_names_a_failed_refresh(
        tmp_path, fixture_raw_dir, fixture_history_root, fixture_nflverse_dir, chart_week6, monkeypatch, capsys):
    import httpx

    def down(league_id, season, week, out_dir):
        raise httpx.ConnectError("down")

    code = _live_analyze(tmp_path, fixture_raw_dir, fixture_history_root, fixture_nflverse_dir, chart_week6,
                         monkeypatch, down, unsaved_week=5)

    out = capsys.readouterr().out
    assert code == 0
    assert "Stats through week 4." in out
    assert "Refresh failed, so the cache is old or absent: history.\n" in out


def _jacobs_repo(tmp_path, fixture_raw_dir, fixture_history_root, fixture_nflverse_dir, monkeypatch):
    """The analyze repo with the nflverse cache, the returns file, and the rosters from before the Jacobs trade."""
    import shutil

    _analyze_repo(tmp_path, fixture_raw_dir, fixture_history_root, monkeypatch)
    shutil.copytree(fixture_nflverse_dir, tmp_path / "data" / "cache" / "nflverse")
    shutil.copy(fixture_history_root.parent / "returns.json", tmp_path / "data" / "2026" / "returns.json")
    _set_back_the_jacobs_trade(tmp_path)


JACOBS_ARGS = ["analyze", "--season", "2026", "--week", "6", "--chart", CHART_FIXTURE,
               "--side", "11:12490,8146", "--side", "12:5850,11834", "--asker", "12"]


def test_analyze_with_claude_prints_the_analysis_the_letters_and_the_verdict(
        tmp_path, fixture_raw_dir, fixture_history_root, fixture_nflverse_dir, monkeypatch, capsys):
    from cornerstone import cli
    from cornerstone.analysis import AnalysisOut

    def fake_claude(system, user, output_model):
        assert output_model is AnalysisOut
        side = {"final_letter": "D", "reason": None, "cited": ["8146.ppg"],
                "analysis": "Garrett Wilson scored 14.2 points per game before the trade. He moves. He starts."}
        return AnalysisOut.model_validate({
            "sides": [{**side, "roster_id": 11, "final_letter": "C", "reason": "Jacobs has not played."},
                      {**side, "roster_id": 12}],
            "verdict": {"choice": "counter", "reason": "Ask for one more starter."},
        })

    monkeypatch.setattr(cli, "analyzer_call", fake_claude)
    _jacobs_repo(tmp_path, fixture_raw_dir, fixture_history_root, fixture_nflverse_dir, monkeypatch)
    code = cli.main(JACOBS_ARGS)

    out = capsys.readouterr().out
    assert code == 0
    # The breakdown's letter is the rubric's. The final letter is Claude's, with its reason when it differs.
    assert "  Rubric letter: B\n" in out and "  Rubric letter: D\n" in out
    assert "  Final letter: C. Reason: Jacobs has not played.\n" in out
    assert "  Final letter: D\n" in out
    assert out.count("  Analysis: Garrett Wilson scored 14.2 points per game before the trade.") == 2
    assert (out.index("Schedule: ") < out.index("Rubric letter: ") < out.index("Final letter: C")
            < out.index("Analysis: "))
    # The fairness reads Claude's letters, C and D, so the trade is still lopsided.
    assert ("\nVerdict for Amon-Ra Dawg Your Team: counter. Ask for one more starter. "
            "(differs from the rubric's default)\nFairness: Lopsided: Amon-Ra Dawg Your Team gives more.\n") in out


def test_analyze_with_claude_says_when_the_call_fell_back(
        tmp_path, fixture_raw_dir, fixture_history_root, fixture_nflverse_dir, monkeypatch, capsys):
    from cornerstone import cli

    monkeypatch.setattr(cli, "analyzer_call", lambda system, user, output_model: None)
    _jacobs_repo(tmp_path, fixture_raw_dir, fixture_history_root, fixture_nflverse_dir, monkeypatch)
    code = cli.main(JACOBS_ARGS)

    out = capsys.readouterr().out
    assert code == 0
    assert out.count("  Analysis: Analysis unavailable\n") == 2
    assert "  Final letter: B\n" in out and "  Final letter: D\n" in out
    assert "The Claude call failed twice, so the rubric's letters and verdict stand." in out
    assert ("\nVerdict for Amon-Ra Dawg Your Team: decline. The trade costs the asking side too much.\n"
            "Fairness: Lopsided: Amon-Ra Dawg Your Team gives more.\n") in out


def _find_repo(tmp_path, fixture_raw_dir, fixture_history_root, fixture_nflverse_dir, monkeypatch):
    """The analyze repo with the nflverse cache and the returns file, as the find command reads them."""
    import shutil

    _analyze_repo(tmp_path, fixture_raw_dir, fixture_history_root, monkeypatch)
    shutil.copytree(fixture_nflverse_dir, tmp_path / "data" / "cache" / "nflverse")
    shutil.copy(fixture_history_root.parent / "returns.json", tmp_path / "data" / "2026" / "returns.json")


# The fixture chart lists 25 players, mostly stars, so no pair of the week 6 snapshot has a win-win on it.
# These rows add a running back of roster 2 and a quarterback and a receiver of roster 3, at their recent points
# per game, so rosters 2 and 3 have one win-win.
FIND_ROWS = {"12527": 11.0, "11560": 8.0, "5947": 7.0}


def _chart_with_rows(tmp_path) -> str:
    """A copy of the fixture chart with the FIND_ROWS rows, as a file the --chart flag reads."""
    chart = json.loads(Path(CHART_FIXTURE).read_text(encoding="utf-8"))
    chart["values"] = {**chart["values"], **FIND_ROWS}
    path = tmp_path / "chart-with-rows.json"
    path.write_text(json.dumps(chart), encoding="utf-8")
    return str(path)


def test_find_prints_each_win_win_with_its_sides_and_the_fairness(
        tmp_path, fixture_raw_dir, fixture_history_root, fixture_nflverse_dir, monkeypatch, capsys):
    from cornerstone import cli

    _find_repo(tmp_path, fixture_raw_dir, fixture_history_root, fixture_nflverse_dir, monkeypatch)
    code = cli.main(["find", "--season", "2026", "--week", "6", "--chart", _chart_with_rows(tmp_path),
                     "--asker", "2", "--partner", "3"])

    out = capsys.readouterr().out
    assert code == 0
    assert "Week 6 of 2026. Chart week 6. Stats through week 5." in out
    # Rosters 2 and 3 have one win-win with these rows: roster 2 gives one player for two.
    assert out.endswith(
        "\n1. All You Need Is Love gives: Ashton Jeanty\n"
        "   Lil Fridge gives: Caleb Williams, Jakobi Meyers\n"
        "Fairness: Good for both\n"
        "  All You Need Is Love: The players it gets gain snap or target share, and the players it gives lose it. "
        "Jeanty: snap share 61%, down, over weeks 4 and 5.\n"
        "  Lil Fridge: The best lineup gains after the trade.\n")
    assert "\n2. " not in out


def test_find_prints_one_line_when_no_swap_is_good_for_both(
        tmp_path, fixture_raw_dir, fixture_history_root, fixture_nflverse_dir, monkeypatch, capsys):
    from cornerstone import cli

    _find_repo(tmp_path, fixture_raw_dir, fixture_history_root, fixture_nflverse_dir, monkeypatch)
    code = cli.main(["find", "--season", "2026", "--week", "6", "--chart", CHART_FIXTURE,
                     "--asker", "1", "--partner", "3"])

    out = capsys.readouterr().out
    assert code == 0
    assert out.endswith("\nNo swap between these rosters is good for both.\n")
    assert "Fairness:" not in out
