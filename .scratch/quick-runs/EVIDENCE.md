# Quick runs: evidence

Spec: `.scratch/quick-runs/PRD.md`. Acceptance tests: `.scratch/quick-runs/ACCEPTANCE.md`.
Built from: `f971d14b`, on 2026-11-13. The agent gives no Test verdict. The Judge gives one for each test in `VERDICTS.md`.
Round time: 0 min for 0 site tests. No test takes screenshots.

The real Bug run used two bootstrap steps, because `main` held no `take` and no `Bugs` map before this spec. The queue calls used the `queue.py` of the Spec branch with `--root` at the run worktree. The brief named `format.md` by its path in the Spec worktree.

## AT-1: Claude Code lists `4ag:quick`

App: both
Then: the skill list names `4ag:quick`, and its path resolves to `.claude/plugin/skills/quick/SKILL.md`.
Files: `evidence/AT-1/output.txt`
Observation: The session started with `--plugin-dir` at the head `a41638d8` lists `4ag:quick` among seven `4ag` skills, and `readlink -f` resolves its `SKILL.md` to `.claude/plugin/skills/quick/SKILL.md` in the worktree. The first session in the file loaded the plugin from the main checkout, through the marketplace `4ag-local`, and did not list it.

## AT-2: Codex lists `4ag:quick`

App: both
Then: the skill list names `4ag:quick`, and `.agents/skills/4ag-quick` resolves to `.claude/plugin/skills/quick`.
Files: `evidence/AT-2/output.txt`
Observation: The output of `codex debug prompt-input "hi"` names `4ag:quick` with its description, and `readlink -f .agents/skills/4ag-quick` resolves to `.claude/plugin/skills/quick` in the worktree.

## AT-3: The skill stops when `diagnosing-bugs` is missing

App: both
Then: the session stops before it writes a file, and its reply names `diagnosing-bugs` as the missing skill.
Files: `evidence/AT-3/output.txt`
Observation: With `HOME` at a scratch folder that holds only the Codex login and no `diagnosing-bugs/SKILL.md`, the session replies that `diagnosing-bugs` is absent and that no files or branches change. `git status --short` shows no new file outside the evidence folder, and the branch list is the same before and after.

## AT-4: `take` puts the key line first and keeps the description

App: both
Then: the first line of the task description is `4ag: .scratch/bugs/pick-owner.md`, the old description follows it unchanged, and the task stays in `Bugs` with the same id.
Files: `evidence/AT-4/output.txt`
Observation: Before, the description is the text as Brian wrote it. After `take`, the raw description is `4ag: .scratch/bugs/pick-owner.md`, a line break, then the same text; the id stays `6j29GCWH6fFqqVHp` and the section id `6j29GCJqM59vMP2G` maps to `Bugs`.

## AT-5: `take` of a name outside the two sections plans no command

App: both
Then: the output plans no `td` command and prints one warning, and the exit code is 0.
Files: `evidence/AT-5/output.txt`
Observation: The output is one warning, `the queue has no open task named 'No such task' in Bugs or Quick Wins. Nothing changed.`, then `0 commands planned, none sent.`, and `echo $?` prints 0.

## AT-6: A push of a bug file goes into the existing section `Bugs`

App: both
Then: the planned `td task add` names the section `Bugs`, and no planned command makes a section `bugs`.
Files: `evidence/AT-6/output.txt`
Observation: The plan holds one `td task add` with `--section id:6j29GCJqM59vMP2G`, and the section list maps that id to `Bugs`. No planned command is a `section create`.

## AT-7: A push of a Quick win file makes `Quick Wins` once

App: both
Then: the plan makes the section `Quick Wins` once, and both tasks go into it.
Files: `evidence/AT-7/output.txt`
Observation: The two tests that push two Quick win files into a fake queue with no `Quick Wins` section both print `ok`. Their source, below the run, asserts one `section create` of `Quick Wins` and that both tasks go into it.

## AT-8: The sweep never archives `Bugs` or `Quick Wins`

App: both
Then: the plan completes the quick task and its wait task, and plans no `section archive` for `Bugs` or `Quick Wins`.
Files: `evidence/AT-8/output.txt`
Observation: The two sweep tests of a merged PR in `Bugs` and in `Quick Wins` both print `ok`. Their source, below the run, asserts `task complete` for the quick task and the wait task, and no `section archive`.

