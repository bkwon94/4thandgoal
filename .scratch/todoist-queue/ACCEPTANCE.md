# Todoist queue: acceptance tests

Spec: `.scratch/todoist-queue/PRD.md`.

The Test verdict: the Judge gives one for each test in `VERDICTS.md`. The Judge is a fresh subagent that reads only this file and the evidence. The PR merges when every test has PASS and Brian gives no FAIL in a PR comment (ADR 0026). The agent that builds the work records the evidence and gives no Test verdict.

The app of a test: `scripts` is the root script and its tests. `tracker` is the files under `.scratch/` and `docs/agents/state.md`. `plugin` is the `4ag` skills. `docs` is the ADRs and `docs/agents/`. `both` is the site and the pipeline.

The queue is the real Todoist project `4thandgoal`. Each real run writes to it. Read the queue for evidence with `td task list --project 4thandgoal --json --all`, `td section list 4thandgoal`, `td label list`, and `td filter list`. Put the nvm `bin` of `td` first on the PATH for these reads.

The throwaway feature: several tests need a label change, a completed task, or a pull. Those tests run on a throwaway feature, so no real ticket changes. Make a temp root, run `git init` in it, and commit a feature `zz-queue-check` with these files:

- `issues/01-zz-ready.md` at `**Status:** ready-for-agent`.
- `issues/02-zz-blocked.md` at `**Status:** blocked`.
- `issues/03-zz-done.md` at `**Status:** done`.
- `decisions/01-grill-zz-question.md` at `**Status:** open`, kind `grill`.
- `decisions/02-research-zz-question.md` at `**Status:** open`, kind `research`.

Run each command with `--root "$T"`. Make each Todoist change of the Given with `td`, and put the command in the evidence. After the last test, delete the section `zz-queue-check` with `td section delete --yes`, and record that command.

## Tests

AT-1: The import loads an open ticket
App: scripts
Stories: 1, 2, 3, 26
Given: the audit of AT-27 is committed on `todoist-queue`, and `.scratch/rankings/pipeline/issues/01-the-formula.md` is `ready-for-agent` after it
When: `python3 scripts/queue.py import` runs in the worktree of `todoist-queue`.
Then: the section `rankings` has the task `01 The formula`, with the labels `ready-for-agent` and `pipeline`, and its description starts with `4ag: .scratch/rankings/pipeline/issues/01-the-formula.md`.
Evidence: the command and its output, and the JSON of that task from `td task list`.

AT-2: A second import changes nothing
App: scripts
Stories: 40, 44
Given: the import of AT-1 is done
When: `python3 scripts/queue.py import --dry-run` runs.
Then: the output lists zero `td` commands that write.
Evidence: the command and its full output.

AT-3: A shared feature gets one section
App: scripts
Stories: 2, 28
Given: the import of AT-1 is done, and `rankings` has a `site/` and a `pipeline/` subfolder
When: the reader lists the tasks of the section `rankings`.
Then: `01 The reader and the route` has the label `site`, and `01 The formula` has the label `pipeline`, both in the one section `rankings`.
Evidence: `td section list 4thandgoal` and the JSON of both tasks.

AT-4: A ticket on a spec branch has no GitHub link
App: scripts
Stories: 12, 13
Given: the import of AT-1 is done, the branch `codex-flow` has no merged PR, and `.scratch/codex-flow/issues/01-the-rules-move-to-agents-md.md` exists only on that branch at `in-review`
When: the reader opens the task `01 The rules move to AGENTS.md`.
Then: it has the label `in-review`, and its description has the line `On the spec branch codex-flow.` and no `github.com` link.
Evidence: the JSON of the task, and `gh pr list --head codex-flow --state all` output.

AT-5: A ticket on main has the full description
App: scripts
Stories: 26, 27, 29, 30
Given: the import of AT-1 is done
When: the reader opens the task `01 The formula`.
Then: its description has, in order, the key line, the app, the blockers, the link `https://github.com/bkwon94/4thandgoal/blob/main/.scratch/rankings/pipeline/issues/01-the-formula.md`, and a summary of 500 characters or fewer that starts "A pure function that takes the history".
Evidence: the JSON of the task.

