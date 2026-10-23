"""
Checks every blurb sentence against its cited facts, in code and with a second Claude call.
A failed blurb is rewritten once with feedback, then replaced by a template sentence.
"""
import logging
import re
import string
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
from cornerstone.names import last_name
from cornerstone.sheet import NUMBER_TOKEN, RANKINGS_CHAPTER, two_team_chapter
from cornerstone.writer import ClaudeCall, RefusalError, WriterError, template_blurb, write_blurb

log = logging.getLogger(__name__)

DECIDED_WORDS = ["decided", "decider", "decide"]
# Gated words need a cited fact ID that contains one of the markers.
GATED_WORDS: list[tuple[list[str], tuple[str, ...]]] = [
    (DECIDED_WORDS + ["won it", "blew it"], (".driver",)),
    (["upset"], (".upset",)),
    (["recent add", "lucky", "waiver add", "free agent add", "new pickup"], (".move.", "W.adds")),
    (["because", "thanks to", "cost", "sank", "carried"], (".driver", ".swing", ".dropswing")),
]
# A number written as a word escapes the digit check, so it must come from a cited fact's text.
# "one" is left out: it is too common as a pronoun.
NUMBER_WORDS = [
    "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven",
    "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen",
    "nineteen", "twenty", "dozen",
]
# A reaction sentence cites no fact, so it must be too short to hide a claim.
REACTION_WORD_LIMIT = 8
# The comma may have no space or a capital "Which"; the \b keeps "whichever" out.
WHICH_TAIL = re.compile(r",\s*which\b", re.IGNORECASE)
# Each chapter is one call, so a page-wide cap on this closer cannot hold. The closer is banned outright.
AND_THATS_TAIL = re.compile(r",\s*and that(?:'|’)?s\b[^,]*$", re.I)
# Two rankings teams whose first sentences share this many opening words read as one stock row.
OPENER_WORDS = 3
# The writer uses curly quotes and dashes, so the plain ASCII set alone misses them.
OPENER_PUNCTUATION = string.punctuation + "“”‘’—"
# A blurb this long needs one sentence with no number, so the prose does not read as a stat sheet.
NUMBERLESS_MIN_SENTENCES = 3
# A number that is read with a vowel sound: 8, 8.13, 80 to 89, 800, 11, 18, 11-1.
# 110 and 180 read "a hundred and ...", so they keep "a".
VOWEL_SOUND_NUMBER = r"8(?:[\d,.]*\d)?|1[18](?:\.\d+)?(?![\d,])"
A_BEFORE_VOWEL_NUMBER = re.compile(rf"(?<!\w)a\s+({VOWEL_SOUND_NUMBER})", re.IGNORECASE)
# "an" before any number; the number then must be one read with a vowel sound.
AN_BEFORE_NUMBER = re.compile(r"(?<!\w)an\s+(\d(?:[\d,.]*\d)?)", re.IGNORECASE)


def normalize_number(number: str) -> str:
    number = number.replace(",", "")
    return number[:-2] if number.endswith(".0") else number


def _numbers(fids: list[str], sheet: FactSheet) -> set[str]:
    return {normalize_number(n) for fid in fids for n in sheet.facts[fid].numbers}


def _whole_pattern(word: str) -> str:
    """The regex for a word or a phrase as a whole, with no word character on either side."""
    return rf"(?<!\w){re.escape(word)}(?!\w)"


def whole_word(word: str, text: str) -> bool:
    return re.search(_whole_pattern(word), text, re.IGNORECASE) is not None


def number_failures(bare: str, cited_numbers: set[str], cited_text: str) -> list[str]:
    """The number rule on prose with the names removed: each digit and each number word must come from the cited facts."""
    failures = [
        f"number {token} is not in the cited facts"
        for token in NUMBER_TOKEN.findall(bare)
        if normalize_number(token) not in cited_numbers
    ]
    failures += [
        f"number word '{word}' is not in the cited facts"
        for word in NUMBER_WORDS
        if whole_word(word, bare) and not whole_word(word, cited_text)
    ]
    return failures


