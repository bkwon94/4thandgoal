# Todoist queue: Brian sees and steers the open work in Todoist

Status: ready-for-agent
Date: 2026-11-12
Apps: neither app changes its product code. The `4ag` plugin skills, a root script, the tracker records, and the tracker rules of both apps change.
Spec branch: `todoist-queue`.
Source: the map `.scratch/todoist-queue/MAP.md` and decision tickets 01 to 05. ADRs 0019, 0021, and 0026.
Tickets: 01 to 08, in `issues/`.

## Problem Statement

Brian cannot easily see or change the current work. The open tickets sit in 20 feature folders under `.scratch/`, and the live work sits on spec branches that `main` does not show. `docs/agents/state.md` names one next ticket per feature, but it is not a list Brian can read on a phone, sort, or triage.

The tracker is also stale. The memory notes name fewer open tickets than the tracker holds. For example, `next-week-byes` has one backlog ticket in the notes and five open tickets in the tracker. Some of the 103 `ready-for-agent` tickets are done or dead. Four tickets use a status outside the set in `docs/agents/triage-labels.md`: `triage`, `built`, `accepted`, and `backlog`. Ideas go to an untracked `scratch.md`.

## Solution

The tracker in `.scratch/` stays the record of the work. The Todoist project `4thandgoal` becomes the queue: the place where Brian sees the open work, orders it, triages it, and adds ideas.

1. An audit fixes the stale tickets first. An agent proposes a result for each open ticket, and Brian approves each line.
2. An import loads the open work into the queue once: one section per feature, one task per ticket and per open decision ticket, and one wait task for each step that waits on Brian.
3. After the import, each `4ag` skill keeps the queue current. It pushes each change of status, makes a wait task when it needs Brian, and pulls the triage of Brian into the `Status:` lines of a feature before work on that feature starts.
4. A merge sweep at the start of each `4ag` skill closes the tasks of each merged spec PR.
5. A failed Todoist call never stops the work. CI never calls Todoist.

Brian then opens Todoist and sees every task that waits on him under the label `ready-for-human`.

## User Stories

1. As Brian, I want each open ticket as one task in Todoist, so that I can see the open work on my phone.
2. As Brian, I want the tasks of one feature together under one section, so that I can read a feature at a glance.
3. As Brian, I want each task to show one status label, so that I know its state without a read of the file.
4. As Brian, I want a filter on `ready-for-human`, so that I see every step that waits on me across all features.
5. As Brian, I want a wait task "Approve PRD" when a spec waits on me, so that a spec does not sit unread.
6. As Brian, I want a wait task "Approve ACCEPTANCE" when the acceptance tests wait on me, so that the flow does not stall.
7. As Brian, I want a wait task "Approve tickets" when the tickets wait on me, so that the flow does not stall.
8. As Brian, I want a wait task "Merge PR #N" when a spec PR waits on my merge, so that I see each PR that is ready.
9. As Brian, I want an open decision ticket as a task, so that I see each grill that waits on my answer.
10. As Brian, I want a `grill` or `prototype` decision ticket to show `ready-for-human`, so that I know it needs me.
11. As Brian, I want a `research` decision ticket to show `ready-for-agent`, so that I know an agent can clear it.
12. As Brian, I want the tickets on a live spec branch in the queue, so that I see the work before it merges.
13. As Brian, I want a ticket to show `in-review` while its PR is open, so that I know the work waits on the merge.
14. As Brian, I want a ticket to show `blocked` when `4ag:implement` cannot build it, so that I see the problem fast.
15. As Brian, I want the tasks of a merged PR to complete without my help, so that the queue stays clean.
16. As Brian, I want the section of a closed feature to be archived, so that the queue shows only live features.
17. As Brian, I want a PR that closes without a merge to mark its wait task `blocked`, so that I notice it.
18. As Brian, I want to change a status label in Todoist, so that I can triage from my phone.
19. As Brian, I want my label change to reach the `Status:` line in git before an agent works on that feature, so that agents follow my triage.
20. As Brian, I want a task that I complete in Todoist to mean `wontfix`, so that I can drop a ticket with one tap.
21. As Brian, I want to say in a comment that a completed task is done, so that a ticket done outside the flow closes as `done`.
22. As Brian, I want my priority and my order in Todoist to stay as I set them, so that a push never undoes my choices.
23. As Brian, I want my own extra labels on a task to stay, so that a push changes only the labels of the flow.
24. As Brian, I want an `Ideas` section, so that I can add an idea from my phone.
25. As Brian, I want an idea to stay in Todoist until I run `4ag:plan` on it, so that git holds only planned work.
26. As Brian, I want each task to name its ticket path, so that I can find the file.
27. As Brian, I want a task of a ticket on `main` to link to the file on GitHub, so that I can read it on my phone.
28. As Brian, I want each task to show its app label, so that I know if it touches the site, the pipeline, or the API.
29. As Brian, I want each task to show its blockers, so that I know why it waits.
30. As Brian, I want a short summary of the ticket in the task, so that I can triage without the file.
31. As Brian, I want an audit of the open tickets before the import, so that the queue does not start full of stale work.
32. As Brian, I want the audit to propose `done` with the commit that did the work, so that I can check its claim.
33. As Brian, I want the audit to propose `wontfix` with a reason, so that I can agree or keep the ticket.
34. As Brian, I want to approve each line of the audit, so that no ticket closes without my word.
35. As Brian, I want the audit report grouped by feature, so that I can read it in about 20 minutes.
36. As Brian, I want each odd status string fixed to a canonical one, so that one word always has one meaning.
37. As Brian, I want a tracker rule to fail a ticket with a status outside the set, so that odd strings cannot come back.
38. As Brian, I want each skill to report a failed Todoist push at the end, so that I know when the queue is behind.
39. As Brian, I want a failed Todoist call to stop no build, so that a Todoist outage does not stop the work.
40. As Brian, I want the import to be safe to run again, so that I can repair the queue after a failure.
41. As Brian, I want an ADR that says what the queue owns and what git owns, so that a later agent does not move the record to Todoist.
42. As an agent, I want one script with five subcommands, so that I push with one line and no Todoist knowledge.
43. As an agent, I want the script to find `td` on its own, so that I do not need the nvm PATH.
44. As an agent, I want each push to be idempotent, so that a second run changes nothing.
45. As an agent, I want the pull to commit on the spec branch, so that I never commit on `main`.
46. As an agent, I want a failed pull to fall back to the git status, so that my work goes on.
47. As an agent, I want the merge sweep to run at the start of my skill, so that the queue is current when I begin.
48. As an agent in a sandbox, I want `TODOIST_API_TOKEN` to work as the login, so that the Codex flow can push too.
49. As the Judge, I want the evidence of a real run against the queue, so that I can check the tool on real data.
50. As a later reader, I want the glossary terms Queue, Wait task, and Merge sweep, so that each word has one meaning.

