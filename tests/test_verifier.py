"""
Tests for the verifier: the code check, the prompt, and the retry loop.
Every test injects a fake call, so none of them reach the Claude API.
"""
from functools import partial

from fakes import FakeWriter

from cornerstone.config import cornerstone_config
from cornerstone.history import load_history
from cornerstone.models import Blurb, Sentence, Verdict, VerifyOut, WriterOut
from cornerstone.parse import parse_week
from cornerstone.provider.sleeper import load_raw
from cornerstone.sheet import build_bundle
from cornerstone.verifier import (
    build_verifier_prompt,
    claude_verify,
    code_check,
    opener_failures,
    page_words,
    reserved_words,
    verify_blurb,
    write_and_verify,
)
from cornerstone.writer import RefusalError, claude_call

CONFIG = cornerstone_config()
PROMPTS = CONFIG.prompts_dir


def _sheet(d):
    return build_bundle(parse_week(load_raw(d)), news=lambda pid: [], config=CONFIG).sheet


def _ch(sheet, key):
    return next(c for c in sheet.chapters if c.key == key)


def _blurb(key, *sentences):
    return Blurb(chapter=key, attempt=1, fallback=False, sentences=list(sentences))


def _s(text, *ids):
    return Sentence(text=text, fact_ids=list(ids))


def test_number_not_in_fact_fails(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "median")
    b = _blurb("median", _s("Six teams cleared 109.83.", "MED.value"))
    assert any("109.83" in m for m in code_check(b, ch, sheet, prompts_dir=PROMPTS))


def test_out_of_scope_player_fails(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "recap_4")
    b = _blurb("recap_4", _s("Tre Tucker had nothing to do with this.", ch.fact_ids[0]))
    assert any("Tre Tucker" in m for m in code_check(b, ch, sheet, prompts_dir=PROMPTS))


def test_in_scope_player_passes(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "recap_4")
    b = _blurb("recap_4", _s("Blake Corum played.", ch.fact_ids[0]), _s("Corum again.", ch.fact_ids[0]))
    assert code_check(b, ch, sheet, prompts_dir=PROMPTS) == []


def test_decided_needs_driver(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "recap_4")
    non_driver = next(f for f in ch.fact_ids if ".driver" not in f)
    b = _blurb("recap_4", _s("A game decided by a quarterback.", non_driver))
    assert any("decided" in m for m in code_check(b, ch, sheet, prompts_dir=PROMPTS))


def test_won_it_needs_driver(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "recap_4")
    non_driver = next(f for f in ch.fact_ids if ".driver" not in f)
    b = _blurb("recap_4", _s("Bernard won it.", non_driver))
    assert "[0] 'won it' needs a cited .driver fact" in code_check(b, ch, sheet, prompts_dir=PROMPTS)
    b = _blurb("recap_4", _s("Bernard won it.", "M4.driver.13274"))
    assert not any("won it" in m for m in code_check(b, ch, sheet, prompts_dir=PROMPTS))


def test_ordinal_matches_cited_number(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "next_week")
    # The Next Week chapter takes at least 2 sentences, so a plain second sentence joins each blurb.
    b = _blurb("next_week", _s("Lil Fridge sits 1st.", "S.1"), _s("The rest of the league chases them.", "S.1"))
    assert code_check(b, ch, sheet, prompts_dir=PROMPTS) == []
    b = _blurb("next_week", _s("Lil Fridge sits 11th.", "S.1"), _s("The rest of the league chases them.", "S.1"))
    assert any("11" in m for m in code_check(b, ch, sheet, prompts_dir=PROMPTS))


def test_ordinal_eleventh_passes_when_cited(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "next_week")
    fid = next(f for f in ch.fact_ids if "11" in sheet.facts[f].numbers)
    team = sheet.facts[fid].teams[0]
    b = _blurb("next_week", _s(f"{team} is 11th.", fid))
    assert not any("number" in m for m in code_check(b, ch, sheet, prompts_dir=PROMPTS))


def test_digits_inside_team_name_are_not_numbers(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "recap_6")
    b = _blurb("recap_6", _s("Pukancun on 3 won.", "M6.result"), _s("Pukancun on 3 again.", "M6.result"))
    assert not any("number" in m for m in code_check(b, ch, sheet, prompts_dir=PROMPTS))


def test_week_number_is_allowed(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "median")
    b = _blurb("median", _s("In week 6 the bar rose, and week 7 is next.", "MED.value"))
    assert not any("number" in m for m in code_check(b, ch, sheet, prompts_dir=PROMPTS))


def test_gated_words_need_markers(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "recap_4")
    fid = ch.fact_ids[0]
    for text, word in [("An upset win.", "upset"), ("They won because of it.", "because")]:
        b = _blurb("recap_4", _s(text, fid))
        assert any(word in m for m in code_check(b, ch, sheet, prompts_dir=PROMPTS)), word


def test_banned_word_fails(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "recap_4")
    b = _blurb("recap_4", _s("A clutch win.", ch.fact_ids[0]))
    assert any("clutch" in m for m in code_check(b, ch, sheet, prompts_dir=PROMPTS))


def test_banned_phrase_fails(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "recap_4")
    b = _blurb("recap_4", _s("That is a lot to hang on.", ch.fact_ids[0]), _s("They won.", "M4.result"))
    assert "[0] banned phrase 'a lot to hang on'" in code_check(b, ch, sheet, prompts_dir=PROMPTS)


def test_wopr_fails_as_a_banned_word(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "recap_4")
    b = _blurb("recap_4", _s("He had a big WOPR.", ch.fact_ids[0]), _s("They won.", "M4.result"))
    assert "[0] banned word 'WOPR'" in code_check(b, ch, sheet, prompts_dir=PROMPTS)


def test_expected_points_fails_as_a_banned_phrase(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "recap_4")
    b = _blurb("recap_4", _s("He beat his Expected Points.", ch.fact_ids[0]), _s("They won.", "M4.result"))
    assert "[0] banned phrase 'expected points'" in code_check(b, ch, sheet, prompts_dir=PROMPTS)


def test_two_which_tails_fail(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "median")
    b = _blurb(
        "median",
        _s("The median was 106.83, which set the bar.", "MED.value"),
        _s("It rose, which is the bar.", "MED.value"),
    )
    failures = code_check(b, ch, sheet, prompts_dir=PROMPTS)
    assert failures == ["[1] 2 sentences have a ', which' tail; a blurb may hold one"]


def test_which_tail_ignores_case_and_space(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "median")
    for text in ["It rose,which is the bar.", "It rose, Which is the bar."]:
        b = _blurb("median", _s("The median was 106.83, which set the bar.", "MED.value"), _s(text, "MED.value"))
        failures = code_check(b, ch, sheet, prompts_dir=PROMPTS)
        assert failures == ["[1] 2 sentences have a ', which' tail; a blurb may hold one"], text


