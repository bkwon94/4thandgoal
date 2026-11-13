# Quick runs: a bug or a small change goes to a merged PR fast

Status: ready-for-agent
Date: 2026-11-13
Apps: neither. The work changes the `4ag` plugin, `scripts/queue.py`, `AGENTS.md`, and `docs/agents/`. The site and the pipeline do not change.
Spec branch: `quick-runs`.
Source: the map `.scratch/quick-runs/MAP.md` and decision ticket 01. ADR 0033, which amends ADR 0026.
Tickets: 01 to 04, in `issues/`.

## Problem Statement

Brian finds a bug on his phone, or wants a small change, such as a label that clips or a wrong score note. Today the only shaped path is the spec flow: a map, a spec, acceptance tests, tickets, ticket branches, evidence, the Judge, and the `verdict` gate. That flow takes hours, and three approvals from Brian, for a fix of ten lines.

So small fixes go around the flow. PRs #27 to #30 and #40 shipped as plain PRs with no record in the tracker, no red evidence before the fix, and no Judge. The builder graded its own work. The fix of the Chrome iOS keyboard in #40 passed every test on the first try and still failed on the phone, because no loop showed the bug red first.

Brian wants one fast path for bugs and small changes. It must put debug skills first and keep the One rules: the tracker is the record, and the builder never gives the Test verdict.

## Solution

A new skill, `4ag:quick`, takes a quick run from Brian's words to an open PR with one stop.

1. Brian runs `4ag:quick` with a description of the bug or the change, or with the name of a task in the queue sections `Bugs` or `Quick Wins`.
2. The skill writes a quick file: up to five items of one kind, each with a done condition of one sentence. It states its call on the four boundary rules of ADR 0033.
3. Brian replies "go" or a fix to a done condition.
4. For each Bug, a subagent runs `diagnosing-bugs` and gets a red loop before any fix. For each Quick win, a subagent runs `tdd`. Each item ends green on the same loop.
5. A fresh Judge reads only the done conditions and the evidence, and gives a Test verdict per item.
6. The skill opens one PR. Brian merges it. The merge sweep closes the task in the queue.

If a boundary rule fails during the run, the skill stops and hands off to `4ag:plan` with what it found.

## User Stories

1. As Brian, I want one command for a bug, so that a fix does not need a map, a spec, and tickets.
2. As Brian, I want one command for a small change, so that a copy fix or a spacing fix ships the same day.
3. As Brian, I want to stop only once, at the start, so that I can leave while the run goes to a PR.
4. As Brian, I want to read each done condition before the build, so that the run does not fix the wrong thing.
5. As Brian, I want to drop a bug into the `Bugs` section from my phone, so that I can file it when I see it.
6. As Brian, I want to drop a small change into a `Quick Wins` section, so that bugs and changes sit apart.
7. As Brian, I want `4ag:quick` to take a queue task by name, so that I do not type the bug twice.
8. As Brian, I want the run to reuse the queue task I filed, so that the queue holds no duplicate.
9. As Brian, I want the skill to tell me when a request is too big for a quick run, so that a feature does not hide in a quick PR.
10. As Brian, I want a run that grows past a boundary rule to stop and hand off to `4ag:plan`, so that the work it found is not lost.
11. As Brian, I want up to five items in one run, so that a short list of fixes from one handoff ships in one PR.
12. As Brian, I want one kind per run, so that each PR reads as bug fixes or as changes, never a mix.
13. As Brian, I want a mixed list split into two runs from one call, so that I do not sort it by hand.
14. As Brian, I want each Bug to show red before the fix, so that I know the fix hits the bug I saw.
15. As Brian, I want each Bug to go green on the same loop, so that the proof is one command, before and after.
16. As Brian, I want a phone-only bug to use a screenshot of a LAN probe page as its red evidence, so that the run does not guess at a cause it cannot see on the Mac.
17. As Brian, I want a fresh Judge to read each item, so that the builder never grades its own work.
18. As Brian, I want the Judge to ask whether the red evidence shows the bug of the done condition, so that a test that fails for some other cause is caught.
19. As Brian, I want the Judge to ask whether the green evidence comes from the same loop at the fixed commit, so that a swapped test is caught.
20. As Brian, I want a text-only item to skip the Judge, so that a copy fix does not wait on a read that adds nothing.
21. As Brian, I want the Test verdicts in the PR body, so that I can merge from the PR page.
22. As Brian, I want the quick file in the tracker, so that the cause and the evidence stay on record after the merge.
23. As Brian, I want the PR body to name no league manager, so that the public repo does not leak notes (ADR 0021).
24. As Brian, I want the merge sweep to close the queue task after my merge, so that the queue stays true with no hand step.
25. As Brian, I want the `Bugs` and `Quick Wins` sections to stay after the sweep, so that my next phone drop has a place to land.
26. As Brian, I want the run to work in Codex as well as in Claude Code, so that I can start a quick run from either harness.
27. As an agent, I want the quick file format in one place, so that I write each quick file the same way.
28. As an agent, I want the boundary rules as a checklist, so that I state my call in one line.
29. As an agent, I want a rule that a loop uses the one fake of a port or real data, so that I never add a mock to reproduce a bug.
30. As an agent, I want `STUCK` as a stop with a reason, so that I do not flail when no loop goes red.
31. As the Judge, I want only the done conditions and the evidence, so that the build context does not sway the Test verdict.
32. As the next agent, I want the cause of each Bug in the quick file, so that a bug that comes back has a head start.
33. As Brian, I want `4ag:plan` to point a bug to `4ag:quick`, so that I use the right entry point.
34. As Brian, I want `AGENTS.md` to name the quick path beside the spec flow, so that a new agent finds it.

