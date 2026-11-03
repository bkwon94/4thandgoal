"""
Read the rows of an nflverse CSV file and parse its values, with the team code map between nflverse and Sleeper.
The nflverse module and the nflverse_usage module both use these helpers.
"""
import csv
import gzip
from pathlib import Path


def _rows(path: Path):
    # Plain and gzip files share one reader, so the caller does not care which one it has.
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8", newline="") as f:
        yield from csv.DictReader(f)


def _number(text: str) -> float:
    # nflverse writes NA for a missing value. A negative value is real data and stays.
    return 0.0 if text in ("", "NA") else float(text)


# Sleeper and nflverse share every team code but this one.
NFLVERSE_TEAM = {"LAR": "LA"}


# The inverse of NFLVERSE_TEAM: the readers name teams as Sleeper does, so they join the rosters.
SLEEPER_TEAM = {nflverse: sleeper for sleeper, nflverse in NFLVERSE_TEAM.items()}


def _sleeper_team(code: str) -> str:
    return SLEEPER_TEAM.get(code, code)


def _yardline(text: str) -> float | None:
    # A missing yard line is unknown, not the goal line: 0 would put every such drop in the end zone.
    return None if text in ("", "NA") else float(text)
