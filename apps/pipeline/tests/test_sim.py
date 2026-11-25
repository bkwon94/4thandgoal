"""
Tests for the season sim in the build of the midseason report: sim.json in the build folder of the season, from the real
saved CPC and NorCal data of 2026 week 8. The rules of the sim run on small leagues in packages/sim/python/tests.
Each client and each build reads the fixture provider, so no test calls Sleeper (ADR 0015).
"""
import gzip
import hashlib
import json
import re
import shutil
import sys
from collections import Counter
from functools import partial
from pathlib import Path

import pytest
from conftest import SAVED, saved_repo
from cpc import ROOT, cpc_client
from fakes import FakeWriter, FixtureProvider, no_news
from test_midseason import CPC_PROVIDER, prime_nflverse

from cornerstone.pipeline import make_bundle, run_midseason, run_sim_fixtures, run_week_sim
from cornerstone.season_sim import schedule_file, week_inputs, week_sim
from cornerstone.value_models import VALUE_MODELS
from facts.writer import claude_call
from league.client import Client, load_client
from league.history import load_saved_weeks
from league.models import History
from league.nflverse import SCHEDULES_URL, cache_path
from league.paths import build_dir, client_dir, history_root, nflverse_cache_dir, week_dir
from rankings.published import render_rankings
from sim.season import SetResult, SimResult, rerun, season_sim, weekly_odds
from sim.tunables import LEVEL_SHRINK_WEEKS

# The rejection reference of a What-if lives with the tests of the sim package, which own the method.
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "packages" / "sim" / "python" / "tests"))
from rejection import rejection_odds

# The nflverse schedule of 2026, the same games as the real cache, which git ignores.
GAMES = Path(__file__).parent / "fixtures" / "nflverse" / "games.csv"


def _client(slug: str, at: Path) -> Client:
    """The real client `slug` with its client data at `at`: a copy of the saved history, week 8, and the published
    rankings of 2026. The NFL data sits at `at`/data with the schedule of the fixtures. No test writes under clients/."""
    data = client_dir(ROOT, slug) / "data" / "2026"
    provider = FixtureProvider(raw_dir=data / "week-08" / "raw", history_root=data / "history")
    real = load_client(ROOT, slug, 2026, provider.fetch_settings, VALUE_MODELS)
    client = real.model_copy(update={"folder": at, "nfl_dir": at / "data"})
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
    run_midseason(2026, 8, _call(), client=client, provider=CPC_PROVIDER)
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
    run_midseason(2026, 8, _call(), client=client, provider=CPC_PROVIDER)
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


def test_the_sim_reads_the_schedule_at_the_one_cache_path_of_the_nflverse_readers(tmp_path):
    # The chapters of the report read the same file through cache_path, so the build keeps one copy of it.
    cache = nflverse_cache_dir(tmp_path)
    cache.mkdir(parents=True)
    shutil.copy(GAMES, cache_path(cache, SCHEDULES_URL, 2026))
    assert schedule_file(tmp_path, 2026) == cache_path(cache, SCHEDULES_URL, 2026)


@pytest.fixture(scope="module")
def cpc_week_10(tmp_path_factory):
    """The weekly build of CPC 2026 week 10 from the saved data, and the sim of the same week from its own load.

    The NFL schedule of the fixtures sits in the cache, so the sim calls no network.
    """
    repo = saved_repo(tmp_path_factory.mktemp("repo"), 10)
    client = cpc_client(at=repo)
    cache = nflverse_cache_dir(client.nfl_dir)
    cache.mkdir(parents=True)
    shutil.copy(GAMES, cache_path(cache, SCHEDULES_URL, 2026))
    bundle, _ = make_bundle(2026, 10, news=no_news, client=client)
    history = History(week=10, weeks=load_saved_weeks(history_root(client.folder, 2026), 10, client.settings.points_key))
    sim = week_sim(2026, 10, history, client=client)
    assert sim is not None
    return client, bundle, history, sim


@pytest.mark.skipif(not (SAVED / "week-10" / "raw").is_dir(), reason="no saved week 10 data")
def test_the_weekly_build_takes_the_odds_and_the_swings_of_the_sim_at_10000_runs(cpc_week_10):
    # AT-2: one engine gives the odds of the week.
    _, bundle, _, sim = cpc_week_10
    assert sim.runs == 10_000
    assert bundle.odds == weekly_odds(sim)
    assert len(bundle.odds.swings) == 6


