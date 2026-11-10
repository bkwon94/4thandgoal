"""
The rule of ADR 0030: one way of judging a trade remains. No code and no page copy of the analyzer and the Finder
holds a word of the old way, such as the rubric, a start letter, a breakdown, an adjuster, a verdict, or a factor row.
"""
import re
from pathlib import Path

from rule_report import Offense, report

REPO = Path(__file__).resolve().parents[4]
# The code and the copy of the analyzer and the Finder: the package, its site side, and the callers in the apps.
ROOTS = ("packages/analyzer/python/src", "packages/analyzer/site/form", "packages/analyzer/site/lib",
         "apps/pipeline/src/cornerstone", "apps/api/src")
SUFFIXES = {".py", ".md", ".ts", ".tsx", ".json"}
# The words of the old way.
OLD_WORDS = re.compile(
    r"rubric|start.letters?|final.letters?|side.letters?|\bLetters?\b|breakdowns?|adjusters?|verdict"
    r"|\bfactors?\b|STEP_WORDS|contenders?|sellers?|middle.team", re.IGNORECASE)
# The letter type of the old way had a capital, so only "Letter" with a capital counts. The plain word stays free.
CASED = re.compile(r"\bLetters?\b")


def _sources() -> list[Path]:
    """Each source file of the roots, with no test file and no folder that a tool writes."""
    files = []
    for root in ROOTS:
        for path in (REPO / root).rglob("*"):
            if (path.is_file() and path.suffix in SUFFIXES and ".test." not in path.name
                    and "node_modules" not in path.parts and "__pycache__" not in path.parts):
                files.append(path)
    return files


def _offenses() -> list[Offense]:
    offenses = []
    for path in _sources():
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            for match in OLD_WORDS.finditer(line):
                word = match.group()
                if word.lower().startswith("letter") and not CASED.fullmatch(word):
                    continue
                offenses.append(Offense(
                    path=str(path.relative_to(REPO)), line=number, rule_id="one-way/old-word",
                    what=f"The line holds the old word '{word}'.",
                    rule="One way of judging remains, so no code and no copy names a part of the old way",
                    adr="ADR 0030",
                    fix="Delete the old part, or name the new part: the Advisor, a Lean, a Case, a Bullet, a Mark, "
                        "a Measure, or a race group."))
    return offenses


def test_no_code_and_no_copy_of_the_analyzer_holds_a_word_of_the_old_way():
    offenses = _offenses()
    assert not offenses, report(offenses)


# The copy of the analyzer page and the Finder cards. The house rules: never "rival", and never the name of the
# commissioner (decision 59 of the spec).
COPY_ROOTS = ("packages/analyzer/site/form", "packages/analyzer/site/lib")
NOT_IN_COPY = re.compile(r"\brivals?\b|\bbrian\b", re.IGNORECASE)


def test_the_copy_of_the_analyzer_and_the_finder_says_no_rival_and_names_no_commissioner():
    offenses = []
    for path in _sources():
        if not any(path.is_relative_to(REPO / root) for root in COPY_ROOTS):
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            for match in NOT_IN_COPY.finditer(line):
                offenses.append(Offense(
                    path=str(path.relative_to(REPO)), line=number, rule_id="one-way/copy-word",
                    what=f"The copy holds the word '{match.group()}'.",
                    rule="The copy says manager or another manager, and the commissioner, never a name",
                    adr="ADR 0030", fix="Write 'manager', 'another manager', or 'the commissioner'."))
    assert not offenses, report(offenses)
