"""
Writes the files of a week: the page.json through the page writer of the week package, and the waiver file.
It also writes the season file of managers. The rankings package writes rankings.json. The site renders the pages.
"""
import json
import logging
from collections.abc import Callable
from pathlib import Path

from cornerstone.managers import managers
from league.files import write_bytes_atomic
from league.models import Blurb, Bundle, Team
from league.season_inputs import SeasonInputs
from week.page import download_bytes, week_site_dir, write_week_page

# The managers file has its own version, so a change to one file never breaks the reader of another. A new key in an
# entry does not need a bump. The rankings package writes rankings.json with its own version.
MANAGERS_SCHEMA_VERSION = 1
# The waiver file has its own version too, so the site reads a week with or without it.
WAIVER_SCHEMA_VERSION = 1

log = logging.getLogger(__name__)


def render_waiver(bundle: Bundle, site_dir: Path) -> Path | None:
    """Write waiver.json beside page.json from the board in the bundle. None when the bundle has no board."""
    if bundle.waiver is None:
        return None
    body = {"schema_version": WAIVER_SCHEMA_VERSION, **bundle.waiver.model_dump(mode="json")}
    out = week_site_dir(site_dir, bundle) / "waiver.json"
    write_bytes_atomic(out, json.dumps(body, ensure_ascii=False, indent=2).encode("utf-8"))
    return out


def render_managers(
    inputs: SeasonInputs, season: int, teams: dict[int, Team], site_dir: Path, players: dict[str, dict] | None = None,
    *, roster_slots: list[str] | None = None, week_awards: dict[int, list[tuple[str, int]]] | None = None,
) -> Path:
    """Write managers.json for the season: one entry per roster through the history week of the `inputs`, in roster
    id order. The `inputs` give the grade. The players and the keywords give the names, the bench, and the awards."""
    season_dir = site_dir / str(season)
    out = season_dir / "managers.json"
    body = {
        "schema_version": MANAGERS_SCHEMA_VERSION, "season": season, "through": inputs.history.week,
        "managers": [
            entry.model_dump(mode="json")
            for entry in managers(inputs, teams, players, roster_slots=roster_slots, week_awards=week_awards)
        ],
    }
    season_dir.mkdir(parents=True, exist_ok=True)
    write_bytes_atomic(out, json.dumps(body, ensure_ascii=False, indent=2).encode("utf-8"))
    return out


def render_week(
    bundle: Bundle,
    blurbs: dict[str, Blurb],
    site_dir: Path,
    fetch_bytes: Callable[[str], bytes | None] = download_bytes,
) -> Path:
    """Save the images of a week and write its page.json and its waiver.json. Return the page.json path."""
    page = write_week_page(bundle, blurbs, site_dir, fetch_bytes)
    render_waiver(bundle, site_dir)
    return page