## Implementation Decisions

### What each place owns

- The tracker in `.scratch/` owns the content and done-ness of each ticket: the body, the blockers, the comments, and the `Status:` line. Only a merge sets `done`.
- The queue owns priority, order, the triage statuses, and ideas. The triage statuses are `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, and `wontfix`.
- The flow statuses are `in-progress`, `in-review`, `blocked`, and `done`. Only the skills set them, and a push always writes them to the queue.
- A push writes a triage status only when it makes a task. After that, the queue wins, and the pull brings the triage status to git.
- `docs/agents/state.md` stays an index of `.scratch/` that agents read. It does not read the queue.

### The shape of the queue

- One Todoist project, `4thandgoal`. The script finds it by name, so the repo holds no Todoist ID.
- One section per feature, named by the feature slug. A shared feature with `site/` and `pipeline/` subfolders gets one section.
- One `Ideas` section for new ideas. No script reads or writes it except to make it.
- One top-level task per open ticket, per open decision ticket, and per wait task. Ticket tasks have no subtasks.
- The section of a feature is archived only after every task in it is complete, because an archive also archives the open tasks.

### The labels

- Seven open status labels: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `in-progress`, `in-review`, `blocked`. Each open task has exactly one.
- `done` completes the task with no status label. `wontfix` completes the task with the label `wontfix`.
- `decision` marks a decision ticket. `site`, `pipeline`, and `api` mark the app.
- The labels of the flow are these eleven. A push replaces only the labels of the flow on a task. It keeps every other label that Brian adds.
- The import makes any missing label of the flow first, because `td label create` makes a duplicate with no check.

### The task content (decision ticket 05)

- **The key.** The first line of the description is `4ag: <path>`. For a ticket or a decision ticket, the path is its file path from the repo root. For a wait task, the path is `<feature>/wait/<kind>`, such as `codex-flow/wait/merge-pr`. The sync reads the open tasks of the project once and matches this line locally, because no Todoist filter reads a description.
- **The title of a ticket task** is the ticket number and its title: `03 The skill sync`. It comes from the H1 of the file, without the `NN:` prefix.
- **The title of a decision task** is `Decision <NN>: <question>`, from the H1 of the decision ticket.
- **The title of a wait task** is one of `Approve PRD`, `Approve ACCEPTANCE`, `Approve tickets`, or `Merge PR #<N>`. The section names the feature, so the title does not.
- **The description**, after the key line, has these lines in order: the app; the blockers as the ticket names them; a link; a summary. Each line is skipped when the ticket has no value for it.
- **The link** is the GitHub URL of the file on `main`, only when the file exists on `main`. A file that exists only on a spec branch gets the line `On the spec branch <slug>.` A wait task for a PR links to the PR.
- **The summary** is the text of the inline `**What to build:**` line, or else the first paragraph of the body, cut to 500 characters. Todoist is private, so a manager name in the summary is allowed (ADR 0021 forbids only public places).
- **The priority** is the Todoist default when the task is made. A push never sets or changes the priority or the order.
- **The app label** comes from the subfolder of a shared feature, else from the App column of the row of the feature in `docs/agents/state.md`, else from the Apps line of the PRD. `both` gives `site` and `pipeline`. No match gives no app label.

