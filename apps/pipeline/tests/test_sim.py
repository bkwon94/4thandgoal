"""
Tests for the season sim in the build of the midseason report: sim.json in the build folder of the season, from the real
saved CPC and NorCal data of 2026 week 8. The rules of the sim run on small leagues in packages/sim/python/tests.
"""
import gzip
import json
import shutil
from functools import partial
from pathlib import Path

import pytest
from cpc import ROOT
from fakes import FakeWriter
from test_midseason import prime_nflverse

from cornerstone.pipeline import run_midseason
from cornerstone.season_sim import schedule_file, week_sim
from cornerstone.value_models import VALUE_MODELS
from facts.writer import claude_call
from league.client import Client, load_client
from league.history import load_saved_weeks
from league.models import History
from league.nflverse import SCHEDULES_URL, cache_path
from league.paths import build_dir, client_dir, history_root, nflverse_cache_dir, week_dir
from league.provider.sleeper import fetch_settings

# The nflverse schedule of 2026, the same games as the real cache, which git ignores.
GAMES = Path(__file__).parent / "fixtures" / "nflverse" / "games.csv"


def _client(slug: str, at: Path) -> Client:
    """The real client `slug` with its client data at `at`: a copy of the saved history, week 8, and the published
    rankings of 2026. The NFL data sits at `at`/data with the schedule of the fixtures. No test writes under clients/."""
    real = load_client(ROOT, slug, 2026, fetch_settings, VALUE_MODELS)
    client = real.model_copy(update={"folder": at, "nfl_dir": at / "data"})
    data = real.folder / "data" / "2026"
    shutil.copytree(data / "history", history_root(client.folder, 2026))
    shutil.copytree(data / "week-08", week_dir(client.folder, 2026, 8))
    published = client.folder / "published" / "2026"
    published.mkdir(parents=True)
    shutil.copy(real.folder / "published" / "2026" / "rankings.json", published / "rankings.json")
    cache = nflverse_cache_dir(client.nfl_dir)
    cache.mkdir(parents=True)
    shutil.copy(GAMES, cache / "games.csv")
    # The report reads the injury report, the id map, and the expected points too. A fresh copy calls no network.
    prime_nflverse(client.nfl_dir)
    return client


def _call():
    """A fake writer with no answer, so each prose block gets its template blurb and no test calls Claude."""
    return partial(claude_call, writer=FakeWriter([]))


def _published_week_8_odds(slug: str) -> dict[int, int]:
    rankings = json.loads((client_dir(ROOT, slug) / "published" / "2026" / "rankings.json").read_text(encoding="utf-8"))
    week = next(week for week in rankings["weeks"] if week["week"] == 8)
    return {row["roster_id"]: row["odds"]["playoff"] for row in week["rows"]}


@pytest.fixture(scope="module")
def cpc_sim(tmp_path_factory) -> tuple[Client, Path]:
    """One build of the CPC report of week 8, shared by the tests that only read its sim.json."""
    client = _client("cpc", tmp_path_factory.mktemp("cpc"))
    run_midseason(2026, 8, _call(), client=client)
    return client, build_dir(client.folder) / "2026" / "sim.json"


def test_the_build_writes_sim_json_with_200_runs_and_the_odds_of_10000_runs(cpc_sim):
    # AT-37.
    _, path = cpc_sim
    sim = json.loads(path.read_text(encoding="utf-8"))
    assert (sim["schema_version"], sim["season"], sim["week"], sim["runs"]) == (1, 2026, 8, 10_000)
    assert len(sim["sample"]) == 200
    assert sim["weeks"] == list(range(9, 18)) and sim["bracket_weeks"] == [15, 16, 17]
    assert len(sim["teams"]) == 12 and sim["names"]["2"] == "All You Need Is Love"
    team = sim["teams"]["2"]
    assert {"playoff", "bye", "final", "title", "seeds", "final_wins", "mean_wins"} <= set(team)
    assert sum(sum(t["seeds"].values()) for t in sim["teams"].values()) == pytest.approx(600, abs=1)
    assert sum(t["title"] for t in sim["teams"].values()) == pytest.approx(100, abs=1)
    # The projections reach the bracket weeks, so a playoff week has a shift too.
    assert any(shifts[-1] for shifts in sim["parameters"]["shifts"].values())
    assert len(gzip.compress(path.read_bytes())) <= 50_000


