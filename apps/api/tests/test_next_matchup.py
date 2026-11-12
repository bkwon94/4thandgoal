"""
Tests for the live card of Your next matchup at the route seam: the FastAPI test client over the live Sleeper week 10 of
cpc, recorded on 2026-11-12 before the games, and the published sim.json of cpc for the league spread.
"""
import shutil
from datetime import datetime
from pathlib import Path

import pytest
import test_api
import test_start_sit
from fakes import FakeJev
from test_api import HEADERS
from test_start_sit import BEFORE_KICKOFF, BO_GIRDS, _edges, sleeper_scores

from league.jev_port import JevError

repo = test_api.repo
settings = test_api.settings
sources = test_api.sources

NEXT_MATCHUP = "/clients/{slug}/next-matchup"
# The real sim.json of the published cpc season, with the league spread of 22.21 points.
SIM = Path(__file__).resolve().parents[3] / "clients" / "cpc" / "published" / "2026" / "sim.json"
# The opponent of Bo Girds in week 10 of cpc: the other roster of matchup 5.
THE_BLUE_TENT = 1


@pytest.fixture
def with_sim(settings):
    """The test repo with the published sim.json of cpc, where the client folder reads it."""
    season = settings.repo / "published" / "2026"
    season.mkdir(parents=True, exist_ok=True)
    shutil.copy(SIM, season / "sim.json")
    return settings


def _stream(api, roster_id: int = BO_GIRDS["cpc"]) -> list[dict]:
    response = api.post(NEXT_MATCHUP.format(slug="cpc"), json={"roster_id": roster_id}, headers=HEADERS)
    assert response.status_code == 200, response.text
    return test_start_sit._chunks(response)


def _card(api, roster_id: int = BO_GIRDS["cpc"]) -> dict:
    [block] = [chunk["data"] for chunk in _stream(api, roster_id) if chunk["type"] == "data-block"]
    return block


def test_the_stream_carries_the_matchup_card_of_the_live_week_with_its_read_time(with_sim, sources):
    # AT-25: the card has the projected totals of the live week 10 and the time of the read of Sleeper.
    api = test_start_sit._api(with_sim, sources)
    card = _card(api)
    assert card["kind"] == "matchup" and card["final"] is False
    assert card["you"]["roster_id"] == BO_GIRDS["cpc"] and card["them"]["roster_id"] == THE_BLUE_TENT
    # The test clock is the time of the request, so the read is within the minute of it.
    assert datetime.fromisoformat(card["read_at"]) == BEFORE_KICKOFF
    # The projected total of Your team is the total of the lineup of Start or sit with its Swaps, from the same scoring.
    lineup = test_start_sit._block(api)
    assert card["you"]["score"] == lineup["swap_total"]
    assert [slot["you"]["name"] for slot in card["slots"]] == [row["player"] for row in lineup["rows"]]
    assert [slot["slot"] for slot in card["slots"]] == ["QB", "RB", "RB", "WR", "WR", "TE", "FLEX", "FLEX", "DEF"]


def test_the_team_with_the_higher_projected_total_has_odds_above_half(with_sim, sources):
    # AT-25: the odds follow the gap of the two totals, and the card of the other team reads the same game.
    api = test_start_sit._api(with_sim, sources)
    mine, theirs = _card(api), _card(api, THE_BLUE_TENT)
    ahead = mine if mine["you"]["score"] > mine["them"]["score"] else theirs
    assert ahead["odds"] > 0.5
    assert mine["odds"] + theirs["odds"] == pytest.approx(1, abs=0.002)
    assert (mine["you"]["score"], mine["them"]["score"]) == (theirs["them"]["score"], theirs["you"]["score"])


def test_a_season_with_no_sim_gives_the_card_with_no_odds(settings, sources):
    card = _card(test_start_sit._api(settings, sources))
    assert card["odds"] is None and card["you"]["score"] > 0


def _without(team: str):
    """The recorded kickoffs of week 10 with the game of `team` taken out, so `team` is on a bye."""
    def scores(season: int, week: int) -> dict:
        payload = sleeper_scores(season, week)
        games = [game for game in payload["data"]["scores"]
                 if team not in (game["metadata"].get("home_team"), game["metadata"].get("away_team"))]
        return {"data": {"scores": games}}
    return scores


def test_a_starter_on_a_bye_lowers_the_projected_total_and_the_odds(with_sim, sources):
    # A bye moves the best starter of Bo Girds out of the lineup. A bench player with a lower projection takes his slot.
    before = _card(test_start_sit._api(with_sim, sources))
    best = max((slot["you"] for slot in before["slots"] if slot["you"]), key=lambda player: player["points"])
    after = _card(test_start_sit._api(with_sim, sources, scores=_without(best["nfl_team"])))
    assert best["name"] not in {slot["you"]["name"] for slot in after["slots"] if slot["you"]}
    assert after["you"]["score"] < before["you"]["score"]
    assert after["odds"] < before["odds"]


def test_a_swap_moves_your_slot_your_projected_total_and_the_odds(with_sim, sources):
    # Story 38: Konata Mumpfield of the bench of Bo Girds takes the WR slot of Matthew Golden at 0.9, as in Start or sit.
    before = _card(test_start_sit._api(with_sim, sources))
    jev = _edges({("Konata Mumpfield", "Matthew Golden"): 0.9})
    api = test_start_sit._api(with_sim, sources, jev=jev)
    after = _card(api)
    # The card makes one Jev request.
    assert len([request for request in jev.requests if "players" in request.state]) == 1
    names = {slot["you"]["name"] for slot in after["slots"] if slot["you"]}
    assert "Konata Mumpfield" in names and "Matthew Golden" not in names
    assert (before["you"]["score"], after["you"]["score"]) == (121.7, 115.6)
    assert after["you"]["score"] == test_start_sit._block(api)["swap_total"]
    assert after["odds"] < before["odds"]
    # The other team stays by projection.
    assert after["them"] == before["them"]


def test_a_failed_jev_read_gives_the_card_by_projection(with_sim, sources):
    # A failed Swap read never breaks the card: Your side falls back to the lineup by projection.
    api = test_start_sit._api(with_sim, sources, jev=FakeJev(error=JevError("down")))
    card = _card(api)
    assert card["you"]["score"] == 121.7 and card["odds"] is not None
    assert "Matthew Golden" in {slot["you"]["name"] for slot in card["slots"] if slot["you"]}
