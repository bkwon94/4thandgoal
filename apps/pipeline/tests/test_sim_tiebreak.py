"""
Tests for the seed order of the sim on the real saved brackets of CPC and NorCal: the order of the sim and of the
standings table equals the Sleeper seeds, with the higher Points Against as the third key (decision 02).
"""
import json

import pytest
from cpc import ROOT

from league.history import load_saved_weeks
from league.models import History
from league.paths import client_dir, history_root
from league.provider.raw import RawLeague
from league.provider.sleeper import league_settings
from league.standings_table import season_records, standings_order
from sim.season import season_sim

# The weeks with a stored Sleeper bracket in the saved data.
WEEKS = [("cpc", week) for week in range(6, 11)] + [("norcal", week) for week in range(8, 11)]


def _saved(slug: str, week: int):
    """The League settings, the history, and the Sleeper seeds 1 to 6 of the saved week `week` of `slug`."""
    data = client_dir(ROOT, slug) / "data" / "2026"
    raw = data / f"week-{week:02d}" / "raw"
    settings = league_settings(RawLeague.model_validate_json((raw / "league.json").read_text(encoding="utf-8")))
    history = History(week=week, weeks=load_saved_weeks(history_root(client_dir(ROOT, slug), 2026), week,
                                                        settings.points_key))
    return settings, history, _seeds(json.loads((raw / "bracket.json").read_text(encoding="utf-8")))


def _seeds(bracket: list[dict]) -> list[int]:
    """Seeds 1 to 6 of a Sleeper bracket of 6 teams. Round 1 pairs seed 4 with 5 and seed 6 with 3. Each round 2 game
    starts with a bye seed: seed 1 in match 3 and seed 2 in match 4."""
    by_match = {game["m"]: game for game in bracket}
    return [by_match[3]["t1"], by_match[4]["t1"], by_match[2]["t2"], by_match[1]["t1"], by_match[1]["t2"],
            by_match[2]["t1"]]


@pytest.mark.parametrize(("slug", "week"), WEEKS)
def test_the_standings_order_gives_the_sleeper_seeds(slug, week):
    # AT-1 and AT-2, in the order of the standings table.
    settings, history, seeds = _saved(slug, week)
    records = season_records(history, week, median_game=settings.median_game)
    print(f"{slug} week {week}: standings {standings_order(records)[:6]} sleeper {seeds}")
    assert standings_order(records)[:6] == seeds


@pytest.mark.parametrize(("slug", "week"), WEEKS)
def test_the_sim_order_gives_the_sleeper_seeds(slug, week):
    # AT-1 and AT-2, in the seed order of the season draw. No regular week is left, so the table of a run is the
    # order of the real records.
    settings, history, seeds = _saved(slug, week)
    records = season_records(history, week, median_game=settings.median_game)
    scores = {rid: [history.weeks[w].scores[rid] for w in range(1, week + 1)] for rid in records}
    run = season_sim(scores, records, {}, season=2026, week=week, settings=settings, runs=1, sample=1).sample[0]
    print(f"{slug} week {week}: sim {run.table[:6]} sleeper {seeds}")
    assert run.table[:6] == seeds
