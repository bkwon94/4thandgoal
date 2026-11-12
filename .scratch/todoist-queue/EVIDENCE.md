# Todoist queue: evidence

Spec: `.scratch/todoist-queue/PRD.md`. Acceptance tests: `.scratch/todoist-queue/ACCEPTANCE.md`.
Built from: `f0461df6`, on 2026-11-12. The agent gives no Test verdict. The Judge gives one for each test in `VERDICTS.md`.
Round time: 0 min for 0 site tests. No test of this spec is a site test.

Each `output.txt` holds each command after `$ `, then its full output, then its exit code. A line that starts with `#` is a note of the agent.
The throwaway feature sits in the temp root `/private/tmp/claude-503/-Users-brian-kwon-repos-4thandgoal/20f729f2-2f60-4416-a60b-31e97ea470fa/scratchpad/zzq`, a `git init` repo with the branch `main`. Its first commit holds the five files that the top of `ACCEPTANCE.md` names. `evidence/AT-8/output.txt` shows the commit and the Status line of each file.
The real queue held the section `pick-reason` until Brian deleted it on purpose. A real `import` would make it again, so AT-1, AT-2, and AT-23 use `import --dry-run`. Its summary line names league managers, so the saved output trims that one line.
`evidence/real-td/` holds real `td` JSON from the throwaway runs: the open zz tasks after AT-12, the completed zz tasks, the comments of the task of AT-15, and the zz section.

## AT-1: The import loads an open ticket

App: scripts
Then: the section `manager-pages` has the task `12 Drop awards from the managers entry`, with the labels `ready-for-agent` and `pipeline`, and its description starts with `4ag: .scratch/manager-pages/pipeline/issues/12-drop-awards-from-managers-entry.md`.
Files: `evidence/AT-1/output.txt`, `evidence/AT-1/task.json`
Observation: The command ran as `import --dry-run`, because a real import would make the deleted section `pick-reason` again. The dry run plans 5 commands: the section and one task of `pick-reason`, and a label update of three tickets whose files moved to `in-review` or `blocked` after the import of ticket 06. The task JSON comes from that import of ticket 06. It shows `12 Drop awards from the managers entry` in the section `6j23MX6W842H5FGG`, which `td section list` names `manager-pages` in AT-3. It has the labels `pipeline` and `ready-for-agent`, and its description starts with `4ag: .scratch/manager-pages/pipeline/issues/12-drop-awards-from-managers-entry.md`. The file of ticket 12 has `**Status:** ready-for-agent`.

## AT-2: A second import changes nothing

App: scripts
Then: the output lists zero `td` commands that write.
Files: `evidence/AT-2/output.txt`
Observation: Brian chose to delete the local branch `pick-reason`, so the import no longer counts it as a live spec. A real `import` then sent 3 label updates, for `readme-module-navigation` 02 and `todoist-queue` 06 and 07, whose files changed after the first import. The next `import --dry-run` lists no command and ends with "0 commands planned, none sent.".

## AT-3: A shared feature gets one section

App: scripts
Then: `11 The bench sentence and the odds change words` has the label `site`, and `12 Drop awards from the managers entry` has the label `pipeline`, both in the one section `manager-pages`.
Files: `evidence/AT-3/output.txt`
Observation: `td section list 4thandgoal` lists one section `manager-pages`, with the id `6j23MX6W842H5FGG`. Task 11 has the labels `ready-for-human` and `site`, and task 12 has `pipeline` and `ready-for-agent`. Both have the `sectionId` `6j23MX6W842H5FGG`. `.scratch/manager-pages` holds the subfolders `site` and `pipeline`.

## AT-4: A ticket on a spec branch has no GitHub link

App: scripts
Then: it has the label `in-review`, and its description has the line `On the spec branch codex-flow.` and no `github.com` link.
Files: `evidence/AT-4/output.txt`
Observation: `gh pr list --head codex-flow --state all` prints nothing, and its JSON form prints `[]`. The file does not exist on `main`, and on `codex-flow` it has `**Status:** in-review`. The task `01 The rules move to AGENTS.md` has the labels `in-review`, `pipeline`, and `site`. Its description has the line `On the spec branch codex-flow.` and no `github.com` text.

