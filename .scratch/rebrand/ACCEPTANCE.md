# Rebrand: acceptance tests

Spec: `.scratch/rebrand/PRD.md`.

The Test verdict: the Judge gives one for each test in `VERDICTS.md`. The Judge is a fresh subagent that reads only this file and the evidence. The PR merges when every test has PASS and Brian gives no FAIL in a PR comment (ADR 0026). The agent that builds the work records the evidence and gives no Test verdict.

Run every command from the root of the worktree of the Spec branch `rebrand`, after the last ticket merges into it. "On `main`" means the same command on `origin/main`, through `git grep <pattern> origin/main` or `git diff origin/main`.

The move of the folder happens after the merge, so no test here covers the real move. The close comment of the runbook ticket records the real checks: `git worktree list`, `launchctl list | grep cornerstone`, and `/plugin`.

## Tests

AT-1: The plugin and its marketplace are named 4ag
App: both
Stories: 2, 4
Given: the Spec branch `rebrand` with every ticket merged
When: the agent runs `claude plugin validate .claude/plugin` and `claude plugin validate .`.
Then: both commands print `Validation passed`, the plugin manifest has `"name": "4ag"`, and the marketplace manifest has `"name": "4ag-local"` and lists a plugin named `4ag`.
Evidence: the two commands and their full output, and the two manifest files.

AT-2: The project settings enable the plugin 4ag
App: both
Stories: 4, 18
Given: the Spec branch `rebrand` with every ticket merged
When: the agent runs `cat .claude/settings.json`.
Then: the file names the marketplace `4ag-local` with the source path `./`, enables `4ag@4ag-local`, and names no `cpc-local` and no `cpc@`.
Evidence: the command and the full file.

AT-3: No skill call names the prefix cpc
App: both
Stories: 3, 6, 7, 10
Given: the Spec branch `rebrand` with every ticket merged
When: the agent runs `git grep -nE 'cpc:(plan|implement|review|to-spec|to-acceptance|to-tickets)' -- ':!.scratch' ':!docs/adr'`.
Then: the command prints nothing.
Evidence: the command and its output, and the same command on `main` with its line count, to show the change.

AT-4: CLAUDE.md lists the six skills as 4ag
App: both
Stories: 5
Given: the Spec branch `rebrand` with every ticket merged
When: the agent runs `grep -oE '4ag:(plan|to-spec|to-acceptance|to-tickets|implement|review)' CLAUDE.md | sort -u`.
Then: the output has six lines: `4ag:implement`, `4ag:plan`, `4ag:review`, `4ag:to-acceptance`, `4ag:to-spec`, and `4ag:to-tickets`. The title line of `CLAUDE.md` is `# 4thandgoal`.
Evidence: the command and its output, and the first line of `CLAUDE.md`.

AT-5: No file names the old folder
App: both
Stories: 1, 8, 11, 13
Given: the Spec branch `rebrand` with every ticket merged
When: the agent runs `git grep -n cpcfantasyfootball -- ':!.scratch' ':!docs/adr' ':!apps/site/docs/runbook-site-host.md' ':!docs/agents/folder-move.md' ':!pnpm-lock.yaml' ':!uv.lock'`.
Then: the command prints nothing. The excluded runbook line is wrangler output that the doc quotes, so it stays. The runbook of the folder move names the old folder, because it moves it.
Evidence: the command and its output, the same command on `main` with its line count, and `grep -c cpcfantasyfootball pnpm-lock.yaml`, which prints `0`.

AT-6: The verdict check keeps its marker and names 4ag review
App: both
Stories: 9, 10
Given: the Spec branch `rebrand` with every ticket merged
When: the agent runs `grep -n 'AGENT_MARKER =' scripts/verdict.py`, `grep -n '4ag:review' scripts/verdict.py`, and the `verdict` tests under `scripts/`.
Then: the marker line is `AGENT_MARKER = "<!-- cpc:agent -->"`, the help message names `4ag:review`, the fixtures under `scripts/fixtures/verdict/` have no diff from `main`, and the tests pass.
Evidence: the three commands and their output, and `git diff origin/main --stat -- scripts/fixtures/verdict`, which prints nothing.

AT-7: The site package is named 4thandgoal-site
App: site
Stories: 11
Given: the Spec branch `rebrand` with every ticket merged
When: the agent runs `node -p "require('./apps/site/package.json').name"`, then `pnpm check:fast` in `apps/site`.
Then: the first command prints `4thandgoal-site`, and the check exits 0.
Evidence: both commands, the first output in full, and the tail of the check output with its exit code.

AT-8: The fast checks of the scripts, the pipeline, and the API pass
App: both
Stories: 25
Given: the Spec branch `rebrand` with every ticket merged
When: the agent runs `make check-fast` in `scripts/`, `apps/pipeline/`, and `apps/api/`.
Then: each run exits 0.
Evidence: each command, the tail of its output, and its exit code.

AT-9: The weekly build script finds the repo from its own path
App: pipeline
Stories: 12
Given: a ticket worktree of the Spec branch, at a path that is not `~/repos/cpcfantasyfootball` and not `~/repos/4thandgoal`
When: the agent runs `grep -n 'repos/' apps/pipeline/bin/cornerstone-build`, then runs only the lines that set `REPO_DIR`, with the script path of that worktree as `$0`, and prints `REPO_DIR`.
Then: the grep prints nothing, and the printed `REPO_DIR` is the absolute path of `apps/pipeline` in that worktree.
Evidence: the worktree path, both commands, and their output. No full build runs.

