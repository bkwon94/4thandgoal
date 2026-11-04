"""
Tests for the start script of the API container: the seed of a new volume, and the one-time move of an old volume.
Each test runs the real script with SEED and DATA set to temp folders, and the command `true`.
"""
import json
import subprocess
from pathlib import Path

ENTRYPOINT = Path(__file__).resolve().parents[1] / "deploy" / "entrypoint.sh"


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _seed(root: Path) -> Path:
    """A seed in the new layout: the CPC data of 2026 and the shared NFL data."""
    seed = root / "seed"
    _write(seed / "clients" / "cpc" / "data" / "2026" / "league.json", '{"league_id": "1"}')
    _write(seed / "clients" / "cpc" / "data" / "2026" / "history" / "week-01" / "matchups.json", "[]")
    _write(seed / "nfl" / "2026" / "returns.json", '{"5850": 9}')
    return seed


def _old_volume(root: Path) -> Path:
    """A volume that an image of the old layout seeded and the service then wrote to."""
    data = root / "data"
    _write(data / ".seeded", "")
    _write(data / "2026" / "history" / "week-01" / "matchups.json", "[]")
    # The live path wrote week 7 to the history after the seed.
    _write(data / "2026" / "history" / "week-07" / "matchups.json", '[{"live": true}]')
    _write(data / "2026" / "week-06" / "raw" / "state.json", "{}")
    _write(data / "2026" / "returns.json", '{"5850": 7}')
    _write(data / "cache" / "players.json", "{}")
    _write(data / "cache" / "nflverse" / "schedules.csv", "x")
    _write(data / "cache" / "charts" / "week-07.json", "{}")
    _write(data / "cache" / "results" / "grade-counts.json", '{"count": 3}')
    return data


def _boot(seed: Path, data: Path) -> subprocess.CompletedProcess:
    return subprocess.run(["sh", str(ENTRYPOINT), "true"], env={"SEED": str(seed), "DATA": str(data), "PATH": "/usr/bin:/bin"},
                          capture_output=True, text=True, check=True)


def test_a_new_volume_gets_the_seed_in_the_new_layout(tmp_path):
    seed, data = _seed(tmp_path), tmp_path / "data"
    _boot(seed, data)
    assert (data / "clients" / "cpc" / "data" / "2026" / "league.json").is_file()
    assert json.loads((data / "nfl" / "2026" / "returns.json").read_text()) == {"5850": 9}
    assert (data / ".seeded").is_file() and (data / ".layout-clients").is_file()


def test_an_old_volume_moves_to_the_new_layout_one_time(tmp_path):
    seed, data = _seed(tmp_path), _old_volume(tmp_path)
    out = _boot(seed, data).stdout
    assert "moves to the client layout" in out
    client = data / "clients" / "cpc" / "data" / "2026"
    # The data the service wrote after the seed survives the move.
    assert json.loads((client / "history" / "week-07" / "matchups.json").read_text()) == [{"live": True}]
    assert (client / "week-06" / "raw" / "state.json").is_file()
    # The seed adds the league file of the season, which the old layout had not.
    assert (client / "league.json").is_file()
    assert not (data / "2026").exists()
    # The NFL caches move to the shared NFL folder. The result cache stays, because fly.toml names its path.
    assert (data / "nfl" / "cache" / "players.json").is_file()
    assert (data / "nfl" / "cache" / "nflverse" / "schedules.csv").is_file()
    assert (data / "nfl" / "cache" / "charts" / "week-07.json").is_file()
    assert json.loads((data / "cache" / "results" / "grade-counts.json").read_text()) == {"count": 3}
    # The returns file of the image wins, as on every boot.
    assert json.loads((data / "nfl" / "2026" / "returns.json").read_text()) == {"5850": 9}
    assert (data / ".layout-clients").is_file()


def test_a_second_boot_moves_nothing_again(tmp_path):
    seed, data = _seed(tmp_path), _old_volume(tmp_path)
    _boot(seed, data)
    _write(data / "clients" / "cpc" / "data" / "2026" / "history" / "week-08" / "matchups.json", "[]")
    out = _boot(seed, data).stdout
    assert "moves to the client layout" not in out
    assert (data / "clients" / "cpc" / "data" / "2026" / "history" / "week-08" / "matchups.json").is_file()
    assert not (data / "2026").exists()


def test_a_client_new_to_the_seed_gets_its_data_on_a_seeded_volume(tmp_path):
    seed, data = _seed(tmp_path), tmp_path / "data"
    _boot(seed, data)
    _write(data / "clients" / "cpc" / "data" / "2026" / "history" / "week-08" / "matchups.json", "[]")
    # A later image holds a second client. The volume has the marker, so the first-boot copy does not run again.
    _write(seed / "clients" / "norcal" / "data" / "2026" / "league.json", '{"league_id": "2"}')
    (seed / "clients" / "empty" / "data").mkdir(parents=True)
    _boot(seed, data)
    assert json.loads((data / "clients" / "norcal" / "data" / "2026" / "league.json").read_text()) == {"league_id": "2"}
    # A client with no tracked data still gets its folder, so the link of the image to it never dangles.
    assert (data / "clients" / "empty" / "data").is_dir()
    # The data folder of a client on the volume stays as the service wrote it.
    assert (data / "clients" / "cpc" / "data" / "2026" / "history" / "week-08" / "matchups.json").is_file()
