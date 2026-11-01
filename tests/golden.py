"""
Builds the four golden files from the week 6 fixtures with no Claude call and no network call.
Run it as a script to rewrite the saved copies under tests/fixtures/golden/.
"""
import json
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from cornerstone.config import cornerstone_config
from cornerstone.history import history_root
from cornerstone.pipeline import run_build, week_dir
from cornerstone.writer import WriterError
from fakes import fixture_nflverse, no_claims, no_news

FIXTURES = Path(__file__).parent / "fixtures"
GOLDEN_DIR = FIXTURES / "golden"
GOLDEN_FILES = ("facts.json", "page.json", "rankings.json", "managers.json")
ET = ZoneInfo("America/New_York")
# The league config the builds and fetches of these tests read.
CONFIG = cornerstone_config()
# Both times are fixed, so the build reads no clock and no file time.
STARTED = datetime(2026, 10, 20, 12, 0, tzinfo=ET)
FETCHED = "2026-10-20T11:56:00-04:00"


def _no_claude(system, user, model):
    # Every attempt fails, so every chapter gets its template blurb and the page is stable.
    raise WriterError("the golden build makes no Claude call")


def build_golden(repo: Path, cache: Path) -> dict[str, Path]:
    """Build week 6 into `repo` from the raw fixtures and the week 1 to 5 history. The nflverse copies go under
    `cache`. It returns the four files by name."""
    raw = week_dir(repo, 2026, 6) / "raw"
    shutil.copytree(FIXTURES / "2026" / "week-06" / "raw", raw)
    # The fixture has no fetch time, and the fallback reads the file time of the copy, which changes per checkout.
    (raw / "fetched.json").write_text(json.dumps({"transactions": FETCHED}), encoding="utf-8")
    shutil.copytree(FIXTURES / "2026" / "history", history_root(repo, 2026))
    page = run_build(repo, 2026, 6, _no_claude, fetch=False, news=no_news, fetch_bytes=lambda url: None,
                     nflverse=fixture_nflverse(cache), research=no_claims, started=STARTED, config=CONFIG)
    season = repo / "site" / "2026"
    return {"facts.json": week_dir(repo, 2026, 6) / "facts.json", "page.json": page,
            "rankings.json": season / "rankings.json", "managers.json": season / "managers.json"}


def main() -> int:
    GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as repo, tempfile.TemporaryDirectory() as cache:
        for name, path in build_golden(Path(repo), Path(cache)).items():
            shutil.copyfile(path, GOLDEN_DIR / name)
            print(f"wrote {GOLDEN_DIR / name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
