"""
Checks every blurb sentence against its cited facts, in code and with a second Claude call.
A failed blurb is rewritten once with feedback, then replaced by a template sentence.
"""
import logging
import re
from importlib import resources

import anthropic
from pydantic import ValidationError

from cornerstone.models import (
    Blurb,
    Chapter,
    FactSheet,
    Verdict,
    VerifyOut,
    VerifyResult,
)
from cornerstone.sheet import NUMBER_TOKEN
from cornerstone.writer import ClaudeCall, RefusalError, template_blurb, write_blurb

log = logging.getLogger(__name__)

# Gated words need a cited fact ID that contains one of the markers.
GATED_WORDS: list[tuple[list[str], tuple[str, ...]]] = [
    (["decided", "decider", "decide"], (".driver",)),
    (["upset"], (".upset",)),
    (["recent add", "lucky", "waiver add", "free agent add"], (".move.", "W.adds")),
    (["because", "thanks to", "cost", "sank", "carried"], (".driver", ".swing")),
]
NAME_SUFFIXES = {"jr.", "sr.", "ii", "iii", "iv"}


def _normalize(number: str) -> str:
    number = number.replace(",", "")
    return number[:-2] if number.endswith(".0") else number


def _whole_word(word: str, text: str) -> bool:
    return re.search(rf"(?<!\w){re.escape(word)}(?!\w)", text, re.IGNORECASE) is not None


def _banned_words() -> list[str]:
    text = resources.files("cornerstone.prompts").joinpath("vocabulary.md").read_text(encoding="utf-8")
    line = text.split("## Banned words", 1)[1].strip().splitlines()[0]
    return [w.strip().rstrip(".") for w in line.split(":", 1)[1].split(",")]


def _remove_names(text: str, names: list[str]) -> str:
    # Longest first, so "Tre Tucker" goes before any shorter name inside it.
    for name in sorted(names, key=len, reverse=True):
        text = text.replace(name, " ")
    return text


def _last_name(full: str) -> str | None:
    parts = [p for p in full.split() if p.lower() not in NAME_SUFFIXES]
    last = parts[-1] if parts else ""
    # Skip short names and odd entries such as "96 (?)": they cause false matches.
    return last if len(last) > 3 and last.isalpha() else None


def _week_numbers(sheet: FactSheet) -> set[str]:
    week = sheet.facts.get("W.week")
    if week is None:
        return set()
    number = int(week.numbers[0])
    return {str(number), str(number + 1)}


def code_check(blurb: Blurb, chapter: Chapter, sheet: FactSheet) -> list[str]:
    failures: list[str] = []
    in_chapter = set(chapter.fact_ids)
    league_teams = {t for f in sheet.facts.values() for t in f.teams}
    league_players = {p for c in sheet.chapters for p in c.scope_players}
    scope_names = [*chapter.scope_teams, *chapter.scope_players]
    in_scope_last = {_last_name(p) for p in chapter.scope_players}
    banned = _banned_words()
    always_allowed = _week_numbers(sheet)

    for i, sentence in enumerate(blurb.sentences):
        valid_ids = []
        for fid in sentence.fact_ids:
            if fid in sheet.facts and fid in in_chapter:
                valid_ids.append(fid)
            else:
                failures.append(f"[{i}] fact ID {fid} is not in this chapter")
        cited = {_normalize(n) for fid in valid_ids for n in sheet.facts[fid].numbers}

        # Digits inside a name ("Pukancun on 3") are not numbers.
        bare = _remove_names(sentence.text, scope_names)
        for token in NUMBER_TOKEN.findall(bare):
            number = _normalize(token)
            if number not in cited and number not in always_allowed:
                failures.append(
                    f"[{i}] number {token} is not in the cited facts {', '.join(sentence.fact_ids)}"
                )

        for team in sorted(league_teams - set(chapter.scope_teams)):
            if team in bare:
                failures.append(f"[{i}] team {team} is not in this chapter")

        for player in sorted(league_players - set(chapter.scope_players)):
            last = _last_name(player)
            # A last name shared with an in-scope player is ambiguous, so it passes.
            if player in bare or (last and last not in in_scope_last and _whole_word(last, bare)):
                failures.append(f"[{i}] player {player} is not on a team in this chapter")

        # Names are stripped first: a team called "Lucky Lambs" is not the word "lucky".
        for word in banned:
            if _whole_word(word, bare):
                failures.append(f"[{i}] banned word '{word}'")

        for words, markers in GATED_WORDS:
            for word in words:
                if _whole_word(word, bare) and not any(
                    m in fid for fid in sentence.fact_ids for m in markers
                ):
                    needs = " or ".join(markers)
                    failures.append(f"[{i}] '{word}' needs a cited {needs} fact")

    count = len(blurb.sentences)
    if not chapter.min_sentences <= count <= chapter.max_sentences:
        failures.append(
            f"[0] {count} sentences; the range is {chapter.min_sentences} to {chapter.max_sentences}"
        )
    return failures


