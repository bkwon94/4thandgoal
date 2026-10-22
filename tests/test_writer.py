"""
Tests for the writer: the prompt, the blurb, and the template fallback.
One live test calls the real Claude API and runs only with -m live.
"""
import re

import pytest

from cornerstone.models import Blurb, Sentence, WriterOut
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


def test_writer_rule_6_gates_decided_on_a_driver_only(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    system, _ = build_writer_prompt(_chapter(sheet, "median"), sheet, None)
    assert '6. Never say "decided" or "decider" unless a cited fact ID contains `.driver`.' in system
    assert "T{n}.{rid}.swing" not in system


def test_a_saved_blurb_with_a_grades_map_still_parses():
    text = '{"chapter": "trade_5", "sentences": [], "attempt": 1, "fallback": false, "grades": {"T5.12": "A"}}'
    blurb = Blurb.model_validate_json(text)
    assert blurb.chapter == "trade_5" and "grades" not in blurb.model_dump()


def test_writer_has_no_trade_recap_rule(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    system, _ = build_writer_prompt(_chapter(sheet, "median"), sheet, None)
    assert "In a trade recap" not in system and "`impact`" not in system and "`.late`" not in system
    assert "grade each side" not in system and "Grade keys" not in system and "`.value`" not in system
    assert "With more than two trades" not in system and "In the Trades chapter" not in system
    assert "18. Never put a number on a draft pick." in system
    assert "19. A drop fact names the receiver only." in system
    assert "Put at most two numbers in a sentence." in system and "Write every number as digits" in system


def _fake_client(monkeypatch, stop_reason="end_turn", parsed_output="parsed", has_usage=True):
    sent = {}

    class Messages:
        def parse(self, **kwargs):
            sent.update(kwargs)
            usage = type("Usage", (), {
                "cache_creation_input_tokens": 0,
                "cache_read_input_tokens": 0,
                "input_tokens": 1,
            })
            return type("Response", (), {
                "stop_reason": stop_reason,
                "parsed_output": parsed_output,
                "usage": usage if has_usage else None,
            })()

    monkeypatch.setattr("cornerstone.writer._get_client", lambda: type("Client", (), {"messages": Messages()})())
    return sent


def test_claude_call_sends_the_system_and_the_user_text_through_parse_call(monkeypatch):
    from cornerstone.writer import claude_call

    sent = _fake_client(monkeypatch)
    assert claude_call("system text", "user text", WriterOut) == "parsed"
    assert sent["system"] == [
        {"type": "text", "text": "system text", "cache_control": {"type": "ephemeral"}}
    ]
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


def test_the_analyzer_call_alone_sets_the_one_hour_lifetime(monkeypatch):
    from cornerstone.analysis import AnalysisOut
    from cornerstone.writer import analyzer_call, claude_call

    sent = _fake_client(monkeypatch)
    analyzer_call("analyzer system", "user text", AnalysisOut)
    assert sent["system"] == [{
        "type": "text",
        "text": "analyzer system",
        "cache_control": {"type": "ephemeral", "ttl": "1h"},
    }]
    # The writer and the verifier share claude_call. They keep five minutes, no ttl.
    claude_call("writer system", "user text", WriterOut)
    assert sent["system"][0]["cache_control"] == {"type": "ephemeral"}


def test_the_analyzer_call_alone_runs_at_medium_effort(monkeypatch):
    from cornerstone.analysis import AnalysisOut
    from cornerstone.writer import analyzer_call, claude_call

    sent = _fake_client(monkeypatch)
    analyzer_call("analyzer system", "user text", AnalysisOut)
    assert sent["output_config"] == {"effort": "medium"}
    claude_call("writer system", "user text", WriterOut)
    assert sent["output_config"] == {"effort": "high"}


# The API route calls `analyze` with no `call` argument, so this default is the API's lifetime.
def test_analyze_uses_the_analyzer_call_by_default():
    import inspect

    from cornerstone.analysis import analyze
    from cornerstone.writer import analyzer_call

    assert inspect.signature(analyze).parameters["call"].default is analyzer_call


def test_parse_call_logs_the_kind_and_the_three_usage_counts(monkeypatch, caplog):
    import logging

    from cornerstone.writer import parse_call

    _fake_client(monkeypatch)
    with caplog.at_level(logging.INFO, logger="cornerstone.writer"):
        parse_call("user text", WriterOut, "system text")
    assert (
        "WriterOut call: cache_creation_input_tokens=0 cache_read_input_tokens=0"
        " input_tokens=1"
    ) in caplog.messages


def test_parse_call_skips_the_log_line_when_the_response_has_no_usage(monkeypatch, caplog):
    import logging

    from cornerstone.writer import parse_call

    _fake_client(monkeypatch, has_usage=False)
    with caplog.at_level(logging.INFO, logger="cornerstone.writer"):
        assert parse_call("user text", WriterOut, "system text") == "parsed"
    assert not any("call: cache_creation_input_tokens" in m for m in caplog.messages)
