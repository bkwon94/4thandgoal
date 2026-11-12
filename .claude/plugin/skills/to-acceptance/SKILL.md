---
name: to-acceptance
description: Write the acceptance tests AT-1, AT-2, and so on of one feature of this repo as .scratch/<feature>/ACCEPTANCE.md, each with its app and its evidence. Use after 4ag:to-spec, before 4ag:to-tickets.
argument-hint: '<feature slug>'
---

# To acceptance

Write the acceptance tests of one spec as `.scratch/<slug>/ACCEPTANCE.md`. An acceptance test is a behavior that a reader checks on the finished work, with evidence. Another agent with none of this conversation records the evidence. Only the Judge, a fresh subagent that reads only this file and the evidence, gives a Test verdict. A FAIL from Brian overrides it (ADR 0026).

## The queue

Run each call at the root of the checkout or worktree. A failed call prints a warning and exits 0, so never stop on it. Name each missed push in the final report.

Start with the merge sweep: `python3 scripts/queue.py sweep`.

Then complete the wait task of the spec: `python3 scripts/queue.py wait <slug> approve-prd --done`.

## Before you start

1. This skill calls no global skill. Check that `.scratch/<slug>/PRD.md` exists.
2. If the spec is missing, stop. Tell Brian to run `4ag:to-spec <slug>` first.
3. Read the spec. Read this conversation for the example values, the limits, and the failure cases that Brian named.

## Steps

1. Draft the tests in the format of [`format.md`](format.md). Use the words of `GLOSSARY.md`.
2. Give every user story a test, or a reason for no test.
3. Show Brian a short list: the id, the title, the app, and the Then line of each test. Add each story with no test, and each expected result that the spec does not give.
4. Change the tests until Brian approves them.
5. Write the file.

## The rules of a test

- **One behavior.** One When and one Then, so a FAIL names one defect.
- **Real data.** Name a real week, such as `2026` week 8. Use no mock.
- **Concrete values.** Name the manager, the player, or the number, so two readers see the same result.
- **Site evidence.** Screenshots at 375, 768, and 1280 px, each in the light theme and the dark theme (ADR 0006).
- **Pipeline evidence.** The command and its output, or the `page.json` fields that change, for a real week.
- **Both apps.** A test of both apps names the pipeline evidence and the site evidence.
- **Out of scope.** Add a test for an Out of Scope item that an agent can build by mistake. Its Then says it does not happen.

The ids are permanent, because the tickets and the Test verdict cite them. A test that no longer applies keeps its id with the word `Retired` and the reason.

## A revision

Only Brian changes an approved test. Show Brian each changed test. After Brian approves, change the file and add a dated line under `## Revisions`.

## The end

Run `python3 scripts/queue.py wait <slug> approve-acceptance`. Then tell Brian that `4ag:to-tickets <slug>` is next.
