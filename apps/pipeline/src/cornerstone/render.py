"""
Writes the files of a week: the page.json through the page writer of the week package, and the waiver file.
It also writes the season files of rankings and managers. The site renders the pages.
"""
import json
import logging
from collections.abc import Callable
from pathlib import Path

from cornerstone.managers import managers
from cornerstone.power_rankings import power_rankings
from league.files import write_bytes_atomic
from league.models import Blurb, Bundle, History, OddsResult, Team
from league.season_inputs import SeasonInputs
from league.standings_table import season_records
from week.page import download_bytes, week_site_dir, write_week_page

# The season file has its own version, so a change to one file never breaks the reader of the other.
RANKINGS_SCHEMA_VERSION = 1
# The managers file has its own version too. A new key in an entry does not need a bump.
MANAGERS_SCHEMA_VERSION = 1
# The waiver file has its own version too, so the site reads a week with or without it.
WAIVER_SCHEMA_VERSION = 1
# The keys of the odds object on a rankings row, in the order of the site type.
RANKINGS_ODDS_KEYS = ("playoff", "bye", "seed", "status")

log = logging.getLogger(__name__)


def render_waiver(bundle: Bundle, site_dir: Path) -> Path | None:
    """Write waiver.json beside page.json from the board in the bundle. None when the bundle has no board."""
    if bundle.waiver is None:
        return None
    body = {"schema_version": WAIVER_SCHEMA_VERSION, **bundle.waiver.model_dump(mode="json")}
    out = week_site_dir(site_dir, bundle) / "waiver.json"
    write_bytes_atomic(out, json.dumps(body, ensure_ascii=False, indent=2).encode("utf-8"))
    return out


def _saved_rankings(path: Path) -> tuple[dict[tuple[int, int], list[dict]], dict[tuple[int, int], dict]]:
    """The blurb sentences and the odds of each week and roster in the last season file.
    A row with no odds gives no odds. An unreadable file gives none of either."""
    if not path.exists():
        return {}, {}
    # A bad last file must not stop the new one. Its past blurbs and odds are lost, and the ranks are rebuilt.
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
        rows = {(w["week"], row["roster_id"]): row for w in body["weeks"] for row in w["rows"]}
        blurbs = {key: row["blurb"] for key, row in rows.items()}
        return blurbs, {key: row["odds"] for key, row in rows.items() if "odds" in row}
    except (OSError, ValueError, KeyError, TypeError) as err:
        log.warning("%s is unreadable, so past weeks lose their blurbs and odds: %s", path, err)
        return {}, {}


def render_rankings(
    history: History, season: int, teams: dict[int, Team], site_dir: Path,
    current: int | None = None, blurb: Blurb | None = None, odds: OddsResult | None = None,
) -> Path:
    """Write rankings.json for the season from every week from 1 to the history week. Rows are in rank order.
    The file holds ranks only: a reader sees "9th hardest schedule", and no one argues over a decimal.
    Week `current` gets the sentences of `blurb` by roster tag. The writer runs for one week only, so every
    other week keeps the blurb it has in the last file, or an empty list.
    Week `current` also gets the `odds` of each roster. A row with no odds in hand keeps the odds of the last
    file, or has no odds key, as the site reads the key as optional."""
    season_dir = site_dir / str(season)
    out = season_dir / "rankings.json"
    saved, saved_odds = _saved_rankings(out)
    # The engine gives the odds of one week only, so the other weeks keep what the last file has.
    fresh_odds = (
        {rid: t.model_dump(include=set(RANKINGS_ODDS_KEYS)) for rid, t in odds.teams.items()}
        if odds is not None else {}
    )
    # Each sentence keeps its fact IDs, as the site type asks. The roster tag only picks the row.
    fresh: dict[int, list[dict]] = {}
    for sentence in blurb.sentences if blurb is not None else []:
        if sentence.roster_id is not None:
            fresh.setdefault(sentence.roster_id, []).append(
                {"text": sentence.text, "fact_ids": list(sentence.fact_ids)},
            )
    weeks = []
    for week, rows in power_rankings(history, history.week).items():
        # The record of each week is the record as of that week, not as of the current one.
        records = season_records(history, week)
        weeks.append({"week": week, "rows": [
            {
                "roster_id": row.roster_id,
                "name": teams[row.roster_id].name,
                "wins": records[row.roster_id][0],
                "losses": records[row.roster_id][1],
                "rank": row.power_rank,
                "movement": row.movement,
                "components": row.ranks,
                "blurb": (
                    fresh.get(row.roster_id, []) if week == current and blurb is not None
                    else saved.get((week, row.roster_id), [])
                ),
            }
            for row in rows
        ]})
        # The odds key is optional on a row, so a row with no odds leaves the key out, not null.
        for row in weeks[-1]["rows"]:
            row_odds = (
                fresh_odds.get(row["roster_id"]) if week == current and odds is not None
                else saved_odds.get((week, row["roster_id"]))
            )
            if row_odds is not None:
                row["odds"] = row_odds
    body = {"schema_version": RANKINGS_SCHEMA_VERSION, "season": season, "weeks": weeks}
    season_dir.mkdir(parents=True, exist_ok=True)
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
