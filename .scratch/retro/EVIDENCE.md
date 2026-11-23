# Retro: evidence

Spec: `.scratch/retro/PRD.md`. Acceptance tests: `.scratch/retro/ACCEPTANCE.md`.
Built from: `a4a97bcb`, on 2026-11-23. The agent gives no Test verdict. The Judge gives one for each test in `VERDICTS.md`.
Round time: 0 min for 0 site tests. No test takes screenshots. The smoke run is skipped, because the diff has no change to `apps/site/` or `apps/api/`.
Each real Retro ran in a fresh `claude -p` session in a detached worktree at `a4a97bcb`, with `--plugin-dir` set to its `.claude/plugin`.

## AT-1: Claude Code lists `4ag:retro`

App: both
Then: the skill list names `4ag:retro`, and its path resolves to `.claude/plugin/skills/retro/SKILL.md`.
Files: `evidence/AT-1/output.txt`
Observation: The fresh `claude -p` session in the detached worktree at a4a97bcb, with `--plugin-dir` set to its `.claude/plugin`, lists `4ag:retro` with the path `.claude/plugin/skills/retro/SKILL.md`. `readlink -f` of that path resolves to the file in the worktree. The plugin loads with `--plugin-dir`, not with a reinstall into the plugin cache.

## AT-2: Codex lists `4ag:retro`

App: both
Then: the skill list names `4ag:retro` once, and `.agents/skills/4ag-retro` resolves to `.claude/plugin/skills/retro`.
Files: `evidence/AT-2/output.txt`
Observation: `grep -o -- "- 4ag:retro:"` counts 1 line in the output of `codex debug prompt-input "hi"`, and each of the 8 `4ag` skills shows once. `readlink -f .agents/skills/4ag-retro` gives `.claude/plugin/skills/retro` in the Spec worktree.

## AT-3: `add` plans one task in `Bugs` with `needs-triage` and no key line

App: both
Then: the output plans one `td task add` in the section `Bugs` with the label `needs-triage`, and its description has no line that starts with `4ag:`.
Files: `evidence/AT-3/output.txt`
Observation: The output plans one `td task add` with `--section id:6j29GCJqM59vMP2G` and `--labels needs-triage`. The description is "A probe of AT-3." and has no line that starts with `4ag:`. It ends "1 command planned, none sent."

## AT-4: `add` plans one task in `Quick Wins`

App: both
Then: the output plans one `td task add` in the section `Quick Wins`, and no planned command makes a second section of that name.
Files: `evidence/AT-4/output.txt`
Observation: The output plans one `td task add` with `--section id:6j29qJG7gF3jxW4p`, which differs from the Bugs section of AT-3. It plans no `td section add`. It ends "1 command planned, none sent."

## AT-5: `add` of a section outside the three plans no command

App: both
Then: the output plans no `td` command and prints one warning that names the three sections, and the exit code is 0.
Files: `evidence/AT-5/output.txt`
Observation: The output prints one warning: "'Backlog' is not a section for a new task. Use Bugs, Quick Wins, Ideas. Nothing changed." It then prints "0 commands planned, none sent." `echo $?` gives 0.

## AT-6: `add` makes a missing section first

App: both
Then: the run passes, and it holds a case where the snapshot has no `Ideas` section and the plan makes the section before the task.
Files: `evidence/AT-6/output.txt`
Observation: 6 cases pass, 92 deselected. The case of the missing section is `AnAdd::test_an_add_to_a_missing_section_makes_the_section_before_the_task`. Its source, in the same file, gives a snapshot with only the section `Bugs`, adds to `Ideas`, and expects `section create` before `task add`. The system `python3` has no `pytest`, so the command uses `.venv/bin/python -m pytest`, with the same arguments.

## AT-7: `4ag:quick` can take a task that `add` made

App: both
Then: the output plans one `td task update` whose description starts with `4ag: .scratch/bugs/retro-probe.md`, then the line "A probe of AT-7.". After the evidence, the agent deletes the task.
Files: `evidence/AT-7/output.txt`
Observation: `add Bugs` sends one `td task add`. `take --dry-run` plans one `td task update` whose description is `4ag: .scratch/bugs/retro-probe.md`, then "A probe of AT-7.". `td task view` before the delete shows the task with the label `needs-triage` and the description "A probe of AT-7.". `td task delete` deletes it, and a second `td task view` gives HTTP 404.

## AT-8: The end of `4ag:quick` names `/4ag:retro`

App: both
Then: the section names `/4ag:retro <PR number>` as an option for Brian.
Files: `evidence/AT-8/output.txt`
Observation: The section "The end" of `quick/SKILL.md` ends with "Brian can run `/4ag:retro <PR number>` to review the run. It is his choice."

## AT-9: The end of `4ag:implement` names `/4ag:retro`

App: both
Then: the section names `/4ag:retro <PR number>` as an option for Brian.
Files: `evidence/AT-9/output.txt`
Observation: The section "The end" of `implement/SKILL.md` holds "Brian can run `/4ag:retro <PR number>` to review the run. It is his choice."

## AT-10: The real quick Retro prints the stage times