@pytest.mark.skipif(not (SAVED / "week-10" / "raw").is_dir(), reason="no saved week 10 data")
def test_each_odds_fact_of_the_week_quotes_the_number_of_the_sim(cpc_week_10):
    # AT-3.
    _, bundle, _, sim = cpc_week_10
    facts = bundle.sheet.facts
    for rid, team in sim.teams.items():
        text = facts[f"ODDS.{rid}"].text
        if team.status == "open":
            assert f"in about {team.playoff}% of runs, with a bye in {team.bye}%" in text, text
        else:
            assert ("clinched" if team.status == "in" else "out of the playoff race") in text, text
    swings = {(s.a, s.b): s for s in sim.swings}
    for fid, fact in facts.items():
        if fid.startswith("SW."):
            a, b = (int(x) for x in fid[3:].split("v"))
            for rid, win, loss in ((a, swings[(a, b)].a_win, swings[(a, b)].a_loss),
                                   (b, swings[(a, b)].b_win, swings[(a, b)].b_loss)):
                if sim.teams[rid].status == "open" and abs(win - loss) >= 5:
                    assert f"at {win}%, a loss at {loss}%" in fact.text, fact.text


@pytest.mark.skipif(not (SAVED / "week-10" / "raw").is_dir(), reason="no saved week 10 data")
def test_rankings_json_takes_the_week_10_odds_of_the_sim_and_keeps_the_odds_of_weeks_1_to_9(cpc_week_10, tmp_path):
    # AT-2 and AT-4. The site folder starts from the published file, as the weekly build does.
    client, bundle, history, sim = cpc_week_10
    published = client_dir(ROOT, "cpc") / "published" / "2026" / "rankings.json"
    (tmp_path / "2026").mkdir()
    shutil.copy(published, tmp_path / "2026" / "rankings.json")
    out = render_rankings(history, 2026, bundle.data.teams, tmp_path, 10, None, bundle.odds,
                          median_game=client.settings.median_game)

    def odds(path: Path) -> dict[int, dict[int, dict]]:
        body = json.loads(path.read_text(encoding="utf-8"))
        return {w["week"]: {row["roster_id"]: row.get("odds") for row in w["rows"]} for w in body["weeks"]}

    before, after = odds(published), odds(out)
    assert {w: after[w] for w in range(1, 10)} == {w: before[w] for w in range(1, 10)}
    assert {rid: row["playoff"] for rid, row in after[10].items()} == {rid: t.playoff for rid, t in sim.teams.items()}
    assert {rid: row["bye"] for rid, row in after[10].items()} == {rid: t.bye for rid, t in sim.teams.items()}


# Bo Girds, the What-if team of the acceptance tests.
BO_GIRDS = 6


def _week_10_what_if(cpc_week_10, held: list[SetResult]):
    client, _, history, _ = cpc_week_10
    inputs = week_inputs(2026, 10, history, client=client)
    assert inputs is not None
    sim = season_sim(inputs.scores, inputs.records, inputs.remaining, season=2026, week=10, settings=client.settings,
                     projected=inputs.projected, you=BO_GIRDS, set_results=held)
    return client, inputs, sim


@pytest.mark.skipif(not (SAVED / "week-10" / "raw").is_dir(), reason="no saved week 10 data")
def test_a_set_loss_below_the_median_agrees_with_an_exact_rejection_reference(cpc_week_10):
    # AT-11. The reference draws plain runs of the same model and keeps the runs where Bo Girds loses week 11 and
    # misses the median. At about 9,000 effective runs and 30,000 kept runs the sample error of the gap is 0.6 points.
    held = [SetResult(week=11, game="loss", median="below")]
    client, inputs, sim = _week_10_what_if(cpc_week_10, held)
    reference, _, kept = rejection_odds(inputs.scores, inputs.records, inputs.remaining, client.settings, BO_GIRDS,
                                        held, runs=60_000, seed=11, projected=inputs.projected)
    weighted = sim.teams[BO_GIRDS].playoff
    print(f"AT-11: weighted {weighted} ({sim.effective_runs} effective runs), reference {reference[BO_GIRDS]:.2f} "
          f"({kept} kept), gap {abs(weighted - reference[BO_GIRDS]):.2f}")
    assert abs(weighted - reference[BO_GIRDS]) <= 1.5


@pytest.mark.skipif(not (SAVED / "week-10" / "raw").is_dir(), reason="no saved week 10 data")
def test_two_runs_with_the_same_set_results_give_equal_output_byte_for_byte(cpc_week_10):
    # AT-12.
    held = [SetResult(week=11, game="win", median="above")]
    outputs = [_week_10_what_if(cpc_week_10, held)[2].model_dump_json().encode() for _ in range(2)]
    hashes = [hashlib.sha256(out).hexdigest() for out in outputs]
    print(f"AT-12: {hashes[0]} {hashes[1]}")
    assert outputs[0] == outputs[1]


