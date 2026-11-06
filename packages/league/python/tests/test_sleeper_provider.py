"""
Tests for the Sleeper adapter of the provider port: the cache dir it takes in its constructor, and the points key
of the projections ahead. Each test passes an httpx.MockTransport, so no test calls the network (ADR 0015).
"""
import json
from pathlib import Path

import httpx

from league.provider.base import Provider
from league.provider.sleeper import SleeperProvider

PLAYERS = {"4046": {"position": "QB", "team": "BUF"}}


def _players_transport(calls: list[str]) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        return httpx.Response(200, json=PLAYERS)
    return httpx.MockTransport(handler)


def test_the_sleeper_provider_is_a_provider(tmp_path: Path):
    provider: Provider = SleeperProvider(tmp_path)
    assert isinstance(provider, Provider)


def test_the_players_fetch_keeps_the_players_file_in_the_cache_dir_of_the_constructor(tmp_path: Path):
    calls: list[str] = []
    provider = SleeperProvider(tmp_path / "cache", transport=_players_transport(calls))
    assert provider.fetch_players() == PLAYERS
    assert json.loads((tmp_path / "cache" / "players.json").read_text()) == PLAYERS


def test_a_second_players_fetch_reads_the_cache_and_calls_no_endpoint(tmp_path: Path):
    calls: list[str] = []
    provider = SleeperProvider(tmp_path, transport=_players_transport(calls))
    provider.fetch_players()
    provider.fetch_players()
    assert calls == ["/v1/players/nfl"]


def _projections_transport() -> httpx.MockTransport:
    rows = [{"player_id": "6794", "stats": {"pts_std": 9.0, "pts_half_ppr": 11.5, "pts_ppr": 14.0}},
            {"player_id": "4046", "stats": {"pts_half_ppr": 20.0}}]
    return httpx.MockTransport(lambda request: httpx.Response(200, json=rows))


def test_the_projections_ahead_take_the_points_key_of_the_league(tmp_path: Path):
    provider = SleeperProvider(tmp_path, transport=_projections_transport())
    ahead = provider.fetch_projections(2026, 8, 9, "pts_ppr")
    # A player with no value at the key has no entry, as a player with no projection has none.
    assert [(entry.week, entry.projections) for entry in ahead] == [(9, {"6794": 14.0})]


# The real CPC draft of 2026, as Sleeper sent it on 2026-11-05.
CPC_DRAFT = Path(__file__).resolve().parents[4] / "apps" / "pipeline" / "tests" / "fixtures" / "2026" / "draft" / "cpc"
CPC_LEAGUE_ID = "1386167364424318976"
CPC_DRAFT_ID = "1386167364436901888"


def _draft_transport(calls: list[str]) -> httpx.MockTransport:
    bodies = {
        f"/v1/league/{CPC_LEAGUE_ID}": {"league_id": CPC_LEAGUE_ID, "draft_id": CPC_DRAFT_ID},
        f"/v1/draft/{CPC_DRAFT_ID}": json.loads((CPC_DRAFT / "draft.json").read_text()),
        f"/v1/draft/{CPC_DRAFT_ID}/picks": json.loads((CPC_DRAFT / "picks.json").read_text()),
    }

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        return httpx.Response(200, json=bodies[request.url.path])
    return httpx.MockTransport(handler)


def test_the_draft_fetch_gives_the_draft_type_and_each_pick_with_its_price_and_saves_both_files(tmp_path: Path):
    calls: list[str] = []
    provider = SleeperProvider(tmp_path / "cache", transport=_draft_transport(calls))
    draft = provider.fetch_draft(CPC_LEAGUE_ID, tmp_path / "draft")
    assert (draft.type, draft.settings.budget, len(draft.picks)) == ("auction", 200, 168)
    first = draft.picks[0]
    assert (first.pick_no, first.roster_id, first.player_id, first.metadata.position, first.metadata.amount) == (
        1, 10, "4866", "RB", "58")
    assert json.loads((tmp_path / "draft" / "picks.json").read_text()) == json.loads(
        (CPC_DRAFT / "picks.json").read_text())
    assert json.loads((tmp_path / "draft" / "draft.json").read_text())["type"] == "auction"
    assert calls == [f"/v1/league/{CPC_LEAGUE_ID}", f"/v1/draft/{CPC_DRAFT_ID}", f"/v1/draft/{CPC_DRAFT_ID}/picks"]
