# Codex flow: acceptance tests

Spec: `.scratch/codex-flow/PRD.md`.

The Test verdict: the Judge gives one for each test in `VERDICTS.md`. The Judge is a fresh subagent that reads only this file and the evidence. The PR merges when every test has PASS and Brian gives no FAIL in a PR comment (ADR 0026). The agent that builds the work records the evidence and gives no Test verdict.

No test changes the site UI, so no test takes screenshots. Each test takes the command and its output. Each Codex run uses Codex CLI 0.167.1 at the root of the worktree `.claude/worktrees/codex-flow`, on the head of the Spec branch `codex-flow`, unless the test says otherwise. A run that commits or calls `gh`, as in AT-13, AT-15, AT-16, and AT-17, starts at the main checkout root instead, because Codex in a linked worktree cannot write its own gitdir. A "scratch copy" is a throwaway clone of that head, outside the repo, so a broken file never reaches a commit.

## Tests

AT-1: Codex lists the six 4ag skills
App: both
Stories: 1, 2, 20
Given: the head of `codex-flow`, and Brian's user skills in `~/.agents/skills/`, which include `implement`, `to-spec`, and `to-tickets`.
When: the agent runs `codex debug prompt-input "hi"` at the worktree root.
Then: the skill list names `4ag:plan`, `4ag:to-spec`, `4ag:to-acceptance`, `4ag:to-tickets`, `4ag:implement`, and `4ag:review`, and the path of each one resolves under `.claude/plugin/skills/`.
Evidence: the command, and the lines of its output that name a `4ag:` skill.

AT-2: `$4ag:implement` loads the repo skill, not the user skill
App: both
Stories: 3
Given: the head of `codex-flow`, and the user skill `~/.agents/skills/implement`.
When: the agent sends `$4ag:implement codex-flow` in a Codex session at the worktree root and stops the session after the skill loads.
Then: the session log injects the skill at `.claude/plugin/skills/implement/SKILL.md`, and it injects no skill from `~/.agents/skills/implement`.
Evidence: the session command, and the lines of the session log that inject a skill.

AT-3: Each symlink resolves to its source skill
App: both
Stories: 4
Given: the head of `codex-flow`.
When: the agent runs `ls -l .agents/skills` and `readlink -f .agents/skills/4ag-*` at the worktree root.
Then: `.agents/skills/` holds exactly six symlinks, `4ag-plan`, `4ag-to-spec`, `4ag-to-acceptance`, `4ag-to-tickets`, `4ag-implement`, and `4ag-review`, and each resolves to `.claude/plugin/skills/<name>` of the same name.
Evidence: the two commands and their output.

AT-4: Each `CLAUDE.md` holds only the import
App: both
Stories: 5, 6
Given: the head of `codex-flow`.
When: the agent runs `cat CLAUDE.md apps/site/CLAUDE.md apps/pipeline/CLAUDE.md` and `git ls-files '*CLAUDE.md'`.
Then: the repo tracks exactly these three `CLAUDE.md` files, and each one holds only the line `@AGENTS.md`.
Evidence: the two commands and their output.

AT-5: Claude Code reads the rules through the import
App: both
Stories: 6
Given: the head of `codex-flow`.
When: the agent runs `claude -p "In this repo, which branch does a ticket branch merge into, and with which git command?"` at the worktree root.
Then: the answer names the Spec branch and `git merge --no-edit`.
Evidence: the command and the full answer.

AT-6: The rules files hold no stale words
App: both
Stories: 7, 24
Given: the head of `codex-flow`.
When: the agent runs `grep -n 'cpc:\|~/.Codex' AGENTS.md apps/site/AGENTS.md apps/pipeline/AGENTS.md`.
Then: the command prints nothing, and each of the three files exists and is tracked.
Evidence: the command, its empty output, and `git ls-files '*AGENTS.md'`.

AT-7: No skill names a Claude-only tool
App: both
Stories: 8
Given: the head of `codex-flow`.
When: the agent runs `grep -rn 'Skill tool\|Agent tool' .claude/plugin/skills`.
Then: the command prints nothing.
Evidence: the command and its empty output.

AT-8: The root `AGENTS.md` maps each neutral phrase to each harness
App: both
Stories: 9
Given: the head of `codex-flow`.
When: the agent prints the section "The harness words" of the root `AGENTS.md`.
Then: the section maps "load the skill" to the Skill tool and to a `$<name>` mention, "start a fresh subagent" to the Agent tool and to `spawn_agent` with `fork_turns: "none"`, "the strong model" to `opus` and to `gpt-6-astra`, and `research` to `mattpocock-skills:research` in Claude.
Evidence: the command and the section text.