def test_the_and_thats_closer_fails(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "median")
    for text in ["The median was 106.83, and that's the bar.", "The median was 106.83, and that’s the bar."]:
        b = _blurb("median", _s(text, "MED.value"), _s("It rose.", "MED.value"))
        failures = code_check(b, ch, sheet, prompts_dir=PROMPTS)
        assert failures == ["[0] the sentence ends in \", and that's X\"; that closer is banned"], text


def test_and_thats_outside_the_closer_passes(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "median")
    b = _blurb("median", _s("The median was 106.83.", "MED.value"), _s("And that's the bar, for now.", "MED.value"))
    assert code_check(b, ch, sheet, prompts_dir=PROMPTS) == []


def test_whichever_is_not_a_which_tail(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "median")
    b = _blurb(
        "median",
        _s("The median was 106.83, which set the bar.", "MED.value"),
        _s("It rose, whichever way you look.", "MED.value"),
    )
    assert code_check(b, ch, sheet, prompts_dir=PROMPTS) == []


def test_banned_phrase_inside_a_team_name_passes(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    # Names are removed before the check, so a team named for a banned phrase is not the phrase.
    base = _ch(sheet, "recap_4")
    ch = base.model_copy(update={"scope_teams": [*base.scope_teams, "A Lot To Hang On"]})
    b = _blurb("recap_4", _s("A Lot To Hang On played.", "M4.result"), _s("They won.", "M4.result"))
    assert code_check(b, ch, sheet, prompts_dir=PROMPTS) == []


def test_one_which_tail_passes(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "median")
    b = _blurb("median", _s("The median was 106.83, which set the bar.", "MED.value"), _s("It rose.", "MED.value"))
    assert code_check(b, ch, sheet, prompts_dir=PROMPTS) == []


def test_sentence_count_out_of_range_fails(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "median")
    b = _blurb("median", _s("The median was 106.83.", "MED.value"))
    assert any("sentences" in m for m in code_check(b, ch, sheet, prompts_dir=PROMPTS))


def test_one_reaction_sentence_passes(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "median")
    b = _blurb("median", _s("The median was 106.83.", "MED.value"), _s("Rough week."))
    assert code_check(b, ch, sheet, prompts_dir=PROMPTS) == []


def test_second_reaction_sentence_fails(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "median")
    b = _blurb("median", _s("The median was 106.83.", "MED.value"), _s("Rough week."), _s("Brutal."))
    failures = code_check(b, ch, sheet, prompts_dir=PROMPTS)
    assert failures == ["[2] a second reaction sentence; a blurb may hold one, so cite a fact"]


def test_reaction_sentence_with_a_digit_fails(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "median")
    b = _blurb("median", _s("The median was 106.83.", "MED.value"), _s("Down 40 again."))
    failures = code_check(b, ch, sheet, prompts_dir=PROMPTS)
    assert any(m.startswith("[1] a reaction sentence has a digit") for m in failures)
    # A reaction sentence cites no IDs, so no message ends in an empty ID list.
    assert "[1] number 40 is not in the cited facts" in failures
    assert not any(m.endswith(" ") for m in failures)


def test_reaction_sentence_past_the_range_fails(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "median")
    cited = [_s("The median was 106.83.", "MED.value")] * ch.max_sentences
    b = _blurb("median", *cited, _s("Rough week."))
    count = ch.max_sentences + 1
    range_failure = f"[0] {count} sentences; the range is {ch.min_sentences} to {ch.max_sentences}"
    assert code_check(b, ch, sheet, prompts_dir=PROMPTS) == [range_failure]


def test_reaction_sentence_with_a_scope_name_fails(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "recap_4")
    for text, name in [("Poor behold the lamb.", "behold the lamb"), ("Corum, again.", "Corum")]:
        b = _blurb("recap_4", _s("behold the lamb lost.", "M4.result"), _s(text))
        failures = code_check(b, ch, sheet, prompts_dir=PROMPTS)
        assert f"[1] a reaction sentence names {name}; cite a fact or drop the name" in failures


def test_reaction_sentence_of_eight_words_fails(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "median")
    b = _blurb("median", _s("The median was 106.83.", "MED.value"), _s("Nobody saw that coming, not even the league."))
    failures = code_check(b, ch, sheet, prompts_dir=PROMPTS)
    assert any(m.startswith("[1] a reaction sentence has 8 or more words") for m in failures)
    b = _blurb("median", _s("The median was 106.83.", "MED.value"), _s("Nobody saw that coming, not even them."))
    assert code_check(b, ch, sheet, prompts_dir=PROMPTS) == []


def test_unknown_fact_id_fails(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "median")
    b = _blurb("median", _s("The median was 106.83.", "NOPE.1"))
    assert any("NOPE.1" in m for m in code_check(b, ch, sheet, prompts_dir=PROMPTS))


def test_prompt_lists_chapter_facts_and_numbered_sentences(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "median")
    b = _blurb("median", _s("The median was 106.83.", "MED.value"))
    system, user = build_verifier_prompt(b, ch, sheet, prompts_dir=PROMPTS)
    assert "fact checker" in system
    assert "- MED.value: " in user and "0. The median was 106.83. [ids: MED.value]" in user


def test_prompt_system_has_vocabulary_then_verifier_rules(fixture_raw_dir):
    from importlib import resources

    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "median")
    b = _blurb("median", _s("The median was 106.83.", "MED.value"))
    system, _ = build_verifier_prompt(b, ch, sheet, prompts_dir=PROMPTS)
    rules = resources.files("cornerstone.prompts").joinpath("verifier.md").read_text(encoding="utf-8").strip()
    assert "margin driver" in system
    assert rules.splitlines()[0] in system
    assert system.index("margin driver") < system.index(rules.splitlines()[0])


def test_prompt_holds_uncited_chapter_facts_and_no_other_matchup(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "recap_4")
    uncited = next(f for f in ch.fact_ids if f not in ("M4.result", "M4.records"))
    b = _blurb("recap_4", _s("A result.", "M4.result"), _s("Records.", "M4.records", "M4.result"))
    _, user = build_verifier_prompt(b, ch, sheet, prompts_dir=PROMPTS)
    assert f"- {uncited}: {sheet.facts[uncited].text}" in user
    assert "- M1.result: " not in user
    assert not any(line.startswith("- M1.") for line in user.splitlines())
    assert "0. A result. [ids: M4.result]" in user
    assert "1. Records. [ids: M4.records, M4.result]" in user


def test_verdict_count_mismatch_marks_all_unsupported(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "median")
    b = _blurb("median", _s("A.", "MED.value"), _s("B.", "MED.value"))
    def fake(s, u, m):
        return VerifyOut(verdicts=[Verdict(index=0, supported=True, reason="ok")])
    verdicts = claude_verify(b, ch, sheet, fake, prompts_dir=PROMPTS)
    assert [v.supported for v in verdicts] == [False, False]
    assert "returned 1 verdicts for 2 sentences" in verdicts[0].reason


def test_code_failure_skips_claude_call(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "median")
    b = _blurb("median", _s("Six teams cleared 109.83.", "MED.value"))

    def fake(s, u, m):
        raise AssertionError("no call expected")

    result = verify_blurb(b, ch, sheet, fake, prompts_dir=PROMPTS)
    assert not result.passed and result.verdicts == []


