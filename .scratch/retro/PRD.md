# Retro: a review of each finished run files fixes to the environment

Status: ready-for-agent
Date: 2026-11-23
Apps: both. The change is to the `4ag` plugin, `scripts/queue.py`, and `GLOSSARY.md`, not to the code of an app.
Spec branch: `retro`.
Source: the session of 2026-11-23. No map and no decision tickets, because the grill cleared all fog. ADR 0014, ADR 0021, ADR 0032, ADR 0033.
Tickets: 01 to 03, in `issues/`.

## Problem Statement

Brian wants each quick run and each spec build to be smoother than the last. Now nothing looks back on a finished run. A lesson goes into a memory note or into the head of Brian, and the next run hits the same problem.

The skill `retro` of `mattpocock-skills` does this job, but three facts block a direct use:

1. It sets `disable-model-invocation: true`. A `4ag` skill cannot load it. Only Brian can start it with `/retro`.
2. It sends a judgement rule to `CODING_STANDARDS.md`, and this repo has no such file. It knows nothing of our places: the rule tests, the `AGENTS.md` files, `GLOSSARY.md`, the skill text, and the queue.
3. It ends with a list in the chat. An accepted fix has no path into the queue, so it gets lost.

## Solution

1. A new skill `4ag:retro` ships in the `4ag` plugin. Brian starts it. It never starts on its own.
2. The end report of `4ag:quick` and of `4ag:implement` prints one line that suggests `/4ag:retro`. A smooth run teaches little, so the choice stays with Brian.
3. The Retro reads the record of one finished run and its session log. It finds the moments where the agent struggled, and it gives the stage times.
4. It shows the candidates in order of severity. Each candidate names its moment in the log. Brian replies with the numbers that he accepts.
5. A new subcommand `queue.py add` files each accepted candidate as one task in `Bugs`, `Quick Wins`, or `Ideas`. Then `4ag:quick` or `4ag:plan` builds it.
6. The Retro proposes and files. It changes no code, no check, and no steering file itself, and it writes no repo file.

## User Stories

1. As Brian, I want to run `/4ag:retro` after a run, so that the next run avoids the problems of this one.
2. As Brian, I want the end report of `4ag:quick` to name `/4ag:retro`, so that I remember the option.
3. As Brian, I want the end report of `4ag:implement` to name `/4ag:retro`, so that I remember the option after a spec build.
4. As Brian, I want the Retro to start only when I ask, so that a smooth run does not make rules that nobody needs.
5. As Brian, I want to give the Retro a PR number, so that it reviews the run of that PR.
6. As Brian, I want to give the Retro the path of a quick file, so that it reviews that quick run.
7. As Brian, I want to give the Retro a feature slug, so that it reviews that spec build.
8. As Brian, I want the Retro to review the current session when I give no input, so that a review right after a run needs no argument.
9. As Brian, I want the Retro to read the quick file, or `EVIDENCE.md` and `VERDICTS.md`, so that it knows what the run built and how the Judge saw it.
10. As Brian, I want the Retro to read the PR comments and the CI runs, so that it sees each red check and each FAIL.
11. As Brian, I want the Retro to read the session log of the run, so that it sees the struggles that the record does not show.
12. As Brian, I want the Retro to find the session log of a past run by itself, so that I do not search for a log file.
13. As Brian, I want the Retro to read the Claude log and the Codex log, so that it works for a run in either harness.
14. As Brian, I want the Retro to show the time of each stage, so that I see where a run spent its time.
15. As Brian, I want each candidate to name its moment in the log with a timestamp, so that I can check that it is real.
16. As Brian, I want the Retro to drop each candidate with no moment in the log, so that it gives no generic advice.
17. As Brian, I want the candidates in order of severity, so that I read the most costly problem first.
18. As Brian, I want each candidate to name its category and its place in the repo, so that I know what the fix changes.
19. As Brian, I want a mechanical mistake to get a check, such as a rule test or a script in `scripts/`, so that a check fails where a sentence would not.
20. As Brian, I want the Retro to report a check that exists but is not connected, so that the fix connects it and does not build a second one.
21. As Brian, I want a slow search for a file or a fact to get a pointer from a file the agent already reads, so that the next agent finds it fast.
22. As Brian, I want a judgement rule to go to a root `CODING_STANDARDS.md`, so that `code-review` in `4ag:implement` reads it.
23. As Brian, I want the Retro to propose `CODING_STANDARDS.md` at the first judgement rule, so that the file exists only when it holds a rule.
24. As Brian, I want the Retro to keep rules out of `AGENTS.md`, so that the file that loads in each session stays short.
25. As Brian, I want the Retro to find lines in a steering file that change nothing, so that I can delete them.
26. As Brian, I want the Retro to find a costly tool call, so that a cheaper tool can replace it.
27. As Brian, I want the Retro to find information that the agent could not reach, so that I can give the agent access to it.
28. As Brian, I want the Retro to find a gap in a `4ag` skill text, so that the fix goes to the skill and not to a memory note.
29. As Brian, I want to accept candidates by number, so that one short reply files them.
30. As Brian, I want each accepted candidate that passes the four rules of ADR 0033 to go to `Bugs` or `Quick Wins`, so that `4ag:quick` can take it.
31. As Brian, I want each larger accepted candidate to go to `Ideas` with a draft `4ag:plan` outcome statement, so that I can start a spec from it.
32. As Brian, I want each queue task of a candidate to hold the moment in the log, so that the agent who builds it knows why.
33. As Brian, I want each queue task of a candidate to carry no name of a league manager, so that the queue follows ADR 0021.
34. As Brian, I want a candidate that I do not accept to go nowhere, so that the queue holds only what I chose.
35. As Brian, I want the Retro to change no code and no steering file itself, so that each fix goes through a quick run or a spec with its own check.
36. As Brian, I want the Retro to write no repo file, so that it needs no branch and no PR.
37. As Brian, I want a failed `td` call to print a warning and not stop the Retro, so that it acts as each other queue call does.
38. As an agent, I want `queue.py add` to be the only way that the Retro makes a task, so that only `queue.py` calls `td`.
39. As an agent, I want `4ag:quick` to take a task that `queue.py add` made, so that a filed candidate becomes a quick run with no extra step.
40. As an agent in Codex, I want `4ag:retro` in my skill list through `.agents/skills/4ag-retro`, so that the Retro runs in Codex too.
41. As an agent, I want the term Retro in `GLOSSARY.md`, so that each skill uses one word for it.
42. As Brian, I want the Retro to start with the merge sweep, as each `4ag` skill does, so that the queue is up to date first.

