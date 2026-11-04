"""
Tests for the rankings package through its published files: page.json and rankings.json of the week 6 fixtures.
Each client is the CPC client with one change: the median game off, or the package list ["week"] (AT-12).
"""
import json
import re
import shutil

import pytest
from cpc import cpc_client
from fakes import fixture_nflverse, no_claims, no_news

from cornerstone.pipeline import run_build
from league.models import History, PastWeek, Sentence, Verdict, VerifyOut
from league.paths import history_root, week_dir
from rankings.odds import playoff_odds
from rankings.power_rankings import power_rankings

WEEKS = 6


def _fake(system, user, model):
    if model.__name__ == "VerifyOut":
        return VerifyOut(verdicts=[Verdict(index=0, supported=True, reason="ok")])
    fid = re.search(r"^- ([A-Z][\w.]*): ", user, re.MULTILINE).group(1)
    return model(sentences=[Sentence(text="Fact sentence.", fact_ids=[fid])] * 2)


@pytest.fixture
def build(tmp_path, tmp_path_factory, fixture_raw_dir, fixture_history_root):
    """Build week 6 for a test client in a temp folder, and give the folder of its published files."""
    shutil.copytree(fixture_raw_dir, week_dir(tmp_path, 2026, WEEKS) / "raw")
    shutil.copytree(fixture_history_root, history_root(tmp_path, 2026))
    offline = {"news": no_news, "fetch_bytes": lambda url: None, "research": no_claims,
               "nflverse": fixture_nflverse(tmp_path_factory.mktemp("nflverse"))}

    def run(packages=None, **settings):
        client = cpc_client(at=tmp_path, **settings)
        if packages is not None:
            client = client.model_copy(update={"values": client.values.model_copy(update={"packages": packages})})
        run_build(tmp_path, 2026, WEEKS, _fake, fetch=False, **offline, client=client)
        return tmp_path / "site" / "2026"

    return run


def _read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_a_league_with_no_median_game_counts_one_game_a_week_in_the_standings(build):
    published = build(median_game=False)
    table = _read(published / f"week-{WEEKS:02d}" / "page.json")["table"]
    assert [row["standing"]["wins"] + row["standing"]["losses"] for row in table] == [WEEKS] * 12
    last = _read(published / "rankings.json")["weeks"][-1]
    assert [row["wins"] + row["losses"] for row in last["rows"]] == [WEEKS] * 12


def test_cpc_with_its_median_game_counts_two_games_a_week_in_the_standings(build):
    published = build()
    table = _read(published / f"week-{WEEKS:02d}" / "page.json")["table"]
    assert [row["standing"]["wins"] + row["standing"]["losses"] for row in table] == [2 * WEEKS] * 12


def _last_week_odds(client):
    """The odds with one week left: rosters 1 to 6 at 10 wins, 7 to 11 at 9 wins, and roster 12 at 8 wins."""
    wins = {rid: 10 if rid <= 6 else 9 if rid <= 11 else 8 for rid in range(1, 13)}
    records = {rid: (w, 26 - w, 1000.0 + rid) for rid, w in wins.items()}
    scores = {rid: [100.0 + rid] * 13 for rid in range(1, 13)}
    remaining = {14: [(1, 12), (2, 11), (3, 10), (4, 9), (5, 8), (6, 7)]}
    return playoff_odds(scores, records, remaining, season=2026, week=13, client=client, runs=200)


def test_a_league_with_no_median_game_counts_one_win_a_week_left_in_the_odds():
    # One win in the last week takes roster 12 to 9, under the 10 wins of the last spot, so it is out.
    off = _last_week_odds(cpc_client(median_game=False)).teams[12]
    assert (off.status, off.playoff, off.bye) == ("out", 0, 0)
    # With the median game, two wins take it to 10, level with the last spot, so it is still open.
    assert _last_week_odds(cpc_client()).teams[12].status == "open"


# Rosters 5 to 12 score 100 to 107, so the median of a week with rosters 1 to 4 under 100 is 101.5.
FILLERS = {rid: 95.0 + rid for rid in range(5, 13)}
PAIRS = [(1, 2), (3, 4), (5, 6), (7, 8), (9, 10), (11, 12)]


def test_a_league_with_no_median_game_drops_the_median_weight_from_the_power_form():
    # Roster 1 beats roster 2, 99 to 90, under the median of 101.5. With no median game, that is its only game.
    week = PastWeek(week=1, scores=FILLERS | {1: 99.0, 2: 90.0, 3: 91.0, 4: 92.0}, pairs=PAIRS, points={},
                    projections={}, stats={}, moves=[])
    row = next(r for r in power_rankings(History(week=1, weeks={1: week}), 1, median_game=False)[1] if r.roster_id == 1)
    # The streak is one head-to-head win, 2 of a cap of 2 times 3 weeks. The weighted record is 2-0. All-play is 3-8.
    streak = (2 + 6) / 12
    assert row.values["form"] == pytest.approx((streak + 1 + 3 / 11) / 3)
    assert (row.head_to_head, row.median) == ((1, 0), None)


def test_a_league_with_no_median_game_has_no_median_record_in_the_power_facts(build):
    published = build(median_game=False)
    facts = _read(published.parents[1] / "data" / "2026" / f"week-{WEEKS:02d}" / "facts.json")["sheet"]["facts"]
    power = [fact["text"] for fid, fact in facts.items() if re.fullmatch(r"PR\.\d+", fid)]
    assert len(power) == 12
    assert not [text for text in power if "median" in text]


def test_a_client_with_no_rankings_gets_no_rankings_file(build):
    published = build(packages=["week"])
    assert (published / f"week-{WEEKS:02d}" / "page.json").is_file()
    assert not (published / "rankings.json").exists()


def test_cpc_with_rankings_gets_the_rankings_file(build):
    assert (build() / "rankings.json").is_file()
