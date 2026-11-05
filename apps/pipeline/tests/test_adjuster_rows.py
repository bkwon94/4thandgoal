"""
Tests for the rows of the result document: a silent row hides, each row reads in plain words, and no row and no
fairness reason holds an inner word. They grade real trades on the week 6 and the week 9 snapshots at the result document seam.
"""
import shutil
from pathlib import Path

import pytest
from conftest import with_carries
from cpc import cpc_client, four_week

from analyzer.analysis import INNER_WORDS, _inner_word_failures, code_only
from analyzer.routes import result_document
from analyzer.rubric import ProposedTrade, TradeSide
from analyzer.tunables import EXPECTED_ADJUSTER_ON
from league.chart import match_chart
from league.models import ChartRead, week_lines
from league.parse import parse_week
from league.paths import returns_path
from league.provider.sleeper import load_raw
from league.slow_sources import load_slow_sources
from league.snapshot import build_snapshot, load_out_for_season, load_returns, load_snapshot

CLIENT = cpc_client()

# Week 6: Brian Robinson on roster 7 and Keaton Mitchell on roster 11. Mitchell backs up a starter on no roster of
# the trade, so no player is a handcuff. The id map fixture lacks the LAC players, so the test adds them.
B_ROBINSON, MITCHELL = "8154", "9511"
LAC_IDS = {MITCHELL: "00-0038454", "12507": "00-0040666", "11647": "00-0039391"}


@pytest.fixture
def slow_snap(fixture_raw_dir, fixture_history_root, chart_week6, fixture_nflverse_dir, tmp_path):
    """The week 6 snapshot with the slow sources from the nflverse fixture, and the LAC players in the id map."""
    cache = tmp_path / "nflverse"
    shutil.copytree(fixture_nflverse_dir, cache)
    slow = load_slow_sources(cache, 2026, 6, fixture_history_root)
    snap = four_week(load_snapshot(fixture_raw_dir, fixture_history_root, chart_week6, slow, client=CLIENT))
    return snap.model_copy(update={"id_map": {**snap.id_map, **LAC_IDS}})


def _trade(first: int, first_gives: list[str], second: int, second_gives: list[str]) -> ProposedTrade:
    return ProposedTrade(season=2026, asker=first, sides=(
        TradeSide(roster_id=first, gives=[{"player_id": pid, "to": second} for pid in first_gives]),
        TradeSide(roster_id=second, gives=[{"player_id": pid, "to": first} for pid in second_gives])))


def _document(trade: ProposedTrade, snapshot) -> dict:
    return result_document(trade, snapshot, code_only(trade, snapshot))


def _rows(document: dict, roster_id: int) -> dict[str, str]:
    """The factors of one side, by name, with the reason of each."""
    side = next(side for side in document["sides"] if side["roster_id"] == roster_id)
    return {factor["name"]: factor["reason"] for factor in side["factors"]}


def test_a_row_that_says_nothing_is_not_in_the_document(slow_snap):
    rows = _rows(_document(_trade(7, [B_ROBINSON], 11, [MITCHELL]), slow_snap), 7)
    # "No player it gets is a handcuff." and "No player it gets is a star out now or has an opportunity." say nothing.
    assert "handcuff" not in rows
    assert "upside" not in rows
    # The deal row, the roster row, and the standing row always show.
    assert {"deal", "roster fit", "standing"} <= set(rows)


# Week 6: roster 5 gets Saquon Barkley of PHI from roster 10 for James Cook of BUF. The PHI bye is in week 10, after the
# Week line weeks 6 and 7. His week 15 to 17 opponents are SEA, HOU, and SF, ranked 18, 28, and 15 against RBs.
SAQUON, COOK = "4866", "8138"


def test_the_schedule_row_names_the_bye_and_each_playoff_opponent_with_its_rank(slow_snap):
    rows = _rows(_document(_trade(10, [SAQUON], 5, [COOK]), slow_snap), 5)
    assert rows["schedule"] == (
        "Barkley has his bye in week 10 and faces SEA (18th most points to RBs), HOU (28th), and SF (15th) "
        "in weeks 15 to 17.")


def test_the_usage_row_gives_the_snap_carry_and_target_shares_of_a_running_back(slow_snap):
    # Worked from the week 6 fixture. Barkley in weeks 3 and 4: 40 of 111 snaps, 17 of 46 carries, 3 of 49 targets.
    # Cook in weeks 4 and 5: 75 of 123 snaps, down from 99 of 140, 37 of 56 carries, and 3 of 31 targets.
    rows = _rows(_document(_trade(10, [SAQUON], 5, [COOK]), slow_snap), 5)
    assert rows["trend and usage"] == (
        "Barkley plays 36% of the snaps, takes 37% of the carries, and sees 6% of the targets; "
        "Cook plays 61% of the snaps (down), takes 66% of the carries, and sees 10% of the targets.")