## AT-5: A ticket on main has the full description

App: scripts
Then: its description has, in order, the key line, the app, the blockers, the link `https://github.com/bkwon94/4thandgoal/blob/main/.scratch/manager-pages/pipeline/issues/12-drop-awards-from-managers-entry.md`, and a summary of 500 characters or fewer that starts "the managers file still carries".
Files: `evidence/AT-5/output.txt`
Observation: The description has four lines in this order: the key line, `App: pipeline`, the link, and the summary. It has no blockers line, and the ticket file says `**Blocked by:** None (can start immediately)`. Todoist stores the link as a titled markdown link, `[4thandgoal/.scratch/... at main · bkwon94/4thandgoal](https://github.com/bkwon94/4thandgoal/blob/main/.scratch/manager-pages/pipeline/issues/12-drop-awards-from-managers-entry.md)`, with the named URL inside the parentheses. The summary has 311 characters and starts "the managers file still carries".

## AT-6: A done ticket stays out of the queue

App: scripts
Then: no task has that key.
Files: `evidence/AT-6/output.txt`
Observation: On `main`, `.scratch/front-door/issues/01-the-front-door-shell.md` has `**Status:** done`. The project has 42 open tasks and 0 completed tasks from 2026-08-14 to 2026-11-13. The search of the descriptions of both lists for `.scratch/front-door/issues/01-` prints nothing.

## AT-7: The import makes the labels, the Ideas section, and the filter

App: scripts
Then: each of the 11 labels of the flow exists once, the section `Ideas` exists once with no task, and the filter "Waits on Brian" exists once with the query `#4thandgoal & @ready-for-human`.
Files: `evidence/AT-7/output.txt`
Observation: `td label list` shows 12 labels, each once: the 7 open statuses, `wontfix`, `decision`, `site`, `pipeline`, and `api`. The section `Ideas` shows once. The filter "Waits on Brian" shows once with the query `#4thandgoal & @ready-for-human`. `td task list` has no `--section` option, so the read of the section used `--filter '#4thandgoal & /Ideas'` and a count by `sectionId`. Both show one task in `Ideas`: "Buy low targets from other rosters". Its description says it comes from `front-door` 12, which the audit closed as `wontfix`.

## AT-8: Decision tickets get labels by kind

App: scripts
Then: `Decision 01: <question>` has `ready-for-human` and `decision`, and `Decision 02: <question>` has `ready-for-agent` and `decision`.
Files: `evidence/AT-8/output.txt`
Observation: The first push made the section `zz-queue-check` and `Decision 01: Does the grill ZZ question need Brian?`, with the labels `ready-for-human` and `decision`. The second push made `Decision 02: What does the research ZZ question find?`, with `ready-for-agent` and `decision`. The task JSON shows the same labels. The temp root has a branch `main` that holds each file, so each description has a GitHub link and not the spec branch line.

## AT-9: A triage label from Brian survives a push

App: scripts
Then: the task still has the label `ready-for-human`.
Files: `evidence/AT-9/output.txt`
Observation: A first push made `01 ZZ ready` with `ready-for-agent`. Then `td task update ... --labels ready-for-human` set the label, and the file still says `ready-for-agent`. The push sent 0 commands. The task JSON before and after the push shows the label `ready-for-human`.

## AT-10: A flow status always wins

App: scripts
Then: the task has the label `in-review` and not `ready-for-human`.
Files: `evidence/AT-10/output.txt`
Observation: The diff changes the Status line of `01-zz-ready.md` from `ready-for-agent` to `in-review`. The first `git diff` ran in the same second as the change and printed nothing; the same diff, run again at the end, shows the change. Before the push, the task has `ready-for-human`. The push sent `td task update ... --labels in-review`, and after it the task has only the label `in-review`.

## AT-11: An extra label from Brian stays

App: scripts
Then: the task still has the label `phone`.
Files: `evidence/AT-11/output.txt`
Observation: `td task update ... --labels in-review,phone` added `phone`. The push sent 0 commands. The task JSON before and after the push shows the labels `in-review` and `phone`.

## AT-12: The priority from Brian stays

