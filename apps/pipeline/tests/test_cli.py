"""
Tests for the cornerstone command line.
They run the real console script.
"""
import json
import subprocess
from pathlib import Path

import pytest
from cpc import cli_root


def _no_nflverse(season, week, player_ids, players):
    raise AssertionError("no test downloads an nflverse file")


def test_help_lists_commands():
    # The test asserts the return code itself.
    out = subprocess.run(["uv", "run", "cornerstone", "--help"], capture_output=True, text=True, check=False)
    assert out.returncode == 0
    for cmd in ("build", "publish", "rewrite", "history"):
        assert cmd in out.stdout


def test_build_stops_when_week_is_not_final(tmp_path, fixture_raw_dir, monkeypatch, capsys, fake_writer):
    import shutil

    from cornerstone import cli

    cli_root(tmp_path)
    shutil.copytree(fixture_raw_dir, tmp_path / "clients" / "cpc" / "data" / "2026" / "week-07" / "raw")
    monkeypatch.chdir(tmp_path)

    code = cli.main(["build", "--client", "cpc", "--season", "2026", "--week", "7", "--no-fetch"], writer=fake_writer)

    assert code == 2
    assert "not final" in capsys.readouterr().out
    # The gate must stop the build before any Claude call.
    assert fake_writer.calls == []


def test_build_with_week_reads_saved_raw(tmp_path, fixture_raw_dir, monkeypatch, capsys, fake_writer):
    import shutil

    import httpx

    from cornerstone import cli, pipeline
    from league.provider.sleeper import SleeperProvider

    def no_fetch(request):
        raise AssertionError("saved raw data must not be fetched again")

    # The gate stops this build first. The patch keeps any later build off the network.
    monkeypatch.setattr(pipeline, "fetch_nflverse", lambda repo: _no_nflverse)
    cli_root(tmp_path)
    shutil.copytree(fixture_raw_dir, tmp_path / "clients" / "cpc" / "data" / "2026" / "week-07" / "raw")
    monkeypatch.chdir(tmp_path)

    code = cli.main(["build", "--client", "cpc", "--week", "7", "--season", "2026"], writer=fake_writer,
                    provider=SleeperProvider(tmp_path / "cache", transport=httpx.MockTransport(no_fetch)))

    assert code == 2
    assert "not final" in capsys.readouterr().out
    # The gate must stop the build before any Claude call.
    assert fake_writer.calls == []


def test_rewrite_without_facts_exits_plainly(tmp_path, monkeypatch, capsys, fake_writer):
    from cornerstone import cli

    cli_root(tmp_path)
    monkeypatch.chdir(tmp_path)

    code = cli.main(["rewrite", "--client", "cpc", "--week", "6", "--season", "2026", "--chapter", "median"], writer=fake_writer)

    out = capsys.readouterr().out
    assert code == 2
    assert out.startswith("Missing file ") and "facts.json" in out
    assert len(out.strip().splitlines()) == 1 and "Traceback" not in out
    # The rewrite must not call Claude.
    assert fake_writer.calls == []


def test_sleeper_failure_exits_plainly(tmp_path, monkeypatch, capsys):
    import httpx

    from cornerstone import cli

    def down(*args, **kwargs):
        raise httpx.ConnectError("no route")

    monkeypatch.setattr(cli, "resolve_week", down)
    cli_root(tmp_path)
    monkeypatch.chdir(tmp_path)

    assert cli.main(["build", "--client", "cpc"]) == 2
    assert "Sleeper request failed: no route" in capsys.readouterr().out


def test_missing_file_message_has_no_none_and_hint_fits_command(tmp_path, monkeypatch, capsys):
    from cornerstone import cli

    def no_name(*args, **kwargs):
        raise FileNotFoundError()

    monkeypatch.setattr(cli, "run_build", no_name)
    monkeypatch.setattr(cli, "run_rewrite", no_name)
    cli_root(tmp_path)
    monkeypatch.chdir(tmp_path)

    assert cli.main(["build", "--client", "cpc", "--season", "2026", "--week", "7", "--no-fetch"]) == 2
    out = capsys.readouterr().out
    assert out == "Missing file. Run the build with --refetch.\n"

    assert cli.main(["rewrite", "--client", "cpc", "--season", "2026", "--week", "7", "--chapter", "median"]) == 2
    out = capsys.readouterr().out
    assert out == "Missing file. Build the week first.\n"


