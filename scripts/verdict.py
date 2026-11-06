"""
Checks the VERDICTS.md of the Judge and the Test verdicts comments of Brian against ACCEPTANCE.md, and prints a rule report.
The verdict workflow runs it on each spec PR. It uses only the Python standard library. See ADR 0026.

VERDICTS.md names the git blob SHA of each file that the Judge read, then holds one line per test:

    ACCEPTANCE.md: <blob SHA>
    EVIDENCE.md: <blob SHA>

    Test verdicts
    AT-1: PASS
    AT-2: FAIL <reason>
"""
import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ADR = "docs/adr/0026-the-judge-gives-the-test-verdicts.md"
RULE = "every acceptance test has a PASS Test verdict from the Judge and no FAIL from Brian"
HEADING = "test verdicts"
# Each PR comment that a cpc skill writes ends with this line. The gh CLI of the agent and Brian share one
# account, so the marker is the only sign that an agent wrote a comment. A marked comment never counts.
AGENT_MARKER = "<!-- cpc:agent -->"
WORDS = {"PASS", "FAIL", "BLOCKED"}

# A test line of ACCEPTANCE.md starts with its id, such as "AT-1: The title". The Trace lines start with "Story".
TEST_LINE = re.compile(r"^AT-(\d+):\s*(.*)$")
# A verdict line may sit in a list: "- AT-1: PASS the note".
VERDICT_LINE = re.compile(r"^\s*(?:[-*]\s+)?AT-(\d+)\s*:\s*(\S*)\s*(.*)$")
# A SHA line of VERDICTS.md names one file that the Judge read: "EVIDENCE.md: <blob SHA>".
SHA_LINE = re.compile(r"^\s*(?:[-*]\s+)?`?(ACCEPTANCE\.md|EVIDENCE\.md)`?\s*:\s*`?([0-9a-f]{40})`?\s*$")
# Each file that the Judge read, and the rule id of a stale copy.
READ_FILES = {"ACCEPTANCE.md": "verdict/stale-acceptance", "EVIDENCE.md": "verdict/stale-evidence"}


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


def verdict_lines(text: str | None) -> list[tuple[int, re.Match]] | None:
    """The line number and the match of each verdict line under the heading, or None if the text has no heading."""
    lines = (text or "").splitlines()
    start = next((i for i, line in enumerate(lines) if _is_heading(line)), None)
    if start is None:
        return None
    numbered = enumerate(lines[start + 1:], start=start + 2)
    return [(number, match) for number, line in numbered if (match := VERDICT_LINE.match(line))]


def judge(acceptance: str, verdicts: str | None, acceptance_path: str = "ACCEPTANCE.md",
          verdicts_path: str = "VERDICTS.md") -> Result:
    """Check the lines of VERDICTS.md. It fails if a live test has no line, a line is not PASS, or a line names no
    live test."""
    tests = acceptance_tests(acceptance)
    result = Result(tests=list(tests))
    lines = verdict_lines(verdicts)
    if lines is None:
        result.offenses.append(Offense(
            verdicts_path, 0, "verdict/no-verdicts", "No VERDICTS.md of the Judge holds the line `Test verdicts`.",
            "run the Judge. It writes the line `Test verdicts`, then one line `AT-<n>: PASS|FAIL` per test.",
        ))
        return result

    seen: dict[str, int] = {}
    for number, match in lines:
        test_id, word = f"AT-{match.group(1)}", match.group(2).upper()
        if test_id in seen:
            result.offenses.append(Offense(
                verdicts_path, number, "verdict/duplicate", f"{test_id} has two lines.",
                f"keep one line for {test_id}.",
            ))
            continue
        seen[test_id] = number
        if test_id not in tests:
            result.offenses.append(Offense(
                verdicts_path, number, "verdict/unknown", f"{test_id} is not a live test of the acceptance file.",
                f"remove the line, or fix the id to a test of `{acceptance_path}`.",
            ))
        elif word not in WORDS:
            result.offenses.append(Offense(
                verdicts_path, number, "verdict/not-pass", f"{test_id} has `{match.group(2)}`, not PASS, FAIL, or BLOCKED.",
                f"write `{test_id}: PASS`, `FAIL`, or `BLOCKED`, then an optional note.",
            ))
        elif word != "PASS":
            result.offenses.append(Offense(
                verdicts_path, number, "verdict/not-pass", f"{test_id} has {word}.",
                "fix the work, record its evidence again, and run a fresh Judge on the test.",
            ))

    for test_id, number in tests.items():
        if test_id not in seen:
            result.offenses.append(Offense(
                acceptance_path, number, "verdict/missing", f"{test_id} has no line in the verdicts of the Judge.",
                f"run a fresh Judge on {test_id}.",
            ))
    return result


