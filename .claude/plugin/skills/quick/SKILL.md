---
name: quick
description: Take a bug or a small change of this repo to an open PR in one quick run, with no spec. Use when Brian describes a bug or a small change, names a handoff file, or names a task in the queue sections Bugs or Quick Wins.
argument-hint: '<description> | <handoff file> | <queue task name> [<queue task name> ...]'
---

# Quick

A quick run takes up to five items of one kind to one open PR (ADR 0033). Each item is a Bug or a Quick win. A Bug shows red on a feedback loop before the fix, and green on the same loop after it. A fresh Judge, the quick Judge, gives each item its Test verdict. Brian stops the run once, at the start, and merges the PR.

The agent never gives a Test verdict, because the agent built the work. A feature does not belong here. Send it to `4ag:plan`.

## The queue

Run each call at the root of the checkout or worktree. A failed call prints a warning and exits 0, so never stop on it. Name each missed push in the final report.

Start with the merge sweep: `python3 scripts/queue.py sweep`.

The steps below hold the other calls.

## Before you start

Write no file and make no branch before these checks pass.

1. Check that these global skills are in the available skill list: `diagnosing-bugs`, `tdd`. The `4ag` skills ship with this skill, so do not check them.
2. If one is missing, stop. Tell Brian the name of the missing skill. Do not guess its steps. In Codex, the install step of `diagnosing-bugs` is step 8 of `docs/agents/codex.md`.
3. Check that the sandbox allows a write to `.git` and a call of `gh`. Run these two commands in the main checkout:
   - `test -w "$(git rev-parse --git-common-dir)"`
   - `gh api repos/{owner}/{repo} --jq .name`
4. If one fails, stop. Tell Brian that the session needs the permission profile of the harness. Quote the error.
5. Read `docs/agents/issue-tracker.md`, ADR 0033 in `docs/adr/`, and the Workflow section of `GLOSSARY.md`.

## Invocation

| Command | Input |
| --- | --- |
| `/4ag:quick <description>` | The words of Brian. |
| `/4ag:quick <handoff file>` | A path to a file that lists the items. |
| `/4ag:quick <task name> [<task name> ...]` | One or more open tasks in the queue sections `Bugs` or `Quick Wins`. |

## Step 1: read the input

1. If the input is a path to a file, read the file.
2. Otherwise, try each name as a queue task. Run `python3 scripts/queue.py take "<name>" .scratch/bugs/probe.md --dry-run`. The dry run sends nothing to Todoist. It prints the title and the description of the task, then the planned `td` command.
3. If the call prints the warning "the queue has no open task", the input is not a task name. Read it as the words of Brian.
4. Write down each item: a title and what is wrong or what changes. Write down the task name of each item from the queue.

## Step 2: sort the items

1. Give each item one kind, with the terms of `GLOSSARY.md`:
   - A Bug: the code does not do what it should.
   - A Quick win: a change of behavior or text on purpose, where no bug exists.
2. Give each item one method:
   - `diagnosing-bugs` for each Bug.
   - `tdd` for a Quick win that changes behavior.
   - `text only` for a Quick win whose only change is text or config, which no test can show. The orchestrator edits it itself.
3. Write one done condition of one sentence for each item. It says when the item is done, in terms that a reader can check.
4. One kind goes in one run. If the input holds both kinds, make two runs: one of the Bugs, one of the Quick wins. Do steps 3 to 5 for each run. Ask Brian for "go" on both runs in one reply.

## Step 3: check the boundary

Check the four rules of ADR 0033 for each run, before you make a branch or a file:

1. **Up to five items of one kind.** The run fits on one branch and one PR. Six items or more fail this rule.
2. **No new term and no ADR.** The run adds no term to `GLOSSARY.md` and needs no ADR.
3. **No moved seam.** The run adds no port, no page, and no new shape of a data file, such as a new field in `page.json`.
4. **One sentence per done condition.** Each item has a done condition of one sentence.

