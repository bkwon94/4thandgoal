"""
Tests for the prose blocks of the midseason report on the real saved CPC facts of week 8: the roast heat, the facts
text that the writer copies, and the template blurb of a failed block. Each one runs the code check of facts.
"""
from functools import partial
from pathlib import Path

import pytest
from cpc import cpc_client
from fakes import FakeWriter
from test_midseason import CPC_PROVIDER, copy_cpc_week_8

from cornerstone.pipeline import run_midseason
from cornerstone.value_models import VALUE_MODELS
from facts.verifier import code_check, page_words
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
    out = run_midseason(2026, 8, partial(claude_call, writer=FakeWriter()), client=client, provider=CPC_PROVIDER)
    return read_draft_facts(out.parent), out, client.voice_dir


def _check(built, key: str, sentences: list[Sentence]) -> list[str]:
    draft, _, voice = built
    chapter = next(c for c in draft.sheet.chapters if c.key == key)
    blurb = Blurb(chapter=key, sentences=sentences, attempt=1, fallback=False)
    return code_check(blurb, chapter, draft.sheet, prompts_dir=voice)


CITED = Sentence(text="NFC Least is 3-13, 12th in the standings.", fact_ids=["ST.4.record"])


def test_a_roast_block_allows_two_reaction_sentences_after_a_cited_one(built):
    # K-2. Two reactions give the roast its heat. The cited sentence keeps a fact behind it.
    sentences = [CITED, Sentence(text="That is not a slump.", fact_ids=[]),
                 Sentence(text="That is a demolition.", fact_ids=[])]
    assert _check(built, "state.roast", sentences) == []


def test_a_roast_block_of_reaction_sentences_only_fails(built):
    sentences = [Sentence(text="Oh no.", fact_ids=[]), Sentence(text="Truly awful.", fact_ids=[])]
    assert any("cites no fact" in failure for failure in _check(built, "state.roast", sentences))


def test_a_blurb_block_still_allows_one_reaction_sentence(built):
    sentences = [CITED, Sentence(text="Ouch.", fact_ids=[]), Sentence(text="Wow.", fact_ids=[])]
    assert any("a second reaction sentence" in failure for failure in _check(built, "state", sentences))


def test_the_writer_of_a_roast_block_hears_that_it_may_write_two_reactions(built):
    draft, _, voice = built
    chapter = next(c for c in draft.sheet.chapters if c.key == "state.roast")
    _, user = build_writer_prompt(chapter, draft.sheet, None, prompts_dir=voice, terms=prose_terms(chapter.key, "hot"))
    assert "2 reaction sentences" in user


def test_the_hot_roast_holds_two_example_roasts_and_the_warm_roast_none():
    hot = "\n".join(prose_terms("state.roast", "hot"))
    warm = "\n".join(prose_terms("state.roast", "warm"))
    assert hot.count("Example roast") == 2 and "Example roast" not in warm
    assert "Never roast life outside fantasy" in hot and "Never roast life outside fantasy" in warm


def test_the_template_blurb_of_each_failed_block_passes_the_code_check_of_the_publish(built):
    # K-4. The writer fails each call, so each block holds its template. The publish rechecks each one in page order.
    draft, out, voice = built
    chapters = {chapter.key: chapter for chapter in draft.sheet.chapters}
    blurbs = report_blurbs(read_midseason(out.parent))
    assert len(blurbs) == 26 and all(blurb.fallback for blurb in blurbs)
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
        open_range = chapter.model_copy(update={"min_sentences": 1})
        for fid in chapter.fact_ids:
            sentence = Sentence(text=draft.sheet.facts[fid].text, fact_ids=[fid])
            blurb = Blurb(chapter=chapter.key, sentences=[sentence], attempt=1, fallback=False)
            found = code_check(blurb, open_range, draft.sheet, prompts_dir=voice)
            if found:
                failures[fid] = found
    assert failures == {}, "\n".join(f"{k}: {draft.sheet.facts[k].text} {v}" for k, v in failures.items())


@pytest.mark.parametrize("roast", ["hot", "warm", "off"])
def test_each_prose_block_hears_the_midseason_writing_notes(roast):
    for key in ("arcs", "arcs.roast"):
        terms = "\n".join(prose_terms(key, roast))
        assert "a 0-4" in terms and "because" in terms
