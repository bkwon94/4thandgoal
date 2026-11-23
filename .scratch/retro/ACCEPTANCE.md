# Retro: acceptance tests

Spec: `.scratch/retro/PRD.md`.

The Test verdict: the Judge gives one for each test in `VERDICTS.md`. The Judge is a fresh subagent that reads only this file and the evidence. The PR merges when every test has PASS and Brian gives no FAIL in a PR comment (ADR 0026). The agent that builds the work records the evidence and gives no Test verdict.

No test changes the site UI, so no test takes screenshots. Each test takes the command and its output. Each run starts on the head of the Spec branch `retro`, unless the test says otherwise. "The real quick Retro" is one run of `/4ag:retro 91` in Claude Code, over PR #91 "Bug: Site tests leak temp folders and reach the live API", merged as `d2c4e9ed`. "The real spec Retro" is one run of `/4ag:retro trade-block`, over the spec build of PR #88, merged as `ae4933cc`. A `--dry-run` call of `queue.py` sends nothing to Todoist.

## Tests

AT-1: Claude Code lists `4ag:retro`
App: both
Stories: 1
Given: the head of `retro`, with the plugin `4ag` installed from that head.
When: the agent starts a Claude Code session at the worktree root and reads the skill list.
Then: the skill list names `4ag:retro`, and its path resolves to `.claude/plugin/skills/retro/SKILL.md`.
Evidence: the line of the skill list that names `4ag:retro`, and `readlink -f` of its path.

AT-2: Codex lists `4ag:retro`
App: both
Stories: 40
Given: the head of `retro`.
When: the agent runs `codex debug prompt-input "hi"` at the worktree root.
Then: the skill list names `4ag:retro` once, and `.agents/skills/4ag-retro` resolves to `.claude/plugin/skills/retro`.
Evidence: the command, the line of its output that names `4ag:retro`, and `readlink -f .agents/skills/4ag-retro`.

AT-3: `add` plans one task in `Bugs` with `needs-triage` and no key line
App: both
Stories: 30, 38
Given: the queue as it is.
When: the agent runs `python3 scripts/queue.py add Bugs "Retro probe bug" --description "A probe of AT-3." --dry-run`.
Then: the output plans one `td task add` in the section `Bugs` with the label `needs-triage`, and its description has no line that starts with `4ag:`.
Evidence: the command and its output.

AT-4: `add` plans one task in `Quick Wins`
App: both
Stories: 30
Given: the queue as it is.
When: the agent runs `python3 scripts/queue.py add "Quick Wins" "Retro probe win" --description "A probe of AT-4." --dry-run`.
Then: the output plans one `td task add` in the section `Quick Wins`, and no planned command makes a second section of that name.
Evidence: the command and its output.

AT-5: `add` of a section outside the three plans no command
App: both
Stories: 37
Given: the queue as it is.
When: the agent runs `python3 scripts/queue.py add Backlog "Retro probe" --description "A probe of AT-5." --dry-run`.
Then: the output plans no `td` command and prints one warning that names the three sections, and the exit code is 0.
Evidence: the command, its output, and `echo $?`.

AT-6: `add` makes a missing section first
App: both
Stories: 30, 31
Given: the unit tests of `queue.py` at the head of `retro`.
When: the agent runs `python3 -m pytest scripts/test_queue.py -q -k add`.
Then: the run passes, and it holds a case where the snapshot has no `Ideas` section and the plan makes the section before the task.
Evidence: the command, its output, and the name of the case of the missing section.

AT-7: `4ag:quick` can take a task that `add` made
App: both
Stories: 39
Given: one real task "Retro probe take" that `python3 scripts/queue.py add Bugs "Retro probe take" --description "A probe of AT-7."` made.
When: the agent runs `python3 scripts/queue.py take "Retro probe take" .scratch/bugs/retro-probe.md --dry-run`.
Then: the output plans one `td task update` whose description starts with `4ag: .scratch/bugs/retro-probe.md`, then the line "A probe of AT-7.". After the evidence, the agent deletes the task.
Evidence: the two commands, their output, `td task view` of the task before the delete, and the delete command.

AT-8: The end of `4ag:quick` names `/4ag:retro`
App: both
Stories: 2
Given: the head of `retro`.
When: the agent reads the section "The end" of `.claude/plugin/skills/quick/SKILL.md`.
Then: the section names `/4ag:retro <PR number>` as an option for Brian.
Evidence: the text of the section.

AT-9: The end of `4ag:implement` names `/4ag:retro`
App: both
Stories: 3
Given: the head of `retro`.
When: the agent reads the section "The end" of `.claude/plugin/skills/implement/SKILL.md`.
Then: the section names `/4ag:retro <PR number>` as an option for Brian.
Evidence: the text of the section.

AT-10: The real quick Retro prints the stage times
App: both
Stories: 5, 12, 14
Given: the session log of the quick run of PR #91 on this machine.
When: the agent runs the real quick Retro in a fresh session, with no path to a log in the prompt.
Then: the reply names the log file that it found, and it prints one line `<stage>: <minutes> min` for each stage of the quick run, then a total.
Evidence: the full reply of the session, and `ls -l` of the log file that it names.

AT-11: Each candidate of the real quick Retro names a moment in the log
App: both
Stories: 15, 16, 17, 18
Given: the reply of AT-10.
When: the agent reads the list of candidates.
Then: the list has at least one candidate, and each candidate names a category of the table of the spec, a timestamp, the place of the fix, and a queue section.
Evidence: the list of candidates, and for each timestamp the matched line of the log, found with `grep`.

