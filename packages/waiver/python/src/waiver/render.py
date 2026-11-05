"""
Writes the waiver file of a week, waiver.json beside page.json, from the waiver board in the bundle.
The waiver package owns the file and its schema version, and the site side of the package reads it (ADR 0011).
"""
import json
from pathlib import Path

from league.files import write_bytes_atomic
from league.models import Bundle
from league.paths import site_week_dir

# The waiver file has its own version, so the site reads a week with or without it.
WAIVER_SCHEMA_VERSION = 1


def render_waiver(bundle: Bundle, site_dir: Path) -> Path | None:
    """Write waiver.json beside page.json from the board in the bundle. None when the bundle has no board."""
    if bundle.waiver is None:
        return None
    body = {"schema_version": WAIVER_SCHEMA_VERSION, **bundle.waiver.model_dump(mode="json")}
    week_dir = site_week_dir(site_dir, bundle.data.season, bundle.data.week)
    week_dir.mkdir(parents=True, exist_ok=True)
    out = week_dir / "waiver.json"
    write_bytes_atomic(out, json.dumps(body, ensure_ascii=False, indent=2).encode("utf-8"))
    return out
