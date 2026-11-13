# Codex flow: evidence

Spec: `.scratch/codex-flow/PRD.md`. Acceptance tests: `.scratch/codex-flow/ACCEPTANCE.md`.
Built from: `d192e8a7`, on 2026-11-12. The agent gives no Test verdict. The Judge gives one for each test in `VERDICTS.md`.
Round time: 0 min for 0 site tests. No test takes screenshots. Each Codex run uses Codex CLI 0.167.2, the version installed now.

## AT-1: Codex lists the six 4ag skills

App: both
Then: the skill list names `4ag:plan`, `4ag:to-spec`, `4ag:to-acceptance`, `4ag:to-tickets`, `4ag:implement`, and `4ag:review`, and the path of each one resolves under `.claude/plugin/skills/`.
Files: `evidence/AT-1/output.txt`
Observation: The skill list at the worktree root names the six `4ag:` skills, each one time. Each file path is `r38/4ag-<name>/SKILL.md`, the prompt defines `r38` as `<worktree>/.agents/skills`, and the real path of each `SKILL.md` is `<worktree>/.claude/plugin/skills/<name>/SKILL.md`.

## AT-2: `$4ag:implement` loads the repo skill, not the user skill

App: both
Then: the session log injects the skill at `.claude/plugin/skills/implement/SKILL.md`, and it injects no skill from `~/.agents/skills/implement`.
Files: `evidence/AT-2/output.txt`
Observation: Line 15 of the session log `~/.codex/sessions/2026/11/12/rollout-2026-11-12T22-28-25-01a1d2f3-0842-7a73-9387-1c130f9b7a95.jsonl` injects `4ag:implement` from `<worktree>/.claude/plugin/skills/implement/SKILL.md`. The log has one `<skill>` line, and `grep -c 'agents/skills/implement'` gives 0.

## AT-3: Each symlink resolves to its source skill

App: both
Then: `.agents/skills/` holds exactly six symlinks, `4ag-plan`, `4ag-to-spec`, `4ag-to-acceptance`, `4ag-to-tickets`, `4ag-implement`, and `4ag-review`, and each resolves to `.claude/plugin/skills/<name>` of the same name.
Files: `evidence/AT-3/output.txt`
Observation: `ls -l` shows six symlinks, each `4ag-<name> -> ../../.claude/plugin/skills/<name>`. `readlink -f` resolves each to `<worktree>/.claude/plugin/skills/<name>`, and git tracks the six links.

## AT-4: Each `CLAUDE.md` holds only the import

App: both
Then: the repo tracks exactly these three `CLAUDE.md` files, and each one holds only the line `@AGENTS.md`.
Files: `evidence/AT-4/output.txt`
Observation: `git ls-files '*CLAUDE.md'` lists `CLAUDE.md`, `apps/pipeline/CLAUDE.md`, and `apps/site/CLAUDE.md`. `cat` prints `@AGENTS.md` three times, and `wc -l` gives 1 line for each file.

## AT-5: Claude Code reads the rules through the import

App: both
Then: the answer names the Spec branch and `git merge --no-edit`.
Files: `evidence/AT-5/output.txt`
Observation: The answer says a ticket branch merges into its spec branch with `git merge --no-edit`, after the check passes. It names "The flow" section of `AGENTS.md` as its source.

## AT-6: The rules files hold no stale words

App: both
Then: the command prints nothing, and each of the three files exists and is tracked.
Files: `evidence/AT-6/output.txt`
Observation: The grep prints nothing and exits 1. `git ls-files '*AGENTS.md'` lists `AGENTS.md`, `apps/pipeline/AGENTS.md`, and `apps/site/AGENTS.md`, and `ls -l` shows each file.

## AT-7: No skill names a Claude-only tool

App: both
Then: the command prints nothing.
Files: `evidence/AT-7/output.txt`
Observation: The grep prints nothing and exits 1.

## AT-8: The root `AGENTS.md` maps each neutral phrase to each harness

App: both
Then: the section maps "load the skill" to the Skill tool and to a `$<name>` mention, "start a fresh subagent" to the Agent tool and to `spawn_agent` with `fork_turns: "none"`, "the strong model" to `opus` and to `gpt-6-astra`, and `research` to `mattpocock-skills:research` in Claude.
Files: `evidence/AT-8/output.txt`
Observation: The table maps "Load the skill `<name>`" to the Skill tool and a `$<name>` mention, and "Start a fresh subagent" to the Agent tool and `spawn_agent` with `fork_turns: "none"`. It maps "With the strong model" to `model: opus` and `model: "gpt-6-astra"`, and "The global skill `research`" to `mattpocock-skills:research` in both columns.

## AT-9: The harness rule catches a missing symlink

