"""
The package values model of each package that a client can take. The pipeline checks each client.toml with them.
league imports no core package, so the app gives the list to the client check of league.
"""
from analyzer.values import AnalyzerValues
from league.client import ValueModels
from league.values import LeagueValues
from managers.values import ManagersValues
from midseason.values import MidseasonValues
from rankings.values import RankingsValues
from sim.values import SimValues
from waiver.values import WaiverValues
from week.values import WeekValues

VALUE_MODELS: ValueModels = (LeagueValues, WeekValues, RankingsValues, ManagersValues, WaiverValues, AnalyzerValues,
                             SimValues, MidseasonValues)
