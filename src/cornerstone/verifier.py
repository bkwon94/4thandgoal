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
from cornerstone.writer import ClaudeCall, RefusalError, WriterError, template_blurb, write_blurb

log = logging.getLogger(__name__)

# A trade swing fact lets the writer say "decided" or a cause word only when its gap is at least
# the margin in the direction of the result. The fact text says so with one of these phrases.
TRADE_SWING_ID = re.compile(r"T\d+\.\d+\.swing")
SWING_AT_LEAST_MARGIN = ("above the margin", "equal to the margin")
DECIDED_WORDS = ["decided", "decider", "decide"]
# Gated words need a cited fact ID that contains one of the markers.
GATED_WORDS: list[tuple[list[str], tuple[str, ...]]] = [
    (DECIDED_WORDS, (".driver",)),
    (["upset"], (".upset",)),
    (["recent add", "lucky", "waiver add", "free agent add"], (".move.", "W.adds")),
    (["because", "thanks to", "cost", "sank", "carried"], (".driver", ".swing", ".dropswing")),
]
GRADE_LETTERS = {"A", "B", "C", "D", "F"}
NAME_SUFFIXES = {"jr.", "sr.", "ii", "iii", "iv"}
# A number written as a word escapes the digit check, so it must come from a cited fact's text.
# "one" is left out: it is too common as a pronoun.
NUMBER_WORDS = [
    "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven",
    "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen",
    "nineteen", "twenty", "dozen",
]


def _normalize(number: str) -> str:
    number = number.replace(",", "")
    return number[:-2] if number.endswith(".0") else number


def _numbers(fids: list[str], sheet: FactSheet) -> set[str]:
    return {_normalize(n) for fid in fids for n in sheet.facts[fid].numbers}


def _is_trade_value(fid: str) -> bool:
    # Only the T facts carry a trade value; MED.value and D.*.value are other values.
    return fid.startswith("T") and fid.endswith(".value")


def _whole_word(word: str, text: str) -> bool:
    return re.search(rf"(?<!\w){re.escape(word)}(?!\w)", text, re.IGNORECASE) is not None


def _banned_words() -> list[str]:
    text = resources.files("cornerstone.prompts").joinpath("vocabulary.md").read_text(encoding="utf-8")
    line = text.split("## Banned words", 1)[1].strip().splitlines()[0]
    return [w.strip().rstrip(".") for w in line.split(":", 1)[1].split(",")]


def _remove_names(text: str, names: list[str]) -> str:
    # Longest first, so "Tre Tucker" goes before any shorter name inside it. Whole words only,
    # so an odd name such as "0" does not remove the digit from "100".
    for name in sorted(names, key=len, reverse=True):
        text = re.sub(rf"(?<!\w){re.escape(name)}(?!\w)", " ", text)
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


def _decisive_swing(fid: str, sheet: FactSheet) -> bool:
    """True for a trade swing fact whose gap, in the direction of the result, is at least the margin."""
    fact = sheet.facts.get(fid)
    return bool(TRADE_SWING_ID.fullmatch(fid) and fact and any(w in fact.text for w in SWING_AT_LEAST_MARGIN))


def _opens_gate(fid: str, word: str, markers: tuple[str, ...], sheet: FactSheet) -> bool:
    """True when a cited fact lets the sentence use a gated word.

    A trade swing fact opens a gate only when it is decisive, so a swing against the result
    never lets the writer say the trade decided or cost the game.
    """
    if TRADE_SWING_ID.fullmatch(fid):
        return (word in DECIDED_WORDS or ".swing" in markers) and _decisive_swing(fid, sheet)
    return any(m in fid for m in markers)


