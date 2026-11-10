"""
Tests for the writer: the prompt, the blurb, and the template fallback.
One live test calls the real Claude API and runs only with -m live.
"""
import re

import pytest
from conftest import SAVED
from cpc import cpc_client

from cornerstone.sheet import build_bundle
from facts.writer import (
    DEFAULT_PROMPTS,
    MOTW_HEADLINE_NOTE,
    build_writer_prompt,
    load_prompt,
    template_blurb,
    write_blurb,
)
from league.models import Blurb, Sentence, WriterOut
from league.parse import parse_week
from league.provider.sleeper import load_raw

CLIENT = cpc_client()
PROMPTS = CLIENT.voice_dir


def _sheet(d):
    return build_bundle(parse_week(load_raw(d)), news=lambda pid: [], client=CLIENT).sheet


def _chapter(sheet, key):
    return next(c for c in sheet.chapters if c.key == key)


def test_the_writer_reads_the_voice_of_the_client_and_the_default_rules(tmp_path, fixture_raw_dir):
    # A client prompts/ folder replaces only the voice. The rule prompt writer.md always comes from the default.
    for name in ("vocabulary.md", "tone.md", "writer.md"):
        (tmp_path / name).write_text(f"League {name} from the temp folder.\n", encoding="utf-8")
    sheet = _sheet(fixture_raw_dir)
    system, _ = build_writer_prompt(_chapter(sheet, "median"), sheet, None, prompts_dir=tmp_path)
    for name in ("vocabulary.md", "tone.md"):
        assert f"League {name} from the temp folder." in system
    assert "League writer.md from the temp folder." not in system
    assert "fact ID" in system