def _banned(heading: str) -> list[str]:
    """The comma list on the line after a vocabulary heading, such as "## Banned words"."""
    text = resources.files("cornerstone.prompts").joinpath("vocabulary.md").read_text(encoding="utf-8")
    line = text.split(heading, 1)[1].strip().splitlines()[0]
    return [w.strip().rstrip(".") for w in line.split(":", 1)[1].split(",")]


def remove_names(text: str, names: list[str]) -> str:
    # Longest first, so "Tre Tucker" goes before any shorter name inside it. Whole words only,
    # so an odd name such as "0" does not remove the digit from "100".
    for name in sorted(names, key=len, reverse=True):
        text = re.sub(_whole_pattern(name), " ", text)
    return text


def team_mentions(team: str, text: str) -> int:
    """The whole-phrase mentions of a team name, in any case.

    A name that is also a common phrase, such as "behold the lamb", counts only as the full phrase.
    A capital at the start of a sentence still counts.
    """
    return len(re.findall(_whole_pattern(team), text, re.IGNORECASE))


def repeated_teams(texts: list[str], teams: list[str]) -> list[tuple[int, str, int]]:
    """Each team named more than once across the texts.

    Each item is the index of the text with the second mention, the team, and the count.
    The prose names a team once, so a second mention is a failure.
    """
    found = []
    for team in sorted(set(teams)):
        counts = [team_mentions(team, text) for text in texts]
        total = sum(counts)
        if total > 1:
            running = 0
            for i, count in enumerate(counts):
                running += count
                if running > 1:
                    found.append((i, team, total))
                    break
    return found


def repeat_failure(where: str, team: str, count: int) -> str:
    """The failure line for a team named more than once. The blurb check and the analysis check share it."""
    return (f"{where}: team {team} is named {count} times; name it once, "
            "then write 'this side', 'they', or the player names")


def _week_numbers(sheet: FactSheet) -> set[str]:
    week = sheet.facts.get("W.week")
    if week is None:
        return set()
    number = int(week.numbers[0])
    return {str(number), str(number + 1)}


def reaction_failures(text: str, scope_names: list[str], scope_last: set[str]) -> list[str]:
    """The limits on a reaction sentence: no digit, no scope name, and fewer than 8 words."""
    failures = []
    if re.search(r"\d", text):
        failures.append("a reaction sentence has a digit; cite a fact or drop the number")
    named = [n for n in scope_names if whole_word(n, text)]
    # A last name alone counts only with its capital, so "that hurts" is not Jalen Hurts.
    named += sorted(last for last in scope_last if last and re.search(_whole_pattern(last), text))
    if named:
        failures.append(f"a reaction sentence names {named[0]}; cite a fact or drop the name")
    if len(text.split()) >= REACTION_WORD_LIMIT:
        failures.append(f"a reaction sentence has {REACTION_WORD_LIMIT} or more words; keep it short or cite a fact")
    return failures


def article_failures(text: str) -> list[str]:
    """The article rule: "an", not "a", before a number read with a vowel sound, such as "an 8.13".
    Any other number takes "a", such as "a 9" or "a 110"."""
    failures = [f"write 'an {number}', not 'a {number}'" for number in A_BEFORE_VOWEL_NUMBER.findall(text)]
    failures += [
        f"write 'a {number}', not 'an {number}'"
        for number in AN_BEFORE_NUMBER.findall(text)
        if not re.fullmatch(VOWEL_SOUND_NUMBER, number)
    ]
    return failures


def numberless_failures(bares: list[str]) -> list[str]:
    """A blurb of 3 or more sentences needs one sentence with no digit. The texts have the names removed."""
    if len(bares) < NUMBERLESS_MIN_SENTENCES or not all(re.search(r"\d", b) for b in bares):
        return []
    indexes = ", ".join(str(i) for i in range(len(bares)))
    return [f"[0] every sentence has a number (sentences {indexes}); write at least one sentence with no number"]


