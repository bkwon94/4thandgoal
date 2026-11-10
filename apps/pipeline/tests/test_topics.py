"""
Tests for topics.json, the Answers of the 7 league Topics of the front door that the weekly build writes per team.
They run the build and the page-json command on recorded data and on the saved CPC week 8, with no network call.
"""
import json
import shutil
from pathlib import Path

from cpc import ROOT, cpc_client
from fakes import FakeJev, fixture_nflverse, no_claims, no_news
from test_pipeline import _fake, _no_bytes, _repo_with_history

from cornerstone.pipeline import run_build, run_page_json
from cornerstone.topics import write_topics
from league.paths import client_dir

LEAGUE_TOPICS = {"week_recap", "last_matchup", "next_matchup", "power_rankings", "playoff_race", "your_season",
                 "leaders_trades"}
CPC = client_dir(ROOT, "cpc")
# Lil Fridge, the team of the acceptance tests.
LIL_FRIDGE = "3"


def _topics(build: Path, season: int, week: int) -> dict:
    return json.loads((build / str(season) / f"week-{week:02d}" / "topics.json").read_text(encoding="utf-8"))


def _saved_week_8(tmp_path: Path) -> Path:
    """A client folder with the saved facts and blurbs of CPC 2026 week 8 and the two season files of its build."""
    data = tmp_path / "data" / "2026" / "week-08"
    data.mkdir(parents=True)
    for name in ("facts.json", "blurbs.json"):
        shutil.copy(CPC / "data" / "2026" / "week-08" / name, data / name)
    season = tmp_path / "build" / "2026"
    season.mkdir(parents=True)
    for name in ("rankings.json", "managers.json"):
        shutil.copy(CPC / "build" / "2026" / name, season / name)
    return tmp_path


def test_the_build_writes_an_answer_of_each_league_topic_for_each_team(tmp_path, fixture_raw_dir,
                                                                        fixture_history_root, tmp_path_factory):
    repo = _repo_with_history(tmp_path, fixture_raw_dir, fixture_history_root)
    run_build(repo, 2026, 6, _fake, fetch=False, news=no_news, fetch_bytes=_no_bytes,
              nflverse=fixture_nflverse(tmp_path_factory.mktemp("nflverse")), research=no_claims, jev=FakeJev(),
              client=cpc_client(at=repo))
    topics = _topics(repo / "build", 2026, 6)
    assert topics["schema_version"] == 1
    assert (topics["season"], topics["week"]) == (2026, 6)
    assert sorted(topics["teams"], key=int) == [str(n) for n in range(1, 13)]
    for answers in topics["teams"].values():
        assert {answer["topic"] for answer in answers} == LEAGUE_TOPICS


def test_week_8_of_cpc_has_7_answers_for_each_of_the_12_teams_and_the_same_page(tmp_path):
    """AT-51 and AT-56: the command writes topics.json from the saved week, and page.json stays as published."""
    folder = _saved_week_8(tmp_path)
    page = run_page_json(folder, 2026, 8, client=cpc_client(at=folder))
    topics = _topics(folder / "build", 2026, 8)
    assert len(topics["teams"]) == 12
    for answers in topics["teams"].values():
        assert sorted(answer["topic"] for answer in answers) == sorted(LEAGUE_TOPICS)
        # Each Suggestion shows one real number, so each fact holds a digit.
        assert all(any(ch.isdigit() for ch in answer["fact"]) for answer in answers)
    # The Topics step writes only its own file, so page.json keeps each byte and the week folder gains one file.
    before = page.read_bytes()
    assert write_topics(folder / "build", 2026, 8) == page.parent / "topics.json"
    assert page.read_bytes() == before
    assert sorted(path.name for path in page.parent.iterdir()) == ["page.json", "topics.json"]


def test_a_league_answer_reuses_the_blurbs_and_the_data_of_the_week(tmp_path):
    folder = _saved_week_8(tmp_path)
    run_page_json(folder, 2026, 8, client=cpc_client(at=folder))
    answers = {a["topic"]: a for a in _topics(folder / "build", 2026, 8)["teams"][LIL_FRIDGE]}
    page = json.loads((CPC / "published" / "2026" / "week-08" / "page.json").read_text(encoding="utf-8"))
    rankings = json.loads((CPC / "build" / "2026" / "rankings.json").read_text(encoding="utf-8"))
    row = next(r for r in rankings["weeks"][-1]["rows"] if r["roster_id"] == 3)

    ranked = answers["power_rankings"]
    assert ranked["fact"] == "6th, down 5"
    assert ranked["text"] == [" ".join(sentence["text"] for sentence in row["blurb"])]

    # Lil Fridge lost game 1 of week 8, 80.11 to 121.16, and its recap is the Answer text.
    last = answers["last_matchup"]
    assert last["fact"] == "Lost 80.11 to 121.16"
    assert last["text"] == [next(m["recap"] for m in page["matchups"] if m["id"] == 1)]
    assert [(r["label"], r["value"], r["you"]) for r in last["rows"]] == [
        ("Maye d'force B with U", "121.16", False), ("Lil Fridge", "80.11", True)]

    assert answers["next_matchup"]["fact"] == "Next: behold the lamb, 6-10"
    assert answers["next_matchup"]["text"] == [page["blurbs"]["next_week"]]
    assert answers["playoff_race"]["fact"] == "86% playoff odds"
    assert answers["your_season"]["fact"] == "10-6, 2nd of 12"
    assert answers["week_recap"]["fact"] == "You scored 80.11, 12th of 12"
    assert answers["week_recap"]["text"] == [page["blurbs"]["motw"]]
    assert answers["leaders_trades"]["text"] == [page["blurbs"]["position_leaders"]]