App: both
Then: the reply names the log file that it found, and it prints one line `<stage>: <minutes> min` for each stage of the quick run, then a total.
Files: `evidence/AT-10/output.txt`, `evidence/AT-10/reply.txt`
Observation: The prompt was only `/4ag:retro 91`. The reply names the main log `~/.claude/projects/-Users-brian-kwon-repos-4thandgoal/273e1874-e353-447c-b1f4-846fe1e64dea.jsonl` and three subagent logs under it. It prints six lines in the shape `<stage>: <minutes> min`, then `Total: 80 min`. `ls -l` lists each named log file.

## AT-11: Each candidate of the real quick Retro names a moment in the log

App: both
Then: the list has at least one candidate, and each candidate names a category of the table of the spec, a timestamp, the place of the fix, and a queue section.
Files: `evidence/AT-11/candidates.txt`, `evidence/AT-11/output.txt`
Observation: The reply lists 5 candidates. Each names a category of the table of the spec, a full timestamp, a place for the fix, and a section, `Bugs` or `Quick Wins`. A `grep -rF` finds each of the 7 timestamps in the main log or in a subagent log, and the file shows the matched line.

## AT-12: An accepted candidate becomes one queue task

App: both
Then: the session runs `queue.py add` once, and the queue holds one new task in the named section, whose description holds the timestamp of the moment. No other candidate gets a task.
Files: `evidence/AT-12/output.txt`
Observation: Brian replied "ok" to the advice to pick 2. The resumed session ran `queue.py add Bugs "The smoke run starts with no API keys"` once, and `td` printed "1 command sent.". `td task view` shows the task with the label `needs-triage`, and its description starts "Moment: 2026-11-21T19:13:39.999Z". The reply says candidates 1, 3, 4, and 5 go nowhere.

## AT-13: The real quick Retro changes no repo file

App: both
Then: the output is empty, and no folder `.scratch/retros/` exists.
Files: `evidence/AT-13/before.txt`, `evidence/AT-13/output.txt`
Observation: `git status --short` in the detached worktree is empty before AT-10 and after AT-12. `ls .scratch/retros` gives "No such file or directory".

## AT-14: A quick file as input finds the same run

App: both
Then: the reply names the same log file as AT-10.
Files: `evidence/AT-14/output.txt`
Observation: The reply of `/4ag:retro .scratch/bugs/site-test-leaks.md` names the main log `273e1874-e353-447c-b1f4-846fe1e64dea.jsonl`, the same file as AT-10. The session ran to its list of candidates; the file holds the full reply.

## AT-15: The real spec Retro reads the Judge and the subagents

App: both
Then: the reply names `EVIDENCE.md`, `VERDICTS.md`, the CI runs of PR #88, and at least one log of a subagent that it read.
Files: `evidence/AT-15/output.txt`
Observation: The reply names `EVIDENCE.md` and `VERDICTS.md` at `ae4933cc`, 16 CI runs of PR #88 with the red run ids 44928994748 and 44933648284, and the 17 subagent logs of session `2435e2e3`, with two by name.

## AT-16: Retired: A run with no log reviews the record only

App: both
Then: the reply says that no log matched, and it lists only candidates from the record of the run.
Files: none
Observation: the test is Retired. No evidence is recorded.

## AT-17: The skill text holds the rules of the spec

App: both
Then: the run passes, and it checks that `.claude/plugin/skills/retro/SKILL.md` names the merge sweep, the four inputs with the current session as the default, the Claude log and the Codex log, the drop of a candidate with no moment, each category of the table with its place, `CODING_STANDARDS.md`, and the check for a manager name.
Files: `evidence/AT-17/output.txt`
Observation: 21 cases of `scripts/test_retro_skill.py` pass, 245 deselected. The names cover the merge sweep, the inputs, the logs, the drop rule, the categories, `CODING_STANDARDS.md`, and the check for a manager name. The command uses `.venv/bin/python -m pytest`, because the system `python3` has no `pytest`.

## AT-18: The term Retro is in the glossary

App: both
Then: the output shows the term in the Workflow section, with the _Avoid_ line "Debrief, postmortem, review".
Files: `evidence/AT-18/output.txt`
Observation: Line 1382 holds `**Retro**:` with its definition and `_Avoid_: Debrief, postmortem, review`. The `## Workflow` heading is at line 1292, and no other `##` heading comes after it.

## AT-19: No run starts a Retro on its own

App: both
Then: each hit is in the section "The end" and names `/4ag:retro` as an option for Brian. No hit tells the agent to load `4ag:retro`.
Files: `evidence/AT-19/output.txt`
Observation: The grep has two hits: line 210 of `quick/SKILL.md` and line 61 of `implement/SKILL.md`. Each is the line "Brian can run `/4ag:retro <PR number>` to review the run. It is his choice." in "The end". No hit tells the agent to load `4ag:retro`.

## AT-20: `4ag:plan` and `4ag:quick` keep their stages

App: both
Then: the diff of `plan` is empty, and `quick` does not name `code-review`.
Files: `evidence/AT-20/output.txt`
Observation: The diff stat of `.claude/plugin/skills/plan` is empty. The grep for `code-review` in `quick/SKILL.md` finds no line and exits 1.
