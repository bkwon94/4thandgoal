"""
The What-if route of the season sim: the sim again with the set results of Your team, on the inputs of the draw in the
latest published week-NN/sim.json. It calls no Sleeper and keeps no answer, so each call runs the sim (decision 03).
"""
import json
import logging
import re
import time
from pathlib import Path

import anyio.from_thread
from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, Field

from analyzer.routes import ServedClient
from sim.season import SetResult, SimResult, SimStopped, rerun

logger = logging.getLogger(__name__)

router = APIRouter()

# The calls of each address in one minute. A manager who taps a result each 2 s for a full minute stays under it, and
# one address cannot hold the shared CPU of the machine for more than about a minute of sim work in each minute.
WHAT_IFS_PER_MINUTE = 30
# A client that went away gets this status. No reader gets it, so the code only marks the stop in the access log.
CLIENT_GONE = 499
_WEEK_FOLDER = re.compile(r"week-(\d+)")
# The sim file of each week folder. The shape of the file lives in sim.published, in the output layer, which the API may
# not import (ADR 0010). The file is the sim result with the names and its schema version, so the route reads it as a
# sim result and reads the version from the file.
SIM_FILE = "sim.json"


class WhatIfRequest(BaseModel):
    """The body of a What-if: Your team and its set results, at most one for each week left."""

    model_config = ConfigDict(populate_by_name=True)

    you: int
    set_results: list[SetResult] = Field(default_factory=list, alias="set")


def latest_week_sim(folder: Path, season: int) -> Path | None:
    """The sim file of the latest published week of `season` in the client folder `folder`, or None with none."""
    weeks = [(int(match.group(1)), path) for path in (folder / "published" / str(season)).glob(f"week-*/{SIM_FILE}")
             if (match := _WEEK_FOLDER.fullmatch(path.parent.name))]
    return max(weeks)[1] if weeks else None


def _week_file(folder: Path, season: int) -> tuple[int, SimResult]:
    """The schema version and the sim result of the latest published week sim file."""
    path = latest_week_sim(folder, season)
    if path is None:
        raise HTTPException(status_code=404, detail=f"No week of {season} has a sim file yet.")
    data = json.loads(path.read_text(encoding="utf-8"))
    return data["schema_version"], SimResult.model_validate(data)


@router.post("/sim/what-if", response_model=None)
def what_if(request: Request, body: WhatIfRequest, served: ServedClient) -> dict | Response:
    """The sim of the latest week again with the set results of Your team. It needs no passphrase.

    The route is a sync def, so FastAPI runs it in the thread pool and the event loop stays free. The sim checks
    between blocks of runs if the client went away, and then stops.
    """
    client = served.client
    if "sim" not in client.values.packages:
        raise HTTPException(status_code=404, detail=f"The client {client.slug} has no sim.")
    schema_version, file = _week_file(client.folder, client.values.latest_season)
    if body.you not in file.records:
        raise HTTPException(status_code=422, detail=f"Roster {body.you} is not a team of the league.")

    def gone() -> bool:
        # The route runs in a worker thread of anyio, so the check of the request runs back on the event loop.
        return anyio.from_thread.run(request.is_disconnected)

    started = time.monotonic()
    try:
        result = rerun(file, you=body.you, set_results=body.set_results, pages=[body.you], stop=gone)
    except SimStopped as stopped:
        logger.info("What-if of %s stopped after %d of %d runs: the client went away", client.slug, stopped.done,
                    stopped.runs)
        return Response(status_code=CLIENT_GONE)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    logger.info("What-if of %s ran %d runs in %.2f s, set weeks %s", client.slug, result.runs,
                time.monotonic() - started, sorted(r.week for r in body.set_results))
    dumped = result.model_dump(mode="json", include={"teams", "sample", "sample_weights"})
    return {
        "schema_version": schema_version, "season": result.season, "week": result.week, "runs": result.runs,
        "effective_runs": result.effective_runs, "you": body.you,
        "set": [r.model_dump(mode="json") for r in sorted(body.set_results, key=lambda r: r.week)],
        "teams": dumped["teams"], "sample": dumped["sample"], "sample_weights": dumped["sample_weights"],
        "page": result.pages[body.you].model_dump(mode="json"),
    }
