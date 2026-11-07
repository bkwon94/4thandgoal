"""
Tests for the draft steals and busts of the midseason report, from the real saved data and drafts of CPC and NorCal 2026.
Each build gets the draft through the fixture provider, so no test calls Sleeper or patches the port (ADR 0015).
"""
import json
import shutil
from pathlib import Path

from cpc import ROOT
from fakes import NORCAL_DRAFT_FIXTURES, FixtureProvider
from test_midseason import _call, _report, build_week_8, prime_nflverse

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


def _cpc_draft(cpc_midseason) -> dict:
    """The draft chapter of the shared CPC week 8 build of the fixture `cpc_midseason`."""
    return _draft(_report(cpc_midseason[1]))


def test_a_cpc_steal_is_matthew_golden_at_2_dollars_and_a_bust_is_aj_brown_at_39_and_just_bad(cpc_midseason):
    # AT-12.
    draft = _cpc_draft(cpc_midseason)
    assert draft["draft_type"] == "auction"
    golden = _by_name(draft["steals"])["Matthew Golden"]
    assert (golden["cost"], golden["position"], golden["team"]) == (2, "WR", "Bo Girds")
    brown = _by_name(draft["busts"])["A.J. Brown"]
    assert (brown["cost"], brown["tag"]) == (39, "just bad")


def test_a_bust_who_missed_games_out_with_an_injury_is_hurt(cpc_midseason):
    # Saquon Barkley sat out weeks 5 to 7 with a hamstring: Out rows in weeks 5 and 6, and no snap in week 7.
    barkley = _by_name(_cpc_draft(cpc_midseason)["busts"])["Saquon Barkley"]
    assert (barkley["cost"], barkley["tag"]) == (58, "hurt")


def test_the_hurt_tag_reads_the_missed_game_rule_of_the_injury_toll(cpc_midseason):
    # Jadarian Price has an Out row of the injury report in week 4 and no snap from week 4 to 8, so he missed 5 games.
    # De'Von Achane has no nflverse row and no snap from week 4. The players file of week 8 gives him IR, so his
    # absence is an injury, and his bust is "hurt".
    busts = _by_name(_cpc_draft(cpc_midseason)["busts"])
    assert (busts["Jadarian Price"]["cost"], busts["Jadarian Price"]["tag"]) == (20, "hurt")
    assert busts["De'Von Achane"]["tag"] == "hurt"


def test_a_steal_has_no_one_that_got_away_line(cpc_midseason):
    # AT-14 is retired: decision 15 removed the line. Tyler Allgeier left Bo Girds, and his row has no line.
    steals = _by_name(_cpc_draft(cpc_midseason)["steals"])
    assert steals["Tyler Allgeier"]["team"] == "Bo Girds"
    assert all("line" not in row for row in steals.values())


def test_the_lists_hold_the_top_5_by_swing_with_starters_only_and_no_kicker_or_defense(cpc_midseason):
    draft = _cpc_draft(cpc_midseason)
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


def test_the_build_saves_the_draft_that_the_provider_gives_in_the_data_folder_of_the_season(cpc_midseason):
    client, _ = cpc_midseason
    saved = json.loads((client.folder / "data" / "2026" / "draft" / "picks.json").read_text(encoding="utf-8"))
    assert len(saved) == 168


def test_the_draft_has_one_prose_block_in_the_review_file(cpc_midseason):
    _, out = cpc_midseason
    review = (out.parent / "midseason-review.md").read_text(encoding="utf-8")
    assert "## draft: Draft Steals and Busts" in review
    assert "## draft." not in review


def test_a_cpc_letdown_is_bijan_robinson_at_81_dollars_with_no_top_17_rb_week_since_week_4(cpc_midseason):
    # AT-65. He cost $81, the top price of the draft, and he is RB3 for the season. His RB ranks of weeks 5 to 8 are
    # 18, 31, 19, and 28 by the half PPR points of CPC, so his last week in the top 17 is week 4, at RB5.
    draft = _cpc_draft(cpc_midseason)
    bijan = _by_name(draft["letdowns"])["Bijan Robinson"]
    assert (bijan["cost"], bijan["price_rank"], bijan["position"], bijan["points_rank"], bijan["last_top_week"]) == (
        81, 1, "RB", 3, 4)
    assert bijan["team"]


def test_a_dear_pick_with_a_top_17_week_in_his_last_4_weeks_played_is_not_a_letdown(cpc_midseason):
    # Jahmyr Gibbs cost $80, the second price of the draft, and he is not a bust. He had a bye in week 6, so his last 4
    # weeks played are weeks 4, 5, 7, and 8, at RB14, RB1, RB18, and RB5.
    draft = _cpc_draft(cpc_midseason)
    assert "Jahmyr Gibbs" not in _by_name(draft["busts"])
    assert "Jahmyr Gibbs" not in _by_name(draft["letdowns"])


def test_no_player_is_both_a_bust_and_a_letdown(cpc_midseason):
    # Saquon Barkley cost $58, the seventh price, and his RB ranks of his last 4 weeks played are 26, 73, 20, and 21.
    # He has no top 17 week there, but he is a bust, so he is not a letdown.
    draft = _cpc_draft(cpc_midseason)
    assert "Saquon Barkley" in _by_name(draft["busts"])
    assert not set(_by_name(draft["busts"])) & set(_by_name(draft["letdowns"]))
    assert all(row["price_rank"] <= 10 for row in draft["letdowns"])


def test_the_writer_can_cite_the_price_the_season_rank_and_the_last_top_week_of_a_letdown(cpc_midseason):
    _, out = cpc_midseason
    facts = json.loads((out.parent / "midseason-facts.json").read_text(encoding="utf-8"))["sheet"]["facts"]
    assert facts["DV.letdown.9509"]["text"] == "To Infinity and Bijan drafted Bijan Robinson for $81, the 1st price of the draft."
    assert facts["DV.letdown.9509.points"]["text"] == "Bijan Robinson is the 3rd drafted RB by points."
    assert facts["DV.letdown.9509.week"]["text"] == "Bijan Robinson was last in the top 17 RBs in week 4."
