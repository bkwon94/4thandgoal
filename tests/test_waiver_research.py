"""
Tests for the research step of the waiver board.
They inject a fake search call at the research seam, so no test reaches the Claude API.
"""
from datetime import datetime
from zoneinfo import ZoneInfo

import anthropic
import pytest
import httpx2

from cornerstone.models import BoardScores, ResearchClaim, ResearchOut, WaiverBoard, WaiverPlayer
from cornerstone.sheet import NUMBER_TOKEN
from cornerstone.verifier import without_urls
from cornerstone.waiver_research import build_research_prompt, research_board
from cornerstone.writer import WriterError

BUILT = datetime(2026, 10, 20, 21, 0, tzinfo=ZoneInfo("America/New_York"))
URL = "https://sports.yahoo.com/fantasy/article/week-7-waiver-wire-141451458.html"


def _player(pid: str, name: str = "Tre Tucker") -> WaiverPlayer:
    return WaiverPlayer(player_id=pid, name=name, position="WR", team="LV", week_projection=9.5,
                        ros_projection=80.0, scores=BoardScores(), board_score=0.5)


def _board(**buckets: list[WaiverPlayer]) -> WaiverBoard:
    return WaiverBoard(week=6, built=BUILT, buckets=buckets, budgets=[])


def _claim(text: str = "Harmon calls him the top add of the week.", url: str = URL) -> ResearchClaim:
    return ResearchClaim(text=text, url=url, source="Yahoo Fantasy", date="2026-10-20", stance="backs")


def _answer(*claims: ResearchClaim):
    def call(system: str, user: str) -> ResearchOut:
        return ResearchOut(claims=list(claims))
    return call


def test_a_claim_with_no_url_is_dropped():
    board = research_board(_board(best_adds=[_player("1")]), _answer(_claim(url=""), _claim("He saw 9 targets.")))
    assert [c.text for c in board.buckets["best_adds"][0].research] == ["He saw 9 targets."]


def test_a_player_keeps_at_most_two_claims():
    board = research_board(_board(best_adds=[_player("1")]), _answer(_claim("A."), _claim("B."), _claim("C.")))
    assert [c.text for c in board.buckets["best_adds"][0].research] == ["A.", "B."]


def test_the_research_reads_at_most_32_players_once_each_and_never_a_drop():
    asked: list[str] = []

    def call(system: str, user: str) -> ResearchOut:
        asked.append(user)
        return ResearchOut(claims=[_claim()])

    adds = [_player(str(i), f"Player {i}") for i in range(30)]
    trending = [adds[0], *(_player(str(i), f"Player {i}") for i in range(30, 40))]
    board = research_board(_board(best_adds=adds, trending=trending, drops=[_player("99", "Drop Guy")]), call)
    assert len(asked) == 32
    assert not any("Drop Guy" in user for user in asked)
    assert board.buckets["trending"][0].research and board.buckets["trending"][0] == board.buckets["best_adds"][0]
    assert not board.buckets["trending"][-1].research
    assert not board.buckets["drops"][0].research


def test_a_failure_for_one_player_leaves_the_other_claims_in_place(caplog):
    def call(system: str, user: str) -> ResearchOut:
        if "Bad Luck" in user:
            raise WriterError("no parsed output")
        return ResearchOut(claims=[_claim()])

    board = research_board(_board(best_adds=[_player("1"), _player("2", "Bad Luck"), _player("3", "Jalen Coker")]),
                           call)
    assert [bool(p.research) for p in board.buckets["best_adds"]] == [True, False, True]
    assert not board.experts_missing
    assert "Bad Luck" in caplog.text


def test_a_failure_for_every_player_sets_the_missing_experts_flag(caplog):
    def call(system: str, user: str) -> ResearchOut:
        raise anthropic.APIConnectionError(request=httpx2.Request("POST", "https://api.anthropic.com"))

    board = research_board(_board(best_adds=[_player("1"), _player("2", "Jalen Coker")]), call)
    assert board.experts_missing
    assert not any(p.research for p in board.buckets["best_adds"])
    assert any(r.levelname == "WARNING" and "every player" in r.message for r in caplog.records)


def test_each_claim_lands_in_the_facts_with_its_url_as_the_citation():
    board = research_board(_board(best_adds=[_player("7")]),
                           _answer(_claim("He ran 31 routes."), _claim("He is the WR2 now.", URL + "?b=2")))
    facts = {f.id: f for f in board.buckets["best_adds"][0].facts}
    assert set(facts) == {"WV.research.7.1", "WV.research.7.2"}
    first = facts["WV.research.7.1"]
    assert first.text.startswith("He ran 31 routes.") and URL in first.text
    assert first.players == ["Tre Tucker"]
    # Every digit outside the URL is in the numbers. The URL digits are the citation, not a claim.
    assert set(NUMBER_TOKEN.findall(without_urls(first.text))) == set(first.numbers) == {"31"}


def test_the_prompt_names_the_yahoo_writers_before_the_wider_web_and_keeps_to_7_days():
    system, user = build_research_prompt(_player("1"), _board())
    order = [system.index(s) for s in ("https://sports.yahoo.com/author/josh-norris/",
                                       "https://sports.yahoo.com/author/hayden-winks/",
                                       "https://sports.yahoo.com/author/matt-harmon/",
                                       "https://sports.yahoo.com/fantasy/article/",
                                       "The wider web")]
    assert order == sorted(order)
    assert "Use only takes and news from the last 7 days before today's date." in system
    assert user.startswith("Today is 2026-10-20.")


@pytest.mark.live
def test_the_real_search_returns_cited_claims_for_one_player(monkeypatch):
    """One real Claude call with web search for one player. It prints the claims and the usage of the call."""
    from cornerstone import writer
    from cornerstone.models import Fact
    from cornerstone.waiver_research import search_call

    responses = []
    client = writer._get_client()

    class Recorder:
        def parse(self, **kwargs):
            responses.append(client.messages.parse(**kwargs))
            return responses[-1]

    monkeypatch.setattr(writer, "_get_client", lambda: type("Client", (), {"messages": Recorder()})())
    player = _player("12345", "Tre Tucker")
    player.facts = [Fact(id="W.usage.12345", text="Tre Tucker played 88% of snaps and took 9 targets last week.",
                         numbers=["88", "9"], teams=[], players=["Tre Tucker"])]
    board = research_board(_board(best_adds=[player]), search_call)
    claims = board.buckets["best_adds"][0].research
    usage = responses[0].usage
    print("claims:", [c.model_dump() for c in claims])
    print("usage:", usage)
    assert not board.experts_missing
    assert all(c.url.startswith("http") for c in claims)
