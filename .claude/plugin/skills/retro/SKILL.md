---
name: retro
description: Review one finished quick run or spec build of this repo, and propose fixes to the environment of the agent, not to the code. Read the record of the run and its session log, give the stage times, list the candidates in order of severity, and file each one that Brian accepts in the queue. Use only when Brian runs /4ag:retro.
argument-hint: '[<PR number> | <quick file> | <feature slug>]'
---

# Retro

A Retro looks back on one finished run: a quick run of `4ag:quick` or a spec build of `4ag:implement`. It finds the moments where the agent struggled. For each moment, it proposes a fix to the environment of the agent, so that the next run avoids the problem. Brian accepts each fix by its number.

Brian starts each Retro. No other skill starts it, because a smooth run teaches little.

The Retro only proposes and files. It changes no code, no check, and no steering file, and it writes no repo file. A quick run or a spec builds each accepted fix later, with its own check.

## The queue

Run each call at the root of the checkout or worktree. A failed call prints a warning and exits 0, so never stop on it. Name each missed call in the final report.

Start with the merge sweep: `python3 scripts/queue.py sweep`.

Step 7 holds the other calls.

## Before you start

1. Check that the global skill `writing-for-agents` is in the available skill list. The `4ag` skills ship with this skill, so do not check them.
2. If it is missing, stop. Tell Brian the name of the missing skill. Do not guess its steps.
3. Run `gh auth status`. If it fails, stop. Tell Brian to run `gh auth login`.
4. Read ADR 0033 in `docs/adr/` and the Workflow section of `GLOSSARY.md`.

## Invocation

| Command | The run |
| --- | --- |
| `/4ag:retro` | With no argument, the run of the current session. |
| `/4ag:retro <PR number>` | The quick run or the spec build of that PR. |
| `/4ag:retro <quick file>` | The quick run of a file under `.scratch/bugs/` or `.scratch/quick-wins/`. |
| `/4ag:retro <feature slug>` | The spec build of the feature `.scratch/<feature slug>/`. |

## Step 1: find the run

1. For a PR number, run `gh pr view <PR number> --json number,title,headRefName,mergeCommit,url,body`. The head branch names the run. A branch `bug-<slug>` or `win-<slug>` is a quick run. Any other branch is the Spec branch of a spec build.
2. For a quick file, read the `Branch:` line of the file. Find the PR with `gh pr list --state all --head <branch> --json number,url`.
3. For a feature slug, the Spec branch is `<slug>`. Find the PR in the same way.
4. With no argument, use the branch and the worktree of the current session.
5. Write down the branch, the worktree path `.claude/worktrees/<branch>`, and the PR number.

## Step 2: read the record of the run

Read each file from the merge commit on `main`, with `git show <commit>:<path>`, or from the branch if the PR is open.

1. For a quick run, read the quick file.
2. For a spec build, read `.scratch/<slug>/PRD.md`, `.scratch/<slug>/EVIDENCE.md`, and `.scratch/<slug>/VERDICTS.md`.
3. For both, read the PR comments: `gh pr view <PR number> --comments`. Note each FAIL from Brian and each review comment.
4. For both, read the CI runs: `gh run list --branch <branch> --json databaseId,conclusion,name,createdAt`. For each red run, read the raw log with `gh run view <run id> --log-failed`.
5. Name each record file that you read in the reply, such as `EVIDENCE.md` and `VERDICTS.md`, and the id of each CI run.

## Step 3: find the session logs

The session log shows the struggles that the record does not show. Read the log of each harness:

- **The Claude log.** Each session is one `.jsonl` file under `~/.claude/projects/<the folder of the repo>/`. The folder name is the path of the checkout or the worktree, with each `/` and `.` as `-`. A worktree has its own folder, such as `-Users-<user>-repos-4thandgoal--claude-worktrees-<branch>`. The logs of the subagents of a session sit in `<session id>/subagents/`.
- **The Codex log.** Each session is one `.jsonl` file under `~/.codex/sessions/<year>/<month>/<day>/`.

1. With no argument, read the log of the current session.
2. Otherwise, find each log that names the branch or the worktree path: `grep -rl -e '<branch>' -e '.claude/worktrees/<branch>' ~/.claude/projects/ ~/.codex/sessions/`.
3. Keep the logs whose time falls between the first commit of the branch and the merge.
4. For a spec build, read the logs of the subagents too. The struggle of a ticket shows in the log of its subagent.
5. Name each log file that you read in the reply, with its full path.
6. If no log matches, or no log is left after item 3, say "No log matched the run." Review the record only, and give no stage times.

## Step 4: give the stage times

Take each stage time from the timestamps of the log. Do not ask for a timestamp step in `4ag:quick` or `4ag:implement`.

