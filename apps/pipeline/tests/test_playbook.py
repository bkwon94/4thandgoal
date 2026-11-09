"""
Tests for the Playbook of each client: the file in its voice folder, its tips, and the Advisor prompt that carries it.
They read the real files under clients/, and they build the prompt from the week 6 snapshot with no Claude call.
"""
import shutil

import pytest
from cpc import ROOT, cpc_client

from analyzer.advisor import build_advisor_prompt, load_playbook
from analyzer.rubric import ProposedTrade, TradeSide
from league.paths import client_dir
from league.slow_sources import load_slow_sources
from league.snapshot import load_snapshot

CPC = cpc_client()
NORCAL = CPC.model_copy(update={"slug": "norcal", "folder": client_dir(ROOT, "norcal")})
# The tips of decision 01 that the cpc Playbook must hold, each as a phrase of the file.
CPC_TIPS = ["half PPR", "QBs and TEs are worth the least", "firms up its lineup", "takes more risk",
            "consensus top 3 to 5 player", "recent points", "trend of usage"]
# A claim about one league: its format, its season, or its managers. A general tip holds none of them.
LEAGUE_CLAIMS = ["half PPR", "this season", "this league", "in this league", "managers here", "RBs are scarce",
                 "2026"]


def test_each_client_folder_has_a_playbook_in_its_voice_folder():
    for folder in sorted((ROOT / "clients").iterdir()):
        if (folder / "client.toml").is_file():
            assert (folder / "prompts" / "playbook.md").is_file(), folder.name


def test_the_cpc_playbook_holds_the_tips_of_the_league():
    # The file wraps its lines, so the test reads it as one line of words.
    playbook = " ".join(load_playbook(CPC).split())
    for tip in CPC_TIPS:
        assert tip in playbook, tip


def test_the_norcal_playbook_holds_general_tips_with_no_league_claim():
    playbook = load_playbook(NORCAL)
    assert playbook.count("\n- ") >= 4
    words = " ".join(playbook.split()).lower()
    for claim in LEAGUE_CLAIMS:
        assert claim.lower() not in words, claim


def test_a_client_with_no_playbook_stops_with_a_plain_message(tmp_path):
    with pytest.raises(FileNotFoundError, match="playbook.md"):
        load_playbook(cpc_client(at=tmp_path))


@pytest.fixture
def snap(fixture_raw_dir, fixture_history_root, chart_week6, fixture_nflverse_dir, tmp_path):
    cache = tmp_path / "nflverse"
    shutil.copytree(fixture_nflverse_dir, cache)
    slow = load_slow_sources(cache, 2026, 6, fixture_history_root)
    return load_snapshot(fixture_raw_dir, fixture_history_root, chart_week6, slow, client=CPC)


@pytest.fixture
def trade():
    return ProposedTrade(season=2026, asker=4, sides=(
        TradeSide(roster_id=4, gives=[{"player_id": "7569", "to": 12}]),
        TradeSide(roster_id=12, gives=[{"player_id": "8146", "to": 4}])))


def test_the_advisor_prompt_carries_the_playbook_of_the_client(snap, trade):
    cpc_system, _ = build_advisor_prompt(trade, snap, {}, None)
    norcal_system, _ = build_advisor_prompt(trade, snap.model_copy(update={"client": NORCAL}), {}, None)
    assert load_playbook(CPC) in cpc_system
    assert load_playbook(NORCAL) in norcal_system
    # The cpc tips live in the cpc Playbook only, so the prompt of NorCal never claims half PPR for its league.
    assert "consensus top 3 to 5 player" not in norcal_system
