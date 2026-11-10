"""
Tests for the Jev check of the weekly build: one request per checked attempt, one question per sentence, and the
answers saved in verify.json. They drive run_build on the week 6 fixtures with FakeJev, so no test calls TypeSafe.
"""
import ast
import logging
import re
import shutil
from datetime import datetime
from pathlib import Path

import pytest
from cpc import cpc_client
from fakes import FakeJev, fixture_nflverse, no_claims, no_news

from cornerstone.pipeline import read_verify, run_build
from cornerstone.sheet import read_bundle
from facts.writer import RefusalError, load_prompt, with_terms
from league.jev import TypeSafeJev
from league.jev_port import ChoiceQuestion, JevError, NoulQuestion
from league.models import Sentence, Verdict, VerifyOut
from league.paths import week_dir
from week.median import median_terms

# A sentence line of the verifier prompt, such as "0. Text [ids: X]".
VERIFY_LINE = re.compile(r"^\d+\. ", re.MULTILINE)


def _call(system, user, model):
    """A Claude stand-in: two sentences that cite the first chapter fact, and one supported verdict per sentence."""
    if model.__name__ == "VerifyOut":
        count = len(VERIFY_LINE.findall(user))
        return VerifyOut(verdicts=[Verdict(index=i, supported=True, reason="ok") for i in range(count)])
    fid = re.search(r"^- ([A-Z][\w.]*): ", user, re.MULTILINE).group(1)
    return model(sentences=[Sentence(text="Fact sentence alpha.", fact_ids=[fid]),
                            Sentence(text="Fact sentence beta.", fact_ids=[fid])])


@pytest.fixture
def offline(tmp_path_factory):
    return {"news": no_news, "fetch_bytes": lambda url: None,
            "nflverse": fixture_nflverse(tmp_path_factory.mktemp("nflverse")), "research": no_claims}


def _build(tmp_path, fixture_raw_dir, offline, jev, call=_call):
    shutil.copytree(fixture_raw_dir, week_dir(tmp_path, 2026, 6) / "raw")
    run_build(tmp_path, 2026, 6, call, fetch=False, **offline, client=cpc_client(at=tmp_path), jev=jev)
    return read_verify(week_dir(tmp_path, 2026, 6) / "verify.json")


def test_each_checked_attempt_saves_its_sentences_and_one_jev_answer_per_sentence(tmp_path, fixture_raw_dir, offline):
    # AT-1 and AT-5: one request per attempt that passed the code check, with one question per sentence.
    jev = FakeJev(yes=0.75)
    verify = _build(tmp_path, fixture_raw_dir, offline, jev)
    checked = [r for results in verify.chapters.values() for r in results if not r.code_failures]
    assert checked
    assert len(jev.requests) == len(checked)
    for result, request in zip(checked, jev.requests, strict=True):
        assert result.sentences == ["Fact sentence alpha.", "Fact sentence beta."]
        assert len(request.questions) == len(result.sentences)
        assert result.jev is not None and result.jev.model == FakeJev.MODEL
        assert [(a.index, a.yes) for a in result.jev.answers] == [(0, 0.75), (1, 0.75)]
        assert result.jev.error is None


def test_the_state_holds_every_chapter_fact_and_the_vocabulary_of_the_client(tmp_path, fixture_raw_dir, offline):
    # AT-6: Jev reads the same facts and the same stat terms that the Claude verifier reads.
    jev = FakeJev()
    verify = _build(tmp_path, fixture_raw_dir, offline, jev)
    client = cpc_client(at=tmp_path)
    chapters = {c.key: c for c in read_bundle(week_dir(tmp_path, 2026, 6) / "facts.json").sheet.chapters}
    checked = [r for results in verify.chapters.values() for r in results if not r.code_failures]
    vocabulary = with_terms(load_prompt(client.voice_dir, "vocabulary.md"), median_terms(client))
    terms = re.findall(r"^- \*\*(.+?)\*\*: (.+)$", vocabulary, re.MULTILINE)
    assert ("median game" in dict(terms)) is client.settings.median_game
    for result, request in zip(checked, jev.requests, strict=True):
        assert set(chapters[result.chapter].fact_ids) <= set(request.state["facts"])
        assert request.state["vocabulary"] == dict(terms)
        assert request.state["blurb"] == result.sentences


