"""
Tests for the verifier: the code check, the prompt, and the retry loop.
Every test injects a fake call, so none of them reach the Claude API.
"""
from cornerstone.models import Blurb, Sentence, Verdict, VerifyOut, WriterOut
from cornerstone.parse import parse_week
from cornerstone.sheet import build_bundle
from cornerstone.sleeper import load_raw
from cornerstone.verifier import (
    build_verifier_prompt,
    claude_verify,
    code_check,
    verify_blurb,
    write_and_verify,
)
from cornerstone.writer import RefusalError


def _sheet(d):
    return build_bundle(parse_week(load_raw(d)), news=lambda pid: []).sheet


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
    assert any("109.83" in m for m in code_check(b, ch, sheet))


def test_out_of_scope_player_fails(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "recap_4")
    b = _blurb("recap_4", _s("Tre Tucker had nothing to do with this.", ch.fact_ids[0]))
    assert any("Tre Tucker" in m for m in code_check(b, ch, sheet))


def test_in_scope_player_passes(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "recap_4")
    b = _blurb("recap_4", _s("Blake Corum played.", ch.fact_ids[0]), _s("Corum again.", ch.fact_ids[0]))
    assert code_check(b, ch, sheet) == []


def test_decided_needs_driver(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "recap_4")
    non_driver = next(f for f in ch.fact_ids if ".driver" not in f)
    b = _blurb("recap_4", _s("A game decided by a quarterback.", non_driver))
    assert any("decided" in m for m in code_check(b, ch, sheet))


def test_ordinal_matches_cited_number(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "next_week")
    b = _blurb("next_week", _s("Lil Fridge sits 1st.", "S.1"))
    assert code_check(b, ch, sheet) == []
    b = _blurb("next_week", _s("Lil Fridge sits 11th.", "S.1"))
    assert any("11" in m for m in code_check(b, ch, sheet))


def test_ordinal_eleventh_passes_when_cited(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "next_week")
    fid = next(f for f in ch.fact_ids if "11" in sheet.facts[f].numbers)
    team = sheet.facts[fid].teams[0]
    b = _blurb("next_week", _s(f"{team} is 11th.", fid))
    assert not any("number" in m for m in code_check(b, ch, sheet))


def test_digits_inside_team_name_are_not_numbers(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "recap_6")
    b = _blurb("recap_6", _s("Pukancun on 3 won.", "M6.result"), _s("Pukancun on 3 again.", "M6.result"))
    assert not any("number" in m for m in code_check(b, ch, sheet))


def test_week_number_is_allowed(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "median")
    b = _blurb("median", _s("In week 6 the bar rose, and week 7 is next.", "MED.value"))
    assert not any("number" in m for m in code_check(b, ch, sheet))


def test_gated_words_need_markers(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "recap_4")
    fid = ch.fact_ids[0]
    for text, word in [("An upset win.", "upset"), ("They won because of it.", "because")]:
        b = _blurb("recap_4", _s(text, fid))
        assert any(word in m for m in code_check(b, ch, sheet)), word


def test_banned_word_fails(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "recap_4")
    b = _blurb("recap_4", _s("A clutch win.", ch.fact_ids[0]))
    assert any("clutch" in m for m in code_check(b, ch, sheet))


def test_sentence_count_out_of_range_fails(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "median")
    b = _blurb("median", _s("The median was 106.83.", "MED.value"))
    assert any("sentences" in m for m in code_check(b, ch, sheet))


def test_unknown_fact_id_fails(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "median")
    b = _blurb("median", _s("The median was 106.83.", "NOPE.1"))
    assert any("NOPE.1" in m for m in code_check(b, ch, sheet))


def test_prompt_lists_chapter_facts_and_numbered_sentences(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "median")
    b = _blurb("median", _s("The median was 106.83.", "MED.value"))
    system, user = build_verifier_prompt(b, ch, sheet)
    assert "fact checker" in system
    assert "- MED.value: " in user and "0. The median was 106.83. [ids: MED.value]" in user


