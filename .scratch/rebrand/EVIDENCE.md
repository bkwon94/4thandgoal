# Rebrand: evidence

Spec: `.scratch/rebrand/PRD.md`. Acceptance tests: `.scratch/rebrand/ACCEPTANCE.md`.
Built from: `434ba546`, on 2026-11-11. The agent gives no Test verdict. The Judge gives one for each test in `VERDICTS.md`.
Round time: 0 min for 0 site tests. No test asks for screenshots.

A note on exit codes: `git grep` and `grep -c` exit 1 when they find no match. So `[exit 1]` after an empty grep output means "no match".

## AT-1: The plugin and its marketplace are named 4ag

App: both
Then: both commands print `Validation passed`, the plugin manifest has `"name": "4ag"`, and the marketplace manifest has `"name": "4ag-local"` and lists a plugin named `4ag`.
Files: `evidence/AT-1/output.txt`
Observation: Both `claude plugin validate` runs print `✔ Validation passed` and exit 0. The plugin manifest has `"name": "4ag"`, and the marketplace manifest has `"name": "4ag-local"` with one plugin `"name": "4ag"`. The validator also lists README, LICENSE, and icon items for a public directory listing, and it says they do not change the result.

## AT-2: The project settings enable the plugin 4ag

App: both
Then: the file names the marketplace `4ag-local` with the source path `./`, enables `4ag@4ag-local`, and names no `cpc-local` and no `cpc@`.
Files: `evidence/AT-2/output.txt`
Observation: `.claude/settings.json` has the marketplace key `4ag-local` with `"path": "./"` and `"4ag@4ag-local": true`. The file holds no `cpc-local` and no `cpc@`.

## AT-3: No skill call names the prefix cpc

App: both
Then: the command prints nothing.
Files: `evidence/AT-3/output.txt`
Observation: The grep on the Spec branch prints nothing. The same grep on `origin/main` counts 44 lines.

## AT-4: CLAUDE.md lists the six skills as 4ag

App: both
Then: the output has six lines: `4ag:implement`, `4ag:plan`, `4ag:review`, `4ag:to-acceptance`, `4ag:to-spec`, and `4ag:to-tickets`. The title line of `CLAUDE.md` is `# 4thandgoal`.
Files: `evidence/AT-4/output.txt`
Observation: The command prints the six lines in that order, and `head -1 CLAUDE.md` prints `# 4thandgoal`.

## AT-5: No file names the old folder

App: both
Then: the command prints nothing. The excluded runbook line is wrangler output that the doc quotes, so it stays. The runbook of the folder move names the old folder, because it moves it.
Files: `evidence/AT-5/output.txt`
Observation: The grep on the Spec branch prints nothing. The same grep on `origin/main` counts 10 lines. `grep -c cpcfantasyfootball pnpm-lock.yaml` prints `0`. The last part of the file shows the excluded runbook line inside a quoted `wrangler` output block, and shows that `docs/agents/folder-move.md` is the runbook that moves `~/repos/cpcfantasyfootball`.

## AT-6: The verdict check keeps its marker and names 4ag review

App: both
Then: the marker line is `AGENT_MARKER = "<!-- cpc:agent -->"`, the help message names `4ag:review`, the fixtures under `scripts/fixtures/verdict/` have no diff from `main`, and the tests pass.
Files: `evidence/AT-6/output.txt`, `evidence/AT-6/head-diff.txt`
Observation: Line 28 is `AGENT_MARKER = "<!-- cpc:agent -->"`, and line 218 names `4ag:review`. The diff of `scripts/fixtures/verdict` against `origin/main` prints nothing. The 21 tests of `test_verdict.py` run and print `OK`. The run is at `34477b17`, and `head-diff.txt` shows that only `docs/agents/folder-move.md` changed from there to `434ba546`.

## AT-7: The site package is named 4thandgoal-site

App: site
Then: the first command prints `4thandgoal-site`, and the check exits 0.
Files: `evidence/AT-7/output.txt`
Observation: The run is at `434ba546`. `env node -p` prints `4thandgoal-site` and exits 0. The `env` skips a shell function named `node` in the agent shell. `pnpm check:fast` in `apps/site` passes 1334 tests in 131 files and exits 0.

## AT-8: The fast checks of the scripts, the pipeline, and the API pass

