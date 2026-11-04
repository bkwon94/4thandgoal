"""
Tests for the median text of the week package: the writer and the verifier get it only when the median game is on.
The CPC client reads the real League settings of the week 6 fixtures, and the voice comes from the real prompt files.
"""
from cpc import cpc_client

from facts.verifier import build_verifier_prompt
from facts.writer import build_writer_prompt
from league.models import Blurb, Chapter, FactSheet, Sentence
from week.median import median_terms

CHAPTER = Chapter(key="awards", title="Awards", fact_ids=[], scope_teams=[], scope_players=[], min_sentences=1,
                  max_sentences=2)
SHEET = FactSheet(facts={}, chapters=[CHAPTER])
MEDIAN_TERM = "**median game**"


def test_a_league_with_the_median_game_gets_the_median_text_and_a_league_with_none_gets_no_text():
    on, off = cpc_client(), cpc_client(median_game=False)
    assert on.settings.median_game
    assert any(MEDIAN_TERM in text for text in median_terms(on))
    assert median_terms(off) == ()


def test_the_writer_prompt_names_the_median_game_only_with_the_median_text():
    client = cpc_client()
    with_text, _ = build_writer_prompt(CHAPTER, SHEET, None, prompts_dir=client.voice_dir, terms=median_terms(client))
    without, _ = build_writer_prompt(CHAPTER, SHEET, None, prompts_dir=client.voice_dir, terms=())
    assert MEDIAN_TERM in with_text
    assert MEDIAN_TERM not in without


def test_the_verifier_prompt_names_the_median_game_only_with_the_median_text():
    client = cpc_client()
    blurb = Blurb(chapter="awards", sentences=[Sentence(text="A line.", fact_ids=[])], attempt=1, fallback=False)
    with_text, _ = build_verifier_prompt(blurb, CHAPTER, SHEET, prompts_dir=client.voice_dir,
                                         terms=median_terms(client))
    without, _ = build_verifier_prompt(blurb, CHAPTER, SHEET, prompts_dir=client.voice_dir)
    assert MEDIAN_TERM in with_text
    assert MEDIAN_TERM not in without
