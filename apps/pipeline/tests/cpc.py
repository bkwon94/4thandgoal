"""
The CPC client of the tests: the values of clients/cpc/client.toml and the League settings of the week 6 fixtures.
A test that writes files passes its own folder, and the client data and the NFL data then both sit in that folder.
"""
import shutil
from pathlib import Path

from league.client import Client, ValueModels, read_client_values
from league.paths import client_dir, league_file, nfl_dir
from league.provider.raw import RawLeague
from league.provider.sleeper import league_settings
from league.snapshot import Snapshot
from league.values import LeagueValues

ROOT = Path(__file__).resolve().parents[3]
FIXTURE_LEAGUE = Path(__file__).parent / "fixtures" / "2026" / "week-06" / "raw" / "league.json"
# The tests of one package run in the env of that package, with no other core package, so the fixture checks only
# the league table. test_rule_client checks each table of each client.toml with the full list of the pipeline.
FIXTURE_MODELS = (LeagueValues,)


def cpc_client(at: Path | None = None, root: Path = ROOT, models: ValueModels = FIXTURE_MODELS, **settings) -> Client:
    """The CPC client. Each keyword changes one League setting, such as playoff_spots=4.

    With no `at`, the client folder and the NFL data sit in the repo layout under `root`. With `at`, the client data
    sits at `at`/data/<season> and the NFL data at `at`/data, so a test folder keeps one short layout: the Returns
    file beside the history, and the caches at `at`/data/cache. A test of the app passes the models of the pipeline
    in `models`, so the client has the values of each package, such as midseason.
    """
    base = league_settings(RawLeague.model_validate_json(FIXTURE_LEAGUE.read_text(encoding="utf-8")))
    folder, nfl = (client_dir(root, "cpc"), nfl_dir(root)) if at is None else (at, at / "data")
    return Client(slug="cpc", folder=folder, nfl_dir=nfl, values=read_client_values(client_dir(ROOT, "cpc"), models),
                  settings=base.model_copy(update=settings))


def cli_root(root: Path) -> Path:
    """A repo root for a run of the CLI: the stub pyproject.toml, the CPC client.toml, and the saved league file of
    2026, so the League settings load with no fetch. The client data sits in `root`/clients/cpc/data."""
    (root / "pyproject.toml").write_text("[project]\nname = 'stub'\n")
    folder = client_dir(root, "cpc")
    league_file(folder, 2026).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(client_dir(ROOT, "cpc") / "client.toml", folder / "client.toml")
    shutil.copy(FIXTURE_LEAGUE, league_file(folder, 2026))
    (nfl_dir(root) / "2026").mkdir(parents=True, exist_ok=True)
    return root


def four_week(snapshot: Snapshot) -> Snapshot:
    """The snapshot with the 4-week rank measure of the weekly report in place of the season measure of the grade.

    The hand counts of many week 6 fixture tests read the points per game of weeks 2 to 5. Those tests check a rule
    that holds for both measures, such as a hole or the due-back step, so they keep their counts this way.
    """
    return snapshot.model_copy(update={"rank_measure": "recent"})