# Week 6: Patrick Mahomes on roster 7 and Lamar Jackson on roster 6.
MAHOMES, LAMAR = "4046", "4881"


def test_a_quarterback_has_no_usage_clause_unless_a_share_moved(slow_snap):
    # Mahomes plays nearly every snap, with flat shares, so he has no clause. Jackson's snap share fell, and that
    # move steps the grade, so the row names it and no other number of his.
    document = _document(_trade(7, [MAHOMES], 6, [LAMAR]), slow_snap)
    for side in (6, 7):
        assert _rows(document, side)["trend and usage"] == "Jackson plays 76% of the snaps (down)."


# Week 6: Chris Olave on roster 2 is on the injury report in week 2. Jakobi Meyers on roster 3 is never on it.
# Wicks on roster 3 for Saquon Barkley on roster 10, who is Out.
OLAVE, OLAVE_GSIS, MEYERS, WICKS = "8144", "00-0037239", "5947", "9486"


def _with_report_weeks(snap, gsis: str, weeks: list[int]):
    injuries = {**snap.injuries, gsis: {**snap.injuries[gsis], **{week: "Questionable" for week in weeks}}}
    return snap.model_copy(update={"injuries": injuries})


def test_the_injury_row_counts_the_weeks_on_the_injury_report(slow_snap):
    # Weeks 2, 3, and 4 of the 5 completed weeks.
    snap = _with_report_weeks(slow_snap, OLAVE_GSIS, [3, 4])
    assert _rows(_document(_trade(3, [MEYERS], 2, [OLAVE]), snap), 3)["injury"] == (
        "Olave was on the injury report in 3 of 5 weeks.")


def test_the_injury_row_names_the_return_week(slow_snap):
    # The trade week is 6, so a return in week 9 is past the return window and steps down.
    snap = slow_snap.model_copy(update={"returns": {SAQUON: 9}})
    assert _rows(_document(_trade(3, [WICKS], 10, [SAQUON]), snap), 3)["injury"] == "Barkley is out until week 9."


def test_the_injury_row_names_a_near_return_week_with_no_step(slow_snap):
    # A return in week 7 is near, so the row has no step, but the return week is still news to the manager.
    # The id map fixture lacks Barkley, so the row also says that no count of report weeks ran for him.
    snap = slow_snap.model_copy(update={"returns": {SAQUON: 7}})
    assert _rows(_document(_trade(3, [WICKS], 10, [SAQUON]), snap), 3)["injury"] == (
        "Barkley is out until week 7. Saquon Barkley has no injury report count on file.")


def test_a_player_with_no_gsis_id_reads_in_plain_words_in_the_injury_and_handcuff_rows(slow_snap):
    # The id map fixture lacks Barkley, so no report count and no handcuff check ran for him.
    # A near return keeps the injury row at no step, so the row adds the note of the count.
    snap = slow_snap.model_copy(update={"returns": {SAQUON: 7}})
    rows = _rows(_document(_trade(3, [WICKS], 10, [SAQUON]), snap), 3)
    assert rows["injury"].endswith("Saquon Barkley has no injury report count on file.")
    assert rows["handcuff"].endswith("Saquon Barkley has no handcuff check on file.")
    # No row names an inner part: not the id map, and not a chart.
    assert [text for text in rows.values() if "id map" in text or "chart" in text] == []


# Week 6: Omarion Hampton on roster 12 holds the top value at RB, so he is a top RB. Collins is on roster 4.
# Rome Odunze on roster 4 and Luther Burden on roster 12 are CHI receivers, and Odunze's snap share is up.
HAMPTON, COLLINS, ODUNZE, BURDEN, WATSON = "12507", "7569", "11620", "12519", "8167"


def _with_status(snap, player: str, status: str | None):
    players = {**snap.players, player: snap.players[player].model_copy(update={"injury_status": status})}
    return snap.model_copy(update={"players": players})


@pytest.mark.parametrize("returns, text", [
    ({HAMPTON: 8}, "Hampton is a top RB, due back in week 8."),
    ({}, "Hampton is a top RB, out now with no return week on file."),
])
def test_the_upside_row_names_a_top_player_out_now_and_his_return(slow_snap, returns, text):
    snap = _with_status(slow_snap, HAMPTON, "Out").model_copy(update={"returns": returns})
    assert _rows(_document(_trade(4, [COLLINS], 12, [HAMPTON]), snap), 4)["upside"] == text