App: scripts
Then: the task still has priority p1.
Files: `evidence/AT-12/output.txt`
Observation: `td task update ... --priority p1` set the priority. The API JSON stores p1 as `"priority": 4`, and the task JSON shows 4 before and after the push. The push sent 0 commands. `td task view` after the push shows `Priority: p1`.

## AT-13: A pull writes the triage of Brian into git

App: scripts
Then: the file has the line `**Status:** needs-info`.
Files: `evidence/AT-13/output.txt`
Observation: `git checkout` put the file back at `ready-for-agent`, and `td task update ... --labels needs-info,phone` set the label. The pull printed `ready-for-agent -> needs-info` and "1 file written.". `git -C "$T" diff` shows the line `**Status:** needs-info`.

## AT-14: A completed task pulls as wontfix

App: scripts
Then: the file has the line `**Status:** wontfix`.
Files: `evidence/AT-14/output.txt`
Observation: The task had no comment, and `td task complete` closed it. The pull printed `needs-info -> wontfix`. `git -C "$T" diff` against the commit shows the line `**Status:** wontfix`.

## AT-15: A completed task with a done comment pulls as done

App: scripts
Then: the file has the line `**Status:** done`.
Files: `evidence/AT-15/output.txt`
Observation: `git checkout` put the file back at `ready-for-agent`. `td task uncomplete` reopened the task of AT-14, `td comment add` added "done in #34", and `td task complete` closed it. The pull printed `ready-for-agent -> done`, and `git -C "$T" diff` shows the line `**Status:** done`.

## AT-16: A failed pull changes no file

App: scripts
Then: the command exits 0 with a warning line, and `git -C "$T" status --short` prints nothing.
Files: `evidence/AT-16/output.txt`
Observation: `git status --short` printed nothing before the run. The pull with `TODOIST_API_TOKEN=invalid` printed one line, "warning: the queue pull of zz-queue-check failed: AUTH_ERROR HTTP 401: Unauthorized. The queue is behind the tracker.", with exit code 0. `git -C "$T" status --short` after it printed nothing.

## AT-17: A wait task opens and closes

App: scripts
Then: the first run makes the task `Approve PRD` in the section `zz-queue-check` with `ready-for-human`, and the second run completes it.
Files: `evidence/AT-17/output.txt`
Observation: Before the runs, no open task has a `zz-queue-check/wait/` key. The first run sent `td task add 'Approve PRD'` in the section `6j23xPvRxhmXMwfG`, which AT-19 names `zz-queue-check`, with the label `ready-for-human`. The second run sent `td task complete` for that task. After it, no open wait task exists, and `td completed list` holds `Approve PRD`.

## AT-18: A merged PR closes the tasks of its done tickets

App: scripts
Then: the tasks of `03-zz-done.md` and `Merge PR #34` are complete.
Files: `evidence/AT-18/output.txt`
Observation: `td task uncomplete` reopened the task of 01. A push never makes the task of a `done` ticket, so `td task add` made the task of `03-zz-done.md` with its key line. `wait ... merge-pr 34` made `Merge PR #34`, and `gh pr view 34` shows `MERGED`. The sweep printed a warning that `git fetch origin main` failed, because the temp root has no remote. It then sent `td task complete` for `03 ZZ done` and for `Merge PR #34`. After the sweep, both tasks are in `td completed list`, and the open list still holds 01, 02, and the two decision tasks.

## AT-19: An open ticket keeps its task and the section

App: scripts
Then: the task of `02-zz-blocked.md` is open, and the section `zz-queue-check` is not archived.
Files: `evidence/AT-19/output.txt`
Observation: On `main` of the temp root, `02-zz-blocked.md` has `**Status:** blocked`. The open task list holds `02 ZZ blocked` with the label `blocked`. `td section list 4thandgoal` lists `zz-queue-check` with the id `6j23xPvRxhmXMwfG`.

## AT-20: A feature with every task complete gets its section archived