## Implementation Decisions

**The skill `4ag:quick`.** A new skill folder in the `4ag` plugin. It holds a short `SKILL.md` and two side files: the format of the quick file, and the brief of the quick Judge. It uses the neutral harness words of `AGENTS.md`, so the harness rule passes. A tracked symlink `.agents/skills/4ag-quick` makes it a Codex skill.

**The steps of the skill.**

1. Run the merge sweep.
2. Check that `mattpocock-skills:diagnosing-bugs` and `mattpocock-skills:tdd` are in the available skill list. If one is missing, stop and name it.
3. Read the input: Brian's words, a handoff file, or a queue task in `Bugs` or `Quick Wins`.
4. Sort the items into Bugs and Quick wins. One kind per run. A mixed input starts two runs.
5. Check the four boundary rules of ADR 0033. State the call in one line.
6. Make the branch `bug-<slug>` or `win-<slug>` from `main` in its own worktree.
7. Write the quick file. Push it to the queue as `in-progress`. Show Brian the items and done conditions. Wait for "go".
8. Build each item in sequence, one subagent per item: `opus` for a Bug, `sonnet` for a Quick win. The orchestrator edits a text-only item itself.
9. Run the Judge once over all items that need it. After a FAIL, fix the item and run a fresh Judge on that item. A second FAIL sets BLOCKED, and the skill opens no PR.
10. Set `Status: done`, write the close comment, push the branch, open the PR, and add the wait task for the merge.

**The quick file.** `.scratch/bugs/<slug>.md` for a run of Bugs, `.scratch/quick-wins/<slug>.md` for a run of Quick wins. The shape:

```markdown
# <Title>

Kind: bug or quick-win
Status: in-progress
Branch: `bug-<slug>` or `win-<slug>`.
Source: the queue task `<name>`, a handoff file, or the session of <date>.
Boundary: the call on the four rules, in one line.

## Items

### 1. <Item title>

Done condition: <one sentence>
Method: diagnosing-bugs, tdd, or text only.
Cause: <for a Bug, the cause the loop found>
Red: <the command, and its output>
Green: <the same command at the fixed commit, and its output>
Test verdict: PASS, FAIL, BLOCKED, or none for a text-only item.

## Comments
```

The quick file is not under `issues/`, so the tracker rule counts it as no ticket, and it gets no row in `docs/agents/state.md`.

**The quick Judge.** A fresh subagent with no build context. It reads only the done conditions and the Red and Green blocks. It answers two questions per item:

1. Does the red evidence show the bug of the done condition, and not some other failure?
2. Does the green evidence come from the same loop, at the fixed commit?

For a Quick win, question 1 reads: does the red evidence show the old behavior that the done condition names? The Judge writes one Test verdict line per item into the quick file.

**The method rules.** A Bug follows all phases of `diagnosing-bugs`. Its Phase 1 command is the Red block. A Quick win follows `tdd`. A loop uses the one fake of a port (ADR 0015) or real data, and never a new mock. A phone-only bug asks Brian for one screenshot of a LAN probe page, per the lesson of #40.

**The boundary stop.** If a boundary rule fails during the run, the skill commits what it has to the branch, writes the finding into the quick file, and stops. It tells Brian to run `4ag:plan` with an outcome statement that it drafts.

