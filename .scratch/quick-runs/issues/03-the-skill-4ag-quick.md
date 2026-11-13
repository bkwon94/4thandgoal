# 03: The skill 4ag:quick

Spec: `.scratch/quick-runs/PRD.md`. Acceptance tests AT-1, AT-2, AT-3, and AT-11 to AT-30.

**App:** both

**What to build:** Brian runs `4ag:quick` with his words, a handoff file, or a task name from `Bugs` or `Quick Wins`. The skill checks the four boundary rules of ADR 0033, writes the quick file, and stops once for "go". Then it builds each item in sequence on one branch, `bug-<slug>` or `win-<slug>`: `diagnosing-bugs` for a Bug, `tdd` for a Quick win. Each item shows red before the fix and green after, on the same loop. A fresh quick Judge gives a Test verdict per item, and a text-only item skips it. The skill closes the quick file, opens one PR, and adds the wait task. A failed boundary rule stops the run and hands off to `4ag:plan` with a draft outcome statement. The skill works in Claude Code and in Codex.

**Blocked by:** 01, 02

**Status:** done

- [x] The plugin holds the skill, the quick file format, and the brief of the quick Judge, in the neutral harness words of `AGENTS.md`.
- [x] A tracked symlink makes the skill a Codex skill, and the harness rule passes.
- [x] The skill stops and names the skill when `diagnosing-bugs` or `tdd` is missing.
- [x] A mixed input starts two runs, and a feature request or six items make no branch.
- [x] The real Bug run on "Pick owner: week_moves names the first owner of a traded pick" goes from the task to an open PR, with red and green evidence and a Test verdict.
- [x] The quick Judge gives FAIL to a planted red loop of another failure and to a planted green loop of another command.
- [x] `make check-fast` passes at the root.

## Comments

- Closes with the squash merge of the spec PR of `quick-runs`. Commits: `edfeb4fa`, with the review fixes `7d39eef7`, `bf128b6e`, `6ab437f0`. Date: 2026-11-13.
- The harness rule passes with the symlink, and the real Bug run went to PR #41 with a PASS from the quick Judge; AT-1 to AT-3 and AT-11 to AT-30 have PASS.
- The first run after the merge is the clean test: a fresh session with `/4ag:quick`, no bootstrap, and timestamps.
- Read 9 files: AGENTS.md, GLOSSARY.md, .scratch/quick-runs/PRD.md, .scratch/quick-runs/ACCEPTANCE.md, .scratch/quick-runs/MAP.md, docs/adr/0033-a-quick-run-skips-the-spec-flow.md, docs/agents/issue-tracker.md, .claude/plugin/skills/implement/SKILL.md, apps/pipeline/tests/test_rule_harness.py.