def build_verifier_prompt(blurb: Blurb, chapter: Chapter, sheet: FactSheet) -> tuple[str, str]:
    system = resources.files("cornerstone.prompts").joinpath("verifier.md").read_text(encoding="utf-8").strip()
    # The verifier sees every chapter fact, cited or not, so a true claim with a missed
    # citation is not judged false. Facts outside the chapter never reach it.
    lines = [
        f"Chapter: {chapter.title}",
        "",
        "Chapter facts:",
        *(f"- {fid}: {sheet.facts[fid].text}" for fid in chapter.fact_ids if fid in sheet.facts),
        "",
        "Sentences. Give one verdict per sentence, in order:",
        *(
            f"{i}. {s.text} [ids: {', '.join(s.fact_ids)}]"
            for i, s in enumerate(blurb.sentences)
        ),
    ]
    return system, "\n".join(lines)


def claude_verify(
    blurb: Blurb, chapter: Chapter, sheet: FactSheet, call: ClaudeCall
) -> list[Verdict]:
    system, user = build_verifier_prompt(blurb, chapter, sheet)
    verdicts = call(system, user, VerifyOut).verdicts
    n, m = len(verdicts), len(blurb.sentences)
    if n != m:
        reason = f"verifier returned {n} verdicts for {m} sentences"
        return [Verdict(index=i, supported=False, reason=reason) for i in range(m)]
    return verdicts


def verify_blurb(
    blurb: Blurb, chapter: Chapter, sheet: FactSheet, call: ClaudeCall
) -> VerifyResult:
    failures = code_check(blurb, chapter, sheet)
    # A code failure is final, so skip the paid Claude call.
    if failures:
        return VerifyResult(chapter=chapter.key, code_failures=failures, verdicts=[], passed=False)
    verdicts = claude_verify(blurb, chapter, sheet, call)
    return VerifyResult(
        chapter=chapter.key,
        code_failures=[],
        verdicts=verdicts,
        passed=all(v.supported for v in verdicts),
    )


def _feedback(result: VerifyResult) -> str:
    return "\n".join(
        [
            *result.code_failures,
            *(f"Sentence {v.index}: {v.reason}" for v in result.verdicts if not v.supported),
        ]
    )


def write_and_verify(
    chapter: Chapter, sheet: FactSheet, call: ClaudeCall
) -> tuple[Blurb, list[VerifyResult]]:
    results: list[VerifyResult] = []
    feedback: str | None = None
    for _ in range(2):
        try:
            blurb = write_blurb(chapter, sheet, call, feedback)
        except (RefusalError, anthropic.APIError) as err:
            # A writer error is a failed attempt, not a crash of the whole report.
            log.warning("writer failed for %s: %s", chapter.key, err)
            result = VerifyResult(
                chapter=chapter.key,
                code_failures=[f"writer error: {err}"],
                verdicts=[],
                passed=False,
            )
        else:
            try:
                result = verify_blurb(blurb, chapter, sheet, call)
            except (RefusalError, anthropic.APIError, ValidationError) as err:
                # One bad verifier response must degrade to the template, not crash the build.
                log.warning("verifier failed for %s: %s", chapter.key, err)
                result = VerifyResult(
                    chapter=chapter.key,
                    code_failures=[f"verifier error: {err}"],
                    verdicts=[],
                    passed=False,
                )
            if result.passed:
                results.append(result)
                return blurb, results
        results.append(result)
        feedback = _feedback(result)
    return template_blurb(chapter, sheet), results