def _chart_repo(tmp_path, fixture_raw_dir, monkeypatch):
    import shutil

    cli_root(tmp_path)
    shutil.copytree(fixture_raw_dir, tmp_path / "clients" / "cpc" / "data" / "2026" / "week-06" / "raw")
    monkeypatch.chdir(tmp_path)


def _pad_rows(value):
    from league.models import ChartRow

    # The name key drops digits, so each pad name spells its number in letters to stay unique.
    return [ChartRow(value=value, name="Pad " + "".join(chr(ord("a") + int(d)) for d in str(i)), position="TE")
            for i in range(100)]


def _save_chart(tmp_path, parsed):
    from league.paths import charts_dir

    # The chart of the cpc client in its client.toml.
    charts = charts_dir(tmp_path / "data" / "nfl", "1QB0.5PPR4pt")
    charts.mkdir(parents=True)
    # A saved parse means the command makes no fetch and no Claude call.
    (charts / "week-06.json").write_text(parsed.model_dump_json())


def _sleeper_state(season):
    from league.provider.raw import RawState

    return lambda: RawState(season=season, display_week=6, season_start_date="2026-09-09")


def test_chart_without_saved_raw_data_prints_the_chart_and_skips_the_match(tmp_path, monkeypatch, capsys):
    from cornerstone import cli
    from league.models import ChartRead, ChartRow

    cli_root(tmp_path)
    monkeypatch.chdir(tmp_path)
    _save_chart(tmp_path, ChartRead(week=6, date="2026-10-13",
                                    rows=[ChartRow(value=60.0, name="Some One", position="RB"), *_pad_rows(50.0)]))

    assert cli.main(["chart", "--client", "cpc", "--season", "2026", "--week", "6"], fetch_state=_sleeper_state("2026")) == 0
    out = capsys.readouterr().out
    assert "60.0  Some One  RB" in out
    assert "header week: pass" in out
    assert "No raw data for week 6, so no player match." in out
    assert "Matched" not in out


def test_chart_without_saved_raw_data_of_a_past_season_says_so(tmp_path, monkeypatch, capsys):
    from cornerstone import cli

    cli_root(tmp_path)
    monkeypatch.chdir(tmp_path)

    assert cli.main(["chart", "--client", "cpc", "--season", "2026", "--week", "6"], fetch_state=_sleeper_state("2027")) == 2
    assert "No raw data" in capsys.readouterr().out


def test_chart_prints_the_table_and_every_guard_when_a_guard_fails(tmp_path, fixture_raw_dir, monkeypatch, capsys):
    from cornerstone import cli
    from league.models import ChartRead, ChartRow

    _chart_repo(tmp_path, fixture_raw_dir, monkeypatch)
    _save_chart(
        tmp_path, ChartRead(week=6, date="2026-10-13", rows=[ChartRow(value=60.0, name="Some One", position="RB")])
    )

    assert cli.main(["chart", "--client", "cpc", "--season", "2026", "--week", "6"]) == 1
    out = capsys.readouterr().out
    assert "60.0  Some One  RB" in out
    assert "header week: pass" in out
    assert "at least 100 rows: FAIL" in out
    assert "no trade values were made" in out
    assert "Matched" not in out