@pytest.mark.skipif(not (SAVED / "week-10" / "raw").is_dir(), reason="no saved week 10 data")
def test_the_level_mean_of_each_team_is_its_season_average_shrunk_with_5_weeks_and_no_injury_term(cpc_week_10):
    # AT-13. The level reads the played-week scores of the saved history only, so an injury does not move it.
    _, _, history, sim = cpc_week_10
    scores = {rid: [history.weeks[n].scores[rid] for n in range(1, 11) if rid in history.weeks[n].scores]
              for rid in sim.records}
    league = sum(sum(s) for s in scores.values()) / sum(len(s) for s in scores.values())
    assert LEVEL_SHRINK_WEEKS == 5
    for rid, own in scores.items():
        expected = (sum(own) + 5 * league) / (len(own) + 5)
        print(f"AT-13: roster {rid} expected {expected:.2f} sim {sim.parameters.level_mean[rid]}")
        assert sim.parameters.level_mean[rid] == pytest.approx(expected, abs=0.005)


def _week_10_client(slug: str, at: Path, week: int = 10) -> Client:
    """The real client `slug` with links to its saved data of `week` and its history at `at`, and the NFL schedule of
    the fixtures in the cache, so the sim step calls no network. No test writes under clients/."""
    data = client_dir(ROOT, slug) / "data" / "2026"
    folder = f"week-{week:02d}"
    provider = FixtureProvider(raw_dir=data / folder / "raw", history_root=data / "history")
    real = load_client(ROOT, slug, 2026, provider.fetch_settings, VALUE_MODELS)
    client = real.model_copy(update={"folder": at, "nfl_dir": at / "data"})
    week_dir(client.folder, 2026, week).mkdir(parents=True)
    for name in ("raw", "facts.json"):
        (week_dir(client.folder, 2026, week) / name).symlink_to(data / folder / name)
    history_root(client.folder, 2026).symlink_to(data / "history")
    cache = nflverse_cache_dir(client.nfl_dir)
    cache.mkdir(parents=True)
    shutil.copy(GAMES, cache_path(cache, SCHEDULES_URL, 2026))
    return client


@pytest.fixture(scope="module")
def week_10_files(tmp_path_factory) -> dict[str, dict]:
    """The sim step of the weekly build of 2026 week 10 for CPC and NorCal, read back from each week-10/sim.json."""
    files = {}
    for slug in ("cpc", "norcal"):
        client = _week_10_client(slug, tmp_path_factory.mktemp(slug))
        out = run_week_sim(2026, 10, client=client)
        assert out == build_dir(client.folder) / "2026" / "week-10" / "sim.json"
        files[slug] = json.loads(out.read_text(encoding="utf-8"))
    return files


def _page(files: dict[str, dict], slug: str, name: str) -> dict:
    sim = files[slug]
    rid = next(rid for rid, team in sim["names"].items() if team == name)
    return sim["pages"][rid]


@pytest.mark.skipif(not (SAVED / "week-10" / "raw").is_dir(), reason="no saved week 10 data")
def test_the_sim_step_writes_week_10_sim_json_with_a_page_for_each_team(week_10_files, cpc_week_10):
    # AT-1, and the odds of the file are the odds of the build (AT-2).
    sim = week_10_files["cpc"]
    counts = (sim["runs"], len(sim["teams"]), len(sim["sample"]), len(sim["sample_weights"]), len(sim["pages"]))
    print(f"AT-1: keys {sorted(sim)} counts {counts}")
    assert counts == (10_000, 12, 200, 200, 12)
    assert (sim["season"], sim["week"], sim["effective_runs"]) == (2026, 10, 10_000)
    assert sim["weeks"] == list(range(11, 18)) and sim["parameters"]["median_game"] is True
    _, bundle, _, _ = cpc_week_10
    assert {int(rid): team["playoff"] for rid, team in sim["teams"].items()} == {
        rid: team.playoff for rid, team in bundle.odds.teams.items()}
    assert re.fullmatch(r"\d+ managers fight for the last (spot|\d+ spots)|The playoff field is all but set", sim["fact"])


# The What-if tests of the API read a saved copy of the week 10 sim file of CPC, because the API env holds no build.
API_WEEK_10_SIM = Path(__file__).resolve().parents[2] / "api" / "tests" / "fixtures" / "sim" / "cpc-week-10-sim.json"


@pytest.mark.skipif(not (SAVED / "week-10" / "raw").is_dir(), reason="no saved week 10 data")
def test_the_week_10_sim_file_of_the_api_tests_equals_a_fresh_sim_step(week_10_files):
    # Run `make sim CLIENT=cpc WEEK=10` and copy the file of the build folder to the fixture if this fails.
    assert json.loads(API_WEEK_10_SIM.read_text(encoding="utf-8")) == week_10_files["cpc"]


