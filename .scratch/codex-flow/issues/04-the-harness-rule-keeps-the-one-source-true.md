# 04: The harness rule keeps the one source true

Spec: `.scratch/codex-flow/PRD.md`. Acceptance tests AT-9, AT-10, and AT-11.

**App:** pipeline

**What to build:** A rule test in the pipeline rule suite reads the tracked files and fails in three cases: a skill with no symlink in `.agents/skills/` that resolves to it, a `CLAUDE.md` that holds more than `@AGENTS.md`, and a skill file that names "the Skill tool" or "the Agent tool". It reports through the shared rule report, with the file, the line, the rule, and the fix, as the other rules do.

**Blocked by:** 03

**Status:** ready-for-agent

- [x] In a scratch copy with the `4ag-review` symlink removed, `make check-fast` fails and names it.
- [x] In a scratch copy with an extra line in the site `CLAUDE.md`, the check fails and names the file.
- [x] In a scratch copy with "the Skill tool" in the `to-spec` skill, the check fails and names the file and line.
- [x] `make check-fast` passes on the head of the Spec branch.
