"""
Tests for the cornerstone command line.
They run the real console script.
"""
import subprocess


def test_help_lists_commands():
    out = subprocess.run(["uv", "run", "cornerstone", "--help"], capture_output=True, text=True)
    assert out.returncode == 0
    for cmd in ("build", "publish", "rewrite"):
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
    monkeypatch.setattr(cli, "claude_call", no_claude)
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'stub'\n")
    shutil.copytree(fixture_raw_dir, tmp_path / "data" / "2026" / "week-07" / "raw")
    monkeypatch.chdir(tmp_path)

    code = cli.main(["build", "--week", "7", "--season", "2026"])

    assert code == 2
    assert "not final" in capsys.readouterr().out