@pytest.mark.skipif(not (SAVED / "week-10" / "raw").is_dir(), reason="no saved week 10 data")
def test_the_ladder_of_bo_girds_names_the_smallest_count_with_odds_of_90_or_more(week_10_files):
    # AT-6. Four weeks left with the median game give 0 to 8 more wins.
    page = _page(week_10_files, "cpc", "Bo Girds")
    print(f"AT-6: {page['sentence']} {[(s['more_wins'], s['playoff'], s['chance']) for s in page['ladder']]}")
    assert page["record"] == [11, 9] and page["weeks_left"] == 4 and page["wins_left"] == 8
    assert [step["more_wins"] for step in page["ladder"]] == list(range(9))
    assert sum(step["chance"] for step in page["ladder"]) == pytest.approx(100, abs=0.5)
    need = min(step["more_wins"] for step in page["ladder"] if (step["playoff"] or 0) >= 90)
    assert page["need"] == need
    assert page["sentence"] == f"Win {need} of the 8 left and you're in."


@pytest.mark.skipif(not (SAVED / "week-10" / "raw").is_dir(), reason="no saved week 10 data")
def test_week_11_of_bo_girds_in_cpc_has_four_results_against_maye_dforce_b_with_u(week_10_files):
    # AT-7.
    sim = week_10_files["cpc"]
    week = _page(week_10_files, "cpc", "Bo Girds")["weeks"][0]
    print(f"AT-7: {week}")
    assert week["week"] == 11 and sim["names"][str(week["opponent"])] == "Maye d'force B with U"
    assert [(r["game"], r["median"], r["wins_added"]) for r in week["results"]] == [
        ("win", "above", 2), ("win", "below", 1), ("loss", "above", 1), ("loss", "below", 0)]
    assert all(r["playoff"] is not None and r["chance"] > 0 for r in week["results"])


@pytest.mark.skipif(not (SAVED / "week-10" / "raw").is_dir(), reason="no saved week 10 data")
def test_week_11_of_bo_girds_in_norcal_has_two_results_against_the_mean_machine(week_10_files):
    # AT-8. NorCal has no median game.
    sim = week_10_files["norcal"]
    page = _page(week_10_files, "norcal", "Bo Girds")
    week = page["weeks"][0]
    print(f"AT-8: {week}")
    assert page["record"] == [5, 5] and page["wins_left"] == 4
    assert week["week"] == 11 and sim["names"][str(week["opponent"])] == "The Mean Machine"
    assert [(r["game"], r["median"], r["wins_added"]) for r in week["results"]] == [("win", None, 1), ("loss", None, 0)]


REASONS = {"2 wins ahead of you", "1 win ahead of you", "Level with you", "1 win behind you",
           "In the race for the last spot"}


@pytest.mark.skipif(not (SAVED / "week-10" / "raw").is_dir(), reason="no saved week 10 data")
def test_the_root_for_rows_of_each_page_follow_the_rules_of_the_spec(week_10_files):
    # AT-9, on Bo Girds and on each other page of both clients.
    week = _page(week_10_files, "cpc", "Bo Girds")["weeks"][0]
    print(f"AT-9: loss {week['loss_playoff']} rows "
          f"{[(r['winner'], r['loser'], r['reason'], r['playoff'], r['playoff'] - week['loss_playoff']) for r in week['root_for']]}")
    assert week["root_for"]
    for sim in week_10_files.values():
        records = {int(rid): record for rid, record in sim["records"].items()}
        place = {rid: n for n, rid in enumerate(sorted(records, key=lambda r: (-records[r][0], -records[r][2], r)), 1)}
        for page in sim["pages"].values():
            for week in page["weeks"]:
                rows = week["root_for"]
                assert len(rows) <= 3
                lifts = [row["playoff"] - week["loss_playoff"] for row in rows]
                assert all(isinstance(row["playoff"], int) and lift >= 1 for row, lift in zip(rows, lifts, strict=True))
                assert [(-lift, place[row["loser"]]) for row, lift in zip(rows, lifts, strict=True)] == sorted(
                    (-lift, place[row["loser"]]) for row, lift in zip(rows, lifts, strict=True))
                assert {row["reason"] for row in rows} <= REASONS


@pytest.mark.skipif(not (SAVED / "week-10" / "raw").is_dir(), reason="no saved week 10 data")
def test_each_result_under_400_effective_runs_has_the_about_flag_and_no_other(week_10_files):
    # AT-10.
    sim = week_10_files["cpc"]
    flagged = plain = 0
    for page in sim["pages"].values():
        for week in page["weeks"]:
            for r in week["results"]:
                assert r["about"] == (r["chance"] / 100 * sim["effective_runs"] < 400)
                flagged += r["about"]
                plain += not r["about"]
    # At 10,000 runs a result is about under 4 percent. No result of week 10 is that rare, but a step of the ladder is.
    steps = [step for page in sim["pages"].values() for step in page["ladder"]]
    assert all(step["about"] == (step["chance"] / 100 * sim["effective_runs"] < 400) for step in steps)
    print(f"AT-10: {flagged} results with about, {plain} with none; {sum(s['about'] for s in steps)} ladder steps "
          f"with about")
    assert plain == 12 * 4 * 4 and any(step["about"] for step in steps)