@pytest.mark.parametrize("out_for_season, text", [
    (True, "Odunze gets more work while Burden is out for the season."),
    (False, "Odunze gets more work while Burden is out."),
])
def test_the_upside_row_says_a_player_gets_more_work_while_a_teammate_is_out(slow_snap, out_for_season, text):
    snap = (slow_snap.model_copy(update={"out_for_season": {*slow_snap.out_for_season, BURDEN}}) if out_for_season
            else _with_status(slow_snap, BURDEN, "Out"))
    assert _rows(_document(_trade(1, [WATSON], 4, [ODUNZE]), snap), 1)["upside"] == text


# Week 6, the NE depth chart: Rhamondre Stevenson on roster 7 first, then TreVeyon Henderson on roster 8. The other
# NE backs take 11, 21, and 21 carries in weeks 3 to 5. At 3 a game Henderson takes 15%, and at 11 a game 38%.
STEVENSON, HENDERSON, CAR_DEF = "7611", "12529", "CAR"
NE_IDS = {STEVENSON: "00-0036875", HENDERSON: "00-0040734"}


@pytest.mark.parametrize("carries, text", [
    (3.0, "Henderson backs up your RB, Stevenson, on the Patriots depth chart."),
    (11.0, ("Henderson backs up your RB, Stevenson, on the Patriots depth chart, but he takes 38% of the carries, "
            "so he is no handcuff.")),
])
def test_the_handcuff_row_names_the_starter_he_backs_up_and_the_team(slow_snap, carries, text):
    snap = with_carries(slow_snap.model_copy(update={"id_map": {**slow_snap.id_map, **NE_IDS}}), HENDERSON,
                        {3: carries, 4: carries, 5: carries})
    assert _rows(_document(_trade(7, [CAR_DEF], 8, [HENDERSON]), snap), 7)["handcuff"] == text


SAVED = CLIENT.folder / "data" / "2026"
# Trade A: roster 10, a seller, gives Omar Cooper Jr. to roster 6, a contender, for Parker Washington.
COOPER, WASHINGTON = "13276", "9487"


@pytest.fixture(scope="module")
def week_9():
    returns_file = returns_path(CLIENT.nfl_dir, 2026)
    return build_snapshot(load_raw(SAVED / "week-08" / "raw"), SAVED / "history", None, trade_week=9,
                          returns=load_returns(returns_file), out_for_season=load_out_for_season(returns_file),
                          client=CLIENT)


@pytest.fixture(scope="module")
def trade_a_document(week_9):
    return _document(_trade(10, [COOPER], 6, [WASHINGTON]), week_9)


def test_the_roster_row_counts_the_players_in_the_top_n_before_and_after(trade_a_document):
    # The WR line of the client is 36. Roster 10 has 2 WRs above it before and after, and gets Washington, the
    # better player by points per game. Roster 6 has 3 before and after.
    assert _rows(trade_a_document, 10)["roster fit"] == "You keep 2 WRs in the top 36, and you get the better player."
    assert _rows(trade_a_document, 6)["roster fit"] == "You keep 3 WRs in the top 36."


def test_the_standing_row_names_the_race_the_need_and_whether_the_trade_meets_it(trade_a_document):
    # Roster 10 is out of the race and gets the better player. Roster 6 holds a playoff spot, and its lineup
    # changes by less than the fit threshold.
    assert _rows(trade_a_document, 10)["standing"] == (
        "Out of the playoff race, so you want the better player for the rest of the season, and you get him.")
    assert _rows(trade_a_document, 6)["standing"] == (
        "In a playoff spot, so you need points now, and this trade keeps your points about the same.")


def test_the_usage_row_gives_one_clause_per_player_with_the_shares_of_a_receiver(trade_a_document):
    # Worked from the saved stat lines. Cooper: 88 of 123 snaps and 10.2 air yards per target in weeks 7 and 8.
    # Washington: 88 of 125 snaps and 42 air yards on 13 targets in weeks 6 and 8. No week and no route share show.
    assert _rows(trade_a_document, 10)["trend and usage"] == (
        "Washington plays 70% of the snaps (down), sees 22% of the targets, and averages 3.2 air yards per target; "
        "Cooper plays 72% of the snaps (up), sees 8% of the targets (down), and averages 10.2 air yards per target.")


# Each row the code writes. The deal, roster, and standing rows are one sentence each. The injury row and the
# schedule row can hold one sentence per player.
ONE_SENTENCE_ROWS = ("deal", "roster fit", "standing")
PLAIN_ROWS = (*ONE_SENTENCE_ROWS, "trend and usage", "injury", "upside", "handcuff", "schedule")


def _one_for_one_trades(snapshot, first: int, second: int) -> list[ProposedTrade]:
    """Every trade of one player for one player between two rosters."""
    return [_trade(first, [mine], second, [theirs])
            for mine in snapshot.rosters[first] for theirs in snapshot.rosters[second]]