AT-12: An accepted candidate becomes one queue task
App: both
Stories: 29, 30, 31, 32, 34
Given: the session of AT-10, after the list of candidates.
When: Brian replies with the number of one candidate.
Then: the session runs `queue.py add` once, and the queue holds one new task in the named section, whose description holds the timestamp of the moment. No other candidate gets a task.
Evidence: the reply of Brian, the command that the session ran with its output, and `td task view` of the new task.

AT-13: The real quick Retro changes no repo file
App: both
Stories: 35, 36
Given: a clean worktree on the head of `retro`, before AT-10.
When: the agent runs `git status --short` after AT-12.
Then: the output is empty, and no folder `.scratch/retros/` exists.
Evidence: `git status --short` before AT-10 and after AT-12, and `ls .scratch/retros`.

AT-14: A quick file as input finds the same run
App: both
Stories: 6
Given: the quick file of PR #91, `.scratch/bugs/site-test-leaks.md`.
When: the agent runs `/4ag:retro .scratch/bugs/site-test-leaks.md` in a fresh session, and stops it after the stage times.
Then: the reply names the same log file as AT-10.
Evidence: the command, the reply up to the stage times, and the log file of AT-10.

AT-15: The real spec Retro reads the Judge and the subagents
App: both
Stories: 7, 9, 10, 11, 13
Given: the session logs of the spec build of `trade-block` on this machine.
When: the agent runs the real spec Retro in a fresh session, and stops it after the list of candidates.
Then: the reply names `EVIDENCE.md`, `VERDICTS.md`, the CI runs of PR #88, and at least one log of a subagent that it read.
Evidence: the full reply of the session.

AT-16: A run with no log reviews the record only
App: both
Stories: 12
Given: a merged PR whose branch name no session log names, found by the agent with `grep -rl` over the Claude log folder and `~/.codex/sessions/`.
When: the agent runs `/4ag:retro <that PR number>` in a fresh session.
Then: the reply says that no log matched, and it lists only candidates from the record of the run.
Evidence: the `grep -rl` command with its empty output, and the full reply.

AT-17: The skill text holds the rules of the spec
App: both
Stories: 4, 8, 13, 16, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 33, 42
Given: the head of `retro`.
When: the agent runs the text test of the skill, `python3 -m pytest scripts -q -k retro`.
Then: the run passes, and it checks that `.claude/plugin/skills/retro/SKILL.md` names the merge sweep, the four inputs with the current session as the default, the Claude log and the Codex log, the drop of a candidate with no moment, each category of the table with its place, `CODING_STANDARDS.md`, and the check for a manager name.
Evidence: the command, its output, and the names of the cases.

AT-18: The term Retro is in the glossary
App: both
Stories: 41
Given: the head of `retro`.
When: the agent runs `grep -n -A2 '^\*\*Retro' GLOSSARY.md`.
Then: the output shows the term in the Workflow section, with the _Avoid_ line "Debrief, postmortem, review".
Evidence: the command and its output.

AT-19: No run starts a Retro on its own
App: both
Stories: none
Given: the head of `retro`.
When: the agent runs `grep -n "retro" .claude/plugin/skills/quick/SKILL.md .claude/plugin/skills/implement/*.md`.
Then: each hit is in the section "The end" and names `/4ag:retro` as an option for Brian. No hit tells the agent to load `4ag:retro`.
Evidence: the command and its output.

AT-20: `4ag:plan` and `4ag:quick` keep their stages
App: both
Stories: none
Given: the head of `retro`.
When: the agent runs `git diff main...retro --stat -- .claude/plugin/skills/plan`, then `grep -n "code-review" .claude/plugin/skills/quick/SKILL.md`.
Then: the diff of `plan` is empty, and `quick` does not name `code-review`.
Evidence: the two commands and their output.

## Trace

Story 1: AT-1
Story 2: AT-8
Story 3: AT-9
Story 4: AT-17, AT-19
Story 5: AT-10
Story 6: AT-14
Story 7: AT-15
Story 8: AT-17
Story 9: AT-15
Story 10: AT-15
Story 11: AT-15
Story 12: AT-10, AT-16
Story 13: AT-15, AT-17
Story 14: AT-10
Story 15: AT-11
Story 16: AT-11, AT-17
Story 17: AT-11
Story 18: AT-11
Story 19: AT-17
Story 20: AT-17
Story 21: AT-17
Story 22: AT-17
Story 23: AT-17
Story 24: AT-17
Story 25: AT-17
Story 26: AT-17
Story 27: AT-17
Story 28: AT-17
Story 29: AT-12
Story 30: AT-3, AT-4, AT-6, AT-12
Story 31: AT-6, AT-12
Story 32: AT-12
Story 33: AT-17
Story 34: AT-12
Story 35: AT-13
Story 36: AT-13
Story 37: AT-5
Story 38: AT-3
Story 39: AT-7
Story 40: AT-2
Story 41: AT-18
Story 42: AT-17
Out of scope "An automatic Retro at the end of each run": AT-19
Out of scope "A change to `4ag:plan`": AT-20
Out of scope "A change to `4ag:quick` to run `code-review`": AT-20
Out of scope "A retro file in the repo": AT-13
Out of scope "An audit of the checks that a past Retro added": no test. Reason: no agent builds it by mistake, because the skill reads one run.
Out of scope "A Retro over many runs at once": no test. Reason: each input names one run.

## Revisions

None yet.
