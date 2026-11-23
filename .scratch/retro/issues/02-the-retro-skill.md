# 02: The skill `4ag:retro` ships in Claude and Codex

Spec: `.scratch/retro/PRD.md`. Acceptance tests AT-1, AT-2, AT-8, AT-9, AT-17, AT-18, AT-19, and AT-20.

**App:** both

**What to build:** A new skill `4ag:retro` in the `4ag` plugin, in the voice and the shape of the other `4ag` skills. It starts with the merge sweep. It checks for the global skill `writing-for-agents`. It takes a PR number, a quick file, a feature slug, or nothing, which means the current session. It reads the record of the run, the PR comments, the CI runs, the Claude log, and the Codex log. It gives the stage times. It holds the table of the seven categories and their places from the spec, with `CODING_STANDARDS.md` for a judgement rule. It drops a candidate with no moment in the log. It shows the candidates in order of severity, files each accepted number with `queue.py add`, and checks each task for the name of a league manager first. It changes no repo file. The skill names no tool of one harness only. The end of `4ag:quick` and of `4ag:implement` names `/4ag:retro <PR number>` as an option for Brian, and no more. A tracked symlink `.agents/skills/4ag-retro` points to the skill, and the loop in step 3 of `docs/agents/codex.md` names `retro`.

**Blocked by:** none

**Status:** ready-for-agent

- [x] A text test reads the real skill file and checks the sweep, the four inputs with the default, the two logs, the drop rule, each category with its place, `CODING_STANDARDS.md`, and the check for a manager name. It passes.
- [x] A text test checks that the end of `4ag:quick` and of `4ag:implement` names `/4ag:retro` only as an option. It passes.
- [x] The rule test of the harness passes with the new symlink.
- [ ] A Claude Code session lists `4ag:retro`, and `codex debug prompt-input "hi"` lists it once.
- [x] `4ag:plan` has no diff, and `4ag:quick` does not name `code-review`.