def test_the_state_holds_the_rule_lines_of_the_vocabulary(tmp_path, fixture_raw_dir, offline):
    # Story 8: Jev reads the same rules that Claude reads, such as the preamble rule and the banned words.
    jev = FakeJev()
    _build(tmp_path, fixture_raw_dir, offline, jev)
    assert jev.requests
    for request in jev.requests:
        rules = request.state["rules"]
        assert any("Each term means exactly what its line says." in rule for rule in rules)
        assert any(rule.startswith("Never write these words: best, star,") for rule in rules)
        assert not any(rule.startswith(("- **", "#")) for rule in rules)


def _code_failure_first(chapter_title):
    """A Claude stand-in whose first blurb of one chapter says "two", which no fact holds, so it fails the code check.
    Every other blurb is the plain one of `_call`."""
    first = [True]

    def call(system, user, model):
        if model.__name__ != "VerifyOut" and f"Chapter: {chapter_title}" in user and first[0]:
            first[0] = False
            fid = re.search(r"^- ([A-Z][\w.]*): ", user, re.MULTILINE).group(1)
            return model(sentences=[Sentence(text="Fact sentence alpha.", fact_ids=[fid]),
                                    Sentence(text="Fact sentence two.", fact_ids=[fid])])
        return _call(system, user, model)
    return call


def test_an_attempt_with_a_code_failure_has_no_jev_check(tmp_path, fixture_raw_dir, offline):
    # AT-4: a code failure skips the Jev check, as it skips the Claude check. The retry gets its own Jev check.
    shutil.copytree(fixture_raw_dir, week_dir(tmp_path, 2026, 6) / "raw")
    client = cpc_client(at=tmp_path)
    run_build(tmp_path, 2026, 6, _call, fetch=False, **offline, client=client, jev=FakeJev())
    awards = next(c for c in read_bundle(week_dir(tmp_path, 2026, 6) / "facts.json").sheet.chapters
                  if c.key == "awards")
    jev = FakeJev()
    run_build(tmp_path, 2026, 6, _code_failure_first(awards.title), fetch=False, **offline, client=client, jev=jev)
    first, second = read_verify(week_dir(tmp_path, 2026, 6) / "verify.json").chapters["awards"]
    assert first.code_failures and first.jev is None
    assert first.sentences == ["Fact sentence alpha.", "Fact sentence two."]
    assert not second.code_failures and second.jev is not None
    assert [r.state["blurb"] for r in jev.requests].count(first.sentences) == 0


@pytest.mark.parametrize(("supported", "yes"), [(True, 0.0), (False, 1.0)])
def test_passed_follows_the_claude_verdicts_only(tmp_path, fixture_raw_dir, offline, supported, yes):
    # AT-2 in a test: a "no" from Jev never fails a blurb, and a "yes" from Jev never passes one.
    def call(system, user, model):
        if model.__name__ == "VerifyOut":
            count = len(VERIFY_LINE.findall(user))
            return VerifyOut(verdicts=[Verdict(index=i, supported=supported, reason="r") for i in range(count)])
        return _call(system, user, model)

    verify = _build(tmp_path, fixture_raw_dir, offline, FakeJev(yes=yes), call)
    checked = [r for results in verify.chapters.values() for r in results if not r.code_failures]
    assert checked
    for result in checked:
        assert result.passed is supported
        assert {a.yes for a in result.jev.answers} == {yes}