## AT-9: A spec section still archives

App: both
Then: the plan archives the section `odds`, as before.
Files: `evidence/AT-9/output.txt`
Observation: The test `AQuickFile.test_a_spec_section_odds_still_archives` prints `ok` at `f971d14b`. Its source, below the run, builds the spec feature `odds` with a done ticket on main and a merged PR, and asserts `task complete` for the ticket and the wait task, then `section archive id:odds`.

## AT-10: An open quick file needs no row in `state.md`

App: both
Then: the tracker rule passes, and the new test of `test_rule_tracker.py` for a quick file passes.
Files: `evidence/AT-10/output.txt`
Observation: A detached commit adds `.scratch/bugs/at10-probe.md` with `Status: in-progress` and no row in `state.md`; the hook passes and `make check-fast` exits 0. The new test `test_an_open_quick_file_needs_no_row` passes, and all 10 tests of `test_rule_tracker.py` pass.

## AT-11: The real Bug run writes the quick file and stops once

App: both
Then: the run writes `.scratch/bugs/<slug>.md` with `Kind: bug`, one item with a done condition of one sentence, and a `Boundary:` line, then stops and asks Brian for "go".
Files: `evidence/AT-11/queue.txt`, `evidence/AT-11/quick-file-at-stop.md`, `evidence/AT-11/reply-before-go.md`
Observation: The quick file at the stop has `Kind: bug`, one item with a done condition of one sentence, and a `Boundary:` line. The reply asks Brian to reply "go", a fix, or "stop". The `take` and `push` calls planned no command, because the task already had this key line and label from AT-26.

## AT-12: The real Bug run uses one branch and one worktree

App: both
Then: one worktree and one branch `bug-<slug>` exist for the run, and no branch `bug-<slug>-<NN>` exists.
Files: `evidence/AT-12/output.txt`
Observation: During the build, `git worktree list` shows one worktree for `bug-pick-owner`, and `git branch --list 'bug-*'` shows `bug-pick-owner` and the separate run `bug-recap-subject` of AT-30. No branch `bug-pick-owner-<NN>` exists.

## AT-13: The red loop fails on the bug before the fix

App: both
Then: the command fails, and its output shows that `week_moves` names the first owner of the traded pick, not its receiver.
Files: `evidence/AT-13/output.txt`
Observation: At `87342a8a`, the command fails with `'2027 round 2 to roster 2' != '2027 round 2 to roster 6'`: `week_moves` names roster 2, the first owner, not roster 6, the receiver. The exit code was not captured; the summary line shows `1 failed`.

## AT-14: The same loop passes after the fix

App: both
Then: the command passes, and the command text is the same as the Red block.
Files: `evidence/AT-14/output.txt`
Observation: At the head `8092dc8a`, after the fix commit `ef0265bb`, the same command prints `1 passed`, and the diff of the Red and Green command lines of the quick file shows no difference.

## AT-15: The loop adds no mock

App: both
Then: the diff adds none of those words. A test reads real data or the one fake of a port.
Files: `evidence/AT-15/output.txt`
Observation: The search of `git diff main...bug-pick-owner` for `mock`, `MagicMock`, `patch(`, and `monkeypatch` on added lines finds no match. The file also holds the added test `test_week_moves.py`, which reads the real saved weeks of cpc from the repo.

## AT-16: The quick Judge writes one Test verdict per item

App: both
Then: the Judge prompt holds only the done conditions and the Red and Green blocks, and the quick file gets one `Test verdict:` line per item.
Files: `evidence/AT-16/judge-prompt.txt`, `evidence/AT-16/judge-reply.txt`, `evidence/AT-16/test-verdict-lines.txt`
Observation: The Judge prompt holds only the done condition and the Red and Green blocks of item 1, with no `Method:`, `Cause:`, or `Boundary:` line. The reply is `Item 1: Test verdict: PASS`, and the quick file has one line `Test verdict: PASS`.

## AT-17: The quick Judge gives FAIL to a red loop of another failure