def roster_tag_failures(blurb: Blurb, chapter: Chapter, sheet: FactSheet) -> list[str]:
    """The roster tag rules of the rankings chapter: every sentence tagged, 1 to 3 sentences per team,
    and the team's first sentence cites its PR fact. A tagged reaction sentence counts toward the 3."""
    teams = {int(fid.split(".")[1]): sheet.facts[fid].teams[0] for fid in chapter.fact_ids if fid.startswith("PR.")}
    by_team: dict[int, list[int]] = {rid: [] for rid in teams}
    failures = []
    for i, sentence in enumerate(blurb.sentences):
        if sentence.roster_id is None:
            failures.append(f"[{i}] the sentence has no roster tag; set roster_id to the team it is about")
        elif sentence.roster_id not in teams:
            failures.append(f"[{i}] roster tag {sentence.roster_id} is not a team in this chapter")
        else:
            by_team[sentence.roster_id].append(i)
    for rid, name in teams.items():
        indexes = by_team[rid]
        if not indexes:
            # A missing team has no sentence to point at, so the message points at the first, as the count check does.
            failures.append(f"[0] team {name} has no sentence; give every team 1 to 3 sentences")
            continue
        if len(indexes) > 3:
            failures.append(f"[{indexes[3]}] team {name} has {len(indexes)} sentences; give every team 1 to 3")
        if f"PR.{rid}" not in blurb.sentences[indexes[0]].fact_ids:
            failures.append(f"[{indexes[0]}] the first sentence about team {name} must cite PR.{rid}")
    return failures


def opener_failures(blurb: Blurb, chapter: Chapter, sheet: FactSheet) -> list[str]:
    """No two teams in the rankings chapter open on the same first 3 words.

    The chapter is one call, so the writer sees all twelve rows, yet it still repeats a stock opener such as
    "Scoring has dipped to". Only the first sentence of each team counts as its opener.
    """
    teams = {int(fid.split(".")[1]): sheet.facts[fid].teams[0] for fid in chapter.fact_ids if fid.startswith("PR.")}
    seen: dict[tuple[str, ...], int] = {}
    # A team whose opener fails never enters `seen`, so a separate set keeps its later sentences out.
    opened: set[int] = set()
    failures = []
    for i, sentence in enumerate(blurb.sentences):
        rid = sentence.roster_id
        if rid not in teams or rid in opened:
            continue
        opened.add(rid)
        # Case and edge punctuation do not make an opener different: "Despite 2," matches "despite 2".
        words = tuple(w.strip(OPENER_PUNCTUATION) for w in sentence.text.lower().split()[:OPENER_WORDS])
        if words in seen:
            failures.append(
                f"[{i}] team {teams[rid]} opens with '{' '.join(words)}', as team {teams[seen[words]]} does;"
                " give each team its own opener"
            )
        else:
            seen[words] = rid
    return failures