App: both
Then: each run exits 0.
Files: `evidence/AT-8/output.txt`, `evidence/AT-8/head-diff.txt`
Observation: `scripts/` has no Makefile, so the root `make check-fast` runs its tests in the section `==> scripts: check-fast`. That run shows the scripts, pipeline, and API sections and exits 0. `make -C apps/pipeline check-fast` and `make -C apps/api check-fast` each exit 0. The runs are at `34477b17`, and `head-diff.txt` shows that only the runbook changed from there to the head.

## AT-9: The weekly build script finds the repo from its own path

App: pipeline
Then: the grep prints nothing, and the printed `REPO_DIR` is the absolute path of `apps/pipeline` in that worktree.
Files: `evidence/AT-9/output.txt`, `evidence/AT-9/head-diff.txt`
Observation: The run is in the detached worktree `.claude/worktrees/rebrand-evidence`, not in the main checkout. `grep -n 'repos/'` prints nothing. The `REPO_DIR` line, run with that worktree's script path as `$0`, prints `/Users/brian.kwon/repos/cpcfantasyfootball/.claude/worktrees/rebrand-evidence/apps/pipeline`. No full build ran.

## AT-10: The LaunchAgent names the new folder

App: pipeline
Then: `plutil` prints `OK`, and each path that the grep prints starts with `/Users/brian.kwon/repos/4thandgoal/`.
Files: `evidence/AT-10/output.txt`
Observation: `plutil -lint` prints `OK`. The grep prints one path, `/Users/brian.kwon/repos/4thandgoal/apps/pipeline/bin/cornerstone-build`.

## AT-11: The runbook gives each step of the move in order

App: both
Then: the runbook says to move on a day other than Tuesday, because the weekly build runs Tuesday at 08:00. It gives nine steps in this order, each with one command and one check command: stop the LaunchAgent; remove the worktrees of merged specs; move `~/repos/cpcfantasyfootball` to `~/repos/4thandgoal`; run `git worktree repair`; move the Claude memory folder `-Users-brian-kwon-repos-cpcfantasyfootball` to `-Users-brian-kwon-repos-4thandgoal`; set the marketplace key `4ag-local` and its path in `~/.claude/settings.json`; rebuild the venv and the node modules; copy and load the LaunchAgent; open a new session and call one `4ag:` skill.
Files: `evidence/AT-11/folder-move.md`
Observation: The file is a copy of `docs/agents/folder-move.md` at `434ba546`. It opens with the Tuesday 08:00 warning, then has sections 1 to 9 in the order of the Then line. Each section has a command block and a line that starts with `Check:`.

## AT-12: The git steps of the move work on a rehearsal

App: both
Then: `git worktree list` in the moved clone shows the new folder path and the worktree, and no line says `prunable`. `git -C <worktree> status` exits 0.
Files: `evidence/AT-12/output.txt`, `evidence/AT-12/head-diff.txt`
Observation: Before the repair, `git worktree list` marks the worktree `prunable`. After the step 4 command of the runbook at `6183edcb`, the list shows `new-name` and `new-name/.claude/worktrees/wt-a` with no `prunable`. `git status` in the worktree prints `On branch wt-a` and exits 0. The last lines show that the rehearsal folder is gone. `head-diff.txt` shows that only step 2 of the runbook changed after `6183edcb`, and step 4 is the same.

## AT-13: No page, package, client, or API code changes

App: both
Then: the command prints nothing.
Files: `evidence/AT-13/output.txt`
Observation: The `git diff origin/main --stat` over the site source, `packages`, `clients`, and the API and pipeline source prints nothing and exits 0.

## AT-14: The domain and the Fly app stay

App: both
Then: the two counts are equal, and `fly.toml` has `app = "cpcfantasy-api"`.
Files: `evidence/AT-14/output.txt`
Observation: The fixed-string count of `4thandgoal.app` is 39 on the Spec branch and 39 on `origin/main`. `fly.toml` line 5 is `app = "cpcfantasy-api"`.

## AT-15: The package names stay

App: both
Then: each count on the Spec branch equals its count on `main`.
Files: `evidence/AT-15/output.txt`
Observation: `@cpc/` counts 608 on both refs, and `cornerstone_api` counts 127 on both refs.

## AT-16: The records stay

App: both
Then: every path in the output is under `.scratch/rebrand/`.
Files: `evidence/AT-16/output.txt`
Observation: The `--stat` output cuts long paths, so the file also has the `--name-only` list. Each of its 15 paths starts with `.scratch/rebrand/`, and no path is under `docs/adr`.