def _good_writer_out():
    return WriterOut(
        sentences=[_s("The median was 106.83.", "MED.value"), _s("It set the bar.", "MED.value")]
    )


def test_pass_on_first_attempt(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "median")

    def fake(system, user, model):
        if model.__name__ == "VerifyOut":
            return VerifyOut(verdicts=[Verdict(index=i, supported=True, reason="ok") for i in range(2)])
        return _good_writer_out()

    blurb, results = write_and_verify(ch, sheet, fake, prompts_dir=PROMPTS)
    assert not blurb.fallback and len(results) == 1 and results[0].passed


def test_two_failures_fall_back(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "median")
    calls = []

    def fake(system, user, model):
        calls.append(model.__name__)
        if model.__name__ == "VerifyOut":
            return VerifyOut(verdicts=[Verdict(index=0, supported=False, reason="not in facts")])
        return model(sentences=[Sentence(text="The median was 106.83.", fact_ids=["MED.value"])] * 2)

    blurb, results = write_and_verify(ch, sheet, fake, prompts_dir=PROMPTS)
    assert blurb.fallback and len(results) == 2 and calls.count("VerifyOut") == 2


def test_refusal_on_first_attempt_then_good_second(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "median")
    writes = []

    def fake(system, user, model):
        if model.__name__ == "VerifyOut":
            return VerifyOut(verdicts=[Verdict(index=i, supported=True, reason="ok") for i in range(2)])
        writes.append(user)
        if len(writes) == 1:
            raise RefusalError("refused")
        return _good_writer_out()

    blurb, results = write_and_verify(ch, sheet, fake, prompts_dir=PROMPTS)
    assert not blurb.fallback and blurb.attempt == 2
    assert results[0].code_failures[0].startswith("writer error")
    assert "writer error" in writes[1]


def test_feedback_reaches_second_attempt(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "median")
    users = []

    def fake(system, user, model):
        if model.__name__ == "VerifyOut":
            ok = len(users) > 1
            return VerifyOut(verdicts=[Verdict(index=i, supported=ok, reason="bad claim") for i in range(2)])
        users.append(user)
        return _good_writer_out()

    blurb, results = write_and_verify(ch, sheet, fake, prompts_dir=PROMPTS)
    assert not blurb.fallback and len(results) == 2
    assert "Sentence 0: bad claim" in users[1]


def test_second_reaction_gets_feedback_and_passes_with_one(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "median")
    users = []

    def fake(system, user, model):
        if model.__name__ == "VerifyOut":
            return VerifyOut(verdicts=[Verdict(index=i, supported=True, reason="ok") for i in range(3)])
        users.append(user)
        last = _s("Brutal.") if len(users) == 1 else _s("It set the bar.", "MED.value")
        return WriterOut(sentences=[_s("The median was 106.83.", "MED.value"), _s("Rough week."), last])

    blurb, results = write_and_verify(ch, sheet, fake, prompts_dir=PROMPTS)
    assert not blurb.fallback and blurb.attempt == 2 and len(results) == 2
    assert "[2] a second reaction sentence" in users[1]
    assert [s.fact_ids for s in blurb.sentences].count([]) == 1


def test_verifier_error_falls_back(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "median")

    def fake(system, user, model):
        if model.__name__ == "VerifyOut":
            raise RefusalError("refused")
        return _good_writer_out()

    blurb, results = write_and_verify(ch, sheet, fake, prompts_dir=PROMPTS)
    assert blurb.fallback and len(results) == 2
    assert results[0].code_failures[0].startswith("verifier error")


def test_gated_word_inside_team_name_passes(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "recap_4").model_copy(deep=True)
    ch.scope_teams.append("Lucky Lambs")
    b = _blurb("recap_4", _s("Lucky Lambs played.", ch.fact_ids[0]), _s("Again.", ch.fact_ids[0]))
    assert not any("lucky" in m.lower() for m in code_check(b, ch, sheet, prompts_dir=PROMPTS))


def test_lucky_passes_with_the_lucky_award_cited(fixture_raw_dir):
    # The Lucky award names its own award, so the word needs no recent add.
    sheet = _sheet(fixture_raw_dir).model_copy(deep=True)
    ch = _ch(sheet, "awards")
    sheet.facts["AW.lucky"] = sheet.facts[ch.fact_ids[0]].model_copy(update={"id": "AW.lucky"})
    ch.fact_ids.append("AW.lucky")
    b = _blurb("awards", _s("The Lucky award goes out.", "AW.lucky"), _s("Again.", ch.fact_ids[0]))
    assert not any("lucky" in m.lower() for m in code_check(b, ch, sheet, prompts_dir=PROMPTS))
    b = _blurb("awards", _s("That was lucky.", ch.fact_ids[0]), _s("Again.", ch.fact_ids[0]))
    assert any("'lucky' needs" in m for m in code_check(b, ch, sheet, prompts_dir=PROMPTS))


def test_unlucky_needs_the_unlucky_award_cited(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir).model_copy(deep=True)
    ch = _ch(sheet, "awards")
    sheet.facts["AW.unlucky"] = sheet.facts[ch.fact_ids[0]].model_copy(update={"id": "AW.unlucky"})
    ch.fact_ids.append("AW.unlucky")
    b = _blurb("awards", _s("The Unlucky award goes out.", "AW.unlucky"), _s("Again.", ch.fact_ids[0]))
    assert not any("lucky" in m.lower() for m in code_check(b, ch, sheet, prompts_dir=PROMPTS))
    b = _blurb("awards", _s("That was unlucky.", ch.fact_ids[0]), _s("Again.", ch.fact_ids[0]))
    assert any("'unlucky' needs" in m for m in code_check(b, ch, sheet, prompts_dir=PROMPTS))


def test_writer_with_no_output_twice_falls_back(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "median")

    def fake(system, user, model):
        if model.__name__ == "VerifyOut":
            raise AssertionError("no verifier call expected")

    blurb, results = write_and_verify(ch, sheet, fake, prompts_dir=PROMPTS)
    assert blurb.fallback and len(results) == 2
    assert all(r.code_failures[0].startswith("writer error") for r in results)


def test_writer_validation_error_is_a_failed_attempt(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "median")

    def fake(system, user, model):
        if model.__name__ == "VerifyOut":
            raise AssertionError("no verifier call expected")
        return model.model_validate({"sentences": "not a list"})

    blurb, results = write_and_verify(ch, sheet, fake, prompts_dir=PROMPTS)
    assert blurb.fallback and len(results) == 2


def test_name_removal_matches_whole_words(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "median").model_copy(deep=True)
    ch.scope_players.append("0")
    b = _blurb("median", _s("A team scored 100.", "MED.value"), _s("Again.", "MED.value"))
    assert any("number 100" in m for m in code_check(b, ch, sheet, prompts_dir=PROMPTS))