App: both
Then: the Judge gives FAIL to the item, and its reason says the red evidence does not show the bug of the done condition.
Files: `evidence/AT-17/changed-red-block.txt`, `evidence/AT-17/judge-prompt.txt`, `evidence/AT-17/judge-reply.txt`
Observation: The changed Red block holds an `ImportError` for `load_history` from the same command. The fresh Judge replies FAIL on question 1, because the red evidence shows an `ImportError`, not the wrong owner of a traded pick.

## AT-18: The quick Judge gives FAIL to a green loop from another command

App: both
Then: the Judge gives FAIL to the item, and its reason says the green evidence does not come from the same loop.
Files: `evidence/AT-18/changed-green-block.txt`, `evidence/AT-18/judge-prompt.txt`, `evidence/AT-18/judge-reply.txt`
Observation: The changed Green block runs `tests/test_free_tools.py`, not `tests/test_week_moves.py`. The fresh Judge replies FAIL on question 2, because the Green command does not match the Red command.

## AT-19: A text-only item skips the Judge

App: both
Then: the Judge prompt holds only the `tdd` item, and the text-only item has `Test verdict: none`.
Files: `evidence/AT-19/judge-prompt.txt`, `evidence/AT-19/judge-reply.txt`, `evidence/AT-19/scratch-quick-file-after.md`, `evidence/AT-19/scratch-quick-file-before.md`
Observation: The prompt holds only item 2, the `tdd` item. In the file after the step, item 1 with `Method: text only` has `Test verdict: none`, and item 2 has `Test verdict: PASS` from the reply.

## AT-20: The real Bug run closes its quick file before the push

App: both
Then: the commit sets `Status: done`, and the quick file holds a `Cause:` line and one close comment under `## Comments`.
Files: `evidence/AT-20/output.txt`, `evidence/AT-20/quick-file-at-close.txt`
Observation: The last commit before the push, `ec33c29a`, changes only the quick file: it sets `Status: done` and adds one close comment of four lines under `## Comments`. The whole quick file at `ec33c29a`, in `quick-file-at-close.txt`, holds `Status: done`, the `Cause:` line of item 1, and the close comment under `## Comments`.

## AT-21: The real Bug run opens one PR with the Test verdicts

App: both
Then: the title starts with `Bug:`, the head is `bug-<slug>`, and the body lists each item, its done condition, and its Test verdict.
Files: `evidence/AT-21/output.txt`
Observation: The title is `Bug: Pick owner: week_moves names the first owner of a traded pick`, the head is `bug-pick-owner`, and the body lists item 1 with its done condition and `Test verdict: PASS`.

## AT-22: The PR body names no league manager

App: both
Then: the search finds no name.
Files: `evidence/AT-22/check.py`, `evidence/AT-22/output.txt`
Observation: The script reads the `users.json` of the clients `cpc` and `norcal`, checks 43 display names and team names against the PR title and body, and prints `Hits: none.`

## AT-23: The quick PR has no `verdict` gate

App: both
Then: `verdict` is `success`, and its log says the PR is not a spec PR.
Files: `evidence/AT-23/output.txt`
Observation: The status `verdict` of the PR head `ec33c29a` is `success` with the description `No .scratch/bug-pick-owner/ACCEPTANCE.md, so this PR needs no Test verdict.`, and the verdict log prints the same line. The lines of `verdict.yml` in the file say that a PR with no `ACCEPTANCE.md` is not a spec PR.

## AT-24: The queue task follows the run

App: both
Then: after "go", the task is the same id as before AT-4 and has the label `in-progress`. After the PR opens, `Bugs` holds a "Merge PR #<number>" wait task.
Files: `evidence/AT-24/after-go.txt`, `evidence/AT-24/after-pr.txt`
Observation: After "go", the task has the id `6j29GCWH6fFqqVHp`, the same as in AT-4, and the label `in-progress`. After the PR opens, `Bugs` holds `Merge PR #41` with the label `ready-for-human`.

## AT-25: The sweep closes the run after the merge