def test_chart_prints_the_table_the_guards_and_the_matches(tmp_path, fixture_raw_dir, monkeypatch, capsys):
    from cornerstone import cli
    from league.models import ChartRead, ChartRow
    from league.parse import parse_week
    from league.provider.sleeper import load_raw

    _chart_repo(tmp_path, fixture_raw_dir, monkeypatch)
    line = parse_week(load_raw(fixture_raw_dir)).matchups[0].a.lines[0]
    parsed = ChartRead(week=6, date="2026-10-13", rows=[
        ChartRow(value=60.0, name=line.name, position=line.position),
        ChartRow(value=50.0, name="Nobody Atall", position="RB"),
        *_pad_rows(50.0),
    ])
    _save_chart(tmp_path, parsed)

    assert cli.main(["chart", "--client", "cpc", "--season", "2026", "--week", "6"]) == 0

    out = capsys.readouterr().out
    assert f"60.0  {line.name}  {line.position}" in out
    assert "header week: pass" in out
    assert "Matched 1 of 102 chart rows" in out


def _analyze_repo(tmp_path, fixture_raw_dir, fixture_history_root, monkeypatch):
    """A repo in tmp_path with the week 6 raw data and history, as the analyze command reads them."""
    import shutil

    cli_root(tmp_path)
    shutil.copytree(fixture_raw_dir, tmp_path / "clients" / "cpc" / "data" / "2026" / "week-06" / "raw")
    shutil.copytree(fixture_history_root, tmp_path / "clients" / "cpc" / "data" / "2026" / "history")
    monkeypatch.chdir(tmp_path)


CHART_FIXTURE = str(Path(__file__).parent / "fixtures" / "charts" / "week-06.json")


