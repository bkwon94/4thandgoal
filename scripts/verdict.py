"""
Checks one Test verdicts comment against the acceptance tests of a feature, and prints a rule report.
The verdict workflow runs it on each spec PR. It uses only the Python standard library. See ADR 0020.
"""
import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ADR = "docs/adr/0020-a-spec-pr-merges-on-the-verdicts-of-its-acceptance-tests.md"
RULE = "every acceptance test has a PASS Test verdict from Brian"
HEADING = "test verdicts"
# Each PR comment that a cpc skill writes ends with this line. The gh CLI of the agent and Brian share one
# account, so the marker is the only sign that an agent wrote a comment. A marked comment never counts.
AGENT_MARKER = "<!-- cpc:agent -->"
WORDS = {"PASS", "FAIL", "BLOCKED"}

# A test line of ACCEPTANCE.md starts with its id, such as "AT-1: The title". The Trace lines start with "Story".
TEST_LINE = re.compile(r"^AT-(\d+):\s*(.*)$")
# A verdict line may sit in a list: "- AT-1: PASS the note".
VERDICT_LINE = re.compile(r"^\s*(?:[-*]\s+)?AT-(\d+)\s*:\s*(\S*)\s*(.*)$")


@dataclass(frozen=True)
class Offense:
    """One break of the rule at one place, in the rule-report shape of the apps."""
    path: str
    line: int
    rule_id: str
    what: str
    fix: str

    def format(self) -> str:
        return "\n".join([
            f"{self.path}:{self.line}  {self.rule_id}",
            f"  {self.what}",
            f"  Rule: {RULE} ({ADR}).",
            f"  Fix: {self.fix}",
        ])


@dataclass
class Result:
    tests: list[str]
    offenses: list[Offense] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not self.offenses

    def _count(self) -> str:
        n = len(self.offenses)
        return f"{n} offense." if n == 1 else f"{n} offenses."

    def report(self) -> str:
        if self.passed:
            return f"0 offenses. {_join(self.tests)} {'has' if len(self.tests) == 1 else 'have'} PASS."
        return "\n\n".join([self._count()] + [offense.format() for offense in self.offenses])

    def summary(self) -> str:
        """One line of 140 characters or fewer, for the description of the commit status."""
        if self.passed:
            text = self.report()
        else:
            text = f"{self._count()} " + " ".join(offense.what for offense in self.offenses)
        return text if len(text) <= 140 else text[:137] + "..."


def _join(ids: list[str]) -> str:
    if len(ids) <= 2:
        return " and ".join(ids)
    return ", ".join(ids[:-1]) + ", and " + ids[-1]


def acceptance_tests(text: str) -> dict[str, int]:
    """The id and the line number of each live test. A test whose title holds the word Retired needs no verdict."""
    tests = {}
    for number, line in enumerate(text.splitlines(), start=1):
        match = TEST_LINE.match(line)
        if match and not re.search(r"\bRetired\b", match.group(2)):
            tests[f"AT-{match.group(1)}"] = number
    return tests


def _is_heading(line: str) -> bool:
    """The heading line may be plain, a markdown heading, or end with a colon: "## Test verdicts:"."""
    return line.strip().lstrip("#").strip().rstrip(":").strip().lower() == HEADING


def has_heading(text: str) -> bool:
    return any(_is_heading(line) for line in text.splitlines())


def judge(acceptance: str, comment: str | None, acceptance_path: str = "ACCEPTANCE.md",
          comment_path: str = "the Test verdicts comment") -> Result:
    """Judge one comment. It fails if a live test has no line, a line is not PASS, or a line names no live test."""
    tests = acceptance_tests(acceptance)
    result = Result(tests=list(tests))
    lines = (comment or "").splitlines()
    start = next((i for i, line in enumerate(lines) if _is_heading(line)), None)
    if start is None:
        result.offenses.append(Offense(
            comment_path, 0, "verdict/no-comment", "No comment by Brian holds the line `Test verdicts`.",
            "Brian writes one PR comment: the line `Test verdicts`, then one line `AT-<n>: PASS|FAIL|BLOCKED` per test.",
        ))
        return result

    seen: dict[str, int] = {}
    for number, line in enumerate(lines[start + 1:], start=start + 2):
        match = VERDICT_LINE.match(line)
        if not match:
            continue
        test_id, word = f"AT-{match.group(1)}", match.group(2).upper()
        if test_id in seen:
            result.offenses.append(Offense(
                comment_path, number, "verdict/duplicate", f"{test_id} has two lines.",
                f"keep one line for {test_id} in a new comment.",
            ))
            continue
        seen[test_id] = number
        if test_id not in tests:
            result.offenses.append(Offense(
                comment_path, number, "verdict/unknown", f"{test_id} is not a live test of the acceptance file.",
                f"remove the line, or fix the id to a test of `{acceptance_path}`.",
            ))
        elif word not in WORDS:
            result.offenses.append(Offense(
                comment_path, number, "verdict/not-pass", f"{test_id} has `{match.group(2)}`, not PASS, FAIL, or BLOCKED.",
                f"write `{test_id}: PASS`, `FAIL`, or `BLOCKED`, then an optional note.",
            ))
        elif word != "PASS":
            result.offenses.append(Offense(
                comment_path, number, "verdict/not-pass", f"{test_id} has {word}.",
                "fix the work with `cpc:review`, then Brian writes a new comment with PASS.",
            ))

    for test_id, number in tests.items():
        if test_id not in seen:
            result.offenses.append(Offense(
                acceptance_path, number, "verdict/missing", f"{test_id} has no line in the Test verdicts comment.",
                f"Brian adds the line `{test_id}: PASS|FAIL|BLOCKED` to a new Test verdicts comment.",
            ))
    return result


def latest_verdict_comment(comments: list[dict], owner: str) -> dict | None:
    """The latest comment by the owner that holds the heading and has no agent marker.

    The list is in the order of the GitHub API, oldest first, so the last match is the latest. An edit of an
    older comment does not make it the latest.
    """
    picked = None
    for item in comments:
        body = item.get("body") or ""
        if item.get("user", {}).get("login") == owner and AGENT_MARKER not in body and has_heading(body):
            picked = item
    return picked


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Check a Test verdicts comment against ACCEPTANCE.md.")
    parser.add_argument("acceptance", help="the path of ACCEPTANCE.md")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--comment", help="a file with the text of one comment")
    source.add_argument("--comments", help="a JSON file of the PR comments, as the GitHub API lists them")
    parser.add_argument("--owner", help="with --comments: the login whose comments count")
    parser.add_argument("--name", help="the path of ACCEPTANCE.md to print in the report")
    parser.add_argument("--summary", help="write the one-line summary to this file")
    args = parser.parse_args(argv)

    acceptance = Path(args.acceptance).read_text()
    name = args.name or args.acceptance
    if args.comments:
        if not args.owner:
            parser.error("--comments needs --owner")
        picked = latest_verdict_comment(json.loads(Path(args.comments).read_text()), args.owner)
        comment = picked["body"] if picked else None
        label = f"comment {picked['id']}" if picked else "the PR comments"
    else:
        comment = Path(args.comment).read_text()
        label = args.comment

    result = judge(acceptance, comment, acceptance_path=name, comment_path=label)
    print(result.report())
    if args.summary:
        Path(args.summary).write_text(result.summary() + "\n")
    return 0 if result.passed else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
