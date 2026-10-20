"""
Tests for the writer: the prompt, the blurb, and the template fallback.
One live test calls the real Claude API and runs only with -m live.
"""
import re

import pytest

from cornerstone.models import Sentence, WriterOut
from cornerstone.parse import parse_week
from cornerstone.sheet import build_bundle
from cornerstone.sleeper import load_raw
from cornerstone.writer import build_writer_prompt, template_blurb, write_blurb


def _sheet(d):
    return build_bundle(parse_week(load_raw(d)), news=lambda pid: []).sheet


def _chapter(sheet, key):
    return next(c for c in sheet.chapters if c.key == key)


def test_prompt_contains_scope_facts_only(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _chapter(sheet, "recap_4")
    system, user = build_writer_prompt(ch, sheet, None)
    assert "Read recap" not in user
    assert "M4." in user and "M1." not in user
    assert "fact ID" in system


def test_user_prompt_lists_scope_facts_in_order(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _chapter(sheet, "recap_4")
    _, user = build_writer_prompt(ch, sheet, None)
    listed = re.findall(r"^- ([A-Z][\w.]*): ", user, re.MULTILINE)
    assert listed == ch.fact_ids
    assert f"Chapter: {ch.title}" in user
    assert f"Write {ch.min_sentences} to {ch.max_sentences} sentences." in user
    assert "Feedback" not in user


def test_system_prompt_has_all_three_files(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    system, _ = build_writer_prompt(_chapter(sheet, "median"), sheet, None)
    assert "Top Scorer" in system and "upset" in system and "recent add" in system
    assert "Dry, specific" in system and "fact ID" in system


def test_feedback_block_appears_only_with_feedback(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _chapter(sheet, "median")
    _, user = build_writer_prompt(ch, sheet, "Sentence 2 is unsupported.")
    assert user.endswith("Feedback from the last attempt:\nSentence 2 is unsupported.")
    assert len(re.findall(r"^- ([A-Z][\w.]*): ", user, re.MULTILINE)) == len(ch.fact_ids)


def test_write_blurb_uses_call(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _chapter(sheet, "median")

    def fake(system, user, model):
        assert model is WriterOut
        return model(sentences=[Sentence(text="Six teams cleared 106.83.", fact_ids=["MED.value"])])

    b = write_blurb(ch, sheet, fake)
    assert b.chapter == "median" and b.sentences[0].fact_ids == ["MED.value"] and not b.fallback
    assert b.attempt == 1


def test_retry_sets_attempt_two_and_passes_feedback(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _chapter(sheet, "median")
    seen = {}

    def fake(system, user, model):
        seen["user"] = user
        return model(sentences=[Sentence(text="x", fact_ids=["MED.value"])])

    b = write_blurb(ch, sheet, fake, feedback="Fix sentence 1.")
    assert b.attempt == 2 and "Fix sentence 1." in seen["user"]


def test_template_blurb(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _chapter(sheet, "recap_4")
    b = template_blurb(ch, sheet)
    assert b.fallback and len(b.sentences) == 1 and b.attempt == 0
    assert b.sentences[0].fact_ids == ["M4.result"]
    assert b.sentences[0].text == sheet.facts["M4.result"].text


def test_template_blurb_without_result_uses_first_fact(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _chapter(sheet, "median")
    b = template_blurb(ch, sheet)
    assert b.sentences[0].fact_ids == [ch.fact_ids[0]]


@pytest.mark.live
def test_live_write_median(fixture_raw_dir):
    from cornerstone.writer import claude_call

    sheet = _sheet(fixture_raw_dir)
    ch = _chapter(sheet, "median")
    b = write_blurb(ch, sheet, claude_call)
    for s in b.sentences:
        print(f"{s.text}  {s.fact_ids}")
    assert 2 <= len(b.sentences) <= 4 and all(s.fact_ids for s in b.sentences)