App: scripts
Then: every task of the section is complete, and the section `zz-queue-check` is archived.
Files: `evidence/AT-20/output.txt`
Observation: The section also held the two open decision tasks of AT-8. So one commit on `main` of the temp root set `done` in the two decision files, and in `01-zz-ready.md` and `02-zz-blocked.md`; the diff shows all four changes. `wait ... merge-pr 34` made a new `Merge PR #34`. Before the sweep, `td section list --full` shows the section with `"isArchived": false`. The sweep sent five `td task complete` commands and `td section archive id:6j23xPvRxhmXMwfG`. After it, the section holds no open task, and `td section list` no longer lists `zz-queue-check`. In AT-21, `td section unarchive` of that id prints "Unarchived: zz-queue-check".

## AT-21: A PR closed without a merge gives blocked

App: scripts
Then: `Merge PR #16` is open with the label `blocked`.
Files: `evidence/AT-21/output.txt`
Observation: `td section unarchive` brought the section back, and `td section list --full` then shows `"isArchived": false`. `wait ... merge-pr 16` made `Merge PR #16` with `ready-for-human`, and `gh pr view 16` shows `CLOSED` with `mergedAt` null. The sweep sent `td task update ... --labels blocked`. After it, `Merge PR #16` is in the open list with the label `blocked`. The end of the file holds the cleanup of the throwaway feature: `td task delete` of `Merge PR #16` and `td section delete --yes` of `zz-queue-check`. After them, no open or completed task has a zz key, and the label list has no `phone` label.

## AT-22: A failed push warns and the work goes on

App: scripts
Then: the command exits 0 and prints one warning line that names `02-zz-blocked.md`.
Files: `evidence/AT-22/output.txt`
Observation: The push with `TODOIST_API_TOKEN=invalid` printed one line, "warning: the queue push of .scratch/zz-queue-check/issues/02-zz-blocked.md failed: AUTH_ERROR HTTP 401: Unauthorized. The queue is behind the tracker.", with exit code 0.

## AT-23: The script finds td with no PATH

App: scripts
Then: the output lists the planned `td` commands, or zero commands, and has no error that `td` or `node` is not found.
Files: `evidence/AT-23/output.txt`
Observation: The command ran as `env -i HOME="$HOME" /usr/bin/python3 scripts/queue.py import --dry-run` and exited 0. The output lists the same 5 planned commands as AT-2 and ends with "5 commands planned, none sent.". It has no line about a missing `td` or `node`.

## AT-24: A dry run sends nothing

App: scripts
Then: the output names a `td task add` command, and the count of open tasks in the project is the same before and after.
Files: `evidence/AT-24/output.txt`
Observation: The new file `04-zz-new.md` had no task before the run. The dry run printed `td task add '04 ZZ new' ...` and "1 command planned, none sent.". The count of open tasks in the project is 45 before and 45 after, and no task has the key of `04-zz-new.md` after it.

## AT-25: The script tests pass on real fixtures

App: scripts
Then: it passes, and the run lists the cases of `test_queue`.
Files: `evidence/AT-25/output.txt`
Observation: `make check-scripts` runs `python3 -B -m unittest discover -s scripts -p 'test_*.py' -v`. It lists 69 cases of `test_queue` among 114 tests, ends with "OK", and exits 0. The fixtures of the zz tasks, the zz section, the completed zz task, and the done comment under `scripts/fixtures/queue/td/` have the field shape of `td`, with ids that no real task has. `evidence/real-td/` holds the real JSON of the same reads. The real JSON has the same keys, except that a completed task also has `responsibleName`, and a real comment has no `projectId`.

## AT-26: The audit report covers each open ticket

App: tracker
Then: each open ticket appears once, under its feature, with `done` and a commit, `wontfix` and a reason, or `open` and a label, and each named commit exists in `git log`.
Files: `evidence/AT-26/check.py`, `evidence/AT-26/output.txt`
Observation: The check lists 71 open tickets on `17f45a15`, the merge base of `main` and `todoist-queue`, and 71 audit lines. No open ticket lacks a line, no ticket has two lines, no line names a ticket that is not open, and no line sits under the heading of another feature. Each `done` line names a commit, each `open` line names a label, and each `wontfix` line has a reason. The proposals are 45 `done`, 9 `wontfix`, and 17 `open`. `git cat-file -e` finds each of the 79 named hashes, which include the 43 commits of the `done` lines.