def blob_sha(data: bytes) -> str:
    """The git blob SHA of the bytes, as `git hash-object` gives it and the GitHub contents API returns it."""
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def stale_files(verdicts: str, head_shas: dict[str, str | None], verdicts_path: str = "VERDICTS.md") -> list[Offense]:
    """An offense for each file whose blob SHA at the PR head is not the SHA that VERDICTS.md names.

    An old verdict must never cover new work, so a change to a file after the Judge read it fails the check.
    """
    named = {}
    for number, line in enumerate(verdicts.splitlines(), start=1):
        match = SHA_LINE.match(line)
        if match:
            named.setdefault(match.group(1), (number, match.group(2)))
    offenses = []
    fix = "record the evidence again, and run a fresh Judge on each test."
    for name, rule_id in READ_FILES.items():
        head = head_shas.get(name)
        if name not in named:
            offenses.append(Offense(verdicts_path, 0, rule_id, f"VERDICTS.md names no blob SHA of {name}.", fix))
        elif head is None:
            offenses.append(Offense(verdicts_path, named[name][0], rule_id, f"The PR head has no {name}.", fix))
        elif head != named[name][1]:
            offenses.append(Offense(
                verdicts_path, named[name][0], rule_id,
                f"{name} is stale: it changed after the Judge read it ({named[name][1][:7]} to {head[:7]}).", fix,
            ))
    return offenses


def brian_fails(comment: str | None, comment_path: str = "the Test verdicts comment") -> list[Offense]:
    """An offense for each FAIL or BLOCKED line of the comment of Brian. A PASS line of Brian changes nothing.

    Only the latest comment counts, so a newer comment with no FAIL for a test clears an older FAIL.
    """
    offenses = []
    for number, match in verdict_lines(comment) or []:
        if match.group(2).upper() in {"FAIL", "BLOCKED"}:
            test_id, word = f"AT-{match.group(1)}", match.group(2).upper()
            offenses.append(Offense(
                comment_path, number, "verdict/brian-fail", f"{test_id} has {word} from Brian.",
                f"fix {test_id} with `cpc:review`. Brian clears it with a newer Test verdicts comment with no FAIL "
                f"for {test_id}.",
            ))
    return offenses


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


def _read(path: str | None) -> str | None:
    """The text of a file, or None if the PR has no such file."""
    return Path(path).read_text() if path and Path(path).is_file() else None


def _head_sha(given: str | None, path: str | None) -> str | None:
    """The given blob SHA, or the SHA of the local file. An empty SHA or no file means the PR has no such file."""
    if given is not None:
        return given or None
    return blob_sha(Path(path).read_bytes()) if path and Path(path).is_file() else None


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Check VERDICTS.md and the comments of Brian against ACCEPTANCE.md.")
    parser.add_argument("acceptance", help="the path of ACCEPTANCE.md")
    parser.add_argument("--verdicts", required=True, help="the path of VERDICTS.md, which the Judge writes")
    parser.add_argument("--evidence", help="the path of EVIDENCE.md")
    # verdict.yml gives the blob SHAs at the PR head from the contents API. Without them, the script computes the
    # SHA of each local file.
    parser.add_argument("--acceptance-sha", help="the blob SHA of ACCEPTANCE.md at the PR head")
    parser.add_argument("--evidence-sha", help="the blob SHA of EVIDENCE.md at the PR head, or empty if it has none")
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--comment", help="a file with the text of one comment of Brian")
    source.add_argument("--comments", help="a JSON file of the PR comments, as the GitHub API lists them")
    parser.add_argument("--owner", help="with --comments: the login whose comments count")
    parser.add_argument("--summary", help="write the one-line summary to this file")
    args = parser.parse_args(argv)

    acceptance = Path(args.acceptance).read_text()
    verdicts = _read(args.verdicts)
    result = judge(acceptance, verdicts, acceptance_path=args.acceptance, verdicts_path=args.verdicts)
    if verdicts is not None:
        head_shas = {
            "ACCEPTANCE.md": _head_sha(args.acceptance_sha, args.acceptance),
            "EVIDENCE.md": _head_sha(args.evidence_sha, args.evidence),
        }
        result.offenses.extend(stale_files(verdicts, head_shas, args.verdicts))

    if args.comments:
        if not args.owner:
            parser.error("--comments needs --owner")
        picked = latest_verdict_comment(json.loads(Path(args.comments).read_text()), args.owner)
        if picked:
            result.offenses.extend(brian_fails(picked["body"], f"comment {picked['id']}"))
    elif args.comment:
        result.offenses.extend(brian_fails(Path(args.comment).read_text(), args.comment))
    print(result.report())
    if args.summary:
        Path(args.summary).write_text(result.summary() + "\n")
    return 0 if result.passed else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
