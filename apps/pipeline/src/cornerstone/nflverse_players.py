"""
Read the targets, target share, air yards share, and WOPR per player per week from the nflverse weekly player file.
The usage takes its targets and target share from this file, so the report counts targets as nflverse does.
"""
from pathlib import Path
from typing import NamedTuple

from cornerstone.models import UsageWeek
from cornerstone.nflverse_rows import _number, _rows
from cornerstone.numbers import round_half_up

# The positions the usage covers. A defender can draw a target on a trick play, but he has no usage.
# The Sleeper position map is the real gate, because only its skill players have a Sleeper ID in the gsis map.
# This filter only trims the file.
PLAYER_POSITIONS = ("QB", "RB", "WR", "TE")


class PlayerWeek(NamedTuple):
    """One row of the weekly player file. A share is in percent."""
    targets: int
    target_share: int
    air_yards_share: int
    wopr: int


def _percent(text: str) -> int:
    # nflverse writes a share as a fraction, such as 0.325. WOPR is on the same scale, so it takes the same factor.
    return int(round_half_up(100 * _number(text)))


def read_player_weeks(path: Path, first_week: int, week: int,
                      sleeper_of_gsis: dict[str, str]) -> dict[tuple[str, int], PlayerWeek] | None:
    """The rows of weeks `first_week` to `week` by Sleeper ID and week. None when the file has no row for week `week`.

    Only the regular season and the QB, RB, WR, and TE positions count. A player with no Sleeper ID in the gsis
    map is not in it.
    """
    has_week = False
    out = {}
    for row in _rows(path):
        if row["season_type"] != "REG" or not row["week"].isdigit():
            continue
        row_week = int(row["week"])
        has_week = has_week or row_week == week
        pid = sleeper_of_gsis.get(row["player_id"])
        if pid is None or row["position"] not in PLAYER_POSITIONS or not first_week <= row_week <= week:
            continue
        out[(pid, row_week)] = PlayerWeek(targets=int(_number(row["targets"])),
                                          target_share=_percent(row["target_share"]),
                                          air_yards_share=_percent(row["air_yards_share"]), wopr=_percent(row["wopr"]))
    return out if has_week else None


def with_player_weeks(usage: dict[str, list[UsageWeek]],
                      player_weeks: dict[tuple[str, int], PlayerWeek]) -> dict[str, list[UsageWeek]]:
    """The usage with the targets, the target share, the air yards share, and the WOPR of the file where it has a row.

    A week with no row in the file keeps our count, and its air yards share and WOPR stay None.
    """
    out = {}
    for pid, weeks in usage.items():
        out[pid] = []
        for u in weeks:
            row = player_weeks.get((pid, u.week))
            out[pid].append(u if row is None else u.model_copy(update=row._asdict()))
    return out