# The playoff fixtures of the sim page tests, which `make sim-fixtures` writes (season-sim ACCEPTANCE.md).
SITE_FIXTURES = Path(__file__).resolve().parents[3] / "packages" / "sim" / "site" / "fixtures"


@pytest.fixture(scope="module")
def playoff_fixture_files(tmp_path_factory) -> tuple[list[str], Path]:
    out = tmp_path_factory.mktemp("fixtures")
    client = _week_10_client("cpc", tmp_path_factory.mktemp("cpc"))
    return run_sim_fixtures(2026, 10, out, client=client), out


@pytest.mark.skipif(not (SAVED / "week-10" / "raw").is_dir(), reason="no saved week 10 data")
def test_the_playoff_fixtures_play_out_stored_run_1_and_name_the_seeds_and_the_champion(playoff_fixture_files):
    lines, out = playoff_fixture_files
    for line in lines:
        print(f"AT-42 AT-43 AT-44 fixture: {line}")
    week_10 = json.loads(API_WEEK_10_SIM.read_text(encoding="utf-8"))
    run = week_10["sample"][0]
    for name, week in (("week-sim-playoffs.json", 14), ("week-sim-round-2.json", 15), ("week-sim-final.json", 17)):
        sim = json.loads((out / name).read_text(encoding="utf-8"))
        assert sim["week"] == week and sim["schedule"] == {}
        playoffs = sim["pages"]["1"]["playoffs"]
        # The seeds are the top 6 of the table of run 1, so the fixture plays out the run.
        assert [t["roster_id"] for t in playoffs["teams"]] == run["table"][:6]
    final = json.loads((out / "week-sim-final.json").read_text(encoding="utf-8"))
    assert final["pages"]["1"]["playoffs"]["champion"] == run["champion"]
    assert final["teams"][str(run["champion"])]["title"] == 100.0