def code_check(blurb: Blurb, chapter: Chapter, sheet: FactSheet) -> list[str]:
    failures: list[str] = []
    in_chapter = set(chapter.fact_ids)
    league_teams = {t for f in sheet.facts.values() for t in f.teams}
    league_players = {p for c in sheet.chapters for p in c.scope_players}
    scope_names = [*chapter.scope_teams, *chapter.scope_players]
    in_scope_last = {last_name(p) for p in chapter.scope_players}
    # Lowercase, because whole_word ignores case.
    scope_team_words = {w.lower() for t in chapter.scope_teams for w in t.split()}
    banned = _banned("## Banned words")
    banned_phrases = _banned("## Banned phrases")
    always_allowed = _week_numbers(sheet)
    reactions = 0
    bares: list[str] = []

    for i, sentence in enumerate(blurb.sentences):
        # A sentence with no fact IDs is the one reaction a blurb may hold.
        if not sentence.fact_ids:
            reactions += 1
            if reactions > 1:
                failures.append(f"[{i}] a second reaction sentence; a blurb may hold one, so cite a fact")
            failures += [f"[{i}] {m}" for m in reaction_failures(sentence.text, scope_names, in_scope_last)]

        valid_ids = []
        for fid in sentence.fact_ids:
            if fid in sheet.facts and fid in in_chapter:
                valid_ids.append(fid)
            else:
                failures.append(f"[{i}] fact ID {fid} is not in this chapter")
        cited = _numbers(valid_ids, sheet)

        # Digits inside a name ("Pukancun on 3") are not numbers.
        bare = remove_names(sentence.text, scope_names)
        bares.append(bare)
        cited_text = " ".join(sheet.facts[fid].text for fid in valid_ids)
        ids = ", ".join(sentence.fact_ids)
        for message in number_failures(bare, cited | always_allowed, cited_text):
            # A digit failure names the cited IDs, so the rewrite sees the facts that the check used.
            # A reaction sentence cites no IDs, so it gets no suffix.
            suffix = "" if message.startswith("number word") or not ids else f" {ids}"
            failures.append(f"[{i}] {message}{suffix}")

        failures += [f"[{i}] {m}" for m in article_failures(sentence.text)]

        # A fact ID belongs in fact_ids. Any bracket in the text is a leaked ID or a stray mark.
        if "[" in sentence.text:
            failures.append(f"[{i}] the text has a '[': put fact IDs in fact_ids only")

        for team in sorted(league_teams - set(chapter.scope_teams)):
            if team in bare:
                failures.append(f"[{i}] team {team} is not in this chapter")

        for player in sorted(league_players - set(chapter.scope_players)):
            last = last_name(player)
            # A last name shared with an in-scope player is ambiguous, so it passes.
            # A word of a scope team name, such as "Love" for All You Need Is Love, is not a player match.
            skip = not last or last in in_scope_last or last.lower() in scope_team_words
            if player in bare or (not skip and whole_word(last, bare)):
                failures.append(f"[{i}] player {player} is not on a team in this chapter")

        # Names are stripped first: a team called "Lucky Lambs" is not the word "lucky".
        for word in banned:
            if whole_word(word, bare):
                failures.append(f"[{i}] banned word '{word}'")
        for phrase in banned_phrases:
            if whole_word(phrase, bare):
                failures.append(f"[{i}] banned phrase '{phrase}'")

        for words, markers in GATED_WORDS:
            for word in words:
                if whole_word(word, bare) and not any(
                    m in fid for fid in sentence.fact_ids for m in markers
                ):
                    needs = " or ".join(markers)
                    failures.append(f"[{i}] '{word}' needs a cited {needs} fact")

    # The 12-team chapters name many teams, so only a chapter about one or two teams gets this check.
    if two_team_chapter(chapter.key):
        for i, team, mentions in repeated_teams([s.text for s in blurb.sentences], chapter.scope_teams):
            failures.append(repeat_failure(f"[{i}] the blurb", team, mentions))

    if chapter.key == RANKINGS_CHAPTER:
        failures += roster_tag_failures(blurb, chapter, sheet)
        failures += opener_failures(blurb, chapter, sheet)

    # The ", which" tail is the stock joke shape, so a blurb gets one.
    tails = [i for i, s in enumerate(blurb.sentences) if WHICH_TAIL.search(s.text)]
    if len(tails) > 1:
        failures.append(f"[{tails[1]}] {len(tails)} sentences have a ', which' tail; a blurb may hold one")

    for i, sentence in enumerate(blurb.sentences):
        if AND_THATS_TAIL.search(sentence.text):
            failures.append(f"[{i}] the sentence ends in \", and that's X\"; that closer is banned")

    # The rankings chapter is twelve short team rows, and each row opens on a rank, so it skips the mix.
    if chapter.key != RANKINGS_CHAPTER:
        failures += numberless_failures(bares)

    count = len(blurb.sentences)
    if not chapter.min_sentences <= count <= chapter.max_sentences:
        failures.append(
            f"[0] {count} sentences; the range is {chapter.min_sentences} to {chapter.max_sentences}"
        )
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