App: pipeline
Then: the check fails, and the harness rule names `review` and the missing symlink `.agents/skills/4ag-review`.
Files: `evidence/AT-9/output.txt`
Observation: In the scratch clone with `git rm .agents/skills/4ag-review`, `make check-fast` exits 2. The report names `.claude/plugin/skills/review/SKILL.md:1  harness/symlink`: "The skill review has no tracked symlink .agents/skills/4ag-review that resolves to it."

## AT-10: The harness rule catches a changed `CLAUDE.md`

App: pipeline
Then: the check fails, and the harness rule names `apps/site/CLAUDE.md`.
Files: `evidence/AT-10/output.txt`
Observation: In the scratch clone with `Extra rule.` staged in `apps/site/CLAUDE.md`, `make check-fast` exits 2. The report names `apps/site/CLAUDE.md:1  harness/claude-md`: "apps/site/CLAUDE.md holds 2 lines, and not only @AGENTS.md."

## AT-11: The harness rule catches a Claude-only tool word

App: pipeline
Then: the check fails, and the harness rule names `.claude/plugin/skills/to-spec/SKILL.md` and the line of the added text.
Files: `evidence/AT-11/output.txt`
Observation: The setup grep puts the added text at line 47. `make check-fast` exits 2, and the report names `.claude/plugin/skills/to-spec/SKILL.md:47  harness/tool-word`: "The line holds "Skill tool"."

## AT-12: The readme rule limits where an `AGENTS.md` sits

App: both
Then: the check fails, and the readme rule names `src/cornerstone/AGENTS.md`.
Files: `evidence/AT-12/output.txt`
Observation: The root `make check-fast` exits 2 at the site member, whose rule names `apps/pipeline/src/cornerstone/AGENTS.md:1  readme/no-nested-rules-file`. A second run of `make -C apps/pipeline check-fast` with the same staged file exits 2, and its rule names `src/cornerstone/AGENTS.md:1  readme/no-nested-rules-file`.

## AT-13: Each skill passes its "Before you start" check in Codex

App: both
Then: each of the six sessions reports that its "Before you start" check passed, and none names a missing skill or tool.
Files: `evidence/AT-13/output.txt`
Observation: At the main checkout root, `plan`, `to-spec`, and `implement` report that the check passed. `to-acceptance` and `to-tickets` stop there because `.scratch/codex-flow/PRD.md` is not on `main`, and at the Spec worktree root both report that the check passed. `review codex-flow` stops at step 3 because `gh pr view codex-flow` finds no PR, and it says no skill or tool is missing; `codex-flow` has no open PR until stage 5. `review 37`, on the open draft spec PR #37, reports that steps 1 to 3 pass, and stops before steps 4 and 5, which change a worktree.

## AT-14: A missing global skill stops the plan skill

App: both
Then: the session stops in "Before you start" and names the missing skill `research`, and it changes no file.
Files: `evidence/AT-14/output.txt`
Observation: The temporary `HOME` has its own Codex home, because the plugin cache of `~/.codex` also lists `mattpocock-skills:research`; its skill list holds `grilling`, `domain-modeling`, and `prototype`, and no `research`. The session loads `4ag:plan` from the plugin skills folder and says "The check failed: `research` is absent", and `git status --short` is the same before and after.

## AT-15: A session with no profile stops the implement skill

App: both
Then: the session stops in "Before you start", names the profile `4ag`, and makes no worktree and no branch.
Files: `evidence/AT-15/output.txt`
Observation: The session starts at the main checkout root with `sandbox: workspace-write [workdir, /tmp, $TMPDIR]` and no network. It reports that the `.git` write probe exits 1 and `gh` cannot connect, names the profile `4ag` in `.codex/config.toml`, and stops; `git worktree list` and `git branch --list 'codex-flow-*'` are the same before and after.

## AT-16: The profile lets a Codex session commit and call `gh`

App: both
Then: the commit succeeds with no prompt, and `gh api` prints `4thandgoal`.
Files: `evidence/AT-16/output.txt`
Observation: The trust entry for the main checkout is in `~/.codex/config.toml`, and each session runs with `approval: never` and `workspace-write (network access enabled)`. Attempt 1 fails in the hook, with Node v22.17.0 and no `node_modules` in the fresh probe; attempt 2 ends before the commit ends. Attempt 3, after `pnpm install` and `uv sync` in the probe and with the Node 24 PATH step, prints `make check-fast....Passed` and `[codex-flow-probe 0c1915b3] probe`, `gh api` prints `4thandgoal`, and `git log -1 codex-flow-probe` shows `0c1915b3 probe`.

## AT-17: A real spec runs end to end in Codex