AT-9: The harness rule catches a missing symlink
App: pipeline
Stories: 22
Given: a scratch copy of the head of `codex-flow`, with `.agents/skills/4ag-review` removed and the removal staged.
When: the agent runs `make check-fast` at the root of the scratch copy.
Then: the check fails, and the harness rule names `review` and the missing symlink `.agents/skills/4ag-review`.
Evidence: the setup commands, the check command, and the lines of the rule report.

AT-10: The harness rule catches a changed `CLAUDE.md`
App: pipeline
Stories: 22
Given: a scratch copy of the head of `codex-flow`, with the line `Extra rule.` added to `apps/site/CLAUDE.md` and staged.
When: the agent runs `make check-fast` at the root of the scratch copy.
Then: the check fails, and the harness rule names `apps/site/CLAUDE.md`.
Evidence: the setup commands, the check command, and the lines of the rule report.

AT-11: The harness rule catches a Claude-only tool word
App: pipeline
Stories: 22
Given: a scratch copy of the head of `codex-flow`, with the line `Call the Skill tool for to-spec.` added to `.claude/plugin/skills/to-spec/SKILL.md` and staged.
When: the agent runs `make check-fast` at the root of the scratch copy.
Then: the check fails, and the harness rule names `.claude/plugin/skills/to-spec/SKILL.md` and the line of the added text.
Evidence: the setup commands, the check command, and the lines of the rule report.

AT-12: The readme rule limits where an `AGENTS.md` sits
App: both
Stories: 23
Given: a scratch copy of the head of `codex-flow`, with a new file `apps/pipeline/src/cornerstone/AGENTS.md` staged.
When: the agent runs `make check-fast` at the root of the scratch copy.
Then: the check fails, and the readme rule names `src/cornerstone/AGENTS.md`.
Evidence: the setup commands, the check command, and the lines of the rule report.

AT-13: Each skill passes its "Before you start" check in Codex
App: both
Stories: 1, 10
Given: the head of `codex-flow`, the profile `4ag`, and the skills `grilling`, `domain-modeling`, `research`, `prototype`, `tdd`, `code-review`, and `resolving-merge-conflicts` in `~/.agents/skills/`.
When: the agent sends each of `$4ag:plan`, `$4ag:to-spec`, `$4ag:to-acceptance`, `$4ag:to-tickets`, `$4ag:implement`, and `$4ag:review` in its own Codex session, with the instruction to stop after "Before you start".
Then: each of the six sessions reports that its "Before you start" check passed, and none names a missing skill or tool.
Evidence: the command and the last message of each of the six sessions.

AT-14: A missing global skill stops the plan skill
App: both
Stories: 11
Given: a temporary `HOME` whose `.agents/skills/` holds `grilling`, `domain-modeling`, and `prototype`, but not `research`.
When: the agent sends `$4ag:plan codex-flow` in a Codex session with that `HOME`, at the worktree root.
Then: the session stops in "Before you start" and names the missing skill `research`, and it changes no file.
Evidence: the setup commands, the session command, its last message, and `git status --short` after the run.

AT-15: A session with no profile stops the implement skill
App: both
Stories: 17
Given: the head of `codex-flow`.
When: the agent sends `$4ag:implement codex-flow` in a Codex session started with `-c 'default_permissions=":workspace"'`, at the worktree root.
Then: the session stops in "Before you start", names the profile `4ag`, and makes no worktree and no branch.
Evidence: the session command, its last message, and `git worktree list` and `git branch --list 'codex-flow-*'` before and after the run.

AT-16: The profile lets a Codex session commit and call `gh`
App: both
Stories: 16
Given: the head of `codex-flow`, and a scratch branch `codex-flow-probe` in the worktree `.claude/worktrees/codex-flow-probe`.
When: the agent tells a Codex session, started at the worktree root with no `-c` flag, to run `git -C .claude/worktrees/codex-flow-probe commit --allow-empty -m probe` and `gh api repos/{owner}/{repo} --jq .name`.
Then: the commit succeeds with no prompt, and `gh api` prints `4thandgoal`.
Evidence: any trust step that came first, the session command, the output of both commands, and `git log -1 codex-flow-probe`. Remove the probe worktree and branch after the run.