AT-10: The LaunchAgent names the new folder
App: pipeline
Stories: 13
Given: the Spec branch `rebrand` with every ticket merged
When: the agent runs `plutil -lint apps/pipeline/launchagents/com.briankwon.cornerstone-weekly.plist` and `grep -n 'repos/' apps/pipeline/launchagents/com.briankwon.cornerstone-weekly.plist`.
Then: `plutil` prints `OK`, and each path that the grep prints starts with `/Users/brian.kwon/repos/4thandgoal/`.
Evidence: both commands and their output.

AT-11: The runbook gives each step of the move in order
App: both
Stories: 14, 15, 16, 17, 18, 19, 20, 21
Given: the Spec branch `rebrand` with every ticket merged
When: the Judge reads the runbook of the folder move in `docs/agents/`.
Then: the runbook says to move on a day other than Tuesday, because the weekly build runs Tuesday at 08:00. It gives nine steps in this order, each with one command and one check command: stop the LaunchAgent; remove the worktrees of merged specs; move `~/repos/cpcfantasyfootball` to `~/repos/4thandgoal`; run `git worktree repair`; move the Claude memory folder `-Users-brian-kwon-repos-cpcfantasyfootball` to `-Users-brian-kwon-repos-4thandgoal`; set the marketplace key `4ag-local` and its path in `~/.claude/settings.json`; rebuild the venv and the node modules; copy and load the LaunchAgent; open a new session and call one `4ag:` skill.
Evidence: the full runbook file.

AT-12: The git steps of the move work on a rehearsal
App: both
Stories: 1, 14, 16
Given: a fresh `git clone` of the repo in the scratchpad, with one worktree added under its `.claude/worktrees/`
When: the agent moves the clone to a new folder name, then runs the `git worktree repair` command of the runbook in the moved clone.
Then: `git worktree list` in the moved clone shows the new folder path and the worktree, and no line says `prunable`. `git -C <worktree> status` exits 0.
Evidence: each command in order and its full output. The agent deletes the rehearsal folders after the run.

AT-13: No page, package, client, or API code changes
App: both
Stories: 22, 23
Given: the Spec branch `rebrand` with every ticket merged
When: the agent runs `git diff origin/main --stat -- apps/site/src packages clients apps/api/src apps/pipeline/src`.
Then: the command prints nothing.
Evidence: the command and its output.

AT-14: The domain and the Fly app stay
App: both
Stories: 22, 23
Given: the Spec branch `rebrand` with every ticket merged
When: the agent runs `git grep -cF '4thandgoal.app' -- ':!.scratch' | awk -F: '{s+=$2} END {print s}'` on the Spec branch and on `main`, and `grep -n '^app' apps/api/fly.toml`.
Then: the two counts are equal, and `fly.toml` has `app = "cpcfantasy-api"`.
Evidence: the three commands and their output.

AT-15: The package names stay
App: both
Stories: 24
Given: the Spec branch `rebrand` with every ticket merged
When: the agent counts the lines that hold `@cpc/` and the lines that hold `cornerstone_api` with `git grep -c`, outside `.scratch/`, on the Spec branch and on `main`.
Then: each count on the Spec branch equals its count on `main`.
Evidence: the commands and the four counts.

AT-16: The records stay
App: both
Stories: 24
Given: the Spec branch `rebrand` with every ticket merged
When: the agent runs `git diff origin/main --stat -- docs/adr .scratch`.
Then: every path in the output is under `.scratch/rebrand/`.
Evidence: the command and its output.

## Trace

Story 1: AT-5, AT-12
Story 2: AT-1
Story 3: AT-3
Story 4: AT-1, AT-2
Story 5: AT-4
Story 6: AT-3
Story 7: AT-3
Story 8: AT-5
Story 9: AT-6
Story 10: AT-3, AT-6
Story 11: AT-5, AT-7
Story 12: AT-9
Story 13: AT-5, AT-10
Story 14: AT-11, AT-12
Story 15: AT-11
Story 16: AT-11, AT-12
Story 17: AT-11
Story 18: AT-2, AT-11
Story 19: AT-11
Story 20: AT-11
Story 21: AT-11
Story 22: AT-13, AT-14
Story 23: AT-13, AT-14
Story 24: AT-15, AT-16
Story 25: AT-8, and the evidence line of every test
Out of scope "A new Product name and a new domain": AT-14
Out of scope "A new Fly app": AT-14
Out of scope "A rename of `cornerstone`, `cornerstone_api`, the `@cpc/*` npm names, and the `cpc-*` Python names": AT-15
Out of scope "A rename of the client `cpc`": AT-13
Out of scope "A rewrite of the ADRs or of the text under `.scratch/`": AT-16
Out of scope "A change to the verdict marker": AT-6
Out of scope "A product brand on the page": AT-13

## Revisions

- 2026-11-11, Brian approved: AT-5 also excludes `docs/agents/folder-move.md`, because the runbook must name the old folder. AT-14 counts with `git grep -cF`, because the `.` of `4thandgoal.app` matched `4thandgoal/apps/` in the new LaunchAgent path.
