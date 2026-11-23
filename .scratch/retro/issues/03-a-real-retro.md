# 03: A real Retro finds its log and files one accepted candidate

Spec: `.scratch/retro/PRD.md`. Acceptance tests AT-10, AT-11, AT-12, AT-13, AT-14, AT-15, and AT-16.

**App:** both

**What to build:** The skill `4ag:retro` works end to end on real runs. Given a PR number, a quick file, or a feature slug, it finds the session log of the run by itself, by the branch name or the worktree path, in the Claude log and the Codex log. For a spec build it reads the logs of the subagents too. It prints one line `<stage>: <minutes> min` for each stage, then the total. Each candidate names a category, a timestamp that a `grep` finds in the log, the place of the fix, and a queue section. When Brian accepts one number, one `queue.py add` makes one task, and the timestamp is in its description. When no log matches, the Retro says so and uses only the record. Change the skill text where the real runs show a gap.

**Blocked by:** 01, 02

**Status:** ready-for-agent

- [x] `/4ag:retro 91` in a fresh session finds the log of PR #91, prints the stage times, and lists candidates with timestamps that a `grep` finds in the log.
- [ ] Brian accepts one candidate, and the queue then holds exactly one new task with the timestamp in its description.
- [x] `git status --short` is empty after the Retro.
- [x] `/4ag:retro .scratch/bugs/site-test-leaks.md` finds the same log as `/4ag:retro 91`.
- [x] `/4ag:retro trade-block` names `EVIDENCE.md`, `VERDICTS.md`, the CI runs of PR #88, and at least one log of a subagent.
- [ ] A merged PR with no matched log gets a reply that says so, with candidates from the record only.