def test_a_client_with_no_prompts_folder_gets_the_default_voice(tmp_path, fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    system, _ = build_writer_prompt(_chapter(sheet, "median"), sheet, None, prompts_dir=tmp_path / "prompts")
    assert load_prompt(DEFAULT_PROMPTS, "tone.md") in system
    assert load_prompt(DEFAULT_PROMPTS, "vocabulary.md") in system


def test_the_cpc_voice_comes_from_the_cpc_client_folder():
    assert CLIENT.voice_dir == CLIENT.folder / "prompts"
    assert (CLIENT.voice_dir / "tone.md").is_file() and (CLIENT.voice_dir / "vocabulary.md").is_file()


def test_prompt_contains_scope_facts_only(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _chapter(sheet, "recap_4")
    system, user = build_writer_prompt(ch, sheet, None, prompts_dir=PROMPTS)
    assert "Read recap" not in user
    assert "M4." in user and "M1." not in user
    assert "fact ID" in system


def test_user_prompt_lists_scope_facts_in_order(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _chapter(sheet, "recap_4")
    _, user = build_writer_prompt(ch, sheet, None, prompts_dir=PROMPTS)
    listed = re.findall(r"^- ([A-Z][\w.]*): ", user, re.MULTILINE)
    assert listed == ch.fact_ids
    assert f"Chapter: {ch.title}" in user
    assert f"Write {ch.min_sentences} to {ch.max_sentences} sentences." in user
    assert "Feedback" not in user


def test_system_prompt_has_all_three_files(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    system, _ = build_writer_prompt(_chapter(sheet, "median"), sheet, None, prompts_dir=PROMPTS)
    assert "Top Scorer" in system and "upset" in system and "recent add" in system
    assert "league group chat" in system and "fact ID" in system


def test_feedback_block_appears_only_with_feedback(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _chapter(sheet, "median")
    _, user = build_writer_prompt(ch, sheet, "Sentence 2 is unsupported.", prompts_dir=PROMPTS)
    assert user.endswith("Feedback from the last attempt:\nSentence 2 is unsupported.")
    assert len(re.findall(r"^- ([A-Z][\w.]*): ", user, re.MULTILINE)) == len(ch.fact_ids)


def test_write_blurb_uses_call(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _chapter(sheet, "median")

    def fake(system, user, model):
        assert model is WriterOut
        return model(sentences=[Sentence(text="Six teams cleared 106.83.", fact_ids=["MED.value"])])

    b = write_blurb(ch, sheet, fake, prompts_dir=PROMPTS)
    assert b.chapter == "median" and b.sentences[0].fact_ids == ["MED.value"] and not b.fallback
    assert b.attempt == 1


def test_retry_sets_attempt_two_and_passes_feedback(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _chapter(sheet, "median")
    seen = {}

    def fake(system, user, model):
        seen["user"] = user
        return model(sentences=[Sentence(text="x", fact_ids=["MED.value"])])

    b = write_blurb(ch, sheet, fake, prompts_dir=PROMPTS, feedback="Fix sentence 1.", attempt=2)
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
    from facts.writer import claude_call

    sheet = _sheet(fixture_raw_dir)
    ch = _chapter(sheet, "median")
    b = write_blurb(ch, sheet, claude_call, prompts_dir=PROMPTS)
    for s in b.sentences:
        print(f"{s.text}  {s.fact_ids}")
    assert 2 <= len(b.sentences) <= 4 and [s.fact_ids for s in b.sentences].count([]) <= 1


def test_prompt_lets_the_manager_take_the_injury_joke(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    system, _ = build_writer_prompt(_chapter(sheet, "recap_5"), sheet, None, prompts_dir=PROMPTS)
    assert "Make no jokes about injuries." not in system
    assert "Make no joke about an injury itself or about a player's health." in system
    assert "Roast the manager, not the player's body." in system
    assert "is now listed" in system
    assert "started while" not in system
    assert "**injury status**" in system
    assert "I.{pid}.pregame" in system and "Friday" in system and "**pre-game status**" in system


def test_writer_rule_6_gates_decided_on_a_driver_only(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    system, _ = build_writer_prompt(_chapter(sheet, "median"), sheet, None, prompts_dir=PROMPTS)
    assert '6. Never say "decided" or "decider" unless a cited fact ID contains `.driver`.' in system
    assert "T{n}.{rid}.swing" not in system


def test_writer_rule_1_allows_one_reaction_sentence(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    system, _ = build_writer_prompt(_chapter(sheet, "median"), sheet, None, prompts_dir=PROMPTS)
    assert "1. Cite one or more fact IDs for every sentence, except one reaction sentence per blurb." in system
    assert "The reaction sentence has no citation and an empty `fact_ids`." in system
    assert "no digit, no team name, no player name, and fewer than 8 words" in system
    assert "Put it after the sentence it reacts to." in system


def test_writer_rule_21_tags_each_rankings_sentence_with_its_team(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    system, _ = build_writer_prompt(_chapter(sheet, "median"), sheet, None, prompts_dir=PROMPTS)
    assert ("21. In the Power rankings chapter, tag every sentence with its team: "
            "set `roster_id` to the number in the team's `PR.` fact ID.") in system
    assert "Give every team 1 to 3 sentences." in system
    assert "Cite the team's `PR.` fact in its first sentence." in system
    assert "Write the teams in power rank order, from 1st to 12th." in system
    assert "A reaction sentence also gets the tag of its team and counts toward that team's 3." in system
    assert "Other chapters leave `roster_id` empty." in system


def test_verifier_prompt_supports_a_reaction_sentence():
    from importlib import resources

    text = resources.files("facts").joinpath("prompts").joinpath("verifier.md").read_text(encoding="utf-8")
    assert "- A sentence with no fact IDs and no claim is supported." in text


def test_tone_has_the_banned_patterns(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    system, _ = build_writer_prompt(_chapter(sheet, "median"), sheet, None, prompts_dir=PROMPTS)
    section = system.split("## Banned patterns", 1)[1].split("\n## ", 1)[0]
    for pattern in ('The ", which is X" tail', '"one of the problems"', '"the entire point"',
                    '"a lot to hang on"', '"a polite way to say"', "explains the joke it just made"):
        assert pattern in section, pattern
    assert "At most one sentence per blurb may end in a ', which' clause. Never use it as the joke." in section


def test_tone_gives_each_banned_pattern_an_example(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    system, _ = build_writer_prompt(_chapter(sheet, "median"), sheet, None, prompts_dir=PROMPTS)
    section = system.split("## Banned patterns", 1)[1].split("\n## ", 1)[0]
    lines = [line for line in section.splitlines() if line.startswith("- ")]
    for pattern in ('The ", which is X" tail', '"one of the problems"', '"the entire point"',
                    '"a lot to hang on"', '"a polite way to say"', "explains the joke it just made"):
        line = next(line for line in lines if pattern in line)
        # The example is a quoted sentence after the pattern name, not the name alone.
        assert re.search(r'"[^"]+\."', line.split(pattern, 1)[1]), pattern


def test_tone_opens_with_the_group_chat_voice(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    system, _ = build_writer_prompt(_chapter(sheet, "median"), sheet, None, prompts_dir=PROMPTS)
    tone = system.split("# Tone", 1)[1].strip()
    voice = "The voice is the league group chat: a member who watched every game and types like a person."
    assert tone.startswith(voice)
    assert "Short sentences, varied length, contractions allowed. No chill. Roast freely." in tone
    assert "Deadpan allowed, not required." in tone
    assert "two jokes" not in system
    assert "No filler sentence. Every sentence states a fact or reacts to the one before it." in system


def test_tone_examples_hold_every_picked_sentence(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    system, _ = build_writer_prompt(_chapter(sheet, "median"), sheet, None, prompts_dir=PROMPTS)
    section = system.split("## Examples", 1)[1].split("\n## ", 1)[0]
    passed = section.split("Passed review:", 1)[1].split("Failed review:", 1)[0]
    # Brian picked these sentences from the week 6 candidates. A prompt edit that drops one fails here.
    for sentence in (
        '"Brutal pickup."',
        '"Not even close."',
        ('"Lil Fridge rolled Brock ‘N’ Roll 126.79 to 88.31, and at least the Brock in the name showed up, '
         'with Brock Purdy as Top Scorer."'),
        '"Ladd McConkey and Terry McLaurin, also on that roster, are now listed Out."',
        '"Return of T Mac flattened Unsolicited Dak Picks 120.29 to 81.47 in an upset."',
        '"Bo Girds cleared it by 2.79, and Amon-Ra Dawg Your Team missed it by exactly that much."',
        '"Matthew Golden alone dropped 3, worth about 14.2."',
    ):
        assert sentence in passed, sentence
    assert "Their numbers and names never appear in a new blurb." in section


def test_writer_rule_4_lets_a_plain_phrase_stand_for_a_stat(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    system, _ = build_writer_prompt(_chapter(sheet, "median"), sheet, None, prompts_dir=PROMPTS)
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
    system, _ = build_writer_prompt(_chapter(sheet, "median"), sheet, None, prompts_dir=PROMPTS)
    assert "In a trade recap" not in system and "`impact`" not in system and "`.late`" not in system
    assert "grade each side" not in system and "Grade keys" not in system and "`.value`" not in system
    assert "With more than two trades" not in system and "In the Trades chapter" not in system
    assert "18. Never put a number on a draft pick." in system
    assert "19. A drop fact names the receiver only." in system
    assert "Put at most two numbers in a sentence." in system and "Write every number as digits" in system


def _stub_writer(stop_reason="end_turn", parsed_output="parsed", has_usage=True, on_usage=None):
    """A ClaudeWriter over a stub client, and the dict of the keyword arguments of its last request."""
    from facts.writer import ClaudeWriter

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

    return ClaudeWriter(client=type("Client", (), {"messages": Messages()})(), on_usage=on_usage), sent


def test_claude_call_sends_the_system_and_the_user_text_through_parse_call():
    from facts.writer import claude_call

    writer, sent = _stub_writer()
    assert claude_call("system text", "user text", WriterOut, writer=writer) == "parsed"
    assert sent["system"] == [
        {"type": "text", "text": "system text", "cache_control": {"type": "ephemeral"}}
    ]
    assert sent["messages"] == [{"role": "user", "content": "user text"}]
    assert sent["output_format"] is WriterOut
    assert sent["output_config"] == {"effort": "high"}


def test_parse_call_raises_on_a_refusal_and_on_no_parsed_output():
    from facts.writer import RefusalError, WriterError, parse_call

    writer, _ = _stub_writer(stop_reason="refusal", parsed_output=None)
    with pytest.raises(RefusalError):
        parse_call("user text", WriterOut, writer=writer)
    writer, _ = _stub_writer(parsed_output=None)
    with pytest.raises(WriterError):
        parse_call("user text", WriterOut, writer=writer)


def test_the_analyzer_call_alone_sets_the_one_hour_lifetime():
    from analyzer.advisor import AdvisorOut
    from facts.writer import analyzer_call, claude_call

    writer, sent = _stub_writer()
    analyzer_call("analyzer system", "user text", AdvisorOut, writer=writer)
    assert sent["system"] == [{
        "type": "text",
        "text": "analyzer system",
        "cache_control": {"type": "ephemeral", "ttl": "1h"},
    }]
    # The writer and the verifier share claude_call. They keep five minutes, no ttl.
    claude_call("writer system", "user text", WriterOut, writer=writer)
    assert sent["system"][0]["cache_control"] == {"type": "ephemeral"}


def test_the_analyzer_call_alone_runs_at_medium_effort():
    from analyzer.advisor import AdvisorOut
    from facts.writer import analyzer_call, claude_call

    writer, sent = _stub_writer()
    analyzer_call("analyzer system", "user text", AdvisorOut, writer=writer)
    assert sent["output_config"] == {"effort": "medium"}
    claude_call("writer system", "user text", WriterOut, writer=writer)
    assert sent["output_config"] == {"effort": "high"}


def test_the_finder_pick_call_runs_on_sonnet_and_the_read_call_on_opus():
    # The pick reads 10 offers in one call, so it must end in 35 s and cost $0.15 or less (AT-33). Sonnet costs half
    # of Opus per token. The read of one trade keeps the Opus model and the medium effort of prototype 04.
    from analyzer.advisor import AdvisorOut
    from analyzer.finder_pick import FinderPickOut
    from facts.writer import analyzer_call, finder_pick_call

    writer, sent = _stub_writer()
    finder_pick_call("finder system", "user text", FinderPickOut, writer=writer)
    assert sent["model"] == "claude-sonnet-5-5"
    assert sent["output_config"] == {"effort": "medium"}
    assert sent["system"][0]["cache_control"] == {"type": "ephemeral", "ttl": "1h"}
    analyzer_call("analyzer system", "user text", AdvisorOut, writer=writer)
    assert sent["model"] == "claude-opus-5-5"
    assert sent["output_config"] == {"effort": "medium"}


def test_the_finder_repair_call_runs_on_sonnet_at_low_effort():
    # A repair fixes the text of one pick on one sheet, so it is a small call. Low effort keeps it short, so the
    # repairs of a press stay within the time and the cost of AT-33.
    from analyzer.finder_pick import PickOut
    from facts.writer import finder_repair_call

    writer, sent = _stub_writer()
    finder_repair_call("repair system", "user text", PickOut, writer=writer)
    assert sent["model"] == "claude-sonnet-5-5"
    assert sent["output_config"] == {"effort": "low"}
    assert sent["system"][0]["cache_control"] == {"type": "ephemeral", "ttl": "1h"}


# The API calls `read_trade` and `pick_trades` with no `call` argument, so these defaults are the API's calls.
def test_the_advisor_read_uses_the_analyzer_call_and_the_finder_pick_its_own_call_by_default():
    import inspect

    from analyzer.advisor import read_trade
    from analyzer.finder_pick import pick_trades
    from facts.writer import analyzer_call, finder_pick_call, finder_repair_call

    assert inspect.signature(read_trade).parameters["call"].default is analyzer_call
    assert inspect.signature(pick_trades).parameters["call"].default is finder_pick_call
    assert inspect.signature(pick_trades).parameters["repair_call"].default is finder_repair_call


def test_parse_call_logs_the_kind_and_the_three_usage_counts(caplog):
    import logging

    from facts.writer import parse_call

    writer, _ = _stub_writer()
    with caplog.at_level(logging.INFO, logger="facts.writer"):
        parse_call("user text", WriterOut, "system text", writer=writer)
    assert (
        "WriterOut call: cache_creation_input_tokens=0 cache_read_input_tokens=0"
        " input_tokens=1"
    ) in caplog.messages


def test_parse_call_skips_the_log_line_when_the_response_has_no_usage(caplog):
    import logging

    from facts.writer import parse_call

    writer, _ = _stub_writer(has_usage=False)
    with caplog.at_level(logging.INFO, logger="facts.writer"):
        assert parse_call("user text", WriterOut, "system text", writer=writer) == "parsed"
    assert not any("call: cache_creation_input_tokens" in m for m in caplog.messages)


def test_a_writer_hands_the_usage_of_each_call_to_its_usage_hook():
    from facts.writer import parse_call

    seen = []
    writer, _ = _stub_writer(on_usage=seen.append)
    parse_call("user text", WriterOut, "system text", writer=writer)
    assert [usage.input_tokens for usage in seen] == [1]


def test_a_writer_with_a_usage_hook_skips_it_when_the_response_has_no_usage():
    from facts.writer import parse_call

    seen = []
    writer, _ = _stub_writer(has_usage=False, on_usage=seen.append)
    parse_call("user text", WriterOut, "system text", writer=writer)
    assert seen == []


def test_a_metered_press_adds_up_the_calls_and_the_dollars_of_each_claude_call_inside_it():
    from facts.writer import FINDER_PICK_MODEL, metered_press, parse_call

    writer, _ = _stub_writer()
    with metered_press() as meter:
        parse_call("user text", WriterOut, "system text", writer=writer)
        parse_call("user text", WriterOut, "system text", writer=writer, model=FINDER_PICK_MODEL)
    # The stub usage reads 1 input token: $4 per million on Opus, $2 per million on Sonnet.
    assert meter.calls == 2
    assert meter.usd == pytest.approx(6 / 1_000_000)
    # A call after the press counts on no meter.
    parse_call("user text", WriterOut, "system text", writer=writer)
    assert meter.calls == 2


def test_a_call_outside_a_metered_press_counts_on_no_meter():
    from facts.writer import metered_press, parse_call

    writer, _ = _stub_writer()
    parse_call("user text", WriterOut, "system text", writer=writer)
    with metered_press() as meter:
        pass
    assert meter.calls == 0 and meter.usd == 0


def test_tone_varies_the_opener_and_moves_upset_off_the_front(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    system, _ = build_writer_prompt(_chapter(sheet, "median"), sheet, None, prompts_dir=PROMPTS)
    section = system.split("## Openers", 1)[1].split("\n## ", 1)[0]
    assert "- Vary the opener." in section
    assert 'Put "upset" mid-sentence or at the end at least half the time' in section


def test_the_motw_recap_gets_the_note_on_the_headline(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    _, motw_recap = build_writer_prompt(_chapter(sheet, "recap_4"), sheet, None, prompts_dir=PROMPTS)
    assert MOTW_HEADLINE_NOTE in motw_recap
    assert "The turn, the lead, and the injury are not the headline. A recap tells them." in motw_recap


def test_another_recap_and_the_motw_get_no_note_on_the_headline(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    for key in ("recap_1", "motw"):
        _, user = build_writer_prompt(_chapter(sheet, key), sheet, None, prompts_dir=PROMPTS)
        assert MOTW_HEADLINE_NOTE not in user, key


def test_tone_makes_roast_the_default_register_with_no_joke_count(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    system, _ = build_writer_prompt(_chapter(sheet, "median"), sheet, None, prompts_dir=PROMPTS)
    assert "- Roast is the default register of the group chat." in system
    assert "as often as the facts allow" in system
    assert "a record below .500, a bench with no cover" in system
    assert "Every blurb has at least one joke" not in system
    assert "Roast bad teams harder" not in system


def test_prompts_ask_for_one_sentence_with_no_number(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    system, _ = build_writer_prompt(_chapter(sheet, "median"), sheet, None, prompts_dir=PROMPTS)
    assert "- At least one sentence per blurb carries no number." in system
    assert "Put at most two numbers in a sentence. At least one sentence per blurb carries no number." in system


def test_tone_asks_for_an_before_a_vowel_sound_number(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    system, _ = build_writer_prompt(_chapter(sheet, "median"), sheet, None, prompts_dir=PROMPTS)
    assert 'Write "an", not "a", before a number that starts with a vowel sound: "an 8.13 projection"' in system


def test_vocabulary_gives_a_plain_phrase_for_each_stat_term(fixture_raw_dir):
    from facts.verifier import GATED_WORDS

    sheet = _sheet(fixture_raw_dir)
    system, _ = build_writer_prompt(_chapter(sheet, "median"), sheet, None, prompts_dir=PROMPTS)
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


def test_vocabulary_has_one_rule_line_for_the_unlucky_and_lucky_awards(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    system, _ = build_writer_prompt(_chapter(sheet, "awards"), sheet, None, prompts_dir=PROMPTS)
    assert ("- **Unlucky**: the starter with the largest gap below his expected points, at least 5 under. "
            "Expected points are what his volume should have scored. "
            "Say \"unlucky\" only in a sentence that cites `AW.unlucky`.") in system
    assert ("- **Lucky**: the starter with the largest gap above his expected points, at least 5 over. "
            "Say \"lucky\" for it only in a sentence that cites `AW.lucky`.") in system
    # The prose names the award and says in plain words what it measures.
    assert '- **Lucky award in prose**: name it "the Lucky award", never a bare "Lucky".' in system
    assert '- **Unlucky award in prose**: name it "the Unlucky award", never a bare "Unlucky".' in system
    assert 'Plain phrase: "what his stat line usually scores".' in system


def test_the_game_changer_and_awards_get_the_motw_note_when_the_game_changer_is_in_it(hbundle):
    # With the history, the Game Changer is Germie Bernard of behold the lamb, a Matchup of the Week team.
    sheet = hbundle.sheet
    for key in ("game_changer", "awards"):
        _, user = build_writer_prompt(_chapter(sheet, key), sheet, None, prompts_dir=PROMPTS)
        assert MOTW_HEADLINE_NOTE in user, key
    for key in ("recap_1", "median", "position_leaders", "rankings"):
        _, user = build_writer_prompt(_chapter(sheet, key), sheet, None, prompts_dir=PROMPTS)
        assert MOTW_HEADLINE_NOTE not in user, key


def test_no_motw_note_when_the_game_changer_is_outside_it(fixture_raw_dir):
    # With no history, the Game Changer is Tre Tucker of All You Need Is Love, outside the Matchup of the Week.
    sheet = _sheet(fixture_raw_dir)
    assert set(_chapter(sheet, "game_changer").scope_teams) != set(_chapter(sheet, "motw").scope_teams)
    for key in ("game_changer", "awards"):
        _, user = build_writer_prompt(_chapter(sheet, key), sheet, None, prompts_dir=PROMPTS)
        assert MOTW_HEADLINE_NOTE not in user, key


def test_tone_bans_the_and_thats_closer(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    system, _ = build_writer_prompt(_chapter(sheet, "median"), sheet, None, prompts_dir=PROMPTS)
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
    system, _ = build_writer_prompt(_chapter(sheet, "median"), sheet, None, prompts_dir=PROMPTS)
    rule = system.split("\n22. ", 1)[1]
    assert rule.startswith("The Power rankings chapter uses the no-number line below in place of rule 15.")
    assert "Never start the first sentences of 2 teams with the same 3 words." in rule
    assert "At least 4 teams get a sentence with no number." in rule
    assert '"form" is a component name. Write "results over the last 3 weeks" in its place.' in rule
    # Rule 15 is the no-number rule that rule 22 replaces for the rankings chapter.
    assert "At least one sentence per blurb carries no number." in system.split("\n15. ", 1)[1].split("\n16. ", 1)[0]


def test_system_prompt_limits_the_odds_to_the_teams_where_they_matter(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    system, _ = build_writer_prompt(_chapter(sheet, "median"), sheet, None, prompts_dir=PROMPTS)
    assert ("Cite a team's odds only when they change what the reader should feel. "
            "A clinch, an out, or a team near 50% is such a case. Do not list odds for all 12.") in system


def test_rankings_rule_cites_the_why_facts_past_the_tunable_thresholds(fixture_raw_dir):
    from rankings.tunables import WHY_MOVE_AT, WHY_ODDS_AT

    sheet = _sheet(fixture_raw_dir)
    system, _ = build_writer_prompt(_chapter(sheet, "median"), sheet, None, prompts_dir=PROMPTS)
    rule = system.split("\n25. ", 1)[1]
    assert rule.startswith("A `PR.{rid}.why` fact gives the game and the component behind a team's move.")
    assert f"Cite it for every team that moved {WHY_MOVE_AT} or more places either way." in rule
    assert ("An `ODDS.{rid}.why` fact gives the projected pace, the season pace, "
            "and the remaining schedule behind the odds.") in rule
    assert f"Cite it for a team under .500 with odds at or above {WHY_ODDS_AT}%." in rule
    assert f"Cite it also for a team over .500 with odds under {WHY_ODDS_AT}%." in rule
    assert "Either why may serve any other team when it helps." in rule
    assert "A team's odds why counts as its odds line under rule 23." in rule
    # The raised cap leaves room for a why sentence beside the team's opener.
    assert "Give every team 1 to 3 sentences." in system


def test_writer_prompt_lists_the_required_facts_after_the_facts(hbundle):
    sheet = hbundle.sheet
    _, user = build_writer_prompt(_chapter(sheet, "rankings"), sheet, None, prompts_dir=PROMPTS)
    facts, required = user.split("\n\nCite each of these facts in its team's sentences: ", 1)
    assert "Facts:" in facts
    assert sorted(required.removesuffix(".").split(", ")) == sorted(_chapter(sheet, "rankings").required)
    _, user = build_writer_prompt(_chapter(sheet, "median"), sheet, None, prompts_dir=PROMPTS)
    assert "Cite each of these facts" not in user


def test_system_prompt_states_the_swing_for_the_must_watch_games(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    system, _ = build_writer_prompt(_chapter(sheet, "next_week"), sheet, None, prompts_dir=PROMPTS)
    assert "State the swing for the Must Watch games. Use the fact's two numbers as given." in system
    assert "A side that stays near one number has no swing. Say that it holds." in system


def test_system_prompt_names_the_must_watch_reasons_and_the_best_other_storyline(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    system, _ = build_writer_prompt(_chapter(sheet, "next_week"), sheet, None, prompts_dir=PROMPTS)
    assert ("An `NX.{a}v{b}.{kind}` fact gives one storyline of a next-week game. Name the reason of each Must Watch "
            "game. For any other game, mention its best storyline only when it is a streak of 4 or more or an "
            "`NX.{a}v{b}.shootout`.") in system


def test_system_prompt_picks_one_shootout_for_the_next_week(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    system, _ = build_writer_prompt(_chapter(sheet, "next_week"), sheet, None, prompts_dir=PROMPTS)
    assert ("an `NX.shootout.` fact gives an NFL game next week where both teams have a positive pass rate over "
            "expected. Mention at most one shootout. Pick the one with the most league starters in it.") in system


def test_the_fake_writer_raises_a_type_error_when_the_answer_is_not_the_asked_model():
    from fakes import FakeWriter

    from league.models import ResearchOut

    with pytest.raises(TypeError, match="the next answer is a ResearchOut, and the call asks for WriterOut"):
        FakeWriter([ResearchOut(claims=[])]).parse("user text", WriterOut)


def test_the_research_call_alone_sends_the_web_search_tool():
    from facts.writer import claude_call
    from league.models import ResearchOut
    from waiver.research import search_call

    writer, sent = _stub_writer()
    search_call("research system", "user text", writer=writer)
    assert [t["name"] for t in sent["tools"]] == ["web_search"]
    assert sent["output_format"] is ResearchOut
    sent.clear()
    claude_call("writer system", "user text", WriterOut, writer=writer)
    assert "tools" not in sent


def test_the_recap_prompt_names_the_game_story_facts(story_bundle):
    sheet = story_bundle.sheet
    system, user = build_writer_prompt(_chapter(sheet, "recap_3"), sheet, None, prompts_dir=PROMPTS)
    assert "29. In a recap chapter, tell how the game was won: the injury, the timing, and the turn." in system
    for marker in ("A `.turn` fact", "A `.lead` fact", "A `.hurt.` fact", "A `.snaps.` fact"):
        assert marker in system
    assert "When the lead changed, cite it for the timing." in system
    assert "Six recaps of one page must not tell the lead the same way." in system
    assert "game time" in system and "slot" not in system.split("29. In a recap chapter", 1)[1]
    assert "Make no joke about the injury itself." in system
    assert '"Out" alone means a team out of the playoffs. For a player, write "listed Out" or name the injury.' in system
    assert f"- M3.turn: {sheet.facts['M3.turn'].text}" in user
    assert f"- M3.lead: {sheet.facts['M3.lead'].text}" in user
    _, user = build_writer_prompt(_chapter(sheet, "recap_5"), sheet, None, prompts_dir=PROMPTS)
    assert "- M5.hurt.11635: " in user and "- M5.snaps.11635: " in user


def test_writer_asks_for_one_concrete_detail_and_allows_a_light_joke(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    system, _ = build_writer_prompt(_chapter(sheet, "median"), sheet, None, prompts_dir=PROMPTS)
    assert ("30. Give every blurb one concrete detail from its facts: "
            "the number, the player, or the lead change that made the chapter.") in system
    assert "Pick the one a league member would repeat to a friend." in system
    assert ("- A light joke is fine where a fact invites it, for a winner too. Not every joke is a roast. "
            "The joke adds no claim beyond the fact.") in system


def test_the_prompt_keeps_the_banned_words_four_number_rules_and_the_listed_out_line(fixture_raw_dir):
    # Rule 30 loosens the voice. These asserts show that the banned words, the banned phrases, four number rules,
    # and the "listed Out" line stay in the prompt word for word, and that rule 30 says they still hold.
    sheet = _sheet(fixture_raw_dir)
    system, _ = build_writer_prompt(_chapter(sheet, "median"), sheet, None, prompts_dir=PROMPTS)
    assert "Never write these words: best, star, carried, hero, MVP, clutch, exploded, cooked, WOPR." in system
    assert ("Never write these phrases: the entire point, one of the problems, a lot to hang on, "
            "a polite way to say, expected points.") in system
    assert ("3. Use only numbers that appear in the facts you cite. Never invent a number. "
            "Never compute a new one.") in system
    assert "16. Write every number as digits, even a small count such as 2 or 3." in system
    assert '17. Never state a count of players, adds, or teams, such as "2 recent adds".' in system
    assert "- Never put more than two numbers in a sentence." in system
    assert '"Out" alone means a team out of the playoffs. For a player, write "listed Out" or name the injury.' in system
    rule_30 = system.split("30. Give every blurb", 1)[1]
    assert "The banned words, the number rules, and rule 11 still hold." in rule_30


def test_the_recap_rule_keeps_the_term_game_time_off_the_page(story_bundle):
    sheet = story_bundle.sheet
    system, _ = build_writer_prompt(_chapter(sheet, "recap_3"), sheet, None, prompts_dir=PROMPTS)
    rule_29 = system.split("29. In a recap chapter", 1)[1]
    assert ('- The term "game time" never appears on the page. Write "after Thursday", '
            '"after the early Sunday games", or "into Monday".') in rule_29


def test_writer_rule_31_states_a_rank_or_a_comparison_only_from_one_fact(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    system, _ = build_writer_prompt(_chapter(sheet, "median"), sheet, None, prompts_dir=PROMPTS)
    assert ("31. State a rank, a superlative, or a comparison only when one listed fact states it. "
            '"The most", "nobody else was close", and "blew past everyone" need a fact that says so.') in system
    assert 'A rank that a fact gives, such as 12th of 12, may read as last or first.' in system
    assert "A direction word such as fell, climbed, or slid is not a comparison when a fact gives the move." in system


@pytest.mark.skipif(not (SAVED / "week-08" / "raw").is_dir(), reason="no saved week 8 data")
def test_each_matchup_blurb_of_week_8_gets_the_impact_rule_and_its_impact_fact(week_8):
    sheet = week_8.sheet
    for n, key in enumerate(["recap_1", "recap_2", "recap_3", "recap_4", "recap_5", "recap_6"], start=1):
        system, user = build_writer_prompt(_chapter(sheet, key), sheet, None, prompts_dir=PROMPTS)
        assert f"- M{n}.impact: {sheet.facts[f'M{n}.impact'].text}" in user
    # The Matchup of the Week of week 8 is matchup 3, The Blue Tent against London Cooking.
    _, user = build_writer_prompt(_chapter(sheet, "motw"), sheet, None, prompts_dir=PROMPTS)
    assert f"- M3.impact: {sheet.facts['M3.impact'].text}" in user
    rule = system.split("\n32. ", 1)[1]
    assert rule.startswith("In the Matchup of the Week chapter and each recap chapter, an `M<n>.impact` fact gives "
                           "what this week did to both teams.")
    assert "Cite it, and say what the week did to both teams. Choose the parts that matter most." in rule
    # The impact fact, not rule 23, gives the odds of a matchup blurb, and the odds keep their kind and their week.
    assert ('Take an odds number in these chapters from the impact fact. Keep "playoff odds" and "this week" in its '
            "sentence. Rule 23 still governs the odds of the other chapters.") in rule
    # Rule 10 asks for the `.upset` fact with a rank change, and most matchups have no upset.
    assert "A standings place from the impact fact needs no `.upset` fact under rule 10." in rule
    assert "Six recaps of one page must not tell the impact the same way." in rule
    assert "In the Matchup of the Week chapter, name the upset in one sentence only." in rule
