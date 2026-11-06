"""
Tests for the draft steals and busts of the midseason report, from the real saved data and drafts of CPC and NorCal 2026.
Each build gets the draft through the fixture provider, so no test calls Sleeper or patches the port (ADR 0015).
"""
import json
import shutil
from pathlib import Path

from cpc import ROOT
from fakes import NORCAL_DRAFT_FIXTURES, FixtureProvider
from test_midseason import CPC_PROVIDER, _call, _cpc_week_8, _report, build_week_8, prime_nflverse

from cornerstone.value_models import VALUE_MODELS
from league.client import Client, read_client_values
from league.paths import client_dir, history_root, league_file, nflverse_cache_dir, week_dir
from league.provider.raw import RawLeague
from league.provider.sleeper import league_settings

NORCAL_DATA = client_dir(ROOT, "norcal") / "data" / "2026"
NORCAL_PROVIDER = FixtureProvider(raw_dir=NORCAL_DATA / "week-08" / "raw", history_root=NORCAL_DATA / "history",
                                  draft_dir=NORCAL_DRAFT_FIXTURES)
# A bust was drafted as a starter, and a steal plays like a starter now. Decision ticket 02.
STARTER_RANK = {"QB": 12, "TE": 12, "RB": 24, "WR": 24}


def _norcal_week_8(tmp_path: Path) -> Client:
    """A NorCal client folder in `tmp_path` with the saved history and week 8 of the real NorCal data, and the NFL
    schedule and the injury report in its NFL data."""
    settings = league_settings(RawLeague.model_validate_json(league_file(client_dir(ROOT, "norcal"), 2026).read_text()))
    client = Client(slug="norcal", folder=tmp_path, nfl_dir=tmp_path / "data",
                    values=read_client_values(client_dir(ROOT, "norcal"), VALUE_MODELS), settings=settings)
    shutil.copytree(NORCAL_DATA / "history", history_root(client.folder, 2026))
    shutil.copytree(NORCAL_DATA / "week-08", week_dir(client.folder, 2026, 8))
    prime_nflverse(client.nfl_dir)
    shutil.copy(Path(__file__).parent / "fixtures" / "nflverse" / "games.csv", nflverse_cache_dir(client.nfl_dir))
    return client


def _draft(report: dict) -> dict:
    act = next(act for act in report["acts"] if act["key"] == "the-moves")
    return next(chapter for chapter in act["chapters"] if chapter["key"] == "draft")["facts"]


def _by_name(rows: list[dict]) -> dict[str, dict]:
    return {row["name"]: row for row in rows}


def _cpc_draft(tmp_path: Path) -> dict:
    return _draft(_report(build_week_8(_call(), client=_cpc_week_8(tmp_path), provider=CPC_PROVIDER)))


def test_a_cpc_steal_is_matthew_golden_at_2_dollars_and_a_bust_is_aj_brown_at_39_and_just_bad(tmp_path):
    # AT-12.
    draft = _cpc_draft(tmp_path)
    assert draft["draft_type"] == "auction"
    golden = _by_name(draft["steals"])["Matthew Golden"]
    assert (golden["cost"], golden["position"], golden["team"]) == (2, "WR", "Bo Girds")
    brown = _by_name(draft["busts"])["A.J. Brown"]
    assert (brown["cost"], brown["tag"]) == (39, "just bad")


def test_a_bust_who_missed_two_games_out_with_an_injury_is_hurt(tmp_path):
    # Saquon Barkley sat out weeks 5 and 6 with a hamstring, by the nflverse injury report.
    barkley = _by_name(_cpc_draft(tmp_path)["busts"])["Saquon Barkley"]
    assert (barkley["cost"], barkley["tag"]) == (58, "hurt")


def test_the_hurt_tag_reads_the_missed_game_rule_of_the_injury_toll(tmp_path):
    # Jadarian Price has no snaps in week 4 with an Out row of the injury report, and no snaps in week 6 with a
    # Sleeper status of out, so he missed 2 games. De'Von Achane has no nflverse row and no Sleeper out status in any
    # week, so the rule finds no missed game, and his bust is "just bad".
    busts = _by_name(_cpc_draft(tmp_path)["busts"])
    assert (busts["Jadarian Price"]["cost"], busts["Jadarian Price"]["tag"]) == (20, "hurt")
    assert busts["De'Von Achane"]["tag"] == "just bad"


def test_a_steal_that_its_drafter_let_go_carries_the_one_that_got_away_line(tmp_path):
    # AT-14: Bo Girds bought Tyler Allgeier for $2 and traded him in week 2. Golden stayed, so he has no line.
    steals = _by_name(_cpc_draft(tmp_path)["steals"])
    allgeier = steals["Tyler Allgeier"]
    assert (allgeier["cost"], allgeier["team"], allgeier["line"]) == (2, "Bo Girds", "the one that got away")
    assert steals["Matthew Golden"]["line"] is None


def test_the_lists_hold_the_top_5_by_swing_with_starters_only_and_no_kicker_or_defense(tmp_path):
    draft = _cpc_draft(tmp_path)
    assert len(draft["steals"]) == 5 and len(draft["busts"]) == 5
    for row in draft["steals"]:
        assert row["points_rank"] <= STARTER_RANK[row["position"]]
        assert row["swing"] == row["cost_rank"] - row["points_rank"] > 0
        assert row["tag"] is None
    for row in draft["busts"]:
        assert row["cost_rank"] <= STARTER_RANK[row["position"]]
        assert row["swing"] == row["cost_rank"] - row["points_rank"] < 0
    assert [row["swing"] for row in draft["steals"]] == sorted((row["swing"] for row in draft["steals"]), reverse=True)
    assert [row["swing"] for row in draft["busts"]] == sorted(row["swing"] for row in draft["busts"])


def test_in_norcal_each_pick_cost_is_its_pick_number_and_no_pick_shows_a_dollar_amount(tmp_path):
    # AT-13.
    client = _norcal_week_8(tmp_path)
    out = build_week_8(_call(), client=client, provider=NORCAL_PROVIDER)
    draft = _draft(_report(out))
    assert draft["draft_type"] == "snake"
    picks = json.loads((NORCAL_DRAFT_FIXTURES / "picks.json").read_text(encoding="utf-8"))
    pick_no = {pick["player_id"]: pick["pick_no"] for pick in picks}
    rows = draft["steals"] + draft["busts"]
    assert len(rows) == 10
    for row in rows:
        assert row["cost"] == pick_no[row["player_id"]]
    facts = json.loads((out.parent / "midseason-facts.json").read_text(encoding="utf-8"))["sheet"]["facts"]
    draft_facts = [f["text"] for fid, f in facts.items() if fid.startswith("DV.")]
    assert draft_facts and not any("$" in text for text in draft_facts)


def test_the_build_saves_the_draft_that_the_provider_gives_in_the_data_folder_of_the_season(tmp_path):
    client = _cpc_week_8(tmp_path)
    build_week_8(_call(), client=client, provider=CPC_PROVIDER)
    saved = json.loads((client.folder / "data" / "2026" / "draft" / "picks.json").read_text(encoding="utf-8"))
    assert len(saved) == 168


def test_the_draft_has_a_prose_block_and_a_roast_block_in_the_review_file(tmp_path):
    client = _cpc_week_8(tmp_path)
    out = build_week_8(_call(), client=client, provider=CPC_PROVIDER)
    review = (out.parent / "midseason-review.md").read_text(encoding="utf-8")
    assert "## draft: Draft Steals and Busts" in review
    assert "## draft.roast:" in review
