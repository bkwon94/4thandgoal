"""Sort the review findings of midseason-report into groups that share no file, for AT-21 of fast-cycle.
Read the commits of the branch only. Print the table of the groups and a check that no two groups share a file."""
import re
import subprocess
import sys

REPO = "/Users/brian.kwon/repos/cpcfantasyfootball"
BRANCH = "midseason-report"
# The commits of the branch only, not of main: a merge of main brings the squash of PR #3, which names S-1 and others.
# The first review ran on 2026-11-05. A later review of the redesign reuses S-8, P-1, and P-3, so the range stops there.
RANGE = ["main..midseason-report", "--until=2026-11-06T00:00"]
# The PR #13 body lists these as not fixed, so they get no fix branch and no group.
NOT_FIXED = {"S-8": "sleeper.load_draft serves only the fake provider (ADR 0015)",
             "S-9": "LeagueSettings.reseed keeps a default for old saved test data"}
IDS = [f"K-{n}" for n in range(1, 16)] + [f"S-{n}" for n in range(1, 12)] + [f"P-{n}" for n in range(4, 7)]


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", REPO, *args], check=True, capture_output=True, text=True).stdout


def commits_of(finding: str) -> list[tuple[str, str]]:
    """The commits whose message names the finding as a whole word, so K-1 does not match K-10."""
    out = git("log", *RANGE, "--no-merges", "--format=%H%x00%s%x00%B%x1e")
    pattern = re.compile(rf"(?<![A-Za-z0-9-]){re.escape(finding)}(?![0-9])")
    found = []
    for record in out.split("\x1e"):
        if not record.strip():
            continue
        sha, subject, body = record.strip("\n").split("\x00", 2)
        if pattern.search(body):
            found.append((sha[:8], subject))
    return found


def files_of(sha: str) -> set[str]:
    return {line for line in git("show", "--name-only", "--format=", sha).splitlines() if line}


def groups_of(findings: dict[str, set[str]]) -> list[list[str]]:
    """Union-find: two findings that share a file go in the same group."""
    parent = {f: f for f in findings}

    def root(f: str) -> str:
        while parent[f] != f:
            parent[f] = parent[parent[f]]
            f = parent[f]
        return f

    owner: dict[str, str] = {}
    for finding, files in findings.items():
        for path in files:
            if path in owner:
                parent[root(finding)] = root(owner[path])
            else:
                owner[path] = finding
    groups: dict[str, list[str]] = {}
    for finding in findings:
        groups.setdefault(root(finding), []).append(finding)
    return sorted(groups.values(), key=lambda g: (-len(g), IDS.index(g[0])))


def main() -> int:
    findings: dict[str, set[str]] = {}
    print("## The findings\n")
    print("| Finding | Commits | Files |")
    print("| --- | --- | --- |")
    for finding in IDS:
        commits = commits_of(finding)
        files: set[str] = set()
        for sha, _ in commits:
            files |= files_of(sha)
        findings[finding] = files
        print(f"| {finding} | {', '.join(sha for sha, _ in commits) or 'NONE'} | {', '.join(sorted(files))} |")
    missing = [f for f, files in findings.items() if not files and f not in NOT_FIXED]
    print(f"\nFindings: {len(IDS)}. Not fixed, per the PR #13 body: "
          + "; ".join(f"{f}: {why}" for f, why in NOT_FIXED.items()) + ".")
    print(f"Findings to group: {len(IDS) - len(NOT_FIXED)}. Fixed findings with no commit: {missing or 'none'}.\n")

    groups = groups_of({f: files for f, files in findings.items() if files})
    print("## The groups\n")
    print("| Group | Findings | Files |")
    print("| --- | --- | --- |")
    letters = "abcdefghijklmnopqrstuvwxyz"
    group_files = []
    for letter, group in zip(letters, groups):
        files = set().union(*(findings[f] for f in group))
        group_files.append((letter, files))
        print(f"| {letter} | {', '.join(group)} | {', '.join(sorted(files))} |")

    print("\n## The check\n")
    shared = [(a, b, fa & fb) for i, (a, fa) in enumerate(group_files) for b, fb in group_files[i + 1:] if fa & fb]
    each_once = sorted(f for g in groups for f in g) == sorted(f for f in IDS if f not in NOT_FIXED)
    print(f"Groups: {len(groups)}. Each finding in exactly one group: {each_once}.")
    print(f"Pairs of groups that share a file: {len(shared)}.")
    for a, b, files in shared:
        print(f"  {a} and {b} share {sorted(files)}")
    ok = not shared and each_once and not missing
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
