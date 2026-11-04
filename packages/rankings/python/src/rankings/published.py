"""
Writes rankings.json, the season file of the rankings: the power rankings of every week, the record, the blurb, and the
odds of each row. The site side of the rankings package reads it with its own schema.
"""
import json
import logging
from pathlib import Path

from league.files import write_bytes_atomic
from league.models import Blurb, History, OddsResult, Team
from league.standings_table import season_records
from rankings.power_rankings import power_rankings

# The season file has its own version, so a change to one file never breaks the reader of another.
RANKINGS_SCHEMA_VERSION = 1
# The keys of the odds object on a rankings row, in the order of the site type.
RANKINGS_ODDS_KEYS = ("playoff", "bye", "seed", "status")

log = logging.getLogger(__name__)


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
    current: int | None = None, blurb: Blurb | None = None, odds: OddsResult | None = None, *,
    median_game: bool = True,
) -> Path:
    """Write rankings.json for the season from every week from 1 to the history week. Rows are in rank order.
    The file holds ranks only: a reader sees "9th hardest schedule", and no one argues over a decimal.
    Week `current` gets the sentences of `blurb` by roster tag. The writer runs for one week only, so every
    other week keeps the blurb it has in the last file, or an empty list.
    Week `current` also gets the `odds` of each roster. A row with no odds in hand keeps the odds of the last
    file, or has no odds key, as the site reads the key as optional.
    With `median_game` off, the ranks and the record of each row count one game a week."""
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
    for week, rows in power_rankings(history, history.week, median_game=median_game).items():
        # The record of each week is the record as of that week, not as of the current one.
        records = season_records(history, week, median_game=median_game)
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