App: both
Then: its spec has a ticket branch merged into its Spec branch, an `EVIDENCE.md`, a `VERDICTS.md`, and an open PR to `main`.
Files: `evidence/AT-17/output.txt`
Observation: The reflog of the Codex Spec branch, now named `readme-module-navigation-private`, shows `merge readme-module-navigation-01: Fast-forward` at `dad744db` and `merge readme-module-navigation-02: Fast-forward` at `8800b549`. The PR branch `readme-module-navigation` is a public copy with 2 commits, and both branches hold `.scratch/readme-module-navigation/EVIDENCE.md` and `VERDICTS.md`. PR https://github.com/bkwon94/4thandgoal/pull/37 is open as a draft from `readme-module-navigation` to `main`.

## AT-18: The Codex Judge is fresh and uses the strong model

App: both
Then: the `spawn_agent` call of the Judge has `fork_turns: "none"` and the model `gpt-6-astra`.
Files: `evidence/AT-18/output.txt`
Observation: Line 983 of `~/.codex/sessions/2026/11/12/rollout-2026-11-12T15-38-49-01a1d17c-07e9-7cf1-98a9-a8eeae498b80.jsonl` calls `spawn_agent` with `task_name` `judge`, `fork_turns` `none`, `model` `gpt-6-astra`, and `reasoning_effort` `high`. The two later Judge calls, lines 1415 and 1995 of `rollout-2026-11-12T16-10-25-01a1d198-f957-7ca3-8dbd-f896cf6b6e4f.jsonl`, have the same values, and each Judge log runs `gpt-6-astra` with effort `high`. The brief text is encrypted in the logs.

## AT-19: A Codex ticket builder is fresh and works in its own worktree

App: both
Then: the `spawn_agent` call of the builder has `fork_turns: "none"`, and its brief names the absolute path of the ticket worktree.
Files: `evidence/AT-19/output.txt`
Observation: Line 57 of `rollout-2026-11-12T15-38-49-01a1d17c-07e9-7cf1-98a9-a8eeae498b80.jsonl` calls `spawn_agent` for `ticket01` with `fork_turns` `none` and `gpt-6-astra`, and line 375 of `rollout-2026-11-12T16-10-25-01a1d198-f957-7ca3-8dbd-f896cf6b6e4f.jsonl` does the same for `ticket02_records`. Each brief is encrypted in the log, so the log does not show its text. Each builder starts with the cwd of the main checkout, and its first command, about 5 to 6 seconds after the spawn, uses the absolute `workdir` `/Users/brian.kwon/repos/4thandgoal/.claude/worktrees/readme-module-navigation-01` or `-02`.

## AT-20: The GitHub ruleset guards `main`

App: both
Then: the ruleset targets `main`, needs the check `verdict`, and has the Repository admin role on its bypass list.
Files: `evidence/AT-20/output.txt`
Observation: The ruleset `main`, id 27138716, is `active`, with `conditions.ref_name.include` `~DEFAULT_BRANCH`, and the default branch is `main`. Its rules are `deletion`, `non_fast_forward`, `required_status_checks` with the context `verdict`, and `pull_request`. Its bypass list holds `actor_id` 5, `actor_type` `RepositoryRole`, `bypass_mode` `always`.

## AT-21: The manual steps are written down with values and a check

App: both
Then: the file lists the ruleset on `main`, the project trust in Codex if AT-16 needed it, the skill `research` in `~/.agents/skills/`, and the removal of the stale untracked `AGENTS.md`, `apps/site/AGENTS.md`, and `.codex/config.toml`, each with exact values and a check.
Files: `evidence/AT-21/output.txt`
Observation: `docs/agents/codex.md` has 7 steps. Step 1 is the project trust, step 4 the `research` link, step 5 the ruleset on `main`, and step 6 the removal of `AGENTS.md`, `apps/site/AGENTS.md`, and `.codex/config.toml`. Each step has exact values and a "Check:" line.

## AT-22: The spec adds no Codex plugin manifest

App: both
Then: the command prints nothing.
Files: `evidence/AT-22/output.txt`
Observation: The command prints nothing and exits 1.

## AT-23: No skill file moves

App: both
Then: the output shows no rename and no delete under `.claude/plugin/skills/`.
Files: `evidence/AT-23/output.txt`
Observation: `git diff --stat -M` lists 10 changed files, with 38 insertions and 28 deletions. `git diff --name-status -M` shows `M` for each of the 10 files, and no `R` or `D`.

## AT-24: No product code changes

App: both
Then: no listed file is under `apps/api/`, and each listed file under an `apps/*/src/` folder is a rule test or the shared rule report.
Files: `evidence/AT-24/output.txt`
Observation: The diff lists 9 files, none under `apps/api/`. The one file under an `apps/*/src/` folder is `apps/site/src/readme-rule.test.ts`; the other files are the `AGENTS.md` and `CLAUDE.md` of each app and four files under `apps/pipeline/tests/`, among them `rule_report.py`.
