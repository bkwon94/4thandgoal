"""
Tests for the prose blocks of the midseason report on the real saved CPC facts of week 8: the voice of each roast level,
the facts text that the writer copies, and the template blurb of a failed block. Each one runs the code check of facts.
"""
from functools import partial
from pathlib import Path

import pytest
from cpc import cpc_client
from fakes import FakeWriter
from test_midseason import CPC_PROVIDER, build_week_8, copy_cpc_week_8

from cornerstone.value_models import VALUE_MODELS
from facts.verifier import build_verifier_prompt, code_check, page_words
from facts.writer import build_writer_prompt, claude_call
from league.models import Blurb, Sentence
from midseason.prose import ProseDraft, prose_terms, read_draft_facts
from midseason.published import read_midseason, report_blurbs


@pytest.fixture(scope="module")
def built(tmp_path_factory) -> tuple[ProseDraft, Path, Path]:
    """One build of the real CPC week 8 with a writer that fails each call: the saved facts, the draft, and the voice
    folder of the client. Each prose block of the draft holds its template blurb."""
    client = cpc_client(at=tmp_path_factory.mktemp("cpc"), models=VALUE_MODELS)
    copy_cpc_week_8(client)
    out = build_week_8(partial(claude_call, writer=FakeWriter()), client=client, provider=CPC_PROVIDER)
    return read_draft_facts(out.parent), out, client.voice_dir


def _check(built, key: str, sentences: list[Sentence]) -> list[str]:
    draft, _, voice = built
    chapter = next(c for c in draft.sheet.chapters if c.key == key)
    blurb = Blurb(chapter=key, sentences=sentences, attempt=1, fallback=False)
    return code_check(blurb, chapter, draft.sheet, prompts_dir=voice)


CITED = Sentence(text="NFC Least is 3-13, 12th in the standings.", fact_ids=["ST.4.record"])
# The prose blocks of the report in page order. Each chapter has one block, and no block is a roast block.
BLOCKS = ["opener", "state", "arcs", "luck", "injuries", "top10", "draft", "waivers", "trades", "lineup", "records",
          "look-ahead"]


QUICK_HITS = ("lineup", "injuries")


def test_each_chapter_has_one_prose_block_of_40_words_or_fewer(built):
    draft, _, _ = built
    assert [chapter.key for chapter in draft.sheet.chapters] == BLOCKS
    assert all(chapter.max_words == 40 for chapter in draft.sheet.chapters if chapter.key not in QUICK_HITS)


def test_each_of_the_two_parts_of_quick_hits_has_20_words_or_fewer(built):
    # P-5. Quick hits holds 40 words in all, so each of its two blocks gets 20.
    draft, _, _ = built
    caps = {chapter.key: chapter.max_words for chapter in draft.sheet.chapters if chapter.key in QUICK_HITS}
    assert caps == {"lineup": 20, "injuries": 20}


def test_a_block_over_40_words_fails_the_check(built):
    long = Sentence(text="NFC Least is 3-13, 12th in the standings, and the season is long, and the bench is deep, "
                         "and the waiver wire is bare, and the trade market is cold, and the fans are quiet.",
                    fact_ids=["ST.4.record"])
    sentences = [CITED, long, Sentence(text="That is not a slump.", fact_ids=[])]
    assert any("words; the limit is 40" in failure for failure in _check(built, "state", sentences))


def test_a_block_allows_two_reaction_sentences_after_a_cited_one(built):
    # K-2. Two reactions give the voice its punch. The cited sentence keeps a fact behind it.
    sentences = [CITED, Sentence(text="That is not a slump.", fact_ids=[]),
                 Sentence(text="That is a demolition.", fact_ids=[])]
    assert _check(built, "state", sentences) == []


def test_a_block_of_reaction_sentences_only_fails(built):
    sentences = [Sentence(text="Oh no.", fact_ids=[]), Sentence(text="Truly awful.", fact_ids=[])]
    assert any("cites no fact" in failure for failure in _check(built, "state", sentences))


def test_a_blurb_may_cite_a_fact_of_another_chapter(built):
    # AT-63. The luck block calls back to a lineup fact, and the check counts it as a fact of the block.
    sentences = [Sentence(text="All You Need Is Love has a Schedule luck of +2.73.", fact_ids=["SL.2.luck"]),
                 Sentence(text="The Blue Tent lost to behold the lamb by 9.04 in week 2.", fact_ids=["LC.1.2"]),
                 Sentence(text="Some gift.", fact_ids=[])]
    assert _check(built, "luck", sentences) == []


