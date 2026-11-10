"""
Tests for the cornerstone command line.
They run the real console script.
"""
import json
import subprocess
from pathlib import Path

from cpc import cli_root, cpc_client
from fakes import FakeJev


def _no_nflverse(season, week, player_ids, players):
    raise AssertionError("no test downloads an nflverse file")


def test_help_lists_commands():
    # The test asserts the return code itself.
    out = subprocess.run(["uv", "run", "cornerstone", "--help"], capture_output=True, text=True, check=False)
    assert out.returncode == 0
    for cmd in ("build", "publish", "rewrite", "history", "advisor-eval"):
        assert cmd in out.stdout


def test_the_cli_has_no_command_that_grades_a_trade_with_code():
    # The Advisor makes the call (ADR 0030), so no command prints a code grade of a trade.
    from cornerstone import cli

    commands = cli.build_parser()._subparsers._group_actions[0].choices
    assert "analyze" not in commands
    assert "find" not in commands


def test_build_stops_when_week_is_not_final(tmp_path, fixture_raw_dir, monkeypatch, capsys, fake_writer):
    import shutil

    from cornerstone import cli

    cli_root(tmp_path)
    shutil.copytree(fixture_raw_dir, tmp_path / "clients" / "cpc" / "data" / "2026" / "week-07" / "raw")
    monkeypatch.chdir(tmp_path)

    code = cli.main(["build", "--client", "cpc", "--season", "2026", "--week", "7", "--no-fetch"], writer=fake_writer,
                    jev=FakeJev())

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
                    provider=SleeperProvider(tmp_path / "cache", transport=httpx.MockTransport(no_fetch)),
                    jev=FakeJev())

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


def test_a_build_with_no_client_slug_exits_and_names_the_slug(tmp_path, monkeypatch, capsys, fake_writer):
    # AT-19: no build ships the wrong league.
    from cornerstone import cli

    cli_root(tmp_path)
    monkeypatch.chdir(tmp_path)
    code = cli.main(["build", "--season", "2026", "--week", "8", "--no-fetch"], writer=fake_writer, jev=FakeJev())
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


def test_the_check_client_command_names_sim_for_a_client_with_midseason_and_no_sim(tmp_path, capsys):
    # AT-48, on a copy of the CPC file, so the real file never changes.
    from cornerstone import cli

    cli_root(tmp_path)
    path = tmp_path / "clients" / "cpc" / "client.toml"
    path.write_text(path.read_text(encoding="utf-8").replace('"midseason", "sim", "eggs"]', '"midseason", "eggs"]', 1))
    assert cli.main(["check-client", str(path.parent)]) == 2
    out = capsys.readouterr().out
    assert "The midseason package needs the sim package. Add sim to the package list." in out


def test_the_midseason_command_writes_the_report_to_the_build_folder(tmp_path, monkeypatch, capsys):
    from fakes import FakeWriter
    from test_midseason import CLEAN_BUILD, CPC_PROVIDER, copy_cpc_week_8

    from cornerstone import cli

    cli_root(tmp_path)
    copy_cpc_week_8(cpc_client(root=tmp_path))
    monkeypatch.chdir(tmp_path)

    args = ["midseason", "--client", "cpc", "--season", "2026", "--week", "8"]
    assert cli.main(args, writer=FakeWriter(list(CLEAN_BUILD)), provider=CPC_PROVIDER) == 0
    out = tmp_path / "clients" / "cpc" / "build" / "2026" / "midseason.json"
    assert str(out) in capsys.readouterr().out
    assert json.loads(out.read_text(encoding="utf-8"))["week"] == 8
    assert not (tmp_path / "clients" / "cpc" / "published").exists()


def test_the_midseason_command_with_no_saved_week_exits_plainly(tmp_path, monkeypatch, capsys):
    from cornerstone import cli

    cli_root(tmp_path)
    monkeypatch.chdir(tmp_path)
    assert cli.main(["midseason", "--client", "cpc", "--season", "2026", "--week", "8"]) == 2
    assert "Run make build CLIENT=cpc WEEK=8 first." in capsys.readouterr().out


def test_the_settings_command_prints_the_derived_sizes(tmp_path, monkeypatch, capsys):
    from cornerstone import cli

    cli_root(tmp_path)
    monkeypatch.chdir(tmp_path)
    assert cli.main(["settings", "--client", "cpc", "--season", "2026"]) == 0
    out = capsys.readouterr().out
    assert "team_count: 12" in out
    assert "lines: {'QB': 24, 'RB': 36, 'WR': 36, 'TE': 24}" in out
    assert "star_rank_by_position: {'QB': 6, 'RB': 12, 'WR': 12, 'TE': 6}" in out


BAD_EGG_FILE = '[[eggs]]\nweek = 8\ntarget = "t"\naction = "tap3"\nconfirmed = true\n'


def test_the_egg_drop_command_with_a_bad_egg_file_exits_non_zero_and_names_the_problem(tmp_path, monkeypatch, capsys):
    from test_midseason import CPC_PROVIDER

    from cornerstone import cli

    cli_root(tmp_path)
    monkeypatch.chdir(tmp_path)
    egg_file = tmp_path / "2026.toml"
    egg_file.write_text(BAD_EGG_FILE, encoding="utf-8")
    args = ["egg-drop", "--client", "cpc", "--season", "2026", "--week", "8", "--eggs-file", str(egg_file)]
    assert cli.main(args, provider=CPC_PROVIDER) == 2
    out = capsys.readouterr().out
    assert str(egg_file) in out and "no page in egg 1" in out


def test_the_drop_after_the_publish_warns_on_a_bad_egg_file_with_the_same_message(tmp_path):
    from cornerstone.egg_drop import drop_after_publish

    egg_file = tmp_path / "2026.toml"
    egg_file.write_text(BAD_EGG_FILE, encoding="utf-8")
    line = drop_after_publish(cpc_client(root=tmp_path), 8, egg_file)
    assert line.startswith("WARNING: the egg drop of week 8 failed:")
    assert str(egg_file) in line and "no page in egg 1" in line
    assert "make egg-drop CLIENT=cpc WEEK=8" in line


def test_chart_reads_a_placed_png_once_and_prints_the_row_count(tmp_path, monkeypatch, capsys):
    import hashlib
    import io
    import json

    from PIL import Image

    from cornerstone import cli
    from league.models import ChartRead, ChartRow
    from league.paths import charts_dir

    cli_root(tmp_path)
    monkeypatch.chdir(tmp_path)
    parsed = ChartRead(week=6, date="2026-10-13", rows=[ChartRow(value=60.0, name="Some One", position="RB"),
                                                        *_pad_rows(50.0)])
    _save_chart(tmp_path, parsed)
    charts = charts_dir(tmp_path / "data" / "nfl", "1QB0.5PPR4pt")
    out = io.BytesIO()
    Image.new("RGB", (40, 40), "white").save(out, format="PNG")
    (charts / "week-06.png").write_bytes(out.getvalue())
    # The saved read names the hash of the placed PNG, so the command reads no image and calls no Claude.
    saved = parsed.model_dump(mode="json") | {"png_sha256": hashlib.sha256(out.getvalue()).hexdigest()}
    (charts / "week-06.json").write_text(json.dumps(saved))

    assert cli.main(["chart", "--client", "cpc", "--season", "2026", "--week", "6"], fetch_state=_sleeper_state("2026")) == 0
    assert "Read 101 chart rows" in capsys.readouterr().out
