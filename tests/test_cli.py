"""
Tests for the cornerstone command line.
They run the real console script.
"""
import subprocess


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
