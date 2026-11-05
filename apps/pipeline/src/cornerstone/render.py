"""
Writes the files of a week: the page.json through the page writer of the week package, and the waiver file
through the waiver package. The rankings and the managers packages each write their own season file.
"""
import logging
from collections.abc import Callable
from pathlib import Path

from league.models import Blurb, Bundle
from waiver.render import render_waiver
from week.page import download_bytes, write_week_page

log = logging.getLogger(__name__)


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
