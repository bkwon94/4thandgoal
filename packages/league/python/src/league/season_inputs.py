"""
The inputs of the season files: the snapshot, the projections ahead, the history, and the chart of one build.
The build makes them once after it saves the week, so the rankings and managers files read one load.
The module stands apart from models.py because it holds a Snapshot, and snapshot.py imports models.py.
It imports only the model module and the snapshot module, so each reader imports it with no upward import.
"""
from dataclasses import dataclass

from league.models import ChartValues, History, ProjectionsAhead
from league.snapshot import Snapshot


@dataclass(frozen=True, kw_only=True)
class SeasonInputs:
    """The four values the season files read together. Only the history is required.

    A saved week can lack its raw data, its projections ahead file, or its chart read. The value is then None, and
    the managers file goes out with no grade or no trade value.
    """
    history: History
    snapshot: Snapshot | None = None
    projections_ahead: ProjectionsAhead | None = None
    chart: ChartValues | None = None