### The script

- One root script that uses only the Python standard library, beside the other root scripts and in their pattern. Its tests run in `make check-fast` through the `scripts-check` target. A skill calls it with `python3`.
- It puts the nvm `bin` folder of `td` first on the PATH of each call, because `td` is on no shell PATH and its shebang needs `node`. It finds that folder from the newest nvm Node that holds `td`. An environment variable can override it.
- It gives each `td` call a timeout of about 10 seconds, because a dead network can hang a call for about 2 minutes.
- It reads `--json` output and the JSON error line on stderr. Every `td` failure exits 1.
- A failed `td` call prints one warning line that names the task, and the script exits 0. The skill then names each missed push in its final report.
- `TODOIST_API_TOKEN` works as the login when the keychain is out of reach, such as in a sandbox.
- Each subcommand has `--dry-run`, which prints the `td` commands it would run and sends nothing.
- Each subcommand has `--root <dir>`, which reads and writes the tracker under that folder in place of the repo root. The acceptance tests use it with a throwaway feature in a temp folder, in the pattern of the `evidence-flags` tests.

### The subcommands

- `push <path>`: makes the task of one ticket or one decision ticket match its file. It makes the section if it is missing. It writes the title, the description, the flow labels, and the status label by the ownership rules above. It moves the task with `td task move` when the section is wrong, because `td task update` cannot change the section. It completes a decision task when the decision ticket is `done`. It never completes a ticket task as `done`, because only the merge sweep does that. It completes a task with the label `wontfix` when the ticket is `wontfix`.
- `pull <feature>`: reads the tasks of the feature from the queue and writes each triage status into the `Status:` line of its ticket. A task that Brian completed sets `wontfix`, unless a comment on the task holds the word `done`, which sets `done`. It keeps any text after the first word of the `Status:` line only when the first word does not change. The skill commits the result on the spec branch of the feature. A failed read changes no file.
- `wait <feature> <kind> [N]`: makes a wait task with the label `ready-for-human`. The kinds are `approve-prd`, `approve-acceptance`, `approve-tickets`, and `merge-pr` with the PR number. A second form completes a wait task: `wait <feature> <kind> --done`.
- `sweep`: for each open `Merge PR #N` task, it runs `gh pr view N --json state`. For a merged PR, it completes each ticket task whose ticket is `done` on `main` after the merge, then the wait task. A ticket that is still open on `main`, such as a follow-up, keeps its task. It archives the section only if every task in it is complete. For a PR closed without a merge, it sets `blocked` on the wait task. An open PR changes nothing.
- `import`: makes the labels of the flow, the `Ideas` section, and the Todoist filter "Waits on Brian" with the query `#4thandgoal & @ready-for-human`, runs `push` for each open ticket and open decision ticket, and makes the wait tasks of each live spec. It reads each feature from its live spec branch if one exists, else from the current checkout. A live spec branch is a local branch that has a `.scratch/<branch>/` folder and no merged PR, per `gh pr list --head <branch> --state merged`. A commit count against `main` does not work, because a squash merge leaves the branch commits off `main`. A second run changes nothing.

### The push points in the skills

Each skill adds one line per push point. The table comes from decision ticket 03.

| Skill and step | Queue action |
| --- | --- |
| Start of each `4ag` skill | `sweep` |
| `4ag:plan` stage 1, after the commit | `push` each decision ticket |
| `4ag:plan` stage 2 start | `pull <feature>` |
| `4ag:plan` stage 2 end | `push` the decision ticket |
| `4ag:to-spec` end | `wait <feature> approve-prd` |
| `4ag:to-acceptance` start and end | complete `approve-prd`, then `wait <feature> approve-acceptance` |
| `4ag:to-tickets` start and end | complete `approve-acceptance`, then `wait <feature> approve-tickets`, then `push` each ticket after the approval, and complete `approve-tickets` |
| `4ag:implement` start | `pull <feature>` |
| `4ag:implement` stage 1 | `push` each ticket that changes to `in-review` or `blocked` |
| `4ag:implement` stage 5, before the push to GitHub | no queue action. The tasks stay `in-review` |
| `4ag:implement` stage 5, after `gh pr create` | `wait <feature> merge-pr <N>` |
| `4ag:review` | `push` each ticket whose status changes |

