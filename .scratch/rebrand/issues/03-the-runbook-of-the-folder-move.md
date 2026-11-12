# 03: The runbook of the folder move

Spec: `.scratch/rebrand/PRD.md`. Acceptance tests AT-11 and AT-12.

**App:** both

**What to build:** Brian moves `~/repos/cpcfantasyfootball` to `~/repos/4thandgoal` after the merge, by one runbook in `docs/agents/`. The runbook says to move on a day other than Tuesday, because the weekly build runs Tuesday at 08:00. It gives nine steps in order, each with one command and one check: stop the LaunchAgent; remove the worktrees of merged specs; move the folder; run `git worktree repair`; move the Claude memory folder `-Users-brian-kwon-repos-cpcfantasyfootball` to `-Users-brian-kwon-repos-4thandgoal`; set the marketplace key `4ag-local` and its path in `~/.claude/settings.json`; rebuild the venv and the node modules; copy and load the LaunchAgent; open a new session and call one `4ag:` skill. The research notes `.scratch/rebrand/decisions/03-research-the-cutover.notes.md`, Part 3, step 8, hold the commands. A rehearsal on a scratch clone proves the git steps.

**Blocked by:** none

**Status:** done

- [x] The runbook has the Tuesday warning and the nine steps in the order above, each with one command and one check.
- [x] On a fresh clone with one worktree in the scratchpad, a move of the clone and the `git worktree repair` command of the runbook give a `git worktree list` with no `prunable`, and `git status` in the worktree exits 0.
- [x] The rehearsal folders are deleted after the run.
- [ ] After the merge, the close comment records the real move: `git worktree list`, `launchctl list | grep cornerstone`, and `/plugin` with `4ag@4ag-local` enabled.

## Comments

Merged into the Spec branch `rebrand` as 4446aa56, the review fixes 37c44b7e to 58118d04, and the evidence fixes 34477b17, 6183edcb, and 434ba546, on 2026-11-11. Closes with the squash merge of the spec PR.
AT-11 and AT-12 have PASS from the Judge; the rehearsal ran the step 4 command on a fresh clone.
The last box waits on the real move: Brian runs docs/agents/folder-move.md after the merge and pastes the three outputs here.
Read 5 files: CLAUDE.md, .scratch/rebrand/PRD.md, .scratch/rebrand/ACCEPTANCE.md, .scratch/rebrand/issues/03-the-runbook-of-the-folder-move.md, .scratch/rebrand/decisions/03-research-the-cutover.notes.md.
