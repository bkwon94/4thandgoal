# 03: The skill 4ag:quick

Spec: `.scratch/quick-runs/PRD.md`. Acceptance tests AT-1, AT-2, AT-3, and AT-11 to AT-30.

**App:** both

**What to build:** Brian runs `4ag:quick` with his words, a handoff file, or a task name from `Bugs` or `Quick Wins`. The skill checks the four boundary rules of ADR 0033, writes the quick file, and stops once for "go". Then it builds each item in sequence on one branch, `bug-<slug>` or `win-<slug>`: `diagnosing-bugs` for a Bug, `tdd` for a Quick win. Each item shows red before the fix and green after, on the same loop. A fresh quick Judge gives a Test verdict per item, and a text-only item skips it. The skill closes the quick file, opens one PR, and adds the wait task. A failed boundary rule stops the run and hands off to `4ag:plan` with a draft outcome statement. The skill works in Claude Code and in Codex.

**Blocked by:** 01, 02

**Status:** in-review

- [x] The plugin holds the skill, the quick file format, and the brief of the quick Judge, in the neutral harness words of `AGENTS.md`.
- [x] A tracked symlink makes the skill a Codex skill, and the harness rule passes.
- [ ] The skill stops and names the skill when `diagnosing-bugs` or `tdd` is missing.
- [ ] A mixed input starts two runs, and a feature request or six items make no branch.
- [ ] The real Bug run on "Pick owner: week_moves names the first owner of a traded pick" goes from the task to an open PR, with red and green evidence and a Test verdict.
- [ ] The quick Judge gives FAIL to a planted red loop of another failure and to a planted green loop of another command.
- [x] `make check-fast` passes at the root.