def test_two_builds_give_the_same_sim_json_byte_for_byte(cpc_sim):
    # AT-3.
    client, path = cpc_sim
    first = path.read_bytes()
    run_midseason(2026, 8, _call(), client=client)
    assert path.read_bytes() == first


def test_in_a_cpc_run_seed_1_meets_the_lowest_seed_left_in_the_semifinal(cpc_sim):
    # CPC reseeds after round 1 (AT-38 of the bracket rule, story 46).
    _, path = cpc_sim
    sim = json.loads(path.read_text(encoding="utf-8"))
    assert sim["parameters"]["reseed"] is True
    for run in sim["sample"]:
        seed = {rid: n for n, rid in enumerate(run["table"][:6], start=1)}
        first_round, semifinal = run["bracket"][0], run["bracket"][1]
        winners = {a if run["scores"][str(a)][6] >= run["scores"][str(b)][6] else b for a, b in first_round}
        left = [run["table"][0], run["table"][1], *winners]
        lowest = max(left, key=seed.__getitem__)
        assert (run["table"][0], lowest) in [tuple(pair) for pair in semifinal]


def test_the_report_takes_the_playoff_odds_of_the_sim(cpc_sim):
    # The app wires the sim into the port of midseason, so the report and sim.json give one number.
    _, path = cpc_sim
    sim = json.loads(path.read_text(encoding="utf-8"))
    report = json.loads((path.parent / "midseason.json").read_text(encoding="utf-8"))
    state = report["acts"][0]["chapters"][0]["facts"]["teams"]
    assert {row["roster_id"]: row["playoff_odds"] for row in state} == {
        int(rid): team["playoff"] for rid, team in sim["teams"].items()}


def test_the_build_leaves_the_published_rankings_unchanged(cpc_sim):
    # AT-51.
    client, _ = cpc_sim
    published = client.folder / "published" / "2026" / "rankings.json"
    real = client_dir(ROOT, "cpc") / "published" / "2026" / "rankings.json"
    assert published.read_bytes() == real.read_bytes()
    assert sorted(path.name for path in published.parent.iterdir()) == ["rankings.json"]


@pytest.mark.parametrize("slug", ["cpc", "norcal"])
def test_the_playoff_odds_of_the_sim_are_within_2_points_of_the_published_week_8_odds(slug, tmp_path):
    # AT-38: the sim keeps the draw of the weekly odds in its own package, and this test holds the two together.
    client = _client(slug, tmp_path)
    history = History(week=8, weeks=load_saved_weeks(history_root(client.folder, 2026), 8, client.settings.points_key))
    sim = week_sim(2026, 8, history, client=client)
    assert sim is not None
    published = _published_week_8_odds(slug)
    gaps = {rid: abs(sim.teams[rid].playoff - odds) for rid, odds in published.items()}
    print(f"{slug}: largest gap {max(gaps.values())} points, roster {max(gaps, key=gaps.__getitem__)}")
    assert max(gaps.values()) <= 2


def test_the_sim_reads_the_schedule_at_the_one_cache_path_of_the_nflverse_readers(tmp_path):
    # The chapters of the report read the same file through cache_path, so the build keeps one copy of it.
    cache = nflverse_cache_dir(tmp_path)
    cache.mkdir(parents=True)
    shutil.copy(GAMES, cache_path(cache, SCHEDULES_URL, 2026))
    assert schedule_file(tmp_path, 2026) == cache_path(cache, SCHEDULES_URL, 2026)