def test_analyze_prints_the_breakdown_per_side_with_no_trade_value(
        tmp_path, fixture_raw_dir, fixture_history_root, monkeypatch, capsys):
    from cornerstone import cli

    _analyze_repo(tmp_path, fixture_raw_dir, fixture_history_root, monkeypatch)
    code = cli.main(["analyze", "--client", "cpc", "--season", "2026", "--week", "6", "--chart", CHART_FIXTURE,
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
    shutil.copytree(fixture_nflverse_dir, tmp_path / "data" / "nfl" / "cache" / "nflverse")
    code = cli.main(["analyze", "--client", "cpc", "--season", "2026", "--week", "6", "--chart", CHART_FIXTURE,
                     "--side", "4:7569", "--side", "12:10236,8146", "--asker", "4", "--no-claude"])

    assert code == 0
    assert ("Sources: schedules, depth charts, points allowed, injuries, expected points, player weeks.\n"
            in capsys.readouterr().out)


def test_analyze_names_the_one_source_the_cache_lacks(
        tmp_path, fixture_raw_dir, fixture_history_root, fixture_nflverse_dir, monkeypatch, capsys):
    import shutil

    from cornerstone import cli

    _analyze_repo(tmp_path, fixture_raw_dir, fixture_history_root, monkeypatch)
    cache = tmp_path / "data" / "nfl" / "cache" / "nflverse"
    shutil.copytree(fixture_nflverse_dir, cache)
    (cache / "ep_weekly_2026.csv").unlink()
    code = cli.main(["analyze", "--client", "cpc", "--season", "2026", "--week", "6", "--chart", CHART_FIXTURE,
                     "--side", "4:7569", "--side", "12:10236,8146", "--asker", "4", "--no-claude"])

    assert code == 0
    assert "Sources missing: expected points.\n" in capsys.readouterr().out


def test_the_source_names_are_the_names_of_the_refreshed_sources():
    from cornerstone import cli
    from league.live import REFRESHED_SOURCES
    from league.snapshot import SLOW_SOURCES

    # The line names each slow source the snapshot can miss, by the key the snapshot gives it.
    assert set(cli._SOURCE_NAMES) == set(SLOW_SOURCES)
    # The line and the refresh name each nflverse file with the same words.
    assert {name for name, _ in REFRESHED_SOURCES} <= set(cli._SOURCE_NAMES.values())


def _set_back_the_jacobs_trade(tmp_path):
    """Rewrite the saved rosters to before the Josh Jacobs trade. The saved rosters show the league after it."""
    import json

    path = tmp_path / "clients" / "cpc" / "data" / "2026" / "week-06" / "raw" / "rosters.json"
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
    shutil.copytree(fixture_nflverse_dir, tmp_path / "data" / "nfl" / "cache" / "nflverse")
    # The returns file has Jacobs back in week 7.
    shutil.copy(fixture_history_root.parent / "returns.json", tmp_path / "data" / "nfl" / "2026" / "returns.json")
    _set_back_the_jacobs_trade(tmp_path)
    code = cli.main(["analyze", "--client", "cpc", "--season", "2026", "--week", "6", "--chart", CHART_FIXTURE,
                     "--side", "11:12490,8146", "--side", "12:5850,11834", "--asker", "12", "--no-claude"])

    out = capsys.readouterr().out
    assert code == 0
    assert "Week 6 of 2026. Chart week 6. Stats through week 5." in out
    # Each side ends with the schedule lean and the final letter, after the seven adjusters with steps.
    assert out.count("  Schedule: even. ") == 2
    assert "  Final letter: A\n" in out and "  Final letter: D\n" in out
    assert out.index("Handcuff: ") < out.index("Schedule: ") < out.index("Final letter: ")
    # The fairness line follows the verdict, then one reason per side in the order of the sides.
    # Jacobs is a top RB out now, so upside steps Unsolicited Dak Picks up. Roster fit steps it down for the same
    # absence, so the net is zero and its reason names both steps.
    assert out.endswith(
        "\nVerdict for Amon-Ra Dawg Your Team: decline. The trade costs the asking side too much.\n"
        "Fairness: Lopsided: Amon-Ra Dawg Your Team gives more.\n"
        "  Unsolicited Dak Picks: Jacobs is a top RB, due back in week 7, but you keep 3 RBs in the top 36 and keep 2 "
        "WRs in the top 36, and Jacobs is due back in week 7, and no other player covers him.\n"
        "  Amon-Ra Dawg Your Team: You keep 4 RBs in the top 36 and keep 5 WRs in the top 36, and your lineup scores "
        "more.\n")
    # The trade values 3.0, 27.5, 11.5, and 55.0, their sums, and the ratios never print.
    for number in ("27.5", "11.5", "55", "30.5", "66.5"):
        assert number not in out


def test_analyze_names_a_player_not_on_the_giving_roster(
        tmp_path, fixture_raw_dir, fixture_history_root, monkeypatch, capsys):
    from cornerstone import cli

    _analyze_repo(tmp_path, fixture_raw_dir, fixture_history_root, monkeypatch)
    code = cli.main(["analyze", "--client", "cpc", "--season", "2026", "--week", "6", "--chart", CHART_FIXTURE,
                     "--side", "4:4034", "--side", "12:10236", "--asker", "4", "--no-claude"])

    assert code == 2
    assert "Christian McCaffrey is no longer on Pukancun on 3." in capsys.readouterr().out


def test_analyze_of_a_week_with_no_chart_reads_the_superstar_from_the_saved_read_before(
        tmp_path, fixture_raw_dir, fixture_history_root, monkeypatch, capsys):
    import shutil

    from cornerstone import cli
    from league.paths import chart_read

    _analyze_repo(tmp_path, fixture_raw_dir, fixture_history_root, monkeypatch)
    # Week 6 has no saved read. The real week 8 read stands in as the saved read of week 5, the week before.
    before = chart_read(tmp_path / "data" / "nfl", "1QB0.5PPR4pt", 5)
    before.parent.mkdir(parents=True)
    shutil.copy(Path(__file__).parent / "fixtures" / "charts" / "read-week-08.json", before)
    # Trade W: roster 6 gives Washington and Walker, roster 12 gives Higgins, Tuten, and Pollard.
    code = cli.main(["analyze", "--client", "cpc", "--season", "2026", "--week", "6",
                     "--side", "6:9487,8151", "--side", "12:6801,12490,5967", "--asker", "12", "--no-claude"])

    out = capsys.readouterr().out
    assert code == 0
    assert out.count("Start letter: C") == 2
    assert "is a superstar, a top 8 player last week." in out


def test_analyze_needs_two_to_four_sides(tmp_path, fixture_raw_dir, fixture_history_root, monkeypatch, capsys):
    from cornerstone import cli

    _analyze_repo(tmp_path, fixture_raw_dir, fixture_history_root, monkeypatch)
    code = cli.main(["analyze", "--client", "cpc", "--season", "2026", "--week", "6", "--side", "4:7569", "--asker", "4", "--no-claude"])

    assert code == 2
    assert "Give --side two to four times, once for each roster." in capsys.readouterr().out


def test_analyze_grades_a_three_side_trade_with_a_destination_per_player(
        tmp_path, fixture_raw_dir, fixture_history_root, monkeypatch, capsys):
    from cornerstone import cli

    _analyze_repo(tmp_path, fixture_raw_dir, fixture_history_root, monkeypatch)
    code = cli.main(["analyze", "--client", "cpc", "--season", "2026", "--week", "6", "--chart", CHART_FIXTURE,
                     "--side", "4:7569@12", "--side", "12:10236@4,8146@7", "--side", "7:11628@4",
                     "--asker", "4", "--no-claude"])

    out = capsys.readouterr().out
    assert code == 0
    assert out.count("Start letter: ") == 3 and out.count("Final letter: ") == 3
    assert "  Gives: Dalton Kincaid to Pukancun on 3, Garrett Wilson to " in out
    assert "  Gets: Dalton Kincaid from " in out
    assert out.count("Fairness: ") == 1


def test_analyze_needs_a_destination_per_player_in_a_three_side_trade(
        tmp_path, fixture_raw_dir, fixture_history_root, monkeypatch, capsys):
    from cornerstone import cli

    _analyze_repo(tmp_path, fixture_raw_dir, fixture_history_root, monkeypatch)
    code = cli.main(["analyze", "--client", "cpc", "--season", "2026", "--week", "6", "--chart", CHART_FIXTURE,
                     "--side", "4:7569", "--side", "12:10236@4,8146@7", "--side", "7:11628@4",
                     "--asker", "4", "--no-claude"])

    assert code == 2
    assert "Give each player a destination, as PLAYER@ROSTER, in a trade of three or more sides." in (
        capsys.readouterr().out)


def test_analyze_prints_one_plain_line_for_a_trade_that_breaks_a_model_rule(
        tmp_path, fixture_raw_dir, fixture_history_root, monkeypatch, capsys):
    from cornerstone import cli

    _analyze_repo(tmp_path, fixture_raw_dir, fixture_history_root, monkeypatch)
    code = cli.main(["analyze", "--client", "cpc", "--season", "2026", "--week", "6", "--chart", CHART_FIXTURE,
                     "--side", "4:7569", "--side", "4:10236", "--asker", "4", "--no-claude"])

    out = capsys.readouterr().out
    assert code == 2
    assert out.strip() == "A proposed trade needs a different roster on each side"


def _live_analyze(tmp_path, fixture_raw_dir, fixture_history_root, fixture_nflverse_dir, chart_week6, monkeypatch,
                  fetch_history_week, unsaved_week=None):
    """Run analyze without --week. The live entry runs for real, with every fetch swapped for a fixture-backed one.

    An `unsaved_week` is removed from the history, so the live build must fetch it.
    """
    import shutil
    from datetime import datetime

    import pytest
    from cpc import cpc_client

    from cornerstone import cli
    from league import live
    from league.provider.sleeper import load_raw

    cli_root(tmp_path)
    shutil.copytree(fixture_history_root, tmp_path / "clients" / "cpc" / "data" / "2026" / "history")
    if unsaved_week is not None:
        shutil.rmtree(tmp_path / "clients" / "cpc" / "data" / "2026" / "history" / f"week-{unsaved_week:02d}")
    shutil.copytree(fixture_nflverse_dir, tmp_path / "data" / "nfl" / "cache" / "nflverse")
    for cached in (tmp_path / "data" / "nfl" / "cache" / "nflverse").iterdir():
        cached.touch()
    monkeypatch.chdir(tmp_path)
    fetched = datetime(2026, 10, 19, 9, 30, tzinfo=cpc_client().tz)
    real = live.live_snapshot
    monkeypatch.setattr(cli, "live_snapshot", lambda season, **kw: real(
        season, client=kw["client"], now=datetime(2026, 10, 19, 12, 0, tzinfo=kw["client"].tz),
        fetch_sleeper=lambda league_id: (load_raw(fixture_raw_dir), fetched),
        fetch_nflverse=lambda url: pytest.fail(f"network call to {url}"),
        fetch_history_week=fetch_history_week,
        read_chart=lambda nfl, start, week, lines, **_: chart_week6))
    return cli.main(["analyze", "--client", "cpc", "--season", "2026", "--side", "4:7569", "--side", "12:10236,8146",
                     "--asker", "4", "--no-claude"])


def _no_history_fetch(league_id, season, week, out_dir):
    raise AssertionError(f"network call for history week {week}")


def test_analyze_without_week_grades_the_live_snapshot_and_prints_the_as_of_line(
        tmp_path, fixture_raw_dir, fixture_history_root, fixture_nflverse_dir, chart_week6, monkeypatch, capsys):
    code = _live_analyze(tmp_path, fixture_raw_dir, fixture_history_root, fixture_nflverse_dir, chart_week6,
                         monkeypatch, _no_history_fetch)

    out = capsys.readouterr().out
    assert code == 0
    # The first line names the completed week, so the known-games line alone counts week 6.
    assert ("Week 6 of 2026. Chart week 6. Stats through week 5. Rosters fetched 2026-10-19T09:30-04:00.\n"
            "Known games of week 6: 14 read, 0 in progress, pending: usage 8 games.\n") in out
    assert "Refresh failed" not in out
    assert "Nico Collins" in out


@pytest.mark.parametrize("pending, line", [
    ({}, "Known games of week 6: 14 read, 0 in progress.\n"),
    ({"snaps": 9, "usage": 13},
     "Known games of week 6: 14 read, 0 in progress, pending: snaps 9 games, usage 13 games.\n"),
    ({"snaps": 1}, "Known games of week 6: 14 read, 0 in progress, pending: snaps 1 game.\n"),
])
def test_the_known_games_line_names_each_pending_count(
        fixture_raw_dir, fixture_history_root, chart_week6, capsys, pending, line):
    from cpc import cpc_client

    from cornerstone import cli
    from league.snapshot import KnownGames, load_snapshot

    snap = load_snapshot(fixture_raw_dir, fixture_history_root, chart_week6, client=cpc_client())
    known = KnownGames(week=6, games=14, pending=pending)
    cli._print_as_of(snap.model_copy(update={"as_of": snap.as_of.model_copy(update={"known_games": known})}))
    assert line in capsys.readouterr().out


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
    assert "Known games" not in out
    assert "Refresh failed, so the cache is old or absent: history.\n" in out


def _jacobs_repo(tmp_path, fixture_raw_dir, fixture_history_root, fixture_nflverse_dir, monkeypatch):
    """The analyze repo with the nflverse cache, the returns file, and the rosters from before the Jacobs trade."""
    import shutil

    _analyze_repo(tmp_path, fixture_raw_dir, fixture_history_root, monkeypatch)
    shutil.copytree(fixture_nflverse_dir, tmp_path / "data" / "nfl" / "cache" / "nflverse")
    shutil.copy(fixture_history_root.parent / "returns.json", tmp_path / "data" / "nfl" / "2026" / "returns.json")
    _set_back_the_jacobs_trade(tmp_path)


JACOBS_ARGS = ["analyze", "--client", "cpc", "--season", "2026", "--week", "6", "--chart", CHART_FIXTURE,
               "--side", "11:12490,8146", "--side", "12:5850,11834", "--asker", "12"]


def test_analyze_with_claude_prints_the_bullets_the_letters_and_the_verdict(
        tmp_path, fixture_raw_dir, fixture_history_root, fixture_nflverse_dir, monkeypatch, capsys):
    from fakes import FakeWriter

    from analyzer.analysis import AnalysisOut
    from cornerstone import cli
    from facts.writer import ANALYZER_CACHE_TTL, ANALYZER_EFFORT

    side = {"final_letter": "D", "reason": None, "cited": ["8146.ppg"],
            "bullets": ["Garrett Wilson scored 14.2 points per game before the trade.", "He moves.", "He starts."]}
    writer = FakeWriter([AnalysisOut.model_validate({
        "sides": [{**side, "roster_id": 11, "final_letter": "B", "reason": "Jacobs has not played."},
                  {**side, "roster_id": 12}],
        "verdict": {"choice": "counter", "reason": "Ask for one more starter."},
    })])
    _jacobs_repo(tmp_path, fixture_raw_dir, fixture_history_root, fixture_nflverse_dir, monkeypatch)
    code = cli.main(JACOBS_ARGS, writer=writer)

    out = capsys.readouterr().out
    assert code == 0
    # One analyzer call, with the analyzer's lifetime and effort.
    assert [(c.output_model, c.cache_ttl, c.effort) for c in writer.calls] == [
        (AnalysisOut, ANALYZER_CACHE_TTL, ANALYZER_EFFORT)]
    # The breakdown's letter is the rubric's. The final letter is Claude's, with its reason when it differs.
    assert "  Rubric letter: A\n" in out and "  Rubric letter: D\n" in out
    assert "  Final letter: B. Reason: Jacobs has not played.\n" in out
    assert "  Final letter: D\n" in out
    assert out.count("  Bullets:\n    - Garrett Wilson scored 14.2 points per game before the trade.\n"
                     "    - He moves.\n    - He starts.\n") == 2
    assert (out.index("Schedule: ") < out.index("Rubric letter: ") < out.index("Final letter: B")
            < out.index("Bullets:"))
    # The fairness reads Claude's letters, B and D, so the trade is still lopsided.
    assert ("\nVerdict for Amon-Ra Dawg Your Team: counter. Ask for one more starter. "
            "(differs from the rubric's default)\nFairness: Lopsided: Amon-Ra Dawg Your Team gives more.\n") in out


def test_analyze_with_claude_says_when_the_call_fell_back(
        tmp_path, fixture_raw_dir, fixture_history_root, fixture_nflverse_dir, monkeypatch, capsys, fake_writer):
    from cornerstone import cli

    _jacobs_repo(tmp_path, fixture_raw_dir, fixture_history_root, fixture_nflverse_dir, monkeypatch)
    # The fake has no answer, so each of the two attempts fails.
    code = cli.main(JACOBS_ARGS, writer=fake_writer)

    out = capsys.readouterr().out
    assert code == 0
    assert len(fake_writer.calls) == 2
    assert out.count("  Bullets: none\n") == 2
    assert "  Final letter: A\n" in out and "  Final letter: D\n" in out
    assert "The Claude call failed twice, so the rubric's letters and verdict stand." in out
    assert ("\nVerdict for Amon-Ra Dawg Your Team: decline. The trade costs the asking side too much.\n"
            "Fairness: Lopsided: Amon-Ra Dawg Your Team gives more.\n") in out


def _find_repo(tmp_path, fixture_raw_dir, fixture_history_root, fixture_nflverse_dir, monkeypatch):
    """The analyze repo with the nflverse cache and the returns file, as the find command reads them."""
    import shutil

    _analyze_repo(tmp_path, fixture_raw_dir, fixture_history_root, monkeypatch)
    shutil.copytree(fixture_nflverse_dir, tmp_path / "data" / "nfl" / "cache" / "nflverse")
    shutil.copy(fixture_history_root.parent / "returns.json", tmp_path / "data" / "nfl" / "2026" / "returns.json")


# The fixture chart lists 25 players, mostly stars, so no pair of the week 6 snapshot has a win-win on it.
# These rows add the quarterback of roster 2 and a quarterback of roster 3, at the trade values the API find
# rows give them, so rosters 2 and 3 have one win-win.
FIND_ROWS = {"6770": 22.0, "9228": 20.0}


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
    code = cli.main(["find", "--client", "cpc", "--season", "2026", "--week", "6", "--chart", _chart_with_rows(tmp_path),
                     "--asker", "2", "--partner", "3"])

    out = capsys.readouterr().out
    assert code == 0
    assert "Week 6 of 2026. Chart week 6. Stats through week 5." in out
    # Rosters 2 and 3 have one win-win with these rows: a swap of quarterbacks.
    assert out.endswith(
        "\n1. All You Need Is Love gives: Joe Burrow\n"
        "   Lil Fridge gives: Bryce Young\n"
        "Fairness: Good for both\n"
        "  All You Need Is Love: Young plays 100% of the snaps (up).\n"
        "  Lil Fridge: You keep 3 QBs in the top 24, and you get the better player, but Young plays 100% of the snaps "
        "(up).\n")
    assert "\n2. " not in out


def test_find_prints_one_line_when_no_swap_is_good_for_both(
        tmp_path, fixture_raw_dir, fixture_history_root, fixture_nflverse_dir, monkeypatch, capsys):
    from cornerstone import cli

    _find_repo(tmp_path, fixture_raw_dir, fixture_history_root, fixture_nflverse_dir, monkeypatch)
    code = cli.main(["find", "--client", "cpc", "--season", "2026", "--week", "6", "--chart", CHART_FIXTURE,
                     "--asker", "1", "--partner", "3"])

    out = capsys.readouterr().out
    assert code == 0
    assert out.endswith("\nNo swap between these rosters is good for both.\n")
    assert "Fairness:" not in out


def test_a_build_with_no_client_slug_exits_and_names_the_slug(tmp_path, monkeypatch, capsys, fake_writer):
    # AT-19: no build ships the wrong league.
    from cornerstone import cli

    cli_root(tmp_path)
    monkeypatch.chdir(tmp_path)
    code = cli.main(["build", "--season", "2026", "--week", "8", "--no-fetch"], writer=fake_writer)
    out = capsys.readouterr().out
    assert code == 2
    assert "--client" in out and "client slug" in out
    assert fake_writer.calls == []


def test_a_build_with_an_unknown_client_names_its_folder(tmp_path, monkeypatch, capsys):
    from cornerstone import cli

    cli_root(tmp_path)
    monkeypatch.chdir(tmp_path)
    assert cli.main(["page-json", "--client", "nope", "--season", "2026", "--week", "8"]) == 2
    assert "nope" in capsys.readouterr().out


def test_the_check_client_command_passes_the_cpc_client(capsys):
    from cornerstone import cli

    folder = Path(__file__).resolve().parents[3] / "clients" / "cpc"
    assert cli.main(["check-client", str(folder)]) == 0
    assert "passes the check" in capsys.readouterr().out


def test_the_check_client_command_names_an_unknown_key_and_the_file(tmp_path, capsys):
    # AT-20, the pipeline side: a copy of the CPC file with a typo under [values.analyzer].
    from cornerstone import cli

    cli_root(tmp_path)
    path = tmp_path / "clients" / "cpc" / "client.toml"
    path.write_text(path.read_text(encoding="utf-8").replace("finder = false", "finder = false\nfinderr = true"))
    assert cli.main(["check-client", str(path.parent)]) == 2
    out = capsys.readouterr().out
    assert "finderr" in out and str(path) in out


def test_the_settings_command_prints_the_derived_sizes(tmp_path, monkeypatch, capsys):
    from cornerstone import cli

    cli_root(tmp_path)
    monkeypatch.chdir(tmp_path)
    assert cli.main(["settings", "--client", "cpc", "--season", "2026"]) == 0
    out = capsys.readouterr().out
    assert "team_count: 12" in out
    assert "lines: {'QB': 24, 'RB': 36, 'WR': 36, 'TE': 24}" in out
    assert "star_rank_by_position: {'QB': 6, 'RB': 12, 'WR': 12, 'TE': 6}" in out