AT-6: A done ticket stays out of the queue
App: scripts
Stories: none
Given: the import of AT-1 is done, and `.scratch/front-door/issues/01-*.md` is `done` on `main`
When: the reader searches the descriptions of all tasks, open and completed, for `.scratch/front-door/issues/01-`.
Then: no task has that key.
Evidence: the search command over the JSON of `td task list` and `td completed list`, and its empty output.

AT-7: The import makes the labels, the Ideas section, and the filter
App: scripts
Stories: 4, 24
Given: the import of AT-1 is done, and the import of AT-2 ran after it
When: the reader lists the labels, the sections, and the filters.
Then: each of the 11 labels of the flow exists once, the section `Ideas` exists once with no task, and the filter "Waits on Brian" exists once with the query `#4thandgoal & @ready-for-human`.
Evidence: `td label list`, `td section list 4thandgoal`, `td filter list`, and `td task list --project 4thandgoal --section Ideas`.

AT-8: Decision tickets get labels by kind
App: scripts
Stories: 9, 10, 11
Given: the throwaway feature in `"$T"`
When: `python3 scripts/queue.py push` runs for each of its two decision tickets with `--root "$T"`.
Then: `Decision 01: <question>` has `ready-for-human` and `decision`, and `Decision 02: <question>` has `ready-for-agent` and `decision`.
Evidence: the commands, their output, and the JSON of both tasks.

AT-9: A triage label from Brian survives a push
App: scripts
Stories: 18, 22
Given: the task of `01-zz-ready.md` exists, and `td` set its label from `ready-for-agent` to `ready-for-human`, while the file still says `ready-for-agent`
When: `python3 scripts/queue.py push "$T"/.scratch/zz-queue-check/issues/01-zz-ready.md --root "$T"` runs.
Then: the task still has the label `ready-for-human`.
Evidence: the `td` command of the Given, the push command and its output, and the task JSON before and after.

AT-10: A flow status always wins
App: scripts
Stories: 13, 14
Given: the task of `01-zz-ready.md` has `ready-for-human`, and the file then changes to `**Status:** in-review`
When: the push of AT-9 runs again.
Then: the task has the label `in-review` and not `ready-for-human`.
Evidence: the file diff, the push command and its output, and the task JSON before and after.

AT-11: An extra label from Brian stays
App: scripts
Stories: 23
Given: `td` added the label `phone` to the task of `01-zz-ready.md`
When: the push of AT-9 runs again.
Then: the task still has the label `phone`.
Evidence: the `td` command of the Given, the push command, and the task JSON before and after.

AT-12: The priority from Brian stays
App: scripts
Stories: 22
Given: `td` set the priority of the task of `01-zz-ready.md` to p1
When: the push of AT-9 runs again.
Then: the task still has priority p1.
Evidence: the `td` command of the Given, the push command, and the task JSON before and after.

AT-13: A pull writes the triage of Brian into git
App: scripts
Stories: 19, 45
Given: the file of `01-zz-ready.md` is back at `ready-for-agent`, and `td` set its task label to `needs-info`
When: `python3 scripts/queue.py pull zz-queue-check --root "$T"` runs.
Then: the file has the line `**Status:** needs-info`.
Evidence: the command, its output, and `git -C "$T" diff`.

AT-14: A completed task pulls as wontfix
App: scripts
Stories: 20
Given: `td task complete` closed the task of `01-zz-ready.md`, with no comment
When: the pull of AT-13 runs again.
Then: the file has the line `**Status:** wontfix`.
Evidence: the `td` command of the Given, the pull command, its output, and `git -C "$T" diff`.

AT-15: A completed task with a done comment pulls as done
App: scripts
Stories: 21
Given: the file of `01-zz-ready.md` is back at `ready-for-agent`, and `td` added the comment "done in #34" to its task and completed it
When: the pull of AT-13 runs again.
Then: the file has the line `**Status:** done`.
Evidence: the `td` commands of the Given, the pull command, its output, and `git -C "$T" diff`.

AT-16: A failed pull changes no file
App: scripts
Stories: 46
Given: the temp root has no uncommitted change
When: `TODOIST_API_TOKEN=invalid python3 scripts/queue.py pull zz-queue-check --root "$T"` runs.
Then: the command exits 0 with a warning line, and `git -C "$T" status --short` prints nothing.
Evidence: the command, its output, its exit code, and the `git status` output.

