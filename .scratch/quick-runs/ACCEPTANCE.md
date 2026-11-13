# Quick runs: acceptance tests

Spec: `.scratch/quick-runs/PRD.md`.

The Test verdict: the Judge gives one for each test in `VERDICTS.md`. The Judge is a fresh subagent that reads only this file and the evidence. The PR merges when every test has PASS and Brian gives no FAIL in a PR comment (ADR 0026). The agent that builds the work records the evidence and gives no Test verdict.

No test changes the site UI, so no test takes screenshots. Each test takes the command and its output. Each run starts on the head of the Spec branch `quick-runs`, unless the test says otherwise. "The real Bug run" is one run of `4ag:quick` in Claude Code on the queue task "Pick owner: week_moves names the first owner of a traded pick" in the section `Bugs`. "The real Quick win run" is one run on the task "Depth sentence is hard to read", which Brian moves to the section `Quick Wins` first. A `--dry-run` call of `queue.py` sends nothing to Todoist.

## Tests

AT-1: Claude Code lists `4ag:quick`
App: both
Stories: 1, 2
Given: the head of `quick-runs`, with the plugin `4ag` installed from that head.
When: the agent starts a Claude Code session at the worktree root and reads the skill list.
Then: the skill list names `4ag:quick`, and its path resolves to `.claude/plugin/skills/quick/SKILL.md`.
Evidence: the line of the skill list that names `4ag:quick`, and `readlink -f` of its path.

AT-2: Codex lists `4ag:quick`
App: both
Stories: 26
Given: the head of `quick-runs`.
When: the agent runs `codex debug prompt-input "hi"` at the worktree root.
Then: the skill list names `4ag:quick`, and `.agents/skills/4ag-quick` resolves to `.claude/plugin/skills/quick`.
Evidence: the command, the line of its output that names `4ag:quick`, and `readlink -f .agents/skills/4ag-quick`.

AT-3: The skill stops when `diagnosing-bugs` is missing
App: both
Stories: 26, 30
Given: a Codex session where `~/.agents/skills/diagnosing-bugs/SKILL.md` does not exist, such as a session with `HOME` set to an empty scratch folder that holds only the Codex login.
When: the agent sends `$4ag:quick fix the pick owner bug`.
Then: the session stops before it writes a file, and its reply names `diagnosing-bugs` as the missing skill.
Evidence: the session command, the reply, and `git status --short` after the session, which shows no new file.

AT-4: `take` puts the key line first and keeps the description
App: both
Stories: 5, 7, 8
Given: the open task "Pick owner: week_moves names the first owner of a traded pick" in `Bugs`, with its description as Brian wrote it.
When: the agent runs `python3 scripts/queue.py take "Pick owner: week_moves names the first owner of a traded pick" .scratch/bugs/pick-owner.md`.
Then: the first line of the task description is `4ag: .scratch/bugs/pick-owner.md`, the old description follows it unchanged, and the task stays in `Bugs` with the same id.
Evidence: `td task view` of the task before and after, and the command output.

AT-5: `take` of a name outside the two sections plans no command
App: both
Stories: 7
Given: the queue as it is after AT-4.
When: the agent runs `python3 scripts/queue.py take "No such task" .scratch/bugs/none.md --dry-run`.
Then: the output plans no `td` command and prints one warning, and the exit code is 0.
Evidence: the command, its output, and `echo $?`.

AT-6: A push of a bug file goes into the existing section `Bugs`
App: both
Stories: 5, 24
Given: a file `.scratch/bugs/<slug>.md` with `Status: in-progress` that has no task yet.
When: the agent runs `python3 scripts/queue.py push .scratch/bugs/<slug>.md --dry-run`.
Then: the planned `td task add` names the section `Bugs`, and no planned command makes a section `bugs`.
Evidence: the command and its output.

