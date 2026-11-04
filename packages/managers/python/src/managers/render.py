"""
Writes managers.json, the season file of the managers: one entry per roster through the history week.
The site reads it with its own schema in @cpc/managers.
"""
import json
from pathlib import Path

from league.files import write_bytes_atomic
from league.models import Team
from league.season_inputs import SeasonInputs
from managers.entries import managers

# The managers file has its own version, so a change to it never breaks the reader of another file.
# A new key in an entry does not need a bump.
MANAGERS_SCHEMA_VERSION = 1


def render_managers(
    inputs: SeasonInputs, season: int, teams: dict[int, Team], site_dir: Path, players: dict[str, dict] | None = None,
    *, roster_slots: list[str] | None = None, week_awards: dict[int, list[tuple[str, int]]] | None = None,
    median_game: bool = True,
) -> Path:
    """Write managers.json for the season: one entry per roster through the history week of the `inputs`, in roster
    id order. The `inputs` give the grade. The players and the keywords give the names, the bench, and the awards.
    With `median_game` off, no week of an entry holds a median."""
    season_dir = site_dir / str(season)
    out = season_dir / "managers.json"
    entries = managers(inputs, teams, players, roster_slots=roster_slots, week_awards=week_awards,
                       median_game=median_game)
    body = {
        "schema_version": MANAGERS_SCHEMA_VERSION, "season": season, "through": inputs.history.week,
        "managers": [entry.model_dump(mode="json") for entry in entries],
    }
    season_dir.mkdir(parents=True, exist_ok=True)
    write_bytes_atomic(out, json.dumps(body, ensure_ascii=False, indent=2).encode("utf-8"))
    return out
