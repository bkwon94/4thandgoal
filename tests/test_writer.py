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
from cornerstone.writer import MOTW_HEADLINE_NOTE, build_writer_prompt, template_blurb, write_blurb


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
    assert "league group chat" in system and "fact ID" in system


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
    assert 2 <= len(b.sentences) <= 4 and [s.fact_ids for s in b.sentences].count([]) <= 1


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


def test_writer_rule_1_allows_one_reaction_sentence(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    system, _ = build_writer_prompt(_chapter(sheet, "median"), sheet, None)
    assert "1. Cite one or more fact IDs for every sentence, except one reaction sentence per blurb." in system
    assert "The reaction sentence has no citation and an empty `fact_ids`." in system
    assert "no digit, no team name, no player name, and fewer than 8 words" in system
    assert "Put it after the sentence it reacts to." in system


def test_writer_rule_21_tags_each_rankings_sentence_with_its_team(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    system, _ = build_writer_prompt(_chapter(sheet, "median"), sheet, None)
    assert ("21. In the Power rankings chapter, tag every sentence with its team: "
            "set `roster_id` to the number in the team's `PR.` fact ID.") in system
    assert "Give every team 1 or 2 sentences." in system
    assert "Cite the team's `PR.` fact in its first sentence." in system
    assert "Write the teams in power rank order, from 1st to 12th." in system
    assert "A reaction sentence also gets the tag of its team and counts toward that team's 2." in system
    assert "Other chapters leave `roster_id` empty." in system


def test_verifier_prompt_supports_a_reaction_sentence():
    from importlib import resources

    text = resources.files("cornerstone.prompts").joinpath("verifier.md").read_text(encoding="utf-8")
    assert "- A sentence with no fact IDs and no claim is supported." in text


def test_tone_has_the_banned_patterns(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    system, _ = build_writer_prompt(_chapter(sheet, "median"), sheet, None)
    section = system.split("## Banned patterns", 1)[1].split("\n## ", 1)[0]
    for pattern in ('The ", which is X" tail', '"one of the problems"', '"the entire point"',
                    '"a lot to hang on"', '"a polite way to say"', "explains the joke it just made"):
        assert pattern in section, pattern
    assert "At most one sentence per blurb may end in a ', which' clause. Never use it as the joke." in section


def test_tone_gives_each_banned_pattern_an_example(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    system, _ = build_writer_prompt(_chapter(sheet, "median"), sheet, None)
    section = system.split("## Banned patterns", 1)[1].split("\n## ", 1)[0]
    lines = [line for line in section.splitlines() if line.startswith("- ")]
    for pattern in ('The ", which is X" tail', '"one of the problems"', '"the entire point"',
                    '"a lot to hang on"', '"a polite way to say"', "explains the joke it just made"):
        line = next(line for line in lines if pattern in line)
        # The example is a quoted sentence after the pattern name, not the name alone.
        assert re.search(r'"[^"]+\."', line.split(pattern, 1)[1]), pattern


def test_tone_opens_with_the_group_chat_voice(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    system, _ = build_writer_prompt(_chapter(sheet, "median"), sheet, None)
    tone = system.split("# Tone", 1)[1].strip()
    voice = "The voice is the league group chat: a member who watched every game and types like a person."
    assert tone.startswith(voice)
    assert "Short sentences, varied length, contractions allowed. No chill. Roast freely." in tone
    assert "Deadpan allowed, not required." in tone
    assert "two jokes" not in system
    assert "No filler sentence. Every sentence states a fact or reacts to the one before it." in system


def test_tone_examples_hold_every_picked_sentence(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    system, _ = build_writer_prompt(_chapter(sheet, "median"), sheet, None)
    section = system.split("## Examples", 1)[1].split("\n## ", 1)[0]
    passed = section.split("Passed review:", 1)[1].split("Failed review:", 1)[0]
    # Brian picked these sentences from the week 6 candidates. A prompt edit that drops one fails here.
    for sentence in (
        '"Brutal pickup."',
        '"Not even close."',
        '"Lil Fridge rolled Brock ‘N’ Roll 126.79 to 88.31, and at least the Brock in the name showed up, '
        'with Brock Purdy as Top Scorer."',
        '"Ladd McConkey and Terry McLaurin, also on that roster, are now listed Out."',
        '"Return of T Mac flattened Unsolicited Dak Picks 120.29 to 81.47 in an upset."',
        '"Bo Girds cleared it by 2.79, and Amon-Ra Dawg Your Team missed it by exactly that much."',
        '"Matthew Golden alone dropped 3, worth about 14.2."',
    ):
        assert sentence in passed, sentence
    assert "Their numbers and names never appear in a new blurb." in section


def test_writer_rule_4_lets_a_plain_phrase_stand_for_a_stat(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    system, _ = build_writer_prompt(_chapter(sheet, "median"), sheet, None)
    assert "4. When you name a stat, use its vocabulary term. You need not name the stat." in system
    assert "A plain phrase that the cited fact supports is fine" in system
    assert "Use only the vocabulary terms." not in system
    assert "15. In a sentence that makes a claim, lead with the claim." in system


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


def test_tone_varies_the_opener_and_moves_upset_off_the_front(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    system, _ = build_writer_prompt(_chapter(sheet, "median"), sheet, None)
    section = system.split("## Openers", 1)[1].split("\n## ", 1)[0]
    assert "- Vary the opener." in section
    assert 'Put "upset" mid-sentence or at the end at least half the time' in section


def test_the_motw_recap_gets_the_note_on_the_headline(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    _, motw_recap = build_writer_prompt(_chapter(sheet, "recap_4"), sheet, None)
    assert MOTW_HEADLINE_NOTE in motw_recap


def test_another_recap_and_the_motw_get_no_note_on_the_headline(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    for key in ("recap_1", "motw"):
        _, user = build_writer_prompt(_chapter(sheet, key), sheet, None)
        assert MOTW_HEADLINE_NOTE not in user, key


def test_tone_asks_for_one_joke_per_blurb(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    system, _ = build_writer_prompt(_chapter(sheet, "median"), sheet, None)
    assert "- Every blurb has at least one joke. A reaction sentence counts as the joke." in system


def test_prompts_ask_for_one_sentence_with_no_number(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    system, _ = build_writer_prompt(_chapter(sheet, "median"), sheet, None)
    assert "- At least one sentence per blurb carries no number." in system
    assert "Put at most two numbers in a sentence. At least one sentence per blurb carries no number." in system


def test_tone_asks_for_an_before_a_vowel_sound_number(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    system, _ = build_writer_prompt(_chapter(sheet, "median"), sheet, None)
    assert 'Write "an", not "a", before a number that starts with a vowel sound: "an 8.13 projection"' in system


def test_vocabulary_gives_a_plain_phrase_for_each_stat_term(fixture_raw_dir):
    from cornerstone.verifier import GATED_WORDS

    sheet = _sheet(fixture_raw_dir)
    system, _ = build_writer_prompt(_chapter(sheet, "median"), sheet, None)
    lines = system.split("# Vocabulary", 1)[1].split("## Banned words", 1)[0].splitlines()
    for term in ("margin driver", "swing player", "recent add", "next opponent win rate"):
        line = next(line for line in lines if line.startswith(f"- **{term}**"))
        assert re.search(r'Plain phrase[^:]*: "[^"]+"', line), term
    driver = next(line for line in lines if line.startswith("- **margin driver**"))
    assert 'Plain phrase for "margin driver" or "decider":' in driver
    assert "A plain phrase needs the same cited fact as its term." in system
    # The plain phrases are examples. The gated words keep their marker rule.
    gated = {word for words, _ in GATED_WORDS for word in words}
    assert {"decider", "decided", "upset", "recent add", "lucky"} <= gated


def test_the_game_changer_and_awards_get_the_motw_note_when_the_game_changer_is_in_it(hbundle):
    # With the history, the Game Changer is Germie Bernard of behold the lamb, a Matchup of the Week team.
    sheet = hbundle.sheet
    for key in ("game_changer", "awards"):
        _, user = build_writer_prompt(_chapter(sheet, key), sheet, None)
        assert MOTW_HEADLINE_NOTE in user, key
    for key in ("recap_1", "median", "position_leaders", "rankings"):
        _, user = build_writer_prompt(_chapter(sheet, key), sheet, None)
        assert MOTW_HEADLINE_NOTE not in user, key


def test_no_motw_note_when_the_game_changer_is_outside_it(fixture_raw_dir):
    # With no history, the Game Changer is Tre Tucker of All You Need Is Love, outside the Matchup of the Week.
    sheet = _sheet(fixture_raw_dir)
    assert set(_chapter(sheet, "game_changer").scope_teams) != set(_chapter(sheet, "motw").scope_teams)
    for key in ("game_changer", "awards"):
        _, user = build_writer_prompt(_chapter(sheet, key), sheet, None)
        assert MOTW_HEADLINE_NOTE not in user, key


def test_tone_bans_the_and_thats_closer(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    system, _ = build_writer_prompt(_chapter(sheet, "median"), sheet, None)
    section = system.split("## Banned patterns", 1)[1].split("\n## ", 1)[0]
    assert '- The ", and that\'s X" closer.' in section
    # The closer is banned outright, so no line allows one per page.
    assert "per page" not in section
    # The examples and the opener line no longer show the closer as the good shape.
    passed = system.split("Passed review:", 1)[1].split("Failed review:", 1)[0]
    openers = system.split("## Openers", 1)[1].split("\n## ", 1)[0]
    assert "and that's" not in passed and "and that's" not in openers


def test_rankings_rule_asks_for_its_own_openers_numberless_rows_and_no_form(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    system, _ = build_writer_prompt(_chapter(sheet, "median"), sheet, None)
    rule = system.split("\n22. ", 1)[1]
    assert rule.startswith("The Power rankings chapter uses the no-number line below in place of rule 15.")
    assert "Never start the first sentences of 2 teams with the same 3 words." in rule
    assert "At least 4 teams get a sentence with no number." in rule
    assert '"form" is a component name. Write "the last 3 weeks" in its place.' in rule
    # Rule 15 is the no-number rule that rule 22 replaces for the rankings chapter.
    assert "At least one sentence per blurb carries no number." in system.split("\n15. ", 1)[1].split("\n16. ", 1)[0]