def test_prompt_system_has_vocabulary_then_verifier_rules(fixture_raw_dir):
    from importlib import resources

    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "median")
    b = _blurb("median", _s("The median was 106.83.", "MED.value"))
    system, _ = build_verifier_prompt(b, ch, sheet)
    rules = resources.files("cornerstone.prompts").joinpath("verifier.md").read_text(encoding="utf-8").strip()
    assert "margin driver" in system
    assert rules.splitlines()[0] in system
    assert system.index("margin driver") < system.index(rules.splitlines()[0])


def test_prompt_holds_uncited_chapter_facts_and_no_other_matchup(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "recap_4")
    uncited = next(f for f in ch.fact_ids if f not in ("M4.result", "M4.records"))
    b = _blurb("recap_4", _s("A result.", "M4.result"), _s("Records.", "M4.records", "M4.result"))
    _, user = build_verifier_prompt(b, ch, sheet)
    assert f"- {uncited}: {sheet.facts[uncited].text}" in user
    assert "- M1.result: " not in user
    assert not any(line.startswith("- M1.") for line in user.splitlines())
    assert "0. A result. [ids: M4.result]" in user
    assert "1. Records. [ids: M4.records, M4.result]" in user


def test_verdict_count_mismatch_marks_all_unsupported(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "median")
    b = _blurb("median", _s("A.", "MED.value"), _s("B.", "MED.value"))
    fake = lambda s, u, m: VerifyOut(verdicts=[Verdict(index=0, supported=True, reason="ok")])
    verdicts = claude_verify(b, ch, sheet, fake)
    assert [v.supported for v in verdicts] == [False, False]
    assert "returned 1 verdicts for 2 sentences" in verdicts[0].reason


def test_code_failure_skips_claude_call(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "median")
    b = _blurb("median", _s("Six teams cleared 109.83.", "MED.value"))

    def fake(s, u, m):
        raise AssertionError("no call expected")

    result = verify_blurb(b, ch, sheet, fake)
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

    blurb, results = write_and_verify(ch, sheet, fake)
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

    blurb, results = write_and_verify(ch, sheet, fake)
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

    blurb, results = write_and_verify(ch, sheet, fake)
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

    blurb, results = write_and_verify(ch, sheet, fake)
    assert not blurb.fallback and len(results) == 2
    assert "Sentence 0: bad claim" in users[1]


def test_verifier_error_falls_back(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "median")

    def fake(system, user, model):
        if model.__name__ == "VerifyOut":
            raise RefusalError("refused")
        return _good_writer_out()

    blurb, results = write_and_verify(ch, sheet, fake)
    assert blurb.fallback and len(results) == 2
    assert results[0].code_failures[0].startswith("verifier error")


def test_gated_word_inside_team_name_passes(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "recap_4").model_copy(deep=True)
    ch.scope_teams.append("Lucky Lambs")
    b = _blurb("recap_4", _s("Lucky Lambs played.", ch.fact_ids[0]), _s("Again.", ch.fact_ids[0]))
    assert not any("lucky" in m.lower() for m in code_check(b, ch, sheet))


def test_writer_with_no_output_twice_falls_back(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "median")

    def fake(system, user, model):
        if model.__name__ == "VerifyOut":
            raise AssertionError("no verifier call expected")
        return None

    blurb, results = write_and_verify(ch, sheet, fake)
    assert blurb.fallback and len(results) == 2
    assert all(r.code_failures[0].startswith("writer error") for r in results)


def test_writer_validation_error_is_a_failed_attempt(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "median")

    def fake(system, user, model):
        if model.__name__ == "VerifyOut":
            raise AssertionError("no verifier call expected")
        return model.model_validate({"sentences": "not a list"})

    blurb, results = write_and_verify(ch, sheet, fake)
    assert blurb.fallback and len(results) == 2


def test_name_removal_matches_whole_words(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "median").model_copy(deep=True)
    ch.scope_players.append("0")
    b = _blurb("median", _s("A team scored 100.", "MED.value"), _s("Again.", "MED.value"))
    assert any("number 100" in m for m in code_check(b, ch, sheet))


