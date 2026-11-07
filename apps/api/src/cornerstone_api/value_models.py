"""
The package values model of each package that the API takes. The API checks each client.toml with them at start.
The API lists no other core package, so the pipeline check and the site build check the tables of the others.
"""
from analyzer.values import AnalyzerValues
from eggs.values import EggsValues
from league.client import ValueModels
from league.values import LeagueValues

VALUE_MODELS: ValueModels = (LeagueValues, AnalyzerValues, EggsValues)