AT-17: A wait task opens and closes
App: scripts
Stories: 5, 6, 7
Given: the throwaway feature has no wait task
When: `python3 scripts/queue.py wait zz-queue-check approve-prd --root "$T"` runs, then the same command with `--done`.
Then: the first run makes the task `Approve PRD` in the section `zz-queue-check` with `ready-for-human`, and the second run completes it.
Evidence: both commands, their output, and the task JSON after each run.

AT-18: A merged PR closes the tasks of its done tickets
App: scripts
Stories: 8, 15
Given: the tasks of all three zz tickets are open, and `wait zz-queue-check merge-pr 34 --root "$T"` made `Merge PR #34`. PR #34 is merged.
When: `python3 scripts/queue.py sweep --root "$T"` runs.
Then: the tasks of `03-zz-done.md` and `Merge PR #34` are complete.
Evidence: the commands, their output, `gh pr view 34 --json state`, and the task JSON after.

AT-19: An open ticket keeps its task and the section
App: scripts
Stories: 16
Given: the sweep of AT-18 ran, and `02-zz-blocked.md` is still `blocked`
When: the reader lists the open tasks and the sections.
Then: the task of `02-zz-blocked.md` is open, and the section `zz-queue-check` is not archived.
Evidence: the task JSON and `td section list 4thandgoal`.

AT-20: A feature with every task complete gets its section archived
App: scripts
Stories: 16
Given: the files of `01-zz-ready.md` and `02-zz-blocked.md` change to `done`, and a new `Merge PR #34` wait task exists
When: the sweep of AT-18 runs again.
Then: every task of the section is complete, and the section `zz-queue-check` is archived.
Evidence: the file diff, the command and its output, and `td section list 4thandgoal` before and after.

AT-21: A PR closed without a merge gives blocked
App: scripts
Stories: 17
Given: the section `zz-queue-check` is unarchived, and `wait zz-queue-check merge-pr 16 --root "$T"` made `Merge PR #16`. PR #16 closed without a merge.
When: the sweep of AT-18 runs again.
Then: `Merge PR #16` is open with the label `blocked`.
Evidence: the commands, their output, `gh pr view 16 --json state,mergedAt`, and the task JSON.

AT-22: A failed push warns and the work goes on
App: scripts
Stories: 38, 39
Given: the throwaway feature
When: `TODOIST_API_TOKEN=invalid python3 scripts/queue.py push "$T"/.scratch/zz-queue-check/issues/02-zz-blocked.md --root "$T"` runs.
Then: the command exits 0 and prints one warning line that names `02-zz-blocked.md`.
Evidence: the command, its full output, and its exit code.

AT-23: The script finds td with no PATH
App: scripts
Stories: 43
Given: the import of AT-1 is done
When: `env -i HOME="$HOME" /usr/bin/python3 scripts/queue.py import --dry-run` runs in the worktree.
Then: the output lists the planned `td` commands, or zero commands, and has no error that `td` or `node` is not found.
Evidence: the command, its full output, and its exit code.

AT-24: A dry run sends nothing
App: scripts
Stories: 42
Given: the throwaway feature has a new ticket `04-zz-new.md` with no task
When: `python3 scripts/queue.py push "$T"/.scratch/zz-queue-check/issues/04-zz-new.md --dry-run --root "$T"` runs.
Then: the output names a `td task add` command, and the count of open tasks in the project is the same before and after.
Evidence: the command, its output, and the task count before and after.

AT-25: The script tests pass on real fixtures
App: scripts
Stories: 42, 44, 48
Given: the finished script and its tests on `todoist-queue`
When: `make check-scripts` runs at the root.
Then: it passes, and the run lists the cases of `test_queue`.
Evidence: the command and its full output, with `-v` on the unittest run.

AT-26: The audit report covers each open ticket
App: tracker
Stories: 31, 32, 33, 35
Given: `main` at the start of the spec, with each open ticket under `issues/`
When: the reader compares `.scratch/todoist-queue/audit.md` with the open tickets of `main`.
Then: each open ticket appears once, under its feature, with `done` and a commit, `wontfix` and a reason, or `open` and a label, and each named commit exists in `git log`.
Evidence: `audit.md`, the list of open tickets of `main`, and a check that runs `git cat-file -e` on each named commit.