### The audit

- The audit is the first ticket. It runs before the import.
- An agent reads each open ticket on `main` and checks it against the git log, the code, and the memory notes. It proposes one result per ticket: `done` with the commit that did the work, `wontfix` with a reason, or `open` with its correct status label.
- It writes one report, grouped by feature, at `.scratch/todoist-queue/audit.md`. Brian approves or changes each line.
- After the approval, the agent writes each `Status:` line and a close comment that names the commit or the reason, per the close comment rule of `docs/agents/issue-tracker.md`. It updates `docs/agents/state.md` in the same commit. The commit is on the spec branch, so it reaches `main` with the PR.
- It also maps the odd strings `triage`, `built`, `accepted`, and `backlog` to a canonical status.
- The audit covers the tickets under `issues/` only. Every decision ticket on `main` is already `done` or `wontfix`.

### The tracker rule

- The tracker rules of both apps fail a ticket under `issues/` whose `Status:` first word is outside this set: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `in-progress`, `in-review`, `blocked`, `done`, `wontfix`.
- A ticket with no `Status:` line stays open and legal, as today.

### The records

- A new ADR records that the queue is a view and a triage tool, and that the tracker in `.scratch/` stays the record. It amends ADR 0021: the cost "no board" now has an answer, and a private Todoist project may hold manager names. The next free number is 0032.
- `docs/agents/issue-tracker.md` gets a section on the queue: what it owns, the labels, the key line, and the script.
- `docs/agents/triage-labels.md` gets the queue label for each status.
- The glossary terms Queue, Wait task, and Merge sweep are already in the Workflow section of `GLOSSARY.md`.

## Testing Decisions

- A good test checks what the script would send to Todoist for a given repo state and a given queue state. It does not check private helpers.
- **The one seam is the plan of a subcommand.** Each subcommand first builds the list of `td` commands it would run, from the files and from the JSON of `td`. `--dry-run` prints that list. The tests call that plan step with real ticket files from `.scratch/` and saved JSON output of real `td` calls, and they check the list.
- No test calls `td` or the network, and no test uses a mock. The saved JSON is real output, kept as fixture files. The `td` calls get a real run against the queue, as evidence of the spec.
- The test cases cover: a new ticket makes a task; a second push of the same file makes no command; a flow status always wins; a triage status in the queue wins after the task exists; extra labels of Brian stay; a ticket on a spec branch gets no GitHub link; a merged PR completes its tasks before the archive; a closed PR gives `blocked`; a completed task pulls as `wontfix`, or as `done` with a comment; a failed `td` call gives a warning and exit 0.
- Prior art: `scripts/test_verdict.py` and `scripts/test_changed_apps.py` test root scripts with the standard `unittest` and fixture files in `scripts/fixtures/`.
- The tracker rule change gets a test in each app, in the pattern of the existing cases in `apps/pipeline/tests/test_rule_tracker.py` and `apps/site/src/tracker-rule.test.ts`.

## Out of Scope

- A triage of the `ready-for-agent` tickets past the audit. Brian does that in the queue after the import.
- The cleanup of the old worktrees. It is not tracker work.
- The root `scratch.md`. Git does not track it. Brian moves its one idea to the `Ideas` section.
- A GitHub Action or any CI call to Todoist. CI never calls `td`.
- A two-way sync of the ticket body or the comments. The queue holds a summary only.
- Subtasks, due dates, and reminders in the queue.
- The `done` tickets on `main`. They never enter the queue.

## Further Notes

- The queue goes stale when no `4ag` skill runs. The merge sweep runs only at the start of a skill. `import` repairs the queue at any time.
- The completed-task read of Todoist covers at most 3 months per call. A pull reads only the tasks of one feature, so this limit does not matter in practice.
- `td` does not retry a rate limit. One import of about 100 tasks is far under the cap of 1000 sync requests per 15 minutes.
- On 2026-11-12, the local branches with a feature folder include `codex-flow`, `front-door-lineup`, and `midseason-report`. `midseason-report` merged as #13, so the import must skip it. The import reads the branches as they are on the day it runs.

## Revisions

- 2026-11-12: Brian approved four fixes with the acceptance tests. The summary reads the inline `**What to build:**` line. The merge sweep completes only the tasks of tickets that are `done` on `main`. Each subcommand gets `--root`. `import` makes the filter "Waits on Brian".
- 2026-11-12: Brian approved a narrower ownership rule from ticket 03. A triage status in the file replaces a flow label in the queue, because only a skill sets a flow label. A triage label from Brian in the queue still wins over a triage status in the file. The script owns 12 labels: the 7 statuses of the flow, `wontfix`, `decision`, `site`, `pipeline`, and `api`. A `spec` decision maps to `ready-for-agent`.