@pytest.mark.skipif(not (SAVED / "week-10" / "raw").is_dir(), reason="no saved week 10 data")
def test_the_playoff_fixtures_of_the_site_tests_equal_a_fresh_fixture_build(playoff_fixture_files):
    # Run `make sim-fixtures` in apps/pipeline if this fails.
    _, out = playoff_fixture_files
    for name in ("week-sim-playoffs.json", "week-sim-round-2.json", "week-sim-final.json"):
        assert json.loads((SITE_FIXTURES / name).read_text(encoding="utf-8")) == json.loads(
            (out / name).read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def cpc_week_11_file(tmp_path_factory) -> dict:
    """The sim step of the weekly build of CPC 2026 week 11, read back from week-11/sim.json."""
    client = _week_10_client("cpc", tmp_path_factory.mktemp("cpc-11"), week=11)
    out = run_week_sim(2026, 11, client=client)
    assert out is not None
    return json.loads(out.read_text(encoding="utf-8"))


CPC_GOALS = ["spot", "bye", "seed-1", "seed-2", "seed-3", "seed-4", "seed-5", "seed-6"]


def _top_status(rid: int, wins: dict[int, int], reach: int, k: int) -> str:
    """The plain check on wins for the top k places, by hand: Clinched when fewer than k other teams can reach the
    wins of `rid`, Out when k other teams already hold more wins than `rid` can reach."""
    others = [o for o in wins if o != rid]
    if sum(wins[o] + reach >= wins[rid] for o in others) < k:
        return "in"
    if sum(wins[o] > wins[rid] + reach for o in others) >= k:
        return "out"
    return "open"


def _hand_goal_status(rid: int, wins: dict[int, int], reach: int, goal: str) -> str:
    if goal == "spot":
        return _top_status(rid, wins, reach, 6)
    if goal == "bye":
        return _top_status(rid, wins, reach, 2)
    k = int(goal.split("-")[1])
    top = _top_status(rid, wins, reach, k)
    above = _top_status(rid, wins, reach, k - 1) if k > 1 else "out"
    if top == "in" and above == "out":
        return "in"
    return "out" if top == "out" or above == "in" else "open"


@pytest.mark.skipif(not (SAVED / "week-11" / "raw").is_dir(), reason="no saved week 11 data")
def test_week_11_sim_json_holds_the_goals_of_each_team_and_the_board(cpc_week_11_file):
    # AT-3. Each of the 12 pages holds the odds and the status of the spot, the bye, and seeds 1 to 6.
    sim = cpc_week_11_file
    assert len(sim["pages"]) == 12 and len(sim["board"]) == 12
    for rid, page in sim["pages"].items():
        assert list(page["goals"]) == CPC_GOALS
        assert page["goals"]["spot"]["odds"] == sim["teams"][rid]["playoff"]
        board = next(row for row in sim["board"] if row["roster_id"] == int(rid))
        assert board["goals"] == page["goals"]
    for rid in ("6", "1"):
        print(f"AT-3: {sim['names'][rid]} {sim['pages'][rid]['goals']}")


@pytest.mark.skipif(not (SAVED / "week-11" / "raw").is_dir(), reason="no saved week 11 data")
def test_each_week_11_page_opens_on_the_best_goal_with_odds_of_5_or_more(cpc_week_11_file):
    # AT-4. The order is 1 seed, bye, spot.
    sim = cpc_week_11_file
    for rid, page in sim["pages"].items():
        odds = {goal: page["goals"][goal]["odds"] for goal in CPC_GOALS}
        best = next((goal for goal in ("seed-1", "bye", "spot") if odds[goal] >= 5), "spot")
        print(f"AT-4: {sim['names'][rid]:<24} {sim['records'][rid][:2]} {odds} open {page['open_goal']}")
        assert page["open_goal"] == best
    fridge = next(rid for rid, name in sim["names"].items() if name == "Lil Fridge")
    assert sim["records"][fridge][:2] == [15, 7]
    assert sim["pages"][fridge]["open_goal"] in ("seed-1", "bye")


@pytest.mark.skipif(not (SAVED / "week-11" / "raw").is_dir(), reason="no saved week 11 data")
def test_each_week_11_status_equals_the_plain_check_on_wins_by_hand(cpc_week_11_file):
    # AT-5. Three weeks left with the median game give 6 more wins at most.
    sim = cpc_week_11_file
    wins = {int(rid): record[0] for rid, record in sim["records"].items()}
    reach = 2 * len(sim["schedule"])
    assert reach == 6
    for rid, page in sim["pages"].items():
        hand = {goal: _hand_goal_status(int(rid), wins, reach, goal) for goal in CPC_GOALS}
        print(f"AT-5: {sim['names'][rid]:<24} wins {wins[int(rid)]} hand {hand}")
        assert {goal: page["goals"][goal]["status"] for goal in CPC_GOALS} == hand


def _paths_of(sim: dict):
    """Each Path of each Finish of each page of the sim file, with its page and its Finish."""
    for rid, page in sim["pages"].items():
        for goal, finishes in page["finishes"].items():
            for finish in finishes:
                for path in finish["paths"]:
                    yield rid, goal, finish, path


@pytest.mark.skipif(not (SAVED / "week-11" / "raw").is_dir(), reason="no saved week 11 data")
def test_the_finish_list_of_bo_girds_sums_to_100_and_4_2_ends_15_13(cpc_week_11_file):
    # AT-6. Three weeks left with the median game give 7 Finishes, 6-0 to 0-6.
    sim = cpc_week_11_file
    rid = next(rid for rid, name in sim["names"].items() if name == "Bo Girds")
    page = sim["pages"][rid]
    assert page["record"] == [11, 11]
    finishes = page["finishes"]["spot"]
    for f in finishes:
        print(f"AT-6: {f['more_wins']}-{6 - f['more_wins']} ends {f['record']} chance {f['chance']} "
              f"odds {f['odds']} case {f['case']} paths {len(f['paths'])}")
    assert [f["more_wins"] for f in finishes] == [6, 5, 4, 3, 2, 1, 0]
    assert sum(f["chance"] for f in finishes) == pytest.approx(100, abs=1)
    assert next(f["record"] for f in finishes if f["more_wins"] == 4) == [15, 13]


@pytest.mark.skipif(not (SAVED / "week-10" / "raw").is_dir(), reason="no saved week 10 data")
def test_a_norcal_finish_list_runs_4_0_to_0_4_with_no_median(week_10_files):
    # AT-7. NorCal has no median game and 4 weeks left.
    sim = week_10_files["norcal"]
    assert sim["parameters"]["median_game"] is False
    for page in sim["pages"].values():
        for finishes in page["finishes"].values():
            assert [f["more_wins"] for f in finishes] == [4, 3, 2, 1, 0]
        assert all(r["median"] is None for week in page["weeks"] for r in week["results"])
    page = _page(week_10_files, "norcal", "Skol Daddy")
    print(f"AT-7: Skol Daddy {[(f['more_wins'], f['odds'], f['chance']) for f in page['finishes']['spot']]}")


@pytest.mark.skipif(not (SAVED / "week-11" / "raw").is_dir(), reason="no saved week 11 data")
def test_each_week_11_path_names_1_to_3_teams_with_400_runs_and_reaches_90_unless_full_or_best(cpc_week_11_file):
    # AT-8 and AT-52. Each condition is a final record at most.
    sim = cpc_week_11_file
    paths = list(_paths_of(sim))
    sizes = [len(path["conditions"]) for *_, path in paths]
    print(f"AT-8 AT-52: {len(paths)} Paths, teams per Path {dict(sorted(Counter(sizes).items()))}, "
          f"fewest runs {min(path['runs'] for *_, path in paths)}")
    assert paths
    for rid, _, finish, path in paths:
        teams = [c["roster_id"] for c in path["conditions"]]
        assert 1 <= len(teams) <= 3 and int(rid) not in teams and len(set(teams)) == len(teams)
        assert path["runs"] >= 400
        assert path["odds"] >= 90 or len(teams) == 3 or finish["case"] == "best"
        for c in path["conditions"]:
            wins, losses = sim["records"][str(c["roster_id"])][:2]
            assert c["record"][0] - wins + c["record"][1] - losses == 6 and c["record"][0] - wins < 6


@pytest.mark.skipif(not (SAVED / "week-11" / "raw").is_dir(), reason="no saved week 11 data")
def test_no_week_11_path_repeats_within_its_finish(cpc_week_11_file):
    # AT-9.
    sim = cpc_week_11_file
    finishes = 0
    for page in sim["pages"].values():
        for goal_finishes in page["finishes"].values():
            for finish in goal_finishes:
                sets = [frozenset((c["roster_id"], tuple(c["record"])) for c in p["conditions"]) for p in finish["paths"]]
                finishes += bool(sets)
                assert len(sets) == len(set(sets))
    print(f"AT-9: {finishes} Finishes with Paths, no repeated Path")


@pytest.mark.skipif(not (SAVED / "week-11" / "raw").is_dir(), reason="no saved week 11 data")
def test_a_sure_or_hopeless_week_11_finish_has_no_path_and_a_best_chance_holds_one(cpc_week_11_file):
    # AT-10 and AT-11.
    sim = cpc_week_11_file
    counts: Counter[str] = Counter()
    for rid, page in sim["pages"].items():
        for goal, finishes in page["finishes"].items():
            for finish in finishes:
                counts[finish["case"]] += 1
                if finish["case"] in ("sure", "none"):
                    assert finish["paths"] == []
                if finish["case"] == "best":
                    assert len(finish["paths"]) == 1 and finish["paths"][0]["odds"] < 90
                    if counts["best"] <= 2:
                        print(f"AT-11: {sim['names'][rid]} {goal} {finish}")
    print(f"AT-10 AT-11: Finishes by case {dict(counts)}")
    assert counts["sure"] and counts["none"] and counts["best"]


def _bo_girds_plan(sim: dict) -> tuple[str, dict, dict]:
    """The roster ID of Bo Girds, his page, and the Week plan of the first Path of his 4-2 Finish for a spot."""
    rid = next(rid for rid, name in sim["names"].items() if name == "Bo Girds")
    page = sim["pages"][rid]
    finish = next(f for f in page["finishes"]["spot"] if f["more_wins"] == 4)
    return rid, page, finish["paths"][0]["plan"]


@pytest.mark.skipif(not (SAVED / "week-11" / "raw").is_dir(), reason="no saved week 11 data")
def test_the_week_plan_of_the_first_4_2_path_of_bo_girds_has_a_row_for_each_of_weeks_12_to_14(cpc_week_11_file):
    # AT-12. Each row holds a result, the Score to beat of its week, and 1 or 2 games to root for.
    sim = cpc_week_11_file
    rid, page, plan = _bo_girds_plan(sim)
    names = sim["names"]
    beat = {s["week"]: s for s in page["score_to_beat"]}
    print(f"AT-12: plan odds {plan['odds']}, any order {plan['any_order']}")
    for week in plan["weeks"]:
        s = beat[week["week"]]
        roots = [f"{names[str(g['winner'])]} over {names[str(g['loser'])]} -> {g['odds']}%" for g in week["root_for"]]
        print(f"AT-12: week {week['week']} vs {names[str(week['opponent'])]}: {week['game']}, {week['median']} median; "
              f"score {s['win']} to win, {s['win_sure']} to be sure; median {s['median']}, {s['median_sure']}; "
              f"root for {roots}")
    assert [week["week"] for week in plan["weeks"]] == [12, 13, 14]
    assert sum((w["game"] == "win") + (w["median"] == "above") for w in plan["weeks"]) == 4
    for week in plan["weeks"]:
        assert week["game"] in ("win", "loss") and week["median"] in ("above", "below")
        assert 1 <= len(week["root_for"]) <= 2
        s = beat[week["week"]]
        assert s["opponent"] == week["opponent"]
        assert s["win_sure"] > s["win"] and s["median_sure"] > s["median"]
    # Week 12 is Bo Girds, roster 6, against roster 5, which Sleeper now calls Teez Nuts.
    assert (int(rid), plan["weeks"][0]["opponent"]) == (6, 5)


@pytest.mark.skipif(not (SAVED / "week-11" / "raw").is_dir(), reason="no saved week 11 data")
def test_the_try_it_odds_of_the_plan_equal_a_what_if_of_its_results_within_1_point(cpc_week_11_file):
    # AT-13. The What-if is the sim again on the inputs of the week file, as the API runs it.
    sim = cpc_week_11_file
    rid, _, plan = _bo_girds_plan(sim)
    held = [SetResult(week=w["week"], game=w["game"], median=w["median"]) for w in plan["weeks"]]
    what_if = rerun(SimResult.model_validate(sim), you=int(rid), set_results=held, pages=[int(rid)])
    odds = what_if.pages[int(rid)].goals["spot"].odds
    print(f"AT-13: rerun(week-11/sim.json, you={rid}, set={[r.model_dump() for r in held]})")
    print(f"AT-13: Try it {plan['odds']}%, What-if {odds}%, effective runs {what_if.effective_runs}")
    assert abs(odds - plan["odds"]) <= 1

@pytest.mark.skipif(not (SAVED / "week-11" / "raw").is_dir(), reason="no saved week 11 data")
def test_the_score_to_beat_of_bo_girds_for_week_12_holds_2_scores_against_teez_nuts_and_2_against_the_median(
        cpc_week_11_file):
    # AT-14. Week 12 is Bo Girds, roster 6, against roster 5, which Sleeper now calls Teez Nuts.
    sim = cpc_week_11_file
    page = sim["pages"]["6"]
    beat = page["score_to_beat"][0]
    card = page["week_card"]
    print(f"AT-14: {beat}")
    assert (beat["week"], beat["opponent"]) == (12, 5) == (card["week"], card["opponent"])
    assert beat["win_sure"] > beat["win"] and beat["median_sure"] > beat["median"]


@pytest.mark.skipif(not (SAVED / "week-11" / "raw").is_dir(), reason="no saved week 11 data")
def test_each_of_the_4_week_12_results_of_bo_girds_roots_for_the_5_other_games(cpc_week_11_file):
    # AT-15 and AT-16, on the spot and the bye. A seed holds its tiles only, to keep sim.json small.
    sim = cpc_week_11_file
    names = sim["names"]
    card = sim["pages"]["6"]["week_card"]
    others = {frozenset(pair) for pair in sim["schedule"]["12"] if 6 not in pair}
    assert len(others) == 5
    assert [(r["game"], r["median"]) for r in card["results"]] == [
        ("win", "above"), ("win", "below"), ("loss", "above"), ("loss", "below")]
    for goal, held in card["goals"].items():
        if goal.startswith("seed-"):
            assert held["root_for"] == [] and held["median_root"] == []
            continue
        assert len(held["root_for"]) == len(held["median_root"]) == 4
        for result, value, rows, medians in zip(card["results"], held["odds"], held["root_for"], held["median_root"],
                                                strict=True):
            assert len(rows) == 5
            assert {frozenset((r["winner"], r["loser"])) for r in rows} == others
            assert all(r["odds"] >= r["other"] for r in rows)
            assert 1 <= len(medians) <= 2
            if goal == "spot":
                print(f"AT-15: {result['game']} {result['median']} -> {value}%: " + "; ".join(
                    f"{names[str(r['winner'])]} beats {names[str(r['loser'])]} -> {r['odds']}%, "
                    f"{names[str(r['loser'])]} wins -> {r['other']}%"
                    + (" (Doesn't matter)" if r["odds"] - r["other"] < 1 else "") for r in rows))
                print("AT-16: " + "; ".join(f"{names[str(m['roster_id'])]} misses the median -> {m['odds']}%"
                                            for m in medians))


@pytest.mark.skipif(not (SAVED / "week-11" / "raw").is_dir(), reason="no saved week 11 data")
def test_a_week_11_tiebreak_gap_shows_only_for_a_team_within_1_win_and_50_points_across_the_edge(cpc_week_11_file):
    # AT-18, checked by hand from the records of the file.
    sim = cpc_week_11_file
    records = {int(rid): r for rid, r in sim["records"].items()}
    order = sorted(records, key=lambda rid: (-records[rid][0], -records[rid][2], -records[rid][3], rid))
    place = {rid: n for n, rid in enumerate(order, start=1)}
    edges = {"spot": 6, "bye": 2, **{f"seed-{n}": n for n in range(1, 7)}}
    shown = 0
    for rid, page in sim["pages"].items():
        you = int(rid)
        for goal, card in page["week_card"]["goals"].items():
            edge = edges[goal]
            close = [o for o in order if o != you and (place[o] <= edge) != (place[you] <= edge)
                     and abs(records[o][0] - records[you][0]) <= 1 and abs(records[o][2] - records[you][2]) <= 50]
            gap = card["tiebreak"]
            if page["goals"][goal]["status"] != "open" or not close:
                assert gap is None
                continue
            assert gap is not None and gap["roster_id"] in close
            shown += 1
            if goal == "spot":
                print(f"AT-18: {sim['names'][rid]} {goal}: {sim['names'][str(gap['roster_id'])]} {gap['points']:+}")
    print(f"AT-18: {shown} gaps")