AT-27: The approved audit lands in the tracker
App: tracker
Stories: 34, 36
Given: Brian approved `audit.md`
When: the reader compares each `Status:` line on `todoist-queue` with its approved line.
Then: each line matches, `docs/agents/state.md` lists each feature with an open ticket, and no ticket has the status `triage`, `built`, `accepted`, or `backlog`.
Evidence: the compare script and its output, the `state.md` diff, and a grep for the four strings with empty output.

AT-28: The tracker rule rejects an odd status
App: both
Stories: 37
Given: a planted ticket `.scratch/zz-rule/issues/01-zz.md` at `**Status:** backlog`, staged in git and never committed
When: the tracker rule of the pipeline and the tracker rule of the site run.
Then: both fail and name `.scratch/zz-rule/issues/01-zz.md`.
Evidence: both commands and their output, then the removal of the planted file.

AT-29: Each skill calls the script at each push point
App: plugin
Stories: 42, 45, 47
Given: the finished skill files of the `4ag` plugin
When: the reader greps the skill files for `scripts/queue.py`.
Then: each row of the push table in the PRD has a call in its skill at its step, and each skill starts with `sweep`.
Evidence: the grep output, laid beside the push table.

AT-30: The records say what the queue owns
App: docs
Stories: 41, 50
Given: the finished records on `todoist-queue`
When: the reader opens ADR 0032, `docs/agents/issue-tracker.md`, `docs/agents/triage-labels.md`, and `GLOSSARY.md`.
Then: ADR 0032 says it amends ADR 0021 and that the tracker in `.scratch/` stays the record. The two docs name the queue, its labels, the key line, and the script. The glossary has Queue, Wait task, and Merge sweep.
Evidence: the text of each part.

AT-31: CI never calls td
App: both
Stories: none
Given: the finished branch `todoist-queue`
When: the reader greps `.github/`, `Makefile`, and the Makefiles of the apps for `td ` and `queue.py`.
Then: the only hit is the `scripts-check` target, which runs unit tests that call no `td`.
Evidence: the grep output.

AT-32: A push does not sync the body or the comments
App: scripts
Stories: none
Given: the task of `02-zz-blocked.md` exists, and the file gets a new line under `## Comments`
When: the push of AT-22 runs without the invalid token.
Then: the task has no Todoist comment, and its description is the same as before.
Evidence: the file diff, the command, `td comment list` of the task, and the task JSON before and after.

## Trace

Story 1: AT-1
Story 2: AT-1, AT-3
Story 3: AT-1
Story 4: AT-7
Story 5: AT-17
Story 6: AT-17. The `approve-acceptance` kind also has a call in AT-29 and a unit test in AT-25.
Story 7: AT-17. The `approve-tickets` kind also has a call in AT-29 and a unit test in AT-25.
Story 8: AT-18
Story 9: AT-8
Story 10: AT-8
Story 11: AT-8
Story 12: AT-4
Story 13: AT-4, AT-10
Story 14: AT-10
Story 15: AT-18
Story 16: AT-19, AT-20
Story 17: AT-21
Story 18: AT-9
Story 19: AT-13
Story 20: AT-14
Story 21: AT-15
Story 22: AT-9, AT-12
Story 23: AT-11
Story 24: AT-7
Story 25: no test. Reason: no script reads the `Ideas` section, and AT-7 shows it stays empty after the import.
Story 26: AT-1, AT-5
Story 27: AT-5
Story 28: AT-3
Story 29: AT-5
Story 30: AT-5
Story 31: AT-26
Story 32: AT-26
Story 33: AT-26
Story 34: AT-27
Story 35: AT-26
Story 36: AT-27
Story 37: AT-28
Story 38: AT-22
Story 39: AT-22
Story 40: AT-2
Story 41: AT-30
Story 42: AT-24, AT-25, AT-29
Story 43: AT-23
Story 44: AT-2, AT-25
Story 45: AT-13, AT-29
Story 46: AT-16
Story 47: AT-29
Story 48: AT-25. No real run: the keychain also works from `env -i`, so a local run cannot tell the token from the keychain.
Story 49: each test with a real run.
Story 50: AT-30
Out of scope "A GitHub Action or any CI call to Todoist": AT-31
Out of scope "A two-way sync of the ticket body or the comments": AT-32
Out of scope "The `done` tickets on `main`": AT-6

## Revisions

None yet.
