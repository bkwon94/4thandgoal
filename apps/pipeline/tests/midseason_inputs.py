"""
The inputs of the midseason build beyond the history: the saved raw files of the report week, the nflverse files that
the chapters read, and a provider with the CPC rosters of 2026-11-05. Each is real data of the repo.
"""
import shutil
from pathlib import Path

from fakes import NFLVERSE_FIXTURES, FixtureProvider

from league.client import Client
from league.nflverse import SCHEDULES_URL, cache_path
from league.paths import client_dir, nflverse_cache_dir, raw_dir

ROOT = Path(__file__).resolve().parents[3]
CPC_DATA = client_dir(ROOT, "cpc") / "data" / "2026"
MIDSEASON_FIXTURES = Path(__file__).parent / "fixtures" / "midseason"
# The rosters of CPC from Sleeper on 2026-11-05, after the week 9 moves. The Buccaneers DEF was dropped by then.
ROSTERS_NOW = MIDSEASON_FIXTURES / "cpc-rosters-now.json"


def copy_report_inputs(client: Client, week: int = 8) -> None:
    """Copy the raw files of `week` and the nflverse files into the client folder of a test.

    The nflverse files are the injury report, the expected points, and the id map of the CPC players, cut from the
    files of 2026-11-05, and the schedules of the nflverse fixtures. Each copy is fresh, so the build fetches none.
    """
    shutil.copytree(CPC_DATA / f"week-{week:02d}" / "raw", raw_dir(client.folder, 2026, week))
    cache = nflverse_cache_dir(client.nfl_dir)
    shutil.copytree(MIDSEASON_FIXTURES / "nflverse", cache, dirs_exist_ok=True)
    shutil.copy(NFLVERSE_FIXTURES / "games.csv", cache_path(cache, SCHEDULES_URL, 2026))


def provider_now(tmp_path: Path) -> FixtureProvider:
    """A provider whose live rosters are the CPC rosters of 2026-11-05, with the other raw files of week 8."""
    now = tmp_path / "now"
    shutil.copytree(CPC_DATA / "week-08" / "raw", now)
    shutil.copy(ROSTERS_NOW, now / "rosters.json")
    return FixtureProvider(raw_dir=now)