State the call in one line, in the shape of the `Boundary:` line of [`format.md`](format.md#the-boundary-line). Brian can override the call.

If a rule fails, do the boundary stop below. Make no branch, no quick file, and no queue call.

## Step 4: make the branch and the quick file

1. Choose a slug of two to four lowercase words with hyphens. The branch is `bug-<slug>` for Bugs, or `win-<slug>` for Quick wins. Check that `git branch --list '<branch>'` prints nothing.
2. Run this in the main checkout: `git worktree add .claude/worktrees/<branch> -b <branch> main`.
3. Do the setup of the worktree in [`../implement/build.md`](../implement/build.md#the-setup-of-a-worktree).
4. In the worktree, write the quick file in the shape of [`format.md`](format.md). The path is `.scratch/bugs/<slug>.md` for Bugs, or `.scratch/quick-wins/<slug>.md` for Quick wins.
5. Commit the quick file with the message `Quick run: <title>`. The hook must pass.
6. For each item from the queue, run `python3 scripts/queue.py take "<task name>" <path of the quick file>`. This puts the key line first in the task, so the next push finds the task and makes no duplicate.
7. Run `python3 scripts/queue.py push <path of the quick file>`. The task gets the label `in-progress`.

## Step 5: stop once for "go"

Show Brian each run: the branch, the path of the quick file, the `Boundary:` line, and for each item its title, kind, method, and done condition. Ask Brian to reply "go" or a fix to a done condition. Then stop and wait.

- **"go".** Go to step 6. Do not stop again, except for a `STUCK`, a boundary stop, or a phone screenshot.
- **A fix.** Change the quick file. Commit it. Show the run again and wait.
- **"stop".** Run `git worktree remove --force .claude/worktrees/<branch>` in the main checkout. Then run `git branch -D <branch>`. Tell Brian that the queue task keeps its key line.

## Step 6: build each item

Build the items in sequence, in the worktree of the run, one fresh subagent per item. The order is the order of the quick file.

1. For a Bug, start a fresh subagent with the strong model. Give it the brief of a Bug below.
2. For a Quick win with `Method: tdd`, start a fresh subagent with the default model. Give it the brief of a Quick win below.
3. For a `text only` item, make the change yourself. Commit it. Fill the item as [`format.md`](format.md#a-text-only-item) shows.
4. After each subagent, read the item in the quick file. Check that it has a `Red:` block, a `Green:` block, and for a Bug a `Cause:` line. Check that `git status --short` shows no change.
5. Run `make check-fast BASE=main` in the worktree after the last item. It must pass.

Each subagent may reply in one of four ways:

- **A report.** Go to the next item.
- **`STUCK: <reason>`.** Set `Status: blocked` in the quick file. Add the reason under `## Comments`. Commit. Run `python3 scripts/queue.py push <path>`. Stop, and tell Brian the item and the reason. Open no PR.
- **`NEEDS SCREENSHOT: <what>`.** The bug shows only on the phone of Brian. Ask Brian for one screenshot of a LAN probe page, per the lesson of PR #40. Give him the bare URL and what to capture. Give the screenshot path to a fresh subagent of the same item, with the same brief.
- **`BOUNDARY: <finding>`.** Check the four rules again with the finding. If a rule fails, do the boundary stop below. If no rule fails, start a fresh subagent of the same item.

Brian can also tell the run that a fix needs more, such as a new field in `page.json`. Check the four rules again in the same way.

The brief of a Bug:

```text
Fix item <n> of the quick run <branch> in the 4thandgoal repo.

Work only in the worktree <absolute path of .claude/worktrees/<branch>>, on the branch <branch>.
Read AGENTS.md, the AGENTS.md of each app you change, and the quick file <path of the quick file>.
Read .claude/plugin/skills/quick/format.md for the shape of the Cause line and the Red and Green blocks.

Put Node 24 or later first on PATH (see Commits in AGENTS.md).

The item: <title>.
Done condition: <done condition>

1. Load the skill `diagnosing-bugs`. Follow each of its phases.
2. Build the feedback loop of Phase 1 as one command that fails on the bug of the done condition.
3. Use real data or the one fake of a port (ADR 0015). Never add a mock: no `mock`, `MagicMock`, `patch(`, or `monkeypatch`.
4. Run the command. Its output must show the bug of the done condition. An import error, a typo, or another failure is not the bug.
5. Commit the loop alone, with no fix. This is the red commit. The hook must pass.
   If the hook runs the loop and rejects the red commit, follow "When the hook runs the loop" in format.md.
6. Fix the cause. Run the same command, character for character. It must pass.
7. Commit the fix. Run `make check-fast BASE=main` at the root of the worktree. It must pass.
8. Write the Cause line, the Red block, and the Green block of the item into the quick file. Commit it.
9. Leave the Test verdict line as it is. Never write a Test verdict.
10. Push nothing. Start no dev server.
11. Report the red commit, the fix commit, the command, and the test count.

If the bug shows only on the phone of Brian, stop. Return `NEEDS SCREENSHOT: <the page and what to capture>`.
If the fix needs a new glossary term, an ADR, a new port, a new page, or a new shape of a data file, stop.
Commit the loop if you have one. Return `BOUNDARY: <what the fix needs, and why>`.
If no loop goes red on the bug, put back each file that you changed, and return
`STUCK: <what I tried / what failed / what I need>`.

Write all output in Simplified Technical English. Rules: `~/.claude/rules/communication/simplified-technical-english.md`.
Active voice, present tense, one instruction per sentence, 20 words or fewer, no `-ing` as a verb, plain words.
Code, technical names, and quoted output are exempt. Refer to Brian by name.
```

The brief of a Quick win is the brief of a Bug, with these changes:

- Step 1 reads: "Load the skill `tdd`. Build the change test-first."
- Step 2 reads: "Write one test as one command that fails on the old behavior that the done condition names."
- Step 4 reads: "Its output must show the old behavior. An import error, a typo, or another failure is not the old behavior."
- Step 6 reads: "Change the code. Run the same command, character for character. It must pass."
- Step 8 has no Cause line.
- The `NEEDS SCREENSHOT` line goes away.

## Step 7: the quick Judge

Run the quick Judge once over each item whose method is not `text only`. See [`judge.md`](judge.md). A text-only item gets `Test verdict: none` and no Judge.

## Step 8: close and open the PR

1. Close the quick file, as [`format.md`](format.md#the-close) shows. Commit with the message `Close the quick run <slug>`. This is the last commit before the push.
2. Push the branch: `git push -u origin <branch>`.
3. Write the PR body of [`format.md`](format.md#the-pr) to a file in a scratch folder outside the repo, `<scratch>`.
4. Check the body for the name of a league manager, as [`format.md`](format.md#no-manager-name) shows. Fix each hit.
5. Run `gh pr create --base main --head <branch> --title "<prefix> <title>" --body-file <file>`. The prefix is `Bug:` for Bugs, or `Quick win:` for Quick wins.
6. Run `python3 scripts/queue.py wait <folder> merge-pr <PR number>`. The folder is `bugs` or `quick-wins`. The wait task lands in `Bugs` or `Quick Wins`.
7. Wait for the CI check: `gh pr checks <PR number> --watch`. If the check `Check` fails, read the log with `gh run view <run id> --log-failed`. Fix the cause in its own commit, then push.

**Stop rule of step 8.** If the push or `gh pr create` fails, stop. Tell Brian the command and its error. If the check `Check` fails two times, stop. Tell Brian the failed test.

## The boundary stop

A boundary rule fails at step 3, or later in the run. Hand off to `4ag:plan`.

1. If a branch exists, write the finding into the quick file. Set the `Boundary:` line to name the rule that fails. Set `Status: blocked`. Add one comment under `## Comments` with the finding and the commits so far. Commit on the branch. Run `python3 scripts/queue.py push <path>`.
2. Push nothing. Open no PR.
3. Tell Brian which rule fails, by its name in step 3, and why.
4. Give Brian a draft outcome statement for `4ag:plan`, as one line he can run: `4ag:plan <what the feature does>, so that <the goal it serves>`. Put in it what the run found.

At step 3, no branch and no quick file exist, so skip part 1. Run `git status --short` and `git branch --list 'bug-*' 'win-*'` before the reply, to show that nothing changed.

## The rules

- Run each `git worktree` command in the main checkout. Commit only in the worktree of the run, never on `main`.
- Never use `--no-verify`. Never force-push. Never merge to `main`. Brian merges the PR.
- Never write a Test verdict. Copy only the lines of the quick Judge. See [`judge.md`](judge.md).
- Never name a league manager in the PR title or body (ADR 0021).
- Only the merge puts `Status: done` on `main`. A quick file gets no row in `docs/agents/state.md`.

## A second start

If the branch of the run exists, find its worktree with `git worktree list`. Read the quick file. Continue at the first item with no `Green:` block, or at the first step that is not done.

## The end

Give Brian the PR address as a bare URL on one line, and the Test verdict of each item. Brian merges the PR. The merge sweep of the next `4ag` skill then completes the queue task and the wait task.