## Implementation Decisions

- **The skill.** `4ag:retro` is a new skill folder in the `4ag` plugin, beside the other seven. It uses the neutral words of the table "The harness words" in `AGENTS.md`, and it names no tool of one harness only (ADR 0014).
- **No load of Matt's `retro`.** The skill copies the categories and the "propose only" rule of the `retro` skill of `mattpocock-skills` 1.3.1, and it maps each category to our places. It does not load that skill, because that skill blocks a load by a model. It loads `writing-for-agents` for the text of each proposed skill or steering change.
- **Before you start.** The skill checks that `writing-for-agents` is in the skill list, as the other `4ag` skills check their global skills.
- **Invocation.** `/4ag:retro` with no argument reviews the current session. `/4ag:retro <PR number>`, `/4ag:retro <quick file>`, and `/4ag:retro <feature slug>` review a finished run.
- **The record of the run.** For a quick run, the quick file. For a spec build, the PRD, `EVIDENCE.md`, and `VERDICTS.md`. For both, the PR comments and the CI runs through `gh`.
- **The session log.** The Claude log is under `~/.claude/projects/<the folder of the repo>/` as one `.jsonl` file per session. The Codex log is under `~/.codex/sessions/`. The Retro finds the session of a past run by the branch name or the worktree path in the log. A spec build has a session for each subagent, and the Retro reads the logs of the subagents too, because the struggle of a ticket shows there. If no log matches, the Retro says so and reviews the record only.
- **The stage times.** The Retro takes each stage time from the timestamps of the log. It prints one line per stage, in the shape `<stage>: <minutes> min`, then the total. `4ag:quick` and `4ag:implement` get no extra timestamp step.
- **The categories and their places.** Each candidate has one category, and the category sets the place of the fix:

  | What went wrong | The fix |
  | --- | --- |
  | A mechanical mistake | A check: a rule test, a script in `scripts/`, a lint rule, or a hook. A check that exists but is not connected gets connected. |
  | A judgement mistake that `code-review` missed | A rule in the root `CODING_STANDARDS.md`. |
  | A slow search for a file or a fact | A pointer from a file that the agent already reads, such as a README or an `AGENTS.md`. |
  | A gap or an error in a `4ag` skill text | A change to that skill. |
  | A costly tool call | A cheaper tool or a change to the call. |
  | A line in a steering file that changes nothing | A delete. |
  | Information that the agent could not reach | Wider access, such as a log file or a read-only token. |

