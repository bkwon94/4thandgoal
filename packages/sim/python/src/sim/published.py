"""
The shape of sim.json and its writer: the sim result with the team names, so the replay reads one file.
The pipeline owns the shape (ADR 0011), and the site side of the package reads it with its own schema.
"""
import json
from collections.abc import Mapping
from pathlib import Path

from league.files import write_bytes_atomic
from sim.season import SimResult

# The season file has its own version, so a change to one file never breaks the reader of another.
SIM_SCHEMA_VERSION = 1
SIM_FILE = "sim.json"


class SimFile(SimResult):
    """The whole of sim.json: the sim result and the name of each team."""
    schema_version: int = SIM_SCHEMA_VERSION
    names: dict[int, str]


def sim_file(result: SimResult, names: Mapping[int, str]) -> SimFile:
    return SimFile(**dict(result), names=dict(names))


def read_sim(season_build: Path) -> SimFile:
    return SimFile.model_validate_json((season_build / SIM_FILE).read_text(encoding="utf-8"))


def write_sim(sim: SimFile, build: Path) -> Path:
    """Write sim.json into the season folder of the build folder `build`. It never writes to published/.

    The file has no indent, because the 200 stored runs hold most of its bytes, and the page loads it whole.
    """
    out = build / str(sim.season) / SIM_FILE
    out.parent.mkdir(parents=True, exist_ok=True)
    body = json.dumps(sim.model_dump(mode="json"), ensure_ascii=False, separators=(",", ":")) + "\n"
    write_bytes_atomic(out, body.encode("utf-8"))
    return out