AT-7: A push of a Quick win file makes `Quick Wins` once
App: both
Stories: 6
Given: no section `Quick Wins` in the queue, and two files under `.scratch/quick-wins/`.
When: the agent runs the tests of `scripts/test_queue.py` that push two Quick win files into a fake queue with no `Quick Wins` section.
Then: the plan makes the section `Quick Wins` once, and both tasks go into it.
Evidence: the pytest command, the names of the tests, and their output.

AT-8: The sweep never archives `Bugs` or `Quick Wins`
App: both
Stories: 24, 25
Given: a fake queue where every task in `Bugs` is complete after a merged PR.
When: the agent runs the sweep tests of `scripts/test_queue.py`.
Then: the plan completes the quick task and its wait task, and plans no `section archive` for `Bugs` or `Quick Wins`.
Evidence: the pytest command, the names of the tests, and their output.

AT-9: A spec section still archives
App: both
Stories: none
Given: a fake queue where every task of the spec feature `odds` is complete after a merged PR.
When: the agent runs the sweep tests of `scripts/test_queue.py`.
Then: the plan archives the section `odds`, as before.
Evidence: the pytest command, the name of the test, and its output.

AT-10: An open quick file needs no row in `state.md`
App: both
Stories: 22
Given: a tracked `.scratch/bugs/<slug>.md` with `Status: in-progress`, and no row for it in `docs/agents/state.md`.
When: the agent runs `make check-fast` at the root.
Then: the tracker rule passes, and the new test of `test_rule_tracker.py` for a quick file passes.
Evidence: the command, the tracker rule lines of its output, and the name of the new test.

AT-11: The real Bug run writes the quick file and stops once
App: both
Stories: 1, 3, 4, 7, 28
Given: the task "Pick owner: week_moves names the first owner of a traded pick" in `Bugs`.
When: the agent runs `4ag:quick` with that task name.
Then: the run writes `.scratch/bugs/<slug>.md` with `Kind: bug`, one item with a done condition of one sentence, and a `Boundary:` line, then stops and asks Brian for "go".
Evidence: the quick file at that stop, and the last reply of the run before "go".

AT-12: The real Bug run uses one branch and one worktree
App: both
Stories: 1
Given: the real Bug run after "go".
When: the agent runs `git worktree list` and `git branch --list 'bug-*'` during the build.
Then: one worktree and one branch `bug-<slug>` exist for the run, and no branch `bug-<slug>-<NN>` exists.
Evidence: the two commands and their output.

AT-13: The red loop fails on the bug before the fix
App: both
Stories: 14
Given: the commit of `bug-<slug>` before the fix.
When: the agent runs the command of the Red block of the quick file.
Then: the command fails, and its output shows that `week_moves` names the first owner of the traded pick, not its receiver.
Evidence: the commit SHA, the command, and its output.

AT-14: The same loop passes after the fix
App: both
Stories: 15
Given: the head of `bug-<slug>` after the fix.
When: the agent runs the same command as in AT-13.
Then: the command passes, and the command text is the same as the Red block.
Evidence: the commit SHA, the command, its output, and a diff of the two command lines.

AT-15: The loop adds no mock
App: both
Stories: 29
Given: the diff of `bug-<slug>` against `main`.
When: the agent runs `git diff main...bug-<slug>` and searches it for `mock`, `MagicMock`, `patch(`, and `monkeypatch`.
Then: the diff adds none of those words. A test reads real data or the one fake of a port.
Evidence: the search command and its output.

AT-16: The quick Judge writes one Test verdict per item
App: both
Stories: 17, 21, 31
Given: the real Bug run after the build.
When: the run starts the quick Judge.
Then: the Judge prompt holds only the done conditions and the Red and Green blocks, and the quick file gets one `Test verdict:` line per item.
Evidence: the Judge prompt as sent, and the `Test verdict:` lines of the quick file.

AT-17: The quick Judge gives FAIL to a red loop of another failure
App: both
Stories: 18
Given: a scratch copy of the quick file of the real Bug run, with its Red block changed to the output of an `ImportError` from the same test command.
When: the agent gives the copy to a fresh quick Judge, with the brief of the skill.
Then: the Judge gives FAIL to the item, and its reason says the red evidence does not show the bug of the done condition.
Evidence: the changed Red block, the Judge prompt, and the reply.

