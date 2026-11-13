# 4thandgoal

This repo holds three apps. The site and the pipeline each have an AGENTS.md with its own commands and rules. Read the one for the app you change.

- `apps/site/` is the Next.js site. Its build copies `clients/<slug>/published/` of one client into `public/` and renders each `page.json` and its images.
- `apps/pipeline/` is the Python pipeline. It builds each week and publishes it into `clients/<slug>/published/`.
- `apps/api/` is the API of the trade analyzer. It imports the pipeline and deploys to Fly. Run `make help` in it.

The root holds one uv workspace and one pnpm workspace, each with one lock file: `uv.lock` and `pnpm-lock.yaml`.
Run `uv sync --all-packages` and `pnpm install` at the root. A member runs with `uv run --exact --package <name>`.

## Style

Write all output in Simplified Technical English. Rules: `~/.claude/rules/communication/simplified-technical-english.md`. Active voice, present tense, one instruction per sentence, 20 words or fewer, no `-ing` as a verb, plain words. Code, technical names, and quoted output are exempt.

## Records

- `GLOSSARY.md` holds the terms of both apps, one section per app, and the workflow terms. Each term has one meaning.
- `docs/adr/` holds one ADR series for both apps. `docs/adr/README.md` maps each old app number to its new number.

## The flow

ADRs 0018 to 0021 and ADR 0026 set the flow. ADR 0026 supersedes ADR 0020. The spec `.scratch/one/` builds it, so its own tickets still merge to `main` as before.

1. `main` is the record branch. No agent commits on `main` or pushes to `main` (ADR 0019).
2. A spec branch is named `<slug>` and starts from `main`.
3. A ticket branch is named `<slug>-<NN>`. It is local, starts from the spec branch, and has its own worktree.
4. A ticket merges into its spec branch with `git merge --no-edit`, after the check passes.
5. One pull request goes from the spec branch to `main`, as a squash merge.
6. An agent records the evidence of each acceptance test `AT-<n>`. The agent gives no test verdict.
7. A fresh subagent, the Judge, gives PASS, FAIL, or BLOCKED for each test in `VERDICTS.md`. A check blocks the merge until each test has PASS. A FAIL from Brian in a PR comment overrides the Judge (ADR 0026).

The weekly `publish` is the one exception. It may push to `main`, and it may stage only `clients/<slug>/published/<season>/`, `clients/<slug>/data/<season>/`, and `clients/<slug>/build/<season>/`.

The repo plugin `4ag` takes an idea to a merged spec. Run its skills in this order. Brian approves the output of each of steps 2 to 4.

1. `4ag:plan <outcome statement>` writes the map and the decision tickets. `4ag:plan <feature>` clears one decision ticket per session.
2. `4ag:to-spec <feature>` writes `PRD.md`.
3. `4ag:to-acceptance <feature>` writes `ACCEPTANCE.md`.
4. `4ag:to-tickets <feature>` writes the tickets and the `state.md` row.
5. `4ag:implement <feature>` builds each ticket on its ticket branch, merges it into the spec branch, records the evidence in `EVIDENCE.md`, has the Judge write `VERDICTS.md`, and opens one PR to `main`.
6. Brian posts no comment unless he gives a FAIL. `4ag:review <PR number>` does one round of feedback per run. The check `verdict` passes when each test has PASS from the Judge and no FAIL from Brian, and Brian merges.

A bug or a small change skips the spec flow. Run `4ag:quick <description or queue task>` instead. It writes a quick file of up to five items of one kind. It builds each item with `diagnosing-bugs` or `tdd`, has a fresh Judge give each Test verdict, and opens one PR. ADR 0033 sets the rules.

## The harness words

The 4ag skills run in Claude Code and in Codex. The skill text uses neutral words. This table maps each one to the tool of each harness.

| The skill says | Claude Code | Codex |
| --- | --- | --- |
| The skill `<name>` is in the available skill list | The skill list of the session names it. | The skill list names it, or `~/.agents/skills/<name>/SKILL.md` exists. Codex hides a skill whose `agents/openai.yaml` sets `allow_implicit_invocation: false`, such as `to-spec`. |
| Load the skill `<name>` | The Skill tool. | A `$<name>` mention, or a read of the `SKILL.md` of the skill. |
| Start a fresh subagent | The Agent tool with `subagent_type: general-purpose`. Never use `fork`, because a fork gets the context of the session. | `spawn_agent` with `fork_turns: "none"`. Keep at most 6 open at a time. Close each finished one with `close_agent`. |
| Start the subagents at the same time, within the limit of the harness | Several Agent tool calls in one message, so they run in parallel. | `spawn_agent` for at most 6 at a time. Close each finished one with `close_agent` before you start the next. |
| Run it in the background | The Bash tool with `run_in_background`. | A background shell command. |
| A scratch folder outside the repo, `<scratch>` | The scratchpad of the session. | `$TMPDIR`. |
| With the default model | `model: sonnet`. | Set no `model`. The subagent uses the default model of the session. |
| With the strong model | `model: opus`. | `model: "gpt-6-astra"` with `reasoning_effort: "high"`. |
| The permission profile of the harness | The permission of the session itself. | The profile `4ag` in `.codex/config.toml`. The fix is in `docs/agents/codex.md`. |
| The global skill `research` | `mattpocock-skills:research`. | `mattpocock-skills:research` in the skill list. It counts as present when `~/.agents/skills/research/SKILL.md` exists. |
| The global skill `diagnosing-bugs` | `mattpocock-skills:diagnosing-bugs`. | `mattpocock-skills:diagnosing-bugs` in the skill list. It counts as present when `~/.agents/skills/diagnosing-bugs/SKILL.md` exists. Step 8 of `docs/agents/codex.md` installs it. |

Each other global skill has the same name in both harnesses.

In Codex, start the session at the main checkout root, never in a worktree. Codex in a linked worktree cannot write its own gitdir.

## Tracker

The tracker is local markdown, because the notes name league managers and the repo is public (ADR 0021).

- The tracker is `.scratch/<feature>/` at the root, for both apps. See `docs/agents/issue-tracker.md`.
- A feature that both old trackers held keeps a `site/` and a `pipeline/` subfolder, each with its own PRD and `issues/`.
- A new feature has an optional `MAP.md`, `decisions/`, `PRD.md`, `ACCEPTANCE.md`, and `issues/`. Old features keep their shape.

## Where the work sits

`docs/agents/state.md` lists each open feature, its next ticket, and its blocker. An agent new to the repo reads it
after this file, then reads one ticket in the tracker.

## Commits

The prek hook runs `pnpm check:fast` of the site, then `make check-fast` of the pipeline and of the API, before each commit.
The prek hook needs Node 24 or later first on PATH, because Node 22.17 cannot read the `.ts` files of `packages/design`.
Never commit with `--no-verify`.