def test_number_word_not_in_fact_fails(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "recap_4")
    b = _blurb("recap_4", _s("They won by five.", "M4.result"), _s("Again.", "M4.result"))
    assert any("'five'" in m for m in code_check(b, ch, sheet))


def test_number_word_in_cited_fact_passes(fixture_raw_dir):
    def news(_player_id):
        return [{"metadata": {"description": "He scored two touchdowns."}, "published": "1792500000000"}]

    sheet = build_bundle(parse_week(load_raw(fixture_raw_dir)), news=news).sheet
    ch = _ch(sheet, "game_changer")
    b = _blurb("game_changer", _s("He scored two touchdowns.", "AW.game_changer.news"))
    assert not any("number word" in m for m in code_check(b, ch, sheet))


def test_fact_id_in_text_fails(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "recap_4")
    b = _blurb("recap_4", _s("See [M4.result].", "M4.result"), _s("Again.", "M4.result"))
    assert any("'['" in m for m in code_check(b, ch, sheet))


def test_vocabulary_has_the_history_terms():
    from importlib import resources

    text = resources.files("cornerstone.prompts").joinpath("vocabulary.md").read_text(encoding="utf-8")
    for term in ("streak", "team trend", "season high", "season low", "season average"):
        assert f"**{term}**" in text


def test_dropswing_passes_the_cost_gate(dbundle):
    sheet = dbundle.sheet
    ch = _ch(sheet, "recap_4")
    b = _blurb("recap_4", _s("The drops cost Bo Girds the game.", "M4.dropswing"))
    assert not [m for m in code_check(b, ch, sheet) if "'cost' needs" in m]


def test_drop_value_alone_fails_the_cost_gate(dbundle):
    sheet = dbundle.sheet
    ch = _ch(sheet, "recap_4")
    b = _blurb("recap_4", _s("The drops cost Bo Girds the game.", "D.12501.value"))
    assert any("'cost' needs" in m for m in code_check(b, ch, sheet))



def test_team_named_twice_fails(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "recap_4")
    b = _blurb("recap_4", _s("behold the lamb won.", "M4.result"), _s("behold the lamb again.", "M4.result"))
    line = ("[1] the blurb: team behold the lamb is named 2 times; name it once, "
            "then write 'this side', 'they', or the player names")
    assert line in code_check(b, ch, sheet)


def test_team_named_once_passes(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "recap_4")
    b = _blurb("recap_4", _s("behold the lamb won.", "M4.result"), _s("They won again.", "M4.result"))
    assert code_check(b, ch, sheet) == []


def test_second_team_named_once_passes(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "recap_4")
    b = _blurb("recap_4", _s("behold the lamb played.", "M4.result"), _s("Bo Girds played.", "M4.result"))
    assert code_check(b, ch, sheet) == []


def test_capital_second_mention_of_team_counts(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "recap_4")
    b = _blurb("recap_4", _s("They beat behold the lamb.", "M4.result"), _s("Behold the lamb lost.", "M4.result"))
    assert any(m.startswith("[1] the blurb: team behold the lamb is named 2 times") for m in code_check(b, ch, sheet))


def test_part_of_team_name_does_not_count(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "recap_4")
    b = _blurb("recap_4", _s("behold the lamb won.", "M4.result"), _s("The lamb ate.", "M4.result"))
    assert not any("is named" in m for m in code_check(b, ch, sheet))


def test_team_name_with_punctuation_named_twice_fails(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "recap_1")
    b = _blurb("recap_1", _s("Brock ‘N’ Roll won.", "M1.result"), _s("Brock ‘N’ Roll again.", "M1.result"))
    assert any(m.startswith("[1] the blurb: team Brock ‘N’ Roll is named 2 times") for m in code_check(b, ch, sheet))


def test_twelve_team_chapter_skips_the_repeat_check(fixture_raw_dir):
    sheet = _sheet(fixture_raw_dir)
    ch = _ch(sheet, "next_week")
    b = _blurb("next_week", _s("Lil Fridge sits 1st.", "S.1"), _s("Lil Fridge plays next.", "S.1"))
    assert not any("is named" in m for m in code_check(b, ch, sheet))
