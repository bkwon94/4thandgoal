# Issue tracker: Local Markdown

Issues and PRDs for both apps live as markdown files in the root `.scratch/`. The notes name league
managers and the repo is public, so the tracker is not GitHub Issues (ADR 0021).

## The conventions

- One feature per directory: `.scratch/<feature-slug>/`.
- Issues are `issues/<NN>-<slug>.md`, numbered from `01`.
- Triage state is a `Status:` line near the top of each file. `triage-labels.md` holds the role strings.
- Comments append to the bottom of the file under a `## Comments` heading.
- A ticket names its blockers as text, such as "Blocked by: 04". The number is a ticket of the same folder.

## The old shape

A feature from before the One spec has two parts:

- `.scratch/<feature-slug>/PRD.md`: the spec.
- `.scratch/<feature-slug>/issues/`: the tickets.

Other files of the feature, such as screenshots, fixtures, and research notes, sit beside them.

## The shared features

Nine features had a folder in the site tracker and in the pipeline tracker: `agent-habits`, `manager-pages`,
`modular`, `next-week-byes`, `rankings`, `rules-as-checks`, `stakes`, `waiver`, and `win-win`. Each one keeps
two subfolders in the old shape:

- `.scratch/<feature-slug>/site/`: the site PRD, the site `issues/`, and the site files.
- `.scratch/<feature-slug>/pipeline/`: the pipeline PRD, the pipeline `issues/`, and the pipeline files.

The tickets keep their old numbers, so `site/issues/01-*.md` and `pipeline/issues/01-*.md` can both exist.
A relative ref in a ticket, such as "Blocked by: 04", names a ticket in its own subfolder. A path names the
subfolder in full: `.scratch/waiver/pipeline/PRD.md`.

## The new shape

A feature after the One spec has this shape. Each part is a file or folder under `.scratch/<feature-slug>/`.

1. `MAP.md`: the map, with the headings DESTINATION, DECISIONS SO FAR, NOT YET SPECIFIED, and OUT OF SCOPE.
   The map is optional.
2. `decisions/<NN>-<kind>-<slug>.md`: one decision ticket for each decision. The kind is `grill`, `research`,
   `prototype`, or `spec`. The notes of a research ticket sit beside it, at `decisions/<NN>-research-<slug>.notes.md`.
3. `PRD.md`: the spec in prose.
4. `ACCEPTANCE.md`: the acceptance tests, each named `AT-<n>`. The Judge gives the Test verdict of each test, and a FAIL from Brian overrides it (ADR 0026).
5. `issues/<NN>-<slug>.md`: the tickets.
6. `EVIDENCE.md`: the evidence of each acceptance test, with no Test verdict. `4ag:implement` writes it.
7. `evidence/AT-<n>/`: the files of each test, such as the screenshots of a site test or the output of a pipeline command.
8. `VERDICTS.md`: the Test verdict of each acceptance test, from the Judge. `4ag:implement` commits it alone, one commit per round.

A new feature uses one folder for both apps. It does not get `site/` and `pipeline/` subfolders.

## The queue

The queue is the private Todoist project `4thandgoal`. It is a view and a triage tool. The tracker in
`.scratch/` stays the record (ADR 0032, which amends ADR 0021).

**What each place owns.**

- The tracker owns the body, the blockers, the comments, and the `Status:` line. Only a merge sets `done`.
- The queue owns priority, order, the triage statuses, and new ideas.
- On a conflict, git wins for content and done-ness. The queue wins for the rest.

**The shape.** One section holds one feature. One top-level task holds one open ticket, one open decision
ticket, or one wait task. The `Ideas` section holds new ideas.

**The labels.** Each open task has one status label: `needs-triage`, `needs-info`, `ready-for-agent`,
`ready-for-human`, `in-progress`, `in-review`, or `blocked`. A `done` task is complete and has no status label.
A `wontfix` task is complete and has the label `wontfix`. `triage-labels.md` maps each status to its label.

**The key line.** The first line of the task description is `4ag: <path>`. A ticket or a decision ticket uses
its file path from the repo root, such as `4ag: .scratch/<feature>/issues/03-<slug>.md`. A wait task uses
`4ag: <feature>/wait/<kind>`. A push finds the task by this line. Git holds no Todoist ID.

**The script.** `scripts/queue.py` is the only code that calls `td`. It has the subcommands `push`, `pull`,
`wait`, `sweep`, and `import`. A skill runs it as `python3 scripts/queue.py <subcommand>`. A failed `td` call
prints one warning and exits 0. CI never calls `td`.

## The state file

`docs/agents/state.md` has one row for each feature with an open ticket. The columns are Feature, App, Next
ticket, Blocked by, and Hold. App is `site`, `pipeline`, or `both`.

- An open ticket is a file under `issues/` whose Status is not `done` and not `wontfix`.
- A PRD, a map, a decision ticket, an acceptance file, and an evidence file are not tickets.
- A ticket in `in-review` or `blocked` is open. `4ag:implement` sets `in-review` after the merge into the spec branch. Before the push, the last commit of the spec branch sets each `in-review` ticket to `done`. So `in-review` exists only on a spec branch, and `main` sees `done` after the squash merge.
- A shared feature gets one row for each subfolder with an open ticket. The App of the row names the subfolder.
- A feature with no subfolder gets one row.

The tracker rules keep the file true: `apps/site/src/tracker-rule.test.ts` and
`apps/pipeline/tests/test_rule_tracker.py`. Both read the tracked files only, through `git ls-files .scratch`.

## The close comment

A ticket closes with one comment under `## Comments`. Each line is one sentence.

1. The merge: the branch, the commits, and the date.
2. The proof: the test count, and the golden diff if one exists.
3. The notes for a later ticket, if any.
4. The files read: "Read N files: path, path, path." Paths are relative to the repo root.

The close comment of a ticket updates `docs/agents/state.md` in the same commit. Set the next ticket of the
feature in its row. A feature with no open ticket leaves the file. A feature with an open ticket keeps its
row, with the next ticket and its blocker.

The files-read line is the measure of the One vision test: an agent changes the repo without a read of most of
it. Count every file the agent read to build the ticket: source, tests, tickets, ADRs. A file the agent only wrote
does not count. A folder that three close comments in a row list is the next README or the next split. Note it
under Further Notes in the PRD of the feature.

## When a skill says "publish to the issue tracker"

Create a new file under `.scratch/<feature-slug>/`. Create the directory if it does not exist.

## When a skill says "fetch the relevant ticket"

Read the file at the referenced path. The user normally passes the path or the issue number directly.
