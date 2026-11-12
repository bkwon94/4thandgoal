---
name: to-tickets
description: Break the spec of one feature of this repo into tracer-bullet tickets at .scratch/<feature>/issues/<NN>-<slug>.md, and add its row to docs/agents/state.md. Use after 4ag:to-acceptance.
argument-hint: '<feature slug>'
---

# To tickets

Break one spec into tickets at `.scratch/<slug>/issues/<NN>-<slug>.md`, and add the feature row to `docs/agents/state.md`. Each ticket builds on a Ticket branch `<slug>-<NN>` that merges into the Spec branch `<slug>`.

## The queue

Run each call at the root of the checkout or worktree. A failed call prints a warning and exits 0, so never stop on it. Name each missed push in the final report.

Start with the merge sweep: `python3 scripts/queue.py sweep`.

Then complete the wait task of the tests and open the next one:

1. `python3 scripts/queue.py wait <slug> approve-acceptance --done`
2. `python3 scripts/queue.py wait <slug> approve-tickets`

## Before you start

1. Check that the skill `to-tickets` is in the available skill list. If it is missing, stop. Tell Brian its name. Do not guess its steps.
2. Check that `.scratch/<slug>/PRD.md` and `.scratch/<slug>/ACCEPTANCE.md` exist. If one is missing, stop. Name the skill that writes it: `4ag:to-spec` or `4ag:to-acceptance`.
3. Read both files, `docs/agents/issue-tracker.md`, and `docs/agents/state.md`.

## Steps

1. Call the Skill tool for `to-tickets`. Do its steps 1 to 4, with the changes below.
2. In the breakdown that Brian approves, show the app of each ticket and the acceptance tests that it makes pass.
3. After Brian approves, write one file for each ticket in the format below. Number from `01`, blockers first. Do not use the template of `to-tickets`.
4. Give each acceptance test at least one ticket that makes it pass.
5. Add one row to `docs/agents/state.md`, as below.
6. Change the Tickets line of the PRD header to the ticket numbers, such as "Tickets: 01 to 04, in `issues/`."
7. Stage the new files with `git add`. The tracker rules read only the tracked files.
8. Run `make check-fast` at the root. It must pass before the commit.
9. After Brian approves, run `python3 scripts/queue.py push <path>` for each ticket. Then run `python3 scripts/queue.py wait <slug> approve-tickets --done`.

## The ticket

Copy the shape of `.scratch/one/issues/*.md`:

```markdown
# <NN>: <Ticket title>

Spec: `.scratch/<slug>/PRD.md`. Acceptance tests AT-<n> and AT-<n>.

**App:** site, pipeline, or both.

**What to build:** <the end-to-end behavior that this ticket makes work, from the reader's side>

**Blocked by:** none, or the numbers of the tickets of this folder.

**Status:** ready-for-agent

- [ ] <A box that a check or a real run proves.>
- [ ] <A box that a check or a real run proves.>
```

Name no source path and no code in a ticket, because they change fast. A published file, such as `page.json` or `managers.json`, is a name and may stay.

## The state row

Add one row for the feature to the table of `docs/agents/state.md`:

```markdown
| `<slug>` | <site, pipeline, or both> | 01 <the title of ticket 01> | none | |
```

The App is `both` when the tickets touch both apps. The Next ticket is the lowest open number. The tracker rule fails a row for a feature with no open ticket, and fails an open ticket with no row.

## The end

Tell Brian that the plan of the spec is done. Name the Spec branch and ticket 01.