## AT-27: The approved audit lands in the tracker

App: tracker
Then: each line matches, `docs/agents/state.md` lists each feature with an open ticket, and no ticket has the status `triage`, `built`, `accepted`, or `backlog`.
Files: `evidence/AT-27/compare.py`, `evidence/AT-27/output.txt`
Observation: The compare script reads each audit proposal with the changes under the Approved heading of `audit.md`. It prints "71 tickets, 0 mismatches", with 44 `done`, 21 `wontfix`, 5 `ready-for-agent`, and 1 `ready-for-human`. The `state.md` diff from `17f45a15` takes the table from 25 rows to 7 rows, and removes the Notes section. The list of tracked tickets that are not `done` or `wontfix` names the same 7 subfolders and features. The grep for the four strings as the first word of a Status line prints nothing, and its count is 0.

## AT-28: The tracker rule rejects an odd status

App: both
Then: both fail and name `.scratch/zz-rule/issues/01-zz.md`.
Files: `evidence/AT-28/output.txt`
Observation: Both rules ran in a detached worktree of `f0461df6`, with the planted file staged. The pipeline rule failed 2 of 9 tests with exit code 1. One offense names `.scratch/zz-rule/issues/01-zz.md:3  tracker/status` with "The ticket has the status backlog, and it is not one of the nine statuses.". The site rule failed 2 of 10 tests with exit code 1, with the same offense line for `.scratch/zz-rule/issues/01-zz.md:3`. In each app, the second failed test says that the feature `zz-rule` has no row in `state.md`. The last command removed the planted file, and `git status --short` then printed nothing.

## AT-29: Each skill calls the script at each push point

App: plugin
Then: each row of the push table in the PRD has a call in its skill at its step, and each skill starts with `sweep`.
Files: `evidence/AT-29/output.txt`, `evidence/AT-29/beside.md`
Observation: The grep finds 20 calls of `scripts/queue.py` in the skill files. `beside.md` puts each row of the push table beside its hits, with the heading above each hit. Each of the six `SKILL.md` files has `## The queue` right after its title, before `## Before you start`, with the line "Start with the merge sweep: `python3 scripts/queue.py sweep`.". `implement/pr.md` has its one call at step 5, after `gh pr create` at step 4.

## AT-30: The records say what the queue owns

App: docs
Then: ADR 0032 says it amends ADR 0021 and that the tracker in `.scratch/` stays the record. The two docs name the queue, its labels, the key line, and the script. The glossary has Queue, Wait task, and Merge sweep.
Files: `evidence/AT-30/output.txt`
Observation: ADR 0032 starts "This ADR amends ADR 0021." and says "The tracker stays the record.". The queue section of `docs/agents/issue-tracker.md` names the queue, the labels, the key line `4ag: <path>`, and the script `scripts/queue.py`. `docs/agents/triage-labels.md` has "The queue labels" with a table that maps each status to its queue label; it names neither the key line nor the script. `GLOSSARY.md` has the terms **Queue**, **Wait task**, and **Merge sweep**.

## AT-31: CI never calls td

App: both
Then: the only hit is the `scripts-check` target, which runs unit tests that call no `td`.
Files: `evidence/AT-31/output.txt`
Observation: The grep for `td ` and `queue.py` in `.github/`, `Makefile`, and the three app Makefiles prints nothing, with exit code 1. A grep for the word `td` also prints nothing. A grep for `check-scripts` and `scripts-check` finds the CI step `make check-scripts` and the target, which runs `python3 -B -m unittest discover -s scripts -p 'test_*.py'`. The one test that calls `main()` with a `td` read sets `QUEUE_TD_BIN` to a folder with no `td` and checks for a `NO_TD` warning.

## AT-32: A push does not sync the body or the comments

App: scripts
Then: the task has no Todoist comment, and its description is the same as before.
Files: `evidence/AT-32/output.txt`
Observation: A first push made `02 ZZ blocked`. The diff adds `## Comments` and one comment line to `02-zz-blocked.md`. The push without the invalid token sent 0 commands. `td comment list` of the task shows `"results": []` before and after. The task JSON shows the same description before and after.