def test_the_writer_and_the_verifier_of_a_block_see_the_facts_of_the_other_chapters(built):
    draft, _, voice = built
    chapter = next(c for c in draft.sheet.chapters if c.key == "luck")
    blurb = Blurb(chapter="luck", sentences=[CITED], attempt=1, fallback=False)
    _, writer = build_writer_prompt(chapter, draft.sheet, None, prompts_dir=voice, terms=prose_terms("savage"))
    _, verifier = build_verifier_prompt(blurb, chapter, draft.sheet, prompts_dir=voice)
    assert "Write 40 words or fewer." in writer
    assert "up to 2 reaction sentences" in writer
    for prompt in (writer, verifier):
        assert "- LC.1.2: " in prompt and "- SL.2.luck: " in prompt
        # The facts of the block come first, then the facts of the rest of the report.
        assert prompt.index("- SL.2.luck: ") < prompt.index("- LC.1.2: ")


@pytest.mark.parametrize("roast", ["off", "warm", "hot", "savage"])
def test_each_voice_holds_the_limits_the_unit_rule_the_count_rule_and_its_level(roast):
    terms = "\n".join(prose_terms(roast))
    assert f"Voice: {roast}." in terms
    for rule in ("Never write about life outside fantasy", "No profanity", "No starred-out swear word",
                 "Name the unit of a number", "points over the line", "head-to-head record",
                 "the median games"):
        assert rule in terms


def test_the_voice_holds_the_samples_of_the_p4_voice_board():
    terms = "\n".join(prose_terms("savage"))
    for line in ("One auction, no survivors.", "Remove the gifts and first place is a rumor.",
                 "That is losing with a head start."):
        assert line in terms
    for level in ("off", "warm", "hot", "savage"):
        assert f"### {level}" in terms


def test_the_template_blurb_of_each_failed_block_passes_the_code_check_of_the_publish(built):
    # K-4. The writer fails each call, so each block holds its template. The publish rechecks each one in page order.
    draft, out, voice = built
    chapters = {chapter.key: chapter for chapter in draft.sheet.chapters}
    blurbs = report_blurbs(read_midseason(out.parent))
    assert len(blurbs) == 12 and all(blurb.fallback for blurb in blurbs)
    # A callout fact is a note to the writer, not prose, so no template reads it.
    assert not any(fid.startswith("CO.") for blurb in blurbs for sentence in blurb.sentences for fid in sentence.fact_ids)
    failures: dict[str, list[str]] = {}
    used: set[str] = set()
    for blurb in blurbs:
        chapter = chapters[blurb.chapter]
        found = code_check(blurb, chapter, draft.sheet, used, prompts_dir=voice)
        if found:
            failures[blurb.chapter] = found
        used |= page_words(blurb, chapter)
    assert failures == {}, "\n".join(f"{k}: {v}" for k, v in failures.items())


def test_each_fact_passes_the_code_check_as_a_sentence_that_cites_it(built):
    # K-3. The writer copies the text of a fact, so a fact with 3 numbers or a banned word costs an attempt.
    draft, _, voice = built
    failures: dict[str, list[str]] = {}
    for chapter in draft.sheet.chapters:
        # A trade fact names each player of the trade, so it may run past the word limit of a block. The writer
        # cuts it to the players of the story, so this check opens the limit.
        open_range = chapter.model_copy(update={"min_sentences": 1, "max_words": None})
        for fid in chapter.fact_ids:
            sentence = Sentence(text=draft.sheet.facts[fid].text, fact_ids=[fid])
            blurb = Blurb(chapter=chapter.key, sentences=[sentence], attempt=1, fallback=False)
            found = code_check(blurb, open_range, draft.sheet, prompts_dir=voice)
            if found:
                failures[fid] = found
    assert failures == {}, "\n".join(f"{k}: {draft.sheet.facts[k].text} {v}" for k, v in failures.items())


@pytest.mark.parametrize("roast", ["off", "warm", "hot", "savage"])
def test_each_prose_block_hears_the_midseason_writing_notes(roast):
    terms = "\n".join(prose_terms(roast))
    assert "a 0-4" in terms and "because" in terms