def code_check(blurb: Blurb, chapter: Chapter, sheet: FactSheet) -> list[str]:
    failures: list[str] = []
    in_chapter = set(chapter.fact_ids)
    league_teams = {t for f in sheet.facts.values() for t in f.teams}
    league_players = {p for c in sheet.chapters for p in c.scope_players}
    scope_names = [*chapter.scope_teams, *chapter.scope_players]
    in_scope_last = {_last_name(p) for p in chapter.scope_players}
    banned = _banned_words()
    always_allowed = _week_numbers(sheet)
    # A trade value or a trade value sum must never reach the page, so a trade chapter bars these numbers.
    trade_value_numbers = (
        _numbers([fid for fid in chapter.fact_ids if _is_trade_value(fid) and fid in sheet.facts], sheet)
        if chapter.key.startswith("trade_") else set()
    )

    for i, sentence in enumerate(blurb.sentences):
        valid_ids = []
        for fid in sentence.fact_ids:
            if fid in sheet.facts and fid in in_chapter:
                valid_ids.append(fid)
            else:
                failures.append(f"[{i}] fact ID {fid} is not in this chapter")
        cited = _numbers(valid_ids, sheet)
        # A number that a cited fact other than a trade value holds too is no leak. A points figure is one.
        cited_not_trade_value = _numbers([fid for fid in valid_ids if not _is_trade_value(fid)], sheet)

        # Digits inside a name ("Pukancun on 3") are not numbers.
        bare = _remove_names(sentence.text, scope_names)
        for token in NUMBER_TOKEN.findall(bare):
            number = _normalize(token)
            if number not in cited and number not in always_allowed:
                failures.append(
                    f"[{i}] number {token} is not in the cited facts {', '.join(sentence.fact_ids)}"
                )
            # A week number is always allowed, so a trade value that equals one is no leak either.
            if number in trade_value_numbers and number not in cited_not_trade_value and number not in always_allowed:
                failures.append(f"[{i}] number {token} is a trade value and may not appear")

        cited_text = " ".join(sheet.facts[fid].text for fid in valid_ids)
        for word in NUMBER_WORDS:
            if _whole_word(word, bare) and not _whole_word(word, cited_text):
                failures.append(f"[{i}] number word '{word}' is not in the cited facts")

        # A fact ID belongs in fact_ids. Any bracket in the text is a leaked ID or a stray mark.
        if "[" in sentence.text:
            failures.append(f"[{i}] the text has a '[': put fact IDs in fact_ids only")

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
                    _opens_gate(fid, word, markers, sheet) for fid in sentence.fact_ids
                ):
                    needs = " or ".join(markers)
                    failures.append(f"[{i}] '{word}' needs a cited {needs} fact")

    count = len(blurb.sentences)
    if not chapter.min_sentences <= count <= chapter.max_sentences:
        failures.append(
            f"[0] {count} sentences; the range is {chapter.min_sentences} to {chapter.max_sentences}"
        )
    if chapter.grade_keys:
        failures += _grade_failures(blurb, chapter)
    return failures


def _grade_failures(blurb: Blurb, chapter: Chapter) -> list[str]:
    failures = [f"[0] grade for {k} is missing" for k in chapter.grade_keys if k not in blurb.grades]
    failures += [f"[0] grade for {k} is not a trade side" for k in blurb.grades if k not in chapter.grade_keys]
    failures += [
        f"[0] grade {k} is '{v}'; use one letter A, B, C, D, or F"
        for k, v in blurb.grades.items()
        if k in chapter.grade_keys and v not in GRADE_LETTERS
    ]
    return failures


def build_verifier_prompt(blurb: Blurb, chapter: Chapter, sheet: FactSheet) -> tuple[str, str]:
    # The vocabulary comes first so the verifier judges stat terms by the writer's definitions.
    prompts = resources.files("cornerstone.prompts")
    system = "\n\n".join(
        prompts.joinpath(name).read_text(encoding="utf-8").strip()
        for name in ("vocabulary.md", "verifier.md")
    )
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
        except (RefusalError, WriterError, ValidationError, anthropic.AnthropicError) as err:
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
            except (RefusalError, WriterError, anthropic.APIError, ValidationError) as err:
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
