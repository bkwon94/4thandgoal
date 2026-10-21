"""
Tests for the writer: the prompt, the blurb, and the template fallback.
One live test calls the real Claude API and runs only with -m live.
"""
import re

import pytest

from cornerstone.models import Grade, Sentence, TradesWriterOut, WriterOut
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


def test_prompt_lets_the_manager_take_the_injury_joke(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    system, _ = build_writer_prompt(_chapter(sheet, "recap_5"), sheet, None)
    assert "Make no jokes about injuries." not in system
    assert "Make no joke about an injury itself or about a player's health." in system
    assert "Roast the manager, not the player's body." in system
    assert "is now listed" in system
    assert "started while" not in system
    assert "**injury status**" in system
    assert "I.{pid}.pregame" in system and "Friday" in system and "**pre-game status**" in system


def test_writer_rule_6_allows_the_trade_swing(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    system, _ = build_writer_prompt(_chapter(sheet, "median"), sheet, None)
    assert "or the sentence cites a trade swing fact `T{n}.{rid}.swing`" in system


def _trades(tbundle):
    return next(c for c in tbundle.sheet.chapters if c.key == "trade_5")


def test_trades_prompt_lists_grade_keys(tbundle):
    _, user = build_writer_prompt(_trades(tbundle), tbundle.sheet, None)
    assert "Grade keys: T5.11, T5.12" in user


def test_write_blurb_maps_grades(tbundle):
    def call(system, user, model):
        assert model is TradesWriterOut
        return model(sentences=[Sentence(text="x.", fact_ids=["T5.sides"])],
                     grades=[Grade(key="T5.12", letter="A")])
    assert write_blurb(_trades(tbundle), tbundle.sheet, call).grades == {"T5.12": "A"}


def test_trades_template_lists_the_sides(tbundle):
    b = template_blurb(_trades(tbundle), tbundle.sheet)
    assert [s.fact_ids for s in b.sentences] == [["T5.sides"]]
    assert b.grades == {}


def test_writer_rules_18_and_19(tbundle):
    system, _ = build_writer_prompt(_trades(tbundle), tbundle.sheet, None)
    assert "18. In a trade chapter, grade each side on value at the moment of the trade" in system
    assert "Never let `impact` or `swing` facts move a grade." in system
    assert ("19. In a trade chapter, write the grade reasons first. Then at most one sentence on how "
            "the trade played out this week, from the `impact` or `swing` facts.") in system
    assert "With more than two trades" not in system and "In the Trades chapter" not in system
    assert "20. Never put a number on a draft pick." in system
    assert "Put at most two numbers in a sentence." in system and "Write every number as digits" in system


def test_trade_template_finds_the_sides_fact(tbundle):
    ch = next(c for c in tbundle.sheet.chapters if c.key == "trade_6")
    shuffled = ch.model_copy(update={"fact_ids": list(reversed(ch.fact_ids))})
    b = template_blurb(shuffled, tbundle.sheet)
    assert [s.fact_ids for s in b.sentences] == [["T6.sides"]]
    assert b.sentences[0].text == tbundle.sheet.facts["T6.sides"].text
    assert b.fallback and b.grades == {}


def test_writer_rule_18_orders_the_positions_and_hides_the_values(tbundle):
    system, _ = build_writer_prompt(_trades(tbundle), tbundle.sheet, None)
    assert ("At equal rank and points, an RB outweighs a WR, a WR outweighs a TE, "
            "and a TE outweighs a QB. A DEF carries little trade value.") in system
    assert ("Weigh the two sides with the `.value` facts. Never write a trade value, "
            "a trade value sum, the chart, or a tier in a sentence.") in system
    assert "kicker" not in system.lower()


def _fake_client(monkeypatch, stop_reason="end_turn", parsed_output="parsed"):
    sent = {}

    class Messages:
        def parse(self, **kwargs):
            sent.update(kwargs)
            return type("Response", (), {"stop_reason": stop_reason, "parsed_output": parsed_output})()

    monkeypatch.setattr("cornerstone.writer._get_client", lambda: type("Client", (), {"messages": Messages()})())
    return sent


def test_claude_call_sends_the_system_and_the_user_text_through_parse_call(monkeypatch):
    from cornerstone.writer import claude_call

    sent = _fake_client(monkeypatch)
    assert claude_call("system text", "user text", WriterOut) == "parsed"
    assert sent["system"] == "system text"
    assert sent["messages"] == [{"role": "user", "content": "user text"}]
    assert sent["output_format"] is WriterOut
    assert sent["output_config"] == {"effort": "high"}


def test_parse_call_raises_on_a_refusal_and_on_no_parsed_output(monkeypatch):
    from cornerstone.writer import RefusalError, WriterError, parse_call

    _fake_client(monkeypatch, stop_reason="refusal", parsed_output=None)
    with pytest.raises(RefusalError):
        parse_call("user text", WriterOut)
    _fake_client(monkeypatch, parsed_output=None)
    with pytest.raises(WriterError):
        parse_call("user text", WriterOut)