AT-18: The quick Judge gives FAIL to a green loop from another command
App: both
Stories: 19
Given: a scratch copy of the quick file of the real Bug run, with its Green block from a different test command.
When: the agent gives the copy to a fresh quick Judge, with the brief of the skill.
Then: the Judge gives FAIL to the item, and its reason says the green evidence does not come from the same loop.
Evidence: the changed Green block, the Judge prompt, and the reply.

AT-19: A text-only item skips the Judge
App: both
Stories: 20
Given: a scratch quick file with two Quick win items, one with `Method: text only` and one with `Method: tdd`.
When: the agent runs the Judge step of the skill on that file.
Then: the Judge prompt holds only the `tdd` item, and the text-only item has `Test verdict: none`.
Evidence: the scratch quick file, the Judge prompt, and the file after the step.

AT-20: The real Bug run closes its quick file before the push
App: both
Stories: 22, 32
Given: the real Bug run after the Judge.
When: the agent reads the last commit of `bug-<slug>` before the push.
Then: the commit sets `Status: done`, and the quick file holds a `Cause:` line and one close comment under `## Comments`.
Evidence: `git show --stat` and `git show` of that commit.

AT-21: The real Bug run opens one PR with the Test verdicts
App: both
Stories: 21
Given: the real Bug run after the push.
When: the agent runs `gh pr view <number> --json title,body,headRefName`.
Then: the title starts with `Bug:`, the head is `bug-<slug>`, and the body lists each item, its done condition, and its Test verdict.
Evidence: the command and its output.

AT-22: The PR body names no league manager
App: both
Stories: 23
Given: the PR of AT-21, and the manager names in `clients/cpc/` and `clients/norcal/`.
When: the agent searches the PR title and body for each manager display name and team name of both clients.
Then: the search finds no name.
Evidence: the search script, the count of names it checked, and its output.

AT-23: The quick PR has no `verdict` gate
App: both
Stories: none
Given: the PR of AT-21, with no `.scratch/bug-<slug>/ACCEPTANCE.md`.
When: the agent reads the commit status `verdict` of the PR head.
Then: `verdict` is `success`, and its log says the PR is not a spec PR.
Evidence: `gh api repos/{owner}/{repo}/commits/<sha>/status` and the line of the verdict log.

AT-24: The queue task follows the run
App: both
Stories: 8, 24
Given: the real Bug run.
When: the agent runs `td task view` on the task after "go", and lists the section `Bugs` after the PR opens.
Then: after "go", the task is the same id as before AT-4 and has the label `in-progress`. After the PR opens, `Bugs` holds a "Merge PR #<number>" wait task.
Evidence: the two `td` outputs.

AT-25: The sweep closes the run after the merge
App: both
Stories: 24, 25
Given: Brian merged the PR of AT-21.
When: the agent runs `python3 scripts/queue.py sweep` at the main checkout root.
Then: the sweep completes the quick task and its wait task, and `td section list 4thandgoal` still lists `Bugs`.
Evidence: the sweep output and the section list.

AT-26: A mixed input starts two runs
App: both
Stories: 12, 13
Given: the two tasks of the real Bug run and the real Quick win run.
When: the agent runs `4ag:quick` with both task names in one call.
Then: the run writes one file under `.scratch/bugs/` and one under `.scratch/quick-wins/`, on two branches `bug-<slug>` and `win-<slug>`, and asks Brian for "go" on each.
Evidence: the two quick files, `git branch --list 'bug-*' 'win-*'`, and the reply at the stop. The agent replies "stop" and removes both worktrees after.

AT-27: The real Quick win run picks `tdd`
App: both
Stories: 2, 6
Given: the task "Depth sentence is hard to read" in `Quick Wins`.
When: the agent runs `4ag:quick` with that task name, up to the stop for "go".
Then: the file `.scratch/quick-wins/<slug>.md` has `Kind: quick-win` and one item with `Method: tdd` or `Method: text only`, and the task is in `Quick Wins`.
Evidence: the quick file and `td task view` of the task.