def test_number_word_not_in_fact_fails(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "recap_4")
    b = _blurb("recap_4", _s("They won by five.", "M4.result"), _s("Again.", "M4.result"))
    assert any("'five'" in m for m in code_check(b, ch, sheet, prompts_dir=PROMPTS))


def test_number_word_in_cited_fact_passes(fixture_raw_dir):
    def news(_player_id):
        return [{"metadata": {"description": "He scored two touchdowns."}, "published": "1792500000000"}]

    sheet = build_bundle(parse_week(load_raw(fixture_raw_dir)), news=news, config=CONFIG).sheet
    ch = _ch(sheet, "game_changer")
    b = _blurb("game_changer", _s("He scored two touchdowns.", "AW.game_changer.news"))
    assert not any("number word" in m for m in code_check(b, ch, sheet, prompts_dir=PROMPTS))


def test_fact_id_in_text_fails(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "recap_4")
    b = _blurb("recap_4", _s("See [M4.result].", "M4.result"), _s("Again.", "M4.result"))
    assert any("'['" in m for m in code_check(b, ch, sheet, prompts_dir=PROMPTS))


def test_vocabulary_has_the_history_terms():
    from importlib import resources

    text = resources.files("cornerstone.prompts").joinpath("vocabulary.md").read_text(encoding="utf-8")
    for term in ("streak", "team trend", "season high", "season low", "season average"):
        assert f"**{term}**" in text


def test_vocabulary_has_the_banned_phrases_line():
    from importlib import resources

    text = resources.files("cornerstone.prompts").joinpath("vocabulary.md").read_text(encoding="utf-8")
    line = ("Never write these phrases: the entire point, one of the problems, a lot to hang on, a polite way to say, "
            "expected points.")
    assert "## Banned phrases\n\n" + line in text
    assert text.index("## Banned words") < text.index("## Banned phrases")


def test_dropswing_passes_the_cost_gate(dbundle):
    sheet = dbundle.sheet
    ch = _ch(sheet, "recap_4")
    b = _blurb("recap_4", _s("The drops cost Bo Girds the game.", "M4.dropswing"))
    assert not [m for m in code_check(b, ch, sheet, prompts_dir=PROMPTS) if "'cost' needs" in m]


def test_drop_value_alone_fails_the_cost_gate(dbundle):
    sheet = dbundle.sheet
    ch = _ch(sheet, "recap_4")
    b = _blurb("recap_4", _s("The drops cost Bo Girds the game.", "D.12501.value"))
    assert any("'cost' needs" in m for m in code_check(b, ch, sheet, prompts_dir=PROMPTS))



def test_team_named_twice_fails(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "recap_4")
    b = _blurb("recap_4", _s("behold the lamb won.", "M4.result"), _s("behold the lamb again.", "M4.result"))
    line = ("[1] the blurb: team behold the lamb is named 2 times; name it once, "
            "then write 'this side', 'they', or the player names")
    assert line in code_check(b, ch, sheet, prompts_dir=PROMPTS)


def test_team_named_once_passes(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "recap_4")
    b = _blurb("recap_4", _s("behold the lamb won.", "M4.result"), _s("They won again.", "M4.result"))
    assert code_check(b, ch, sheet, prompts_dir=PROMPTS) == []


def test_second_team_named_once_passes(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "recap_4")
    b = _blurb("recap_4", _s("behold the lamb played.", "M4.result"), _s("Bo Girds played.", "M4.result"))
    assert code_check(b, ch, sheet, prompts_dir=PROMPTS) == []


def test_capital_second_mention_of_team_counts(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "recap_4")
    b = _blurb("recap_4", _s("They beat behold the lamb.", "M4.result"), _s("Behold the lamb lost.", "M4.result"))
    failures = code_check(b, ch, sheet, prompts_dir=PROMPTS)
    assert any(m.startswith("[1] the blurb: team behold the lamb is named 2 times") for m in failures)


def test_part_of_team_name_does_not_count(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "recap_4")
    b = _blurb("recap_4", _s("behold the lamb won.", "M4.result"), _s("The lamb ate.", "M4.result"))
    assert not any("is named" in m for m in code_check(b, ch, sheet, prompts_dir=PROMPTS))


def test_team_name_with_punctuation_named_twice_fails(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "recap_1")
    b = _blurb("recap_1", _s("Brock ‘N’ Roll won.", "M1.result"), _s("Brock ‘N’ Roll again.", "M1.result"))
    failures = code_check(b, ch, sheet, prompts_dir=PROMPTS)
    assert any(m.startswith("[1] the blurb: team Brock ‘N’ Roll is named 2 times") for m in failures)


def test_twelve_team_chapter_skips_the_repeat_check(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "next_week")
    b = _blurb("next_week", _s("Lil Fridge sits 1st.", "S.1"), _s("Lil Fridge plays next.", "S.1"))
    assert not any("is named" in m for m in code_check(b, ch, sheet, prompts_dir=PROMPTS))


def _rankings(raw_dir, history_root):
    raw = load_raw(raw_dir)
    sheet = build_bundle(parse_week(raw), news=lambda pid: [], history=load_history(history_root, raw, week=6),
                         config=CONFIG).sheet
    return sheet, _ch(sheet, "rankings")


def _tagged(text, rid, *ids):
    return Sentence(text=text, fact_ids=list(ids), roster_id=rid)


def _good_rankings(sheet, ch):
    """One sentence per team in rank order: the first clause of the team's PR fact, tagged with its roster.
    The clause holds one number, so the sentence stays under the limit of two.
    The sentence also cites the team's required facts, so the blurb leaves none uncited."""
    rids = [int(fid.split(".")[1]) for fid in ch.fact_ids if fid.startswith("PR.") and not fid.endswith(".why")]
    return [_tagged(_first_clause(sheet.facts[f"PR.{rid}"].text, ","), rid, f"PR.{rid}", *_required_of(ch, rid))
            for rid in rids]


def _first_clause(text, mark):
    """The text up to the first `mark`, as a sentence, so a test sentence holds fewer numbers than its fact."""
    return text.split(mark, 1)[0] + "."


def _required_of(ch, rid):
    return [fid for fid in ch.required if int(fid.split(".")[1]) == rid]


def _standing_id(sheet, ch, rid):
    """The ID of the standing fact of a roster in the rankings chapter."""
    team = sheet.facts[f"PR.{rid}"].teams
    return next(fid for fid in ch.fact_ids if fid.startswith("S.") and sheet.facts[fid].teams == team)


def test_a_good_rankings_blurb_passes(fixture_raw_dir, fixture_history_root):
    sheet, ch = _rankings(fixture_raw_dir, fixture_history_root)
    assert code_check(_blurb("rankings", *_good_rankings(sheet, ch)), ch, sheet, prompts_dir=PROMPTS) == []


def test_a_rankings_blurb_that_leaves_a_required_fact_uncited_fails(fixture_raw_dir, fixture_history_root):
    sheet, ch = _rankings(fixture_raw_dir, fixture_history_root)
    assert "ODDS.12.why" in ch.required
    sentences = [s.model_copy(update={"fact_ids": [f for f in s.fact_ids if f != "ODDS.12.why"]})
                 for s in _good_rankings(sheet, ch)]
    failures = code_check(_blurb("rankings", *sentences), ch, sheet, prompts_dir=PROMPTS)
    assert "[0] required fact ODDS.12.why is not cited" in failures