def test_a_failed_claude_check_keeps_the_sentences_and_the_jev_answers_of_its_attempt(
        tmp_path, fixture_raw_dir, offline):
    # A Claude check that raises fails the attempt, and the attempt still keeps its sentences and its Jev answers.
    def call(system, user, model):
        if model.__name__ == "VerifyOut":
            raise RefusalError("refused")
        return _call(system, user, model)

    jev = FakeJev(yes=0.75)
    verify = _build(tmp_path, fixture_raw_dir, offline, jev, call)
    failed = [r for results in verify.chapters.values() for r in results
              if r.code_failures and r.code_failures[0].startswith("verifier error")]
    assert failed
    assert len(failed) == len(jev.requests)
    for result in failed:
        assert not result.passed
        assert result.sentences == ["Fact sentence alpha.", "Fact sentence beta."]
        assert result.jev is not None and result.jev.model == FakeJev.MODEL
        assert [(a.index, a.yes) for a in result.jev.answers] == [(0, 0.75), (1, 0.75)]


def _build_into(root, fixture_raw_dir, offline, jev):
    """One build of week 6 into `root` at a set clock, so two builds differ only by their Jev."""
    shutil.copytree(fixture_raw_dir, week_dir(root, 2026, 6) / "raw")
    started = datetime.fromisoformat("2026-10-20T11:58:00-04:00")
    page = run_build(root, 2026, 6, _call, fetch=False, **offline, started=started, client=cpc_client(at=root),
                     jev=jev)
    directory = week_dir(root, 2026, 6)
    return (page.read_text(encoding="utf-8"), (directory / "blurbs.json").read_text(encoding="utf-8"),
            read_verify(directory / "verify.json"))


def test_a_failed_jev_call_records_its_error_and_leaves_the_build_as_it_is(
        tmp_path, fixture_raw_dir, offline, caplog):
    # AT-3 in a test: a failed call logs one warning per checked attempt, and the blurbs, `passed`, and the page
    # are the same as in a build where every Jev call answers.
    page, blurbs, verify = _build_into(tmp_path / "ok", fixture_raw_dir, offline, FakeJev())
    error = JevError("TypeSafeError: No API key was provided.")
    with caplog.at_level(logging.WARNING, logger="facts.verifier"):
        failed_page, failed_blurbs, failed_verify = _build_into(tmp_path / "failed", fixture_raw_dir, offline,
                                                                FakeJev(error=error))
    checked = [r for results in failed_verify.chapters.values() for r in results if not r.code_failures]
    assert checked
    for result in checked:
        assert result.jev is not None and result.jev.error == str(error)
        assert result.jev.answers == [] and result.jev.model is None
    warnings = [r.getMessage() for r in caplog.records if "Jev check failed" in r.getMessage()]
    assert len(warnings) == len(checked)
    assert all(str(error) in w for w in warnings)
    assert failed_blurbs == blurbs
    assert failed_page == page
    passed = {k: [r.passed for r in v] for k, v in verify.chapters.items()}
    assert {k: [r.passed for r in v] for k, v in failed_verify.chapters.items()} == passed


def _jev_lines(caplog):
    return [r.getMessage() for r in caplog.records
            if r.name == "cornerstone.pipeline" and r.getMessage().startswith("Jev:")]


def test_the_build_log_has_one_jev_line_with_the_checks_the_errors_and_the_tokens(
        tmp_path, fixture_raw_dir, offline, caplog):
    # AT-7 in a test: the count of checks equals the attempts with a `jev`, and FakeJev counts 100 tokens a question.
    with caplog.at_level(logging.INFO, logger="cornerstone.pipeline"):
        _, _, verify = _build_into(tmp_path / "ok", fixture_raw_dir, offline, FakeJev())
    checks = [r.jev for results in verify.chapters.values() for r in results if r.jev is not None]
    tokens = sum(c.input_tokens or 0 for c in checks)
    assert checks and tokens == 100 * sum(len(c.answers) for c in checks)
    assert _jev_lines(caplog) == [f"Jev: {len(checks)} checks, 0 errors, {tokens} input tokens"]