@pytest.mark.parametrize("first, second", [(7, 11), (1, 4), (3, 12)])
def test_no_row_holds_an_inner_word_on_the_week_6_trades(slow_snap, first, second):
    # Rosters 1 and 3 hold a playoff spot, roster 4 is out of the race, and rosters 7, 11, and 12 are middle teams.
    texts = [reason for trade in _one_for_one_trades(slow_snap, first, second)
             for side in (first, second) for name, reason in _rows(_document(trade, slow_snap), side).items()
             if name in PLAIN_ROWS]
    assert texts
    assert [(text, failure) for text in texts if (failure := _inner_word_failures("row", text))] == []


def test_no_row_holds_an_inner_word_on_the_week_9_trades(week_9):
    texts = [reason for trade in _one_for_one_trades(week_9, 10, 6)
             for side in (10, 6) for name, reason in _rows(_document(trade, week_9), side).items()
             if name in PLAIN_ROWS]
    assert [(text, failure) for text in texts if (failure := _inner_word_failures("row", text))] == []


@pytest.mark.parametrize("first, second", [(7, 11), (1, 4), (3, 12)])
def test_no_fairness_reason_holds_an_inner_word_on_the_week_6_trades(slow_snap, first, second):
    # The fairness line shows the rows of the steps of a side, else its deal row, so it reads the same plain words.
    texts = [side["reason"] for trade in _one_for_one_trades(slow_snap, first, second)
             for side in _document(trade, slow_snap)["fairness"]["sides"]]
    assert texts
    assert [(text, failure) for text in texts if (failure := _inner_word_failures("fairness", text))] == []


def test_a_fairness_reason_is_one_row_or_a_step_up_row_but_a_step_down_row(slow_snap):
    # Saquon for Cook: one side gets a roster fit step up and a trend step down, so its reason joins the two rows.
    document = _document(_trade(10, [SAQUON], 5, [COOK]), slow_snap)
    joined = 0
    for side in document["fairness"]["sides"]:
        rows = _rows(document, side["roster_id"]).values()
        pairs = {up.removesuffix(".") + ", but " + down for up in rows for down in rows if up != down}
        assert side["reason"] in rows or side["reason"] in pairs
        joined += side["reason"] in pairs
    assert joined == 1


WEEK_9_READ = Path(__file__).parent / "fixtures" / "charts" / "read-week-09.json"
# Trade W, Brian's trade of week 9: Bo Girds, roster 6, gives Washington and Walker to Teehee, roster 12, for
# Tee Higgins, Bhayshul Tuten, and Tony Pollard.
WALKER = "8151"
TRADE_W = ((6, [WASHINGTON, WALKER]), (12, ["6801", "12490", "5967"]))


@pytest.fixture(scope="module")
def week_9_chart(week_9):
    """The week 9 snapshot with the trade values of the week 9 chart read, matched as the CLI does."""
    read = ChartRead.model_validate_json(WEEK_9_READ.read_text(encoding="utf-8"))
    chart = match_chart(read, week_lines(parse_week(load_raw(SAVED / "week-08" / "raw"))))
    return week_9.model_copy(update={"chart": chart})


def test_trade_w_is_fair_and_teehee_names_the_superstar_then_the_roster_loss(week_9_chart):
    # Teehee gets one step up for Walker and one step down for roster fit. The net is zero, so its reason names both.
    (bo_girds, bo_gives), (teehee, teehee_gives) = TRADE_W
    document = _document(_trade(bo_girds, bo_gives, teehee, teehee_gives), week_9_chart)
    fit = _rows(document, teehee)["roster fit"]
    assert fit.startswith("You go from 4 RBs in the top 36 to 3")
    assert (document["fairness"]["state"], document["fairness"]["gives_more"]) == ("fair", None)
    assert [side["reason"] for side in document["fairness"]["sides"]] == [
        _rows(document, bo_girds)["roster fit"],
        "Kenneth Walker III is a superstar, a top 8 player this week, but " + fit[0].lower() + fit[1:]]


def test_the_check_reads_each_inner_word_of_decision_03():
    assert INNER_WORDS == ["trade value", "highest-value", "best lineup", "the line", "hole", "win-now move",
                           "return bet", "star", "opportunity", "one step", "no step", "takes RB", "takes WR",
                           "takes TE", "takes QB", "sits on the bench"]


def test_each_row_is_one_sentence_with_no_step_word(trade_a_document):
    for side in trade_a_document["sides"]:
        for factor in side["factors"]:
            if factor["name"] in ONE_SENTENCE_ROWS:
                assert factor["reason"].count(". ") == 0 and factor["reason"].endswith(".")
            for words in ("one step up", "one step down", "no step"):
                assert words not in factor["reason"].lower()


def test_no_document_has_an_expected_gap_row(trade_a_document):
    assert EXPECTED_ADJUSTER_ON is False
    assert [f["name"] for side in trade_a_document["sides"] for f in side["factors"] if f["name"] == "expected gap"] == []