def test_a_required_fact_cited_in_another_team_sentence_fails(fixture_raw_dir, fixture_history_root):
    sheet, ch = _rankings(fixture_raw_dir, fixture_history_root)
    sentences = [s.model_copy(update={"fact_ids": [f for f in s.fact_ids if f != "ODDS.12.why"]})
                 for s in _good_rankings(sheet, ch)]
    other = next(i for i, s in enumerate(sentences) if s.roster_id != 12)
    sentences[other].fact_ids.append("ODDS.12.why")
    failures = code_check(_blurb("rankings", *sentences), ch, sheet, prompts_dir=PROMPTS)
    assert "[0] required fact ODDS.12.why is not cited" in failures


def test_a_rankings_sentence_with_no_roster_tag_fails(fixture_raw_dir, fixture_history_root):
    sheet, ch = _rankings(fixture_raw_dir, fixture_history_root)
    sentences = _good_rankings(sheet, ch)
    sentences.insert(1, _s("Rough week."))
    assert "[1] the sentence has no roster tag; set roster_id to the team it is about" in code_check(
        _blurb("rankings", *sentences), ch, sheet, prompts_dir=PROMPTS)


def test_a_team_with_no_rankings_sentence_fails(fixture_raw_dir, fixture_history_root):
    sheet, ch = _rankings(fixture_raw_dir, fixture_history_root)
    sentences = _good_rankings(sheet, ch)
    last = sentences.pop()
    sentences.append(_tagged("Rough week.", sentences[0].roster_id))
    team = sheet.facts[f"PR.{last.roster_id}"].teams[0]
    assert f"[0] team {team} has no sentence; give every team 1 to 3 sentences" in code_check(
        _blurb("rankings", *sentences), ch, sheet, prompts_dir=PROMPTS)


def test_a_team_with_four_rankings_sentences_fails(fixture_raw_dir, fixture_history_root):
    sheet, ch = _rankings(fixture_raw_dir, fixture_history_root)
    sentences = _good_rankings(sheet, ch)
    rid = sentences[0].roster_id
    standing = _standing_id(sheet, ch, rid)
    sentences[1:1] = [_tagged(sheet.facts[standing].text, rid, standing),
                      _tagged(sheet.facts[standing].text, rid, standing), _tagged("Rough week.", rid)]
    team = sheet.facts[f"PR.{rid}"].teams[0]
    assert f"[3] team {team} has 4 sentences; give every team 1 to 3" in code_check(
        _blurb("rankings", *sentences), ch, sheet, prompts_dir=PROMPTS)


def test_a_tagged_reaction_counts_toward_the_three(fixture_raw_dir, fixture_history_root):
    sheet, ch = _rankings(fixture_raw_dir, fixture_history_root)
    sentences = _good_rankings(sheet, ch)
    # The first team's standing fact holds 721.96, and the fixture names one player 96, so the test uses the second.
    rid = sentences[1].roster_id
    standing = _standing_id(sheet, ch, rid)
    sentences[2:2] = [_tagged(_first_clause(sheet.facts[standing].text, " and "), rid, standing),
                      _tagged("Rough week.", rid)]
    assert code_check(_blurb("rankings", *sentences), ch, sheet, prompts_dir=PROMPTS) == []


def test_a_first_rankings_sentence_without_the_pr_fact_fails(fixture_raw_dir, fixture_history_root):
    sheet, ch = _rankings(fixture_raw_dir, fixture_history_root)
    sentences = _good_rankings(sheet, ch)
    rid = sentences[3].roster_id
    standing = _standing_id(sheet, ch, rid)
    sentences[3] = _tagged(sheet.facts[standing].text, rid, standing)
    team = sheet.facts[f"PR.{rid}"].teams[0]
    assert f"[3] the first sentence about team {team} must cite PR.{rid}" in code_check(
        _blurb("rankings", *sentences), ch, sheet, prompts_dir=PROMPTS)


def test_other_chapters_pass_with_no_roster_tag(fixture_raw_dir, fixture_history_root):
    sheet, _ = _rankings(fixture_raw_dir, fixture_history_root)
    ch = _ch(sheet, "next_week")
    # The Next Week chapter takes at least 2 sentences.
    b = _blurb("next_week", _s("Lil Fridge sits 1st.", "S.1"), _s("The rest of the league chases them.", "S.1"))
    assert code_check(b, ch, sheet, prompts_dir=PROMPTS) == []


def test_a_blurb_where_every_sentence_has_a_number_fails(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "recap_4")
    score = sheet.facts["M4.result"].numbers[0]
    b = _blurb("recap_4", *(_s(f"They scored {score}.", "M4.result") for _ in range(3)))
    assert ("[0] every sentence has a number (sentences 0, 1, 2); write at least one sentence with no number"
            in code_check(b, ch, sheet, prompts_dir=PROMPTS))


def test_a_blurb_with_one_sentence_with_no_number_passes_the_number_mix(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "recap_4")
    score = sheet.facts["M4.result"].numbers[0]
    b = _blurb("recap_4", _s(f"They scored {score}.", "M4.result"), _s(f"Then {score}.", "M4.result"),
               _s("Rough week."))
    assert not any("every sentence has a number" in m for m in code_check(b, ch, sheet, prompts_dir=PROMPTS))


def test_a_two_sentence_blurb_with_numbers_only_passes_the_number_mix(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "recap_4")
    score = sheet.facts["M4.result"].numbers[0]
    b = _blurb("recap_4", *(_s(f"They scored {score}.", "M4.result") for _ in range(2)))
    assert not any("every sentence has a number" in m for m in code_check(b, ch, sheet, prompts_dir=PROMPTS))


def test_the_rankings_chapter_skips_the_number_mix(fixture_raw_dir, fixture_history_root):
    sheet, ch = _rankings(fixture_raw_dir, fixture_history_root)
    assert not any("every sentence has a number" in m
                   for m in code_check(_blurb("rankings", *_good_rankings(sheet, ch)), ch, sheet, prompts_dir=PROMPTS))


def test_a_before_a_number_with_a_vowel_sound_fails(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "game_changer")
    b = _blurb("game_changer", _s("He beat a 8.13 projection.", "AW.game_changer"))
    assert "[0] write 'an 8.13', not 'a 8.13'" in code_check(b, ch, sheet, prompts_dir=PROMPTS)
    for number in ("11", "18", "85"):
        b = _blurb("game_changer", _s(f"He beat a {number} projection.", "AW.game_changer"))
        assert f"[0] write 'an {number}', not 'a {number}'" in code_check(b, ch, sheet, prompts_dir=PROMPTS), number


