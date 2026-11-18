"""
The shapes of the sim files and their writers: the season file of the midseason report and the week file of the sim
page, each the sim result with the team names. The pipeline owns the shapes (ADR 0011), and the site side reads them.
"""
import json
from collections.abc import Mapping
from pathlib import Path

from pydantic import Field

from league.files import write_bytes_atomic
from league.paths import site_week_dir
from sim.page import SimPage
from sim.season import SimResult

# The season file has its own version, so a change to one file never breaks the reader of another.
SIM_SCHEMA_VERSION = 1
WEEK_SIM_SCHEMA_VERSION = 1
SIM_FILE = "sim.json"


class SimFile(SimResult):
    """The whole of sim.json: the sim result and the name of each team."""
    schema_version: int = SIM_SCHEMA_VERSION
    names: dict[int, str]
    # The season file keeps the shape that the midseason replay reads, so it leaves out the effective runs, the run
    # weights, the pages, and the league fact.
    effective_runs: int | None = Field(default=None, exclude=True)
    sample_weights: list[float] = Field(default_factory=list, exclude=True)
    pages: dict[int, SimPage] = Field(default_factory=dict, exclude=True)
    fact: str | None = Field(default=None, exclude=True)


class WeekSimFile(SimResult):
    """The whole of week-NN/sim.json: the sim result of the week with a page for each team, and the name of each
    team. The sim page reads the latest week, and the What-if reads the inputs of its draw."""
    schema_version: int = WEEK_SIM_SCHEMA_VERSION
    names: dict[int, str]


def sim_file(result: SimResult, names: Mapping[int, str]) -> SimFile:
    return SimFile(**dict(result), names=dict(names))


def week_sim_file(result: SimResult, names: Mapping[int, str]) -> WeekSimFile:
    return WeekSimFile(**dict(result), names=dict(names))


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


def read_week_sim(path: Path) -> WeekSimFile:
    return WeekSimFile.model_validate_json(path.read_text(encoding="utf-8"))


def write_week_sim(sim: WeekSimFile, build: Path) -> Path:
    """Write sim.json into the week folder of the build folder `build`, beside page.json. It never writes to
    published/. The file has no indent, as the season file has none."""
    out = site_week_dir(build, sim.season, sim.week) / SIM_FILE
    out.parent.mkdir(parents=True, exist_ok=True)
    body = json.dumps(sim.model_dump(mode="json"), ensure_ascii=False, separators=(",", ":")) + "\n"
    write_bytes_atomic(out, body.encode("utf-8"))
    return out