AT-17: A real spec runs end to end in Codex
App: both
Stories: 12, 21
Given: the ticket `week-8-fixes` 07, "the READMEs name the module an agent needs", and the head of `codex-flow`.
When: Brian and a Codex session run `$4ag:plan`, `$4ag:to-spec`, `$4ag:to-acceptance`, `$4ag:to-tickets`, and `$4ag:implement` for it, from the main checkout root, with the `.codex/config.toml` of `codex-flow` in place.
Then: its spec has a ticket branch merged into its Spec branch, an `EVIDENCE.md`, a `VERDICTS.md`, and an open PR to `main`.
Evidence: the Spec branch name, `git log --oneline` of the Spec branch, the paths of `EVIDENCE.md` and `VERDICTS.md`, and the PR URL.

AT-18: The Codex Judge is fresh and uses the strong model
App: both
Stories: 14, 15
Given: the Codex session of AT-17.
When: the agent reads the session log at the step that starts the Judge.
Then: the `spawn_agent` call of the Judge has `fork_turns: "none"` and the model `gpt-6-astra`.
Evidence: the path of the session log and the lines of the `spawn_agent` call of the Judge.

AT-19: A Codex ticket builder is fresh and works in its own worktree
App: both
Stories: 12
Given: the Codex session of AT-17.
When: the agent reads the session log at the step that starts the ticket builder.
Then: the `spawn_agent` call of the builder has `fork_turns: "none"`, and its brief names the absolute path of the ticket worktree.
Evidence: the path of the session log and the lines of the `spawn_agent` call of the builder.

AT-20: The GitHub ruleset guards `main`
App: both
Stories: 18
Given: Brian did the manual step for the ruleset.
When: the agent runs `gh api repos/{owner}/{repo}/rulesets` and `gh api repos/{owner}/{repo}/rulesets/<id>` for the ruleset on `main`.
Then: the ruleset targets `main`, needs the check `verdict`, and has the Repository admin role on its bypass list.
Evidence: the two commands and the fields of their output that show the target, the required check, and the bypass list.

AT-21: The manual steps are written down with values and a check
App: both
Stories: 19
Given: the head of `codex-flow`.
When: the agent prints `docs/agents/codex.md`.
Then: the file lists the ruleset on `main`, the project trust in Codex if AT-16 needed it, the skill `research` in `~/.agents/skills/`, and the removal of the stale untracked `AGENTS.md`, `apps/site/AGENTS.md`, and `.codex/config.toml`, each with exact values and a check.
Evidence: the command and the file text.

AT-22: The spec adds no Codex plugin manifest
App: both
Stories: none
Given: the head of `codex-flow`.
When: the agent runs `git ls-files | grep codex-plugin`.
Then: the command prints nothing.
Evidence: the command and its empty output.

AT-23: No skill file moves
App: both
Stories: none
Given: the head of `codex-flow`.
When: the agent runs `git diff --stat -M main...codex-flow -- .claude/plugin/skills`.
Then: the output shows no rename and no delete under `.claude/plugin/skills/`.
Evidence: the command and its output.

AT-24: No product code changes
App: both
Stories: none
Given: the head of `codex-flow`.
When: the agent runs `git diff --name-only main...codex-flow -- apps/`.
Then: no listed file is under `apps/api/`, and each listed file under an `apps/*/src/` folder is a rule test or the shared rule report.
Evidence: the command and its output.

## Trace

Story 1: AT-1, AT-13
Story 2: AT-1
Story 3: AT-2
Story 4: AT-3
Story 5: AT-4
Story 6: AT-4, AT-5
Story 7: AT-6
Story 8: AT-7
Story 9: AT-8
Story 10: AT-13
Story 11: AT-14
Story 12: AT-17, AT-19
Story 13: no test. Reason: no real spec has more than 6 tickets ready at one time, and a made-up spec breaks the rule of real data. The skill text holds the rule.
Story 14: AT-18
Story 15: AT-18
Story 16: AT-16
Story 17: AT-15
Story 18: AT-20
Story 19: AT-21
Story 20: AT-1
Story 21: AT-17
Story 22: AT-9, AT-10, AT-11
Story 23: AT-12
Story 24: AT-6. The removal from the main checkout is a manual step after the merge, in AT-21.
Out of scope "A Codex plugin manifest": AT-22
Out of scope "A move of the skills out of `.claude/`": AT-23
Out of scope "A change to the product code of the site, the pipeline, or the API": AT-24

## Revisions

- 2026-11-12: Brian approved that Codex starts at the main checkout root, not in a worktree, after ticket 02 found the limit. AT-17 and the note above the tests change to match.