def test_the_jev_line_counts_each_failed_call_as_an_error_with_no_tokens(tmp_path, fixture_raw_dir, offline, caplog):
    with caplog.at_level(logging.INFO, logger="cornerstone.pipeline"):
        _, _, verify = _build_into(tmp_path / "failed", fixture_raw_dir, offline, FakeJev(error=JevError("timeout")))
    count = sum(r.jev is not None for results in verify.chapters.values() for r in results)
    assert count
    assert _jev_lines(caplog) == [f"Jev: {count} checks, {count} errors, 0 input tokens"]


def test_an_old_verify_file_loads_with_no_sentences_and_no_jev(tmp_path):
    # AT-8: a file of the shape before the Jev check, and a version 1 file, still load.
    attempt = '{"chapter": "median", "code_failures": [], "verdicts": [], "passed": true}'
    today = tmp_path / "verify.json"
    today.write_text('{"build": {"started": "2026-10-20T11:58:00-04:00", "sources": {"history": true}},'
                     f' "chapters": {{"median": [{attempt}]}}}}')
    version_1 = tmp_path / "verify-1.json"
    version_1.write_text(f'{{"median": [{attempt}]}}')
    for path in (today, version_1):
        [result] = read_verify(path).chapters["median"]
        assert result.passed and result.sentences is None and result.jev is None


def test_the_adapter_with_no_key_raises_the_one_jev_error_and_calls_no_network(monkeypatch):
    # The SDK reads the key when the adapter makes its client, so a missing key fails before any request.
    monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)
    question = NoulQuestion(instructions="Is the sky blue?", yes="It is blue.", no="It is another color.")
    with pytest.raises(JevError, match="API key"):
        TypeSafeJev().ask({"sky": "blue"}, {"blue": question})


@pytest.mark.live
def test_the_adapter_answers_one_noul_from_the_live_api():
    # A live test: it calls TypeSafe with TYPESAFE_API_KEY. Run it on purpose with `uv run pytest -m live`.
    question = NoulQuestion(instructions="Does `sky` say the sky is blue?", yes="It says blue.", no="It says gray.")
    answers = TypeSafeJev().ask({"sky": "The sky is blue today."}, {"blue": question})
    assert answers.model.startswith("jev-")
    assert 0.5 < answers.nouls["blue"] <= 1


def test_only_the_adapter_in_the_league_package_imports_the_sdk():
    # AT-10: every other module reaches Jev through the port, so a change of vendor touches one file.
    repo = Path(__file__).resolve().parents[3]
    sources = [*repo.glob("apps/*/src/**/*.py"), *repo.glob("packages/*/python/src/**/*.py")]
    importers = []
    for path in sources:
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            names = ([alias.name for alias in node.names] if isinstance(node, ast.Import)
                     else [node.module or ""] if isinstance(node, ast.ImportFrom) else [])
            if any(name.split(".")[0] == "typesafe_sdk" for name in names):
                importers.append(path.relative_to(repo).as_posix())
    assert importers == ["packages/league/python/src/league/jev.py"]


@pytest.mark.live
def test_the_adapter_answers_one_choice_and_one_noul_in_one_live_request():
    # A live test: it calls TypeSafe with TYPESAFE_API_KEY. The route of the front door asks a Choice and Nouls together.
    color = ChoiceQuestion(instructions="Which color does `sky` give the sky?",
                           options={"blue": "The sky is blue.", "gray": "The sky is gray."})
    clear = NoulQuestion(instructions="Does `sky` say the sky is clear?", yes="It says clear.", no="It says cloudy.")
    answers = TypeSafeJev().ask({"sky": "The sky is blue and clear today."}, {"color": color, "clear": clear})
    assert max(answers.choices["color"], key=answers.choices["color"].get) == "blue"
    assert set(answers.nouls) == {"clear"}