1. For a quick run, the stages are the steps of `4ag:quick`: the boundary and the "go", the build of each item, the smoke run, the quick Judge, and the PR to a green check.
2. For a spec build, the stages are the stages of `4ag:implement`: the build of each ticket, the review, the evidence, the Judge, and the PR to a green check.
3. Print one line per stage in the shape `<stage>: <minutes> min`. Then print the line `Total: <minutes> min`. Keep each stage line to that shape. Put a note on its own line under it.

## Step 5: find the candidates

1. Load the skill `writing-for-agents`. Use it for the text of each proposed change to a skill or a steering file.
2. Read the logs from start to end. Look for each moment where the agent struggled: a red check, a retry, a long search, a wrong guess, a question to Brian, a `STUCK`, or a fix round.
3. Give each moment one category from the table below. The category sets the place of the fix.
4. Copy the timestamp of each moment in full from the `timestamp` field of its log line, such as `2026-11-21T19:28:19.766Z`. A `grep` of that text finds the line. The log writes UTC, so never label the time as a local time.
5. Drop each candidate with no moment in the log. A candidate with no moment is generic advice.
6. Before you propose a check, read `Makefile`, `scripts/`, the rule tests, and `.github/workflows/`. A check that exists is the finding, not a reason to build a second check.

## The categories

| What went wrong | The fix |
| --- | --- |
| A mechanical mistake | A check: a rule test, a script in `scripts/`, a lint rule, or a hook. A check that exists but is not connected gets connected. |
| A judgement mistake that `code-review` missed | A rule in the root `CODING_STANDARDS.md`. |
| A slow search for a file or a fact | A pointer from a file that the agent already reads, such as a README or an `AGENTS.md`. |
| A gap or an error in a `4ag` skill text | A change to that skill. |
| A costly tool call | A cheaper tool or a change to the call. |
| A line in a steering file that changes nothing | A delete. |
| Information that the agent could not reach | Wider access, such as a log file or a read-only token. |

- A mistake with a fixed pattern is mechanical. It gets a check, because a check fails and a sentence does not.
- A judgement rule goes to `CODING_STANDARDS.md`, because `code-review` reads it at review time.
- If no such file exists, the candidate of the first judgement rule proposes `CODING_STANDARDS.md` at the repo root, with that rule.
- Never propose a rule in an `AGENTS.md` or a `CLAUDE.md`. Each session loads them. They hold pointers only.
- A gap in a `4ag` skill gets a change to that skill, never a memory note.

## Step 6: show the candidates

Show the candidates as one numbered list, in order of severity. Put the most costly problem first. Each item has:

1. The category, from the table.
2. The moment: the timestamp, the log file, and one line of what happened.
3. The proposed fix and its place in the repo.
4. The queue section: `Bugs`, `Quick Wins`, or `Ideas`.

Ask Brian to reply with the numbers that he accepts. Then stop and wait. A candidate that Brian does not accept goes nowhere.

The section of a candidate:

- A candidate that passes the four rules of ADR 0033 goes to `Bugs` when it fixes a mistake, or to `Quick Wins` when it changes text or behavior on purpose.
- A larger candidate goes to `Ideas`. Its description holds a draft outcome statement: `4ag:plan <what the feature does>, so that <the goal it serves>`.

## Step 7: file each accepted candidate

Do these steps for each number that Brian accepts, and for no other candidate.

1. Write the title and the description of the task. The description holds the moment with its timestamp, the category, and the proposed fix.
2. Write the description to a file in a scratch folder outside the repo, `<scratch>`.
3. Check the title and the description for the name of a league manager (ADR 0021). Run this check at the root of the checkout. Rewrite the text until it prints `Hits: none.`

   ```sh
   python3 - <description file> "<title>" <<'EOF'
   import json, pathlib, re, sys
   text = (pathlib.Path(sys.argv[1]).read_text() + "\n" + sys.argv[2]).lower()
   names = set()
   for path in pathlib.Path("clients").glob("*/data/**/users.json"):
       for user in json.loads(path.read_text()):
           names.add(user.get("display_name") or "")
           names.add((user.get("metadata") or {}).get("team_name") or "")
   names.discard("")
   hits = sorted(name for name in names if re.search(rf"\b{re.escape(name.lower())}\b", text))
   print(f"Checked {len(names)} names. Hits: {', '.join(hits) or 'none'}.")
   EOF
   ```

4. Run `python3 scripts/queue.py add <section> "<title>" --description "<text>"`. The section is `Bugs`, `Quick Wins`, or `Ideas`. Make each task only with `queue.py add`.

## The rules

- Change no code, no check, no skill, and no steering file. Write no repo file, and make no branch and no PR.
- Never propose a candidate with no moment in the log.
- File only the numbers that Brian accepts.
- Never name a league manager in a queue task (ADR 0021).

## The end

Give Brian the stage times, the number of candidates, and each task that `queue.py add` made, with its section. Name each failed call. Brian builds a task in `Bugs` or `Quick Wins` with `4ag:quick`, and a task in `Ideas` with `4ag:plan`.