App: both
Then: the sweep completes the quick task and its wait task, and `td section list 4thandgoal` still lists `Bugs`.
Files: `evidence/AT-25/first-run-before-fix-e1.txt`, `evidence/AT-25/output.txt`
Observation: The first sweep after the merge planned 0 commands; the file `first-run-before-fix-e1.txt` keeps it, and fix E1 changed the sweep. The sweep at `8a55b056` sends `td task complete` for the quick task and the wait task, neither task is open after it, and `td section list` still lists `Bugs`.

## AT-26: A mixed input starts two runs

App: both
Then: the run writes one file under `.scratch/bugs/` and one under `.scratch/quick-wins/`, on two branches `bug-<slug>` and `win-<slug>`, and asks Brian for "go" on each.
Files: `evidence/AT-26/after-stop.txt`, `evidence/AT-26/branches.txt`, `evidence/AT-26/bugs-pick-owner.md`, `evidence/AT-26/quick-wins-depth-sentence.md`, `evidence/AT-26/reply-at-stop.md`, `evidence/AT-26/step-4-queue.txt`, `evidence/AT-26/steps-1-3.txt`
Observation: The run writes `.scratch/bugs/pick-owner.md` on `bug-pick-owner` and `.scratch/quick-wins/depth-sentence.md` on `win-depth-sentence`, and the reply asks for "go" on each run. After "stop", both worktrees and branches are gone.

## AT-27: The real Quick win run picks `tdd`

App: both
Then: the file `.scratch/quick-wins/<slug>.md` has `Kind: quick-win` and one item with `Method: tdd` or `Method: text only`, and the task is in `Quick Wins`.
Files: `evidence/AT-27/queue.txt`, `evidence/AT-27/quick-file-at-stop.md`, `evidence/AT-27/task-view.txt`
Observation: The quick file has `Kind: quick-win` and one item with `Method: text only`. The task view shows the section id `6j29qJG7gF3jxW4p`, which maps to `Quick Wins`.

## AT-28: A feature request stops and hands off to `4ag:plan`

App: both
Then: the run makes no branch and no quick file, says that the rule of no moved seam fails, and gives a draft outcome statement for `4ag:plan`.
Files: `evidence/AT-28/output.txt`, `evidence/AT-28/reply.md`
Observation: The dry run of `take` finds no task, and the reply says that rule 3, no moved seam, fails and gives a draft line for `4ag:plan`. The branch list and `git status --short` are the same before and after: only `bug-pick-owner` of AT-11 and the untracked evidence folder.

## AT-29: Six items stop the run

App: both
Then: the run makes no branch, and says that the rule of up to five items fails.
Files: `evidence/AT-29/output.txt`, `evidence/AT-29/reply.md`, `evidence/AT-29/tasks.txt`
Observation: Step 1 finds each of six tasks of `Bugs`, and the reply says that rule 1, up to five items of one kind, fails. The branch list is the same before and after, with only `bug-pick-owner` of AT-11.

## AT-30: A run that grows past a rule stops and keeps its work

App: both
Then: the run commits its quick file with the finding, opens no PR, and gives a draft outcome statement for `4ag:plan`.
Files: `evidence/AT-30/output.txt`, `evidence/AT-30/queue.txt`, `evidence/AT-30/quick-file-after-stop.md`, `evidence/AT-30/reply.md`
Observation: The last commit `2c422bbd` changes only the quick file. The file has `Status: blocked`, a `Boundary:` line that fails rule 3, and the finding under `## Comments`. No PR exists, the branch is not pushed, and the reply gives a draft line for `4ag:plan`.

## AT-31: The pointers name `4ag:quick`

App: both
Then: `AGENTS.md` names `4ag:quick` in The flow, `4ag:plan` names it in one line, `issue-tracker.md` gives the quick file shape, and `codex.md` gives the install step of `diagnosing-bugs`.
Files: `evidence/AT-31/output.txt`
Observation: `AGENTS.md:44` names `4ag:quick` in The flow, `plan/SKILL.md:11` names it in one line, `issue-tracker.md:79` starts the section "The quick file" with its shape, and `codex.md` gives the install step of `diagnosing-bugs`.

## AT-32: `4ag:implement` and `4ag:review` do not change

App: both
Then: the output is empty.
Files: `evidence/AT-32/output.txt`
Observation: The command prints no output and exits 0. It uses `origin/main` in place of `main`, because the local `main` is one commit behind `origin/main`.