def test_the_right_article_before_a_number_passes(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "game_changer")
    for text in ("He beat an 8.13 projection.", "He beat a 9.1 projection.", "He beat a 110 projection."):
        b = _blurb("game_changer", _s(text, "AW.game_changer"))
        assert not any("write 'an" in m for m in code_check(b, ch, sheet, prompts_dir=PROMPTS)), text


def test_an_before_a_number_with_no_vowel_sound_fails(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "game_changer")
    for number in ("9", "110"):
        b = _blurb("game_changer", _s(f"He beat an {number} projection.", "AW.game_changer"))
        assert f"[0] write 'a {number}', not 'an {number}'" in code_check(b, ch, sheet, prompts_dir=PROMPTS), number


def test_an_before_8_passes(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "game_changer")
    b = _blurb("game_changer", _s("He beat an 8 projection.", "AW.game_changer"))
    assert not any("not 'an" in m for m in code_check(b, ch, sheet, prompts_dir=PROMPTS))


def _no_love_recap_6(sheet):
    # recap_6 has All You Need Is Love in scope. Without Jeremiyah Love, no scope player is named Love.
    base = _ch(sheet, "recap_6")
    return base.model_copy(update={"scope_players": [p for p in base.scope_players if p != "Jeremiyah Love"]})


def test_team_name_word_as_a_last_name_passes(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _no_love_recap_6(sheet)
    b = _blurb(
        "recap_6",
        _s("All You Need Is Love won.", "M6.result"),
        _s("Love was the word of the week.", "M6.result"),
        _s("Love is apparently not enough."),
    )
    assert code_check(b, ch, sheet, prompts_dir=PROMPTS) == []


def test_lowercase_team_name_word_as_a_last_name_passes(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "position_leaders")
    b = _blurb("position_leaders", _s("The lamb is lost.", ch.fact_ids[0]))
    failures = code_check(b, ch, sheet, prompts_dir=PROMPTS)
    assert not any("player CeeDee Lamb is not on a team in this chapter" in m for m in failures)


def test_full_name_still_fails_when_last_name_is_a_team_name_word(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _no_love_recap_6(sheet)
    b = _blurb("recap_6", _s("Jordan Love sat.", "M6.result"), _s("They won.", "M6.result"))
    failures = code_check(b, ch, sheet, prompts_dir=PROMPTS)
    assert any("player Jordan Love is not on a team in this chapter" in m for m in failures)


def test_last_name_outside_team_names_still_fails(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    # No fixture roster has Jalen Hurts, so a chapter outside recap_4 adds him to the league.
    extra = _ch(sheet, "recap_1").model_copy(update={"key": "extra", "scope_players": ["Jalen Hurts"]})
    sheet = sheet.model_copy(update={"chapters": [*sheet.chapters, extra]})
    ch = _ch(sheet, "recap_4")
    b = _blurb("recap_4", _s("Hurts had 3 touchdowns.", "M4.result"), _s("They won.", "M4.result"))
    failures = code_check(b, ch, sheet, prompts_dir=PROMPTS)
    assert any("player Jalen Hurts is not on a team in this chapter" in m for m in failures)


def test_game_changer_sentence_naming_his_own_player_passes(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "game_changer")
    b = _blurb("game_changer", _s("Tre Tucker carried the win.", "M6.swing.10213"), _s("They won.", "M6.result"))
    assert not any("player" in m for m in code_check(b, ch, sheet, prompts_dir=PROMPTS))


def test_game_changer_sentence_naming_another_player_fails(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "game_changer")
    b = _blurb("game_changer", _s("Tyler Shough threw to Tre Tucker.", "M6.swing.10213"), _s("They won.", "M6.result"))
    failures = code_check(b, ch, sheet, prompts_dir=PROMPTS)
    assert any("player Tyler Shough is not on a team in this chapter" in m for m in failures)


def test_two_rankings_teams_with_the_same_opener_fail(fixture_raw_dir, fixture_history_root):
    sheet, ch = _rankings(fixture_raw_dir, fixture_history_root)
    sentences = _good_rankings(sheet, ch)
    for i in (2, 5):
        rid = sentences[i].roster_id
        sentences[i] = _tagged("Despite 2 straight losses, this side holds.", rid, f"PR.{rid}")
    first = sheet.facts[f"PR.{sentences[2].roster_id}"].teams[0]
    second = sheet.facts[f"PR.{sentences[5].roster_id}"].teams[0]
    assert (f"[5] team {second} opens with 'despite 2 straight', as team {first} does; give each team its own opener"
            in code_check(_blurb("rankings", *sentences), ch, sheet, prompts_dir=PROMPTS))


def test_a_second_sentence_may_share_an_opener(fixture_raw_dir, fixture_history_root):
    sheet, ch = _rankings(fixture_raw_dir, fixture_history_root)
    sentences = _good_rankings(sheet, ch)
    # Only the first sentence of a team is its opener, so a later sentence with the same words passes.
    sentences.insert(1, _tagged(sentences[1].text, sentences[0].roster_id, f"PR.{sentences[0].roster_id}"))
    failures = code_check(_blurb("rankings", *sentences), ch, sheet, prompts_dir=PROMPTS)
    assert not any("opens with" in m for m in failures)


def test_a_failed_opener_keeps_the_second_sentence_of_its_team_out(fixture_raw_dir, fixture_history_root):
    sheet, ch = _rankings(fixture_raw_dir, fixture_history_root)
    # Team 2 fails on its opener. Its second sentence is not an opener, so team 9 may open on the same words.
    b = _blurb(
        "rankings",
        _tagged("Scoring has dipped to 600.", 5, "PR.5"),
        _tagged("Scoring has dipped too.", 2, "PR.2"),
        _tagged("Despite 2 straight losses, they hold.", 2, "PR.2"),
        _tagged("Despite 2 straight wins, they climb.", 9, "PR.9"),
    )
    failures = opener_failures(b, ch, sheet)
    assert len(failures) == 1
    assert failures[0].startswith("[1] ")


def test_an_opener_ignores_curly_quotes_and_question_marks(fixture_raw_dir, fixture_history_root):
    sheet, ch = _rankings(fixture_raw_dir, fixture_history_root)
    b = _blurb(
        "rankings",
        _tagged("“Scoring has dipped.”", 5, "PR.5"),
        _tagged("Scoring has? dipped too.", 2, "PR.2"),
    )
    assert [m[:4] for m in opener_failures(b, ch, sheet)] == ["[1] "]


# A research fact carries its source URL as text. The fact ID is the citation, as for any fact.
CLAIM_URL = "https://sports.yahoo.com/fantasy/article/week-7-waiver-wire-141451458.html"


def _claim_sheet():
    from cornerstone.models import Chapter, Fact, FactSheet

    text = f"Tucker ran 31 routes and leads the Raiders wideouts. Source: Yahoo Fantasy, {CLAIM_URL}"
    claim = Fact(id="WV.research.7.1", text=text, numbers=["31"], teams=[], players=["Tre Tucker"])
    chapter = Chapter(key="waiver", title="Waiver wire", fact_ids=[claim.id], scope_teams=[],
                      scope_players=["Tre Tucker"], min_sentences=1, max_sentences=2)
    return FactSheet(facts={claim.id: claim}, chapters=[chapter]), chapter


def test_a_cited_research_fact_passes_with_its_url_in_the_sentence():
    sheet, ch = _claim_sheet()
    b = _blurb("waiver", _s(f"Tre Tucker ran 31 routes, per Yahoo Fantasy: {CLAIM_URL}", "WV.research.7.1"))
    assert code_check(b, ch, sheet, prompts_dir=PROMPTS) == []


def test_a_sentence_with_a_url_and_no_fact_id_is_a_reaction_and_fails_on_an_uncited_digit():
    sheet, ch = _claim_sheet()
    failures = code_check(_blurb("waiver", _s(f"Tucker ran 31 routes ({CLAIM_URL}).")), ch, sheet, prompts_dir=PROMPTS)
    assert "[0] number 31 is not in the cited facts" in failures
    assert any("reaction sentence" in f for f in failures)


def test_a_cited_research_claim_still_fails_on_a_banned_word():
    sheet, ch = _claim_sheet()
    b = _blurb("waiver", _s(f"Tre Tucker is the best add, per Yahoo Fantasy: {CLAIM_URL}", "WV.research.7.1"))
    assert "[0] banned word 'best'" in code_check(b, ch, sheet, prompts_dir=PROMPTS)


def test_in_scope_two_word_last_name_does_not_name_an_out_of_scope_player(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    # recap_3 has Amon-Ra St. Brown in scope. A.J. Brown is in the league but not in recap_3.
    ch = _ch(sheet, "recap_3")
    assert "Amon-Ra St. Brown" in ch.scope_players
    b = _blurb("recap_3", _s("St. Brown also played.", "M3.result"), _s("They won.", "M3.result"))
    assert not any("player A.J. Brown" in m for m in code_check(b, ch, sheet, prompts_dir=PROMPTS))


def _awards_with_luck(fixture_raw_dir):
    """The awards chapter with AW.lucky and AW.unlucky facts, so the word gate passes and only the count can fail."""
    sheet = _sheet(fixture_raw_dir).model_copy(deep=True)
    ch = _ch(sheet, "awards")
    for fid in ("AW.lucky", "AW.unlucky"):
        sheet.facts[fid] = sheet.facts[ch.fact_ids[0]].model_copy(update={"id": fid})
        ch.fact_ids.append(fid)
    return sheet, ch


def test_lucky_in_two_sentences_fails_and_names_both(fixture_raw_dir):
    sheet, ch = _awards_with_luck(fixture_raw_dir)
    b = _blurb(
        "awards",
        _s("The Lucky award goes out.", "AW.lucky"),
        _s("Again.", ch.fact_ids[0]),
        _s("That was LUCKY.", "AW.lucky"),
    )
    failures = code_check(b, ch, sheet, prompts_dir=PROMPTS)
    assert failures == ["[2] sentences [0] and [2] say 'lucky'; a page may say it once"]


def test_unlucky_in_two_sentences_fails(fixture_raw_dir):
    sheet, ch = _awards_with_luck(fixture_raw_dir)
    b = _blurb(
        "awards",
        _s("The Unlucky award goes out.", "AW.unlucky"),
        _s("That was unlucky.", "AW.unlucky"),
    )
    failures = code_check(b, ch, sheet, prompts_dir=PROMPTS)
    assert failures == ["[1] sentences [0] and [1] say 'unlucky'; a page may say it once"]


def test_lucky_once_and_unlucky_once_pass(fixture_raw_dir):
    # "unlucky" holds "lucky" inside it, but the whole-word match does not count it as "lucky".
    sheet, ch = _awards_with_luck(fixture_raw_dir)
    b = _blurb(
        "awards",
        _s("The Lucky award goes out.", "AW.lucky"),
        _s("The Unlucky award goes out.", "AW.unlucky"),
    )
    assert code_check(b, ch, sheet, prompts_dir=PROMPTS) == []


def test_lucky_after_an_earlier_chapter_said_it_fails(fixture_raw_dir):
    # Chapter A said "lucky", so the build passes the word in; chapter B fails on its own "lucky".
    sheet, ch = _awards_with_luck(fixture_raw_dir)
    b = _blurb("awards", _s("Again.", ch.fact_ids[0]), _s("The Lucky award goes out.", "AW.lucky"))
    assert code_check(b, ch, sheet, prompts_dir=PROMPTS, used_words={"lucky"}) == [
        "[1] says 'lucky', but another chapter of this page already did"
    ]


def test_unlucky_after_an_earlier_lucky_passes(fixture_raw_dir):
    # Chapter A said "lucky" once and chapter B says "unlucky" once: each word is used once on the page.
    sheet, ch = _awards_with_luck(fixture_raw_dir)
    b = _blurb("awards", _s("The Unlucky award goes out.", "AW.unlucky"), _s("Again.", ch.fact_ids[0]))
    assert code_check(b, ch, sheet, prompts_dir=PROMPTS, used_words={"lucky"}) == []


def test_page_words_skips_a_team_name_and_unlucky(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "recap_4").model_copy(deep=True)
    ch.scope_teams.append("Lucky Lambs")
    b = _blurb("recap_4", _s("Lucky Lambs played.", ch.fact_ids[0]), _s("That was unlucky.", ch.fact_ids[0]))
    assert page_words(b, ch) == {"unlucky"}
    assert page_words(b, None) == {"lucky", "unlucky"}


def test_write_and_verify_sends_the_page_word_failure_to_the_rewrite(fixture_raw_dir):
    sheet, ch = _awards_with_luck(fixture_raw_dir)
    users = []

    def fake(system, user, model):
        if model.__name__ == "VerifyOut":
            return VerifyOut(verdicts=[Verdict(index=i, supported=True, reason="ok") for i in range(2)])
        users.append(user)
        return WriterOut(sentences=[_s("The Lucky award goes out.", "AW.lucky"), _s("Again.", ch.fact_ids[0])])

    blurb, results = write_and_verify(ch, sheet, fake, prompts_dir=PROMPTS, used_words={"lucky"})
    assert blurb.fallback and len(results) == 2
    assert "another chapter of this page already did" in users[1]


def test_the_awards_chapter_owns_lucky_when_the_sheet_has_the_lucky_award(fixture_raw_dir):
    # The awards chapter must always name the award, so every other chapter starts with "lucky" used.
    sheet, awards = _awards_with_luck(fixture_raw_dir)
    assert reserved_words("motw", sheet) == {"lucky", "unlucky"}
    assert reserved_words("awards", sheet) == set()
    motw = _ch(sheet, "motw")
    b = _blurb("motw", _s("That was lucky.", *motw.fact_ids[:1]), _s("Again.", *motw.fact_ids[:1]))
    assert "[0] says 'lucky', but another chapter of this page already did" in code_check(
        b, motw, sheet, prompts_dir=PROMPTS, used_words=reserved_words("motw", sheet)
    )
    b = _blurb("awards", _s("The Lucky award goes out.", "AW.lucky"), _s("Again.", awards.fact_ids[0]))
    assert code_check(b, awards, sheet, prompts_dir=PROMPTS, used_words=reserved_words("awards", sheet)) == []


def test_no_award_fact_reserves_no_word(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    assert "AW.lucky" not in sheet.facts
    assert reserved_words("motw", sheet) == set()


def test_the_first_writer_call_hears_the_used_words(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "median")
    users = []

    def fake(system, user, model):
        if model.__name__ == "VerifyOut":
            return VerifyOut(verdicts=[Verdict(index=i, supported=True, reason="ok") for i in range(2)])
        users.append(user)
        return _good_writer_out()

    blurb, _ = write_and_verify(ch, sheet, fake, prompts_dir=PROMPTS, used_words={"lucky"})
    assert "Words this page already uses:\nDo not say 'lucky'. Another chapter of this page already does." in users[0]
    # No last attempt exists yet, so the first call has no feedback section and the pass saves attempt 1.
    assert "Feedback from the last attempt:" not in users[0]
    assert blurb.attempt == 1
    users.clear()
    write_and_verify(ch, sheet, fake, prompts_dir=PROMPTS)
    assert "Do not say" not in users[0]


def test_the_retry_still_hears_the_used_words(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "median")
    users = []

    def fake(system, user, model):
        if model.__name__ == "VerifyOut":
            # Attempt 1 fails for an unsupported sentence, not for a page word.
            return VerifyOut(verdicts=[Verdict(index=0, supported=len(users) > 1, reason="not in facts"),
                                       Verdict(index=1, supported=True, reason="ok")])
        users.append(user)
        return _good_writer_out()

    write_and_verify(ch, sheet, fake, prompts_dir=PROMPTS, used_words={"lucky"})
    assert len(users) == 2
    assert "Sentence 0: not in facts" in users[1]
    assert "Do not say 'lucky'. Another chapter of this page already does." in users[1]


def _open_odds_fact(sheet, ch):
    """The first odds fact in the chapter that holds a percent: a team with the playoff odds still open."""
    fid = next(f for f in ch.fact_ids if f.startswith("ODDS.") and not f.endswith(".why") and sheet.facts[f].numbers)
    return fid, sheet.facts[fid]


def test_an_odds_number_with_no_kind_fails(fixture_raw_dir, fixture_history_root):
    sheet, ch = _rankings(fixture_raw_dir, fixture_history_root)
    fid, fact = _open_odds_fact(sheet, ch)
    number = fact.numbers[0]
    b = _blurb("rankings", _tagged(f"A loss means {number}%.", 1, fid))
    assert f"[0] odds number {number} needs 'playoff odds' or 'bye odds' in the same sentence" in code_check(
        b, ch, sheet, prompts_dir=PROMPTS)


def test_an_odds_number_with_its_kind_passes(fixture_raw_dir, fixture_history_root):
    sheet, ch = _rankings(fixture_raw_dir, fixture_history_root)
    fid, fact = _open_odds_fact(sheet, ch)
    b = _blurb("rankings", _tagged(f"The playoff odds sit at {fact.numbers[0]}%.", 1, fid))
    assert not any("odds number" in m for m in code_check(b, ch, sheet, prompts_dir=PROMPTS))


def _story_recap():
    return _blurb(
        "recap_3",
        _s("Amon-Ra Dawg Your Team led by 12.24 after the early Sunday games, then Monday night flipped it.",
           "M3.turn", "M3.lead"),
        _s("Drake Maye put up 23.8 on Monday, and Maye d'force B with U won.", "M3.turn", "M3.result"),
        _s("The lead changed hands on Monday night.", "M3.lead"),
    )


def test_the_code_check_accepts_a_recap_that_cites_the_game_story_facts(story_bundle):
    sheet = story_bundle.sheet
    assert code_check(_story_recap(), _ch(sheet, "recap_3"), sheet, prompts_dir=PROMPTS) == []


def test_the_code_check_accepts_the_clock_of_a_hurt_fact(story_bundle):
    sheet = story_bundle.sheet
    blurb = _blurb(
        "recap_5",
        _s("Ladd McConkey was hurt with 3:06 left in the 1st quarter.", "M5.hurt.11635"),
        _s("He played 8 of 68 snaps.", "M5.snaps.11635"),
        _s("London Cooking cruised anyway.", "M5.result"),
    )
    assert code_check(blurb, _ch(sheet, "recap_5"), sheet, prompts_dir=PROMPTS) == []


def test_write_and_verify_keeps_a_recap_that_cites_the_game_story_facts(story_bundle):
    sheet = story_bundle.sheet
    recap = _story_recap()
    writer = FakeWriter([WriterOut(sentences=recap.sentences),
                         VerifyOut(verdicts=[Verdict(index=i, supported=True, reason="ok") for i in range(3)])])
    blurb, results = write_and_verify(_ch(sheet, "recap_3"), sheet, partial(claude_call, writer=writer),
                                      prompts_dir=PROMPTS)
    assert not blurb.fallback and results[0].passed and len(writer.calls) == 2


def test_a_recap_that_holds_a_turn_fact_and_does_not_cite_it_fails(story_bundle):
    sheet = story_bundle.sheet
    blurb = _blurb(
        "recap_3",
        _s("Maye d'force B with U beat Amon-Ra Dawg Your Team 113.55 to 104.04.", "M3.result"),
        _s("The lead changed hands on Monday night.", "M3.lead"),
    )
    assert code_check(blurb, _ch(sheet, "recap_3"), sheet, prompts_dir=PROMPTS) == [
        "[0] the chapter holds the turn fact M3.turn; cite it and tell the turn"]



def test_verifier_prompt_gates_a_rank_or_a_comparison_on_one_fact():
    from importlib import resources

    text = resources.files("cornerstone.prompts").joinpath("verifier.md").read_text(encoding="utf-8")
    assert ("- A rank, a superlative, or a comparison must be stated in one cited fact. "
            "Do not compute it by comparing facts.") in text
    assert ('"The most", "the bottom", "topped everyone", "swept the board", "a full game in the standings" '
            "are unsupported unless one fact says so.") in text
    assert "A sentence may use any listed fact, cited or not." in text


def test_a_sentence_with_three_numbers_fails(hbundle):
    sheet = hbundle.sheet
    ch = _ch(sheet, "median")
    b = _blurb("median", _s("Brock ‘N’ Roll sits 6th at 6-6 with 59% playoff odds.", "S.6", "ODDS.1"))
    assert "[0] the sentence holds 3 numbers; the limit is two" in code_check(b, ch, sheet, prompts_dir=PROMPTS)


def test_a_record_and_a_percent_pass_as_two_numbers(hbundle):
    sheet = hbundle.sheet
    ch = _ch(sheet, "median")
    b = _blurb("median", _s("Brock ‘N’ Roll sits at 6-6 with 59% playoff odds.", "S.6", "ODDS.1"))
    failures = code_check(b, ch, sheet, prompts_dir=PROMPTS)
    assert not any("numbers; the limit is two" in m for m in failures), failures