**The queue.** `scripts/queue.py` gets three changes:

1. A name map. The folder `bugs` names the section `Bugs`, and the folder `quick-wins` names the section `Quick Wins`. Every other feature keeps its slug as the section name. Every place that reads or makes a section name uses the map.
2. No archive. The sweep never archives `Bugs` or `Quick Wins`, even when every task in it is complete.
3. A `take` subcommand. `queue.py take <task name> <path>` finds the open task of that name in `Bugs` or `Quick Wins`, prints its title and description, and writes the key line `4ag: <path>` as the first line of its description. The task keeps its other text. A failed call prints a warning and exits 0, like the other subcommands.

`push`, `wait`, and the sweep then treat the quick file like a ticket. `pull` and `import` stay as they are, because a quick run is short and lives on one branch.

**The close.** The last commit before the push sets `Status: done` and writes one close comment, in the shape of `docs/agents/issue-tracker.md`. Only the merge puts `done` on `main`.

**The PR.** The title starts with `Bug:` or `Quick win:`. The body lists each item, its done condition, and its Test verdict. It names no league manager. No `ACCEPTANCE.md` exists, so `verdict.yml` passes the PR. CI runs the full suite. Brian merges.

**The pointers.** `AGENTS.md` names the quick path in The flow, beside the spec flow. `4ag:plan` says in one line that a bug or a small change goes to `4ag:quick`. `docs/agents/issue-tracker.md` adds the quick file shape. `GLOSSARY.md` and ADR 0033 already hold the terms and the decision.

**Codex.** `diagnosing-bugs` is not in `~/.agents/skills/` today. `docs/agents/codex.md` adds the one-time install step. The skill stops and names the skill when it is missing, like `4ag:plan` does.

## Testing Decisions

A good test checks behavior at the highest seam: the `td` commands that `queue.py` plans, and the files the rules read. It does not check private functions.

The seams:

1. **The plan of `queue.py`.** `scripts/test_queue.py` already tests `plan_push`, `plan_wait`, and `plan_sweep` against a fake queue. New tests:
   - A push of `.scratch/bugs/<slug>.md` goes into the existing section `Bugs`, and makes no section `bugs`.
   - A push of `.scratch/quick-wins/<slug>.md` makes the section `Quick Wins` once.
   - A sweep after a merge completes the done quick task and its wait task, and never archives `Bugs` or `Quick Wins`.
   - A spec feature keeps its slug as its section name, and its section still archives.
   - `take` plans one update that puts the key line first and keeps the old description.
   - `take` of a name with no open task in `Bugs` or `Quick Wins` plans no command.
2. **The harness rule.** `apps/pipeline/tests/test_rule_harness.py` already checks that each plugin skill has a Codex symlink and names no Claude-only tool. It covers `4ag:quick` with no new test.
3. **The tracker rule.** `apps/pipeline/tests/test_rule_tracker.py` already ignores files outside `issues/`. One new test: a tracked `.scratch/bugs/<slug>.md` with an open status needs no row.
4. **The skill as a whole.** No unit test reads a skill. The acceptance tests run one real quick run on a real bug from the `Bugs` section, and record its quick file, its PR, and the sweep after the merge.

Prior art: the `plan_sweep` tests near "the section is archived after every task in it is complete", and the tracker rule tests that build a temp `.scratch` tree.

## Out of Scope

- Parallel items in their own worktrees. Most runs hold one or two items. Add it if a run of five is too slow.
- A `verdict` gate on a quick PR. Brian merges each PR. Add it if a FAIL slips into a merge.
- A change to the steps of `4ag:implement` or `4ag:review`. A quick run has its own short steps.
- `pull` and `import` for quick files. A quick run lives on one branch for less than a day.
- The install of `diagnosing-bugs` on Brian's Mac for Codex. The spec writes the step; Brian runs it.

## Further Notes

- The section `Bugs` exists now, made by hand on 2026-11-13, and holds tasks with no key line. The sweep skips a task with no key line, so those tasks stay until a quick run takes them.
- A branch `bug-<slug>` holds no `.scratch/bug-<slug>/` folder, so `spec_branches` in `queue.py` and `verdict.yml` both treat it as no spec. This is the intent.
- A fresh worktree needs `pnpm install` before the prek hook passes. The skill runs it when it makes the worktree.
- The first real quick run is the test of this spec. Its time from "go" to an open PR is the number to watch. The target is under one hour for one Bug.