AT-28: A feature request stops and hands off to `4ag:plan`
App: both
Stories: 9
Given: the head of `quick-runs`.
When: the agent runs `4ag:quick add a page that shows the draft board of each season`.
Then: the run makes no branch and no quick file, says that the rule of no moved seam fails, and gives a draft outcome statement for `4ag:plan`.
Evidence: the reply, and `git status --short` and `git branch --list 'bug-*' 'win-*'` after the run.

AT-29: Six items stop the run
App: both
Stories: 11
Given: the head of `quick-runs`.
When: the agent runs `4ag:quick` with six Bug tasks from `Bugs` in one call.
Then: the run makes no branch, and says that the rule of up to five items fails.
Evidence: the reply, and `git branch --list 'bug-*'` after the run.

AT-30: A run that grows past a rule stops and keeps its work
App: both
Stories: 10
Given: a real Bug run on the task "Recaps: a paragraph with no clear subject, and an injury named twice", stopped after its red loop, where the agent tells the run that the fix needs a new field in `page.json`.
When: the run checks the boundary rules again.
Then: the run commits its quick file with the finding, opens no PR, and gives a draft outcome statement for `4ag:plan`.
Evidence: `git log -1 --stat` of the branch, the finding in the quick file, and the reply.

AT-31: The pointers name `4ag:quick`
App: both
Stories: 33, 34, 27
Given: the head of `quick-runs`.
When: the agent runs `grep -n "4ag:quick" AGENTS.md .claude/plugin/skills/plan/SKILL.md` and `grep -n "quick" docs/agents/issue-tracker.md docs/agents/codex.md`.
Then: `AGENTS.md` names `4ag:quick` in The flow, `4ag:plan` names it in one line, `issue-tracker.md` gives the quick file shape, and `codex.md` gives the install step of `diagnosing-bugs`.
Evidence: the commands and their output.

AT-32: `4ag:implement` and `4ag:review` do not change
App: both
Stories: none
Given: the head of `quick-runs`.
When: the agent runs `git diff --stat main...quick-runs -- .claude/plugin/skills/implement .claude/plugin/skills/review`.
Then: the output is empty.
Evidence: the command and its output.

## Trace

Story 1: AT-1, AT-11, AT-12
Story 2: AT-1, AT-27
Story 3: AT-11
Story 4: AT-11
Story 5: AT-4, AT-6
Story 6: AT-7, AT-27
Story 7: AT-4, AT-5, AT-11
Story 8: AT-4, AT-24
Story 9: AT-28
Story 10: AT-30
Story 11: AT-29
Story 12: AT-26
Story 13: AT-26
Story 14: AT-13
Story 15: AT-14
Story 16: no test. Reason: no open bug is phone-only, and a planted one costs a phone round for a rule of one line. The first real phone bug checks it.
Story 17: AT-16
Story 18: AT-17
Story 19: AT-18
Story 20: AT-19
Story 21: AT-16, AT-21
Story 22: AT-10, AT-20
Story 23: AT-22
Story 24: AT-6, AT-8, AT-24, AT-25
Story 25: AT-8, AT-25
Story 26: AT-2, AT-3
Story 27: AT-31
Story 28: AT-11
Story 29: AT-15
Story 30: AT-3
Story 31: AT-16
Story 32: AT-20
Story 33: AT-31
Story 34: AT-31
Out of scope "a verdict gate on a quick PR": AT-23
Out of scope "a change to the steps of 4ag:implement or 4ag:review": AT-32
Out of scope "parallel items in their own worktrees": AT-12
Out of scope "pull and import for quick files": no test. Reason: an agent that adds them breaks no behavior that a reader sees.
Out of scope "the install of diagnosing-bugs on Brian's Mac": AT-3

## Revisions

None yet.