- **`CODING_STANDARDS.md`.** No such file exists. The first accepted judgement rule files a candidate that makes it at the repo root. `code-review` already reads the file when it exists. `4ag:quick` does not start to run `code-review`.
- **The accept step.** The Retro shows a numbered list in order of severity. Each item has the category, the moment in the log with its timestamp, the proposed fix, and the queue section. The Retro drops each candidate with no moment. Brian replies with numbers. The Retro files only those.
- **The section of a candidate.** A candidate that passes the four rules of ADR 0033 goes to `Bugs` when it fixes a mistake, or to `Quick Wins` when it changes text or behavior on purpose. A larger candidate goes to `Ideas`, and its description holds a draft outcome statement: `4ag:plan <what the feature does>, so that <the goal it serves>`.
- **`queue.py add`.** A new subcommand: `python3 scripts/queue.py add <section> <title> --description <text>`. The section is `Bugs`, `Quick Wins`, or `Ideas`. It makes one task in that section of the project `4thandgoal`, with the label `needs-triage`, and it makes the section first if it is missing. The task has no key line. `queue.py take` adds the key line when `4ag:quick` claims the task. A failed call prints one warning and exits 0, as each other subcommand does. `--dry-run` prints the plan and sends nothing.
- **No manager name.** The Retro checks the title and the description of each task for the name of a league manager before `queue.py add`, as `4ag:quick` checks a PR body (ADR 0021).
- **The end lines.** "The end" of `4ag:quick` and of `4ag:implement` gets one more sentence: Brian can run `/4ag:retro <PR number>` to review the run.
- **Codex.** A tracked symlink `.agents/skills/4ag-retro` points to the skill folder. The rule test of the harness already fails without it. The loop in step 3 of `docs/agents/codex.md` names `retro` with the other skills.
- **The term.** `GLOSSARY.md` holds the term Retro in its Workflow section. The Spec branch already holds it.
- **No ADR.** The choice is easy to change, and nothing in it surprises a reader.

## Testing Decisions

- A good test checks the behavior that a reader sees: the `td` commands that a subcommand plans, or the text of a skill file. It does not check private helpers.
- **The seam of `queue.py add`.** The pure planning function returns the list of `td` commands from a queue snapshot. The tests call it with a snapshot and compare the commands. This is the seam of `plan_push`, `plan_wait`, and `plan_take`. The prior art is `scripts/test_queue.py`. Cases: a task in each of the three sections, a missing section, a bad section name, and the `needs-triage` label.
- **The seam of the skill text.** A test reads the real skill files and checks what they name, as `scripts/test_skill_smoke.py` does. Cases: `4ag:retro` names the merge sweep, the four inputs, the accept step, `queue.py add`, the three sections, and the check for a manager name. The end of `4ag:quick` and of `4ag:implement` names `/4ag:retro`.
- **The rule tests that already run.** `apps/pipeline/tests/test_rule_harness.py` fails without the symlink, and it fails if the new skill names the Skill tool or the Agent tool. `scripts/retry_rule.py` and the tracker rules run as before.
- **One real run.** The evidence of the spec includes one Retro over a real finished run, such as PR #91 or a recent quick run. It shows the stage times, the candidates with their moments, and one candidate filed in the queue by `queue.py add`. This is a real run with the real queue, not a fake.
- No test mocks `td` or `gh`. The planning functions take a snapshot and need no mock.

## Out of Scope

- An automatic Retro at the end of each run. Brian starts each Retro.
- A change to `4ag:plan`. The queue carries each accepted fix.
- A change to `4ag:quick` to run `code-review`. It adds time to each quick run.
- A retro file in the repo, such as `.scratch/retros/`. It needs a branch and a PR for each Retro.
- An audit of the checks that a past Retro added. The Retro sees one run, so it cannot tell that a rule fires too often. Brian prunes checks himself.
- A Retro over many runs at once, to find a pattern across runs.

## Further Notes

- The source of the categories is the `retro` skill and its doc in `mattpocock-skills` 1.3.1, in the Claude plugin cache. The path holds a version number.
- Matt's doc names the main weak spot: an agent at the end of a run forgets the middle and invents generic advice. The rule that each candidate names a moment in the log is the guard against it.
- The memory notes of Brian hold past stage times, such as the 3.6 h build of `midseason-report`. A first real Retro can compare against them.
