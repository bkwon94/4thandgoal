# The Judge

Stage 4 of `4ag:implement`. A fresh subagent, the Judge, gives the Test verdict of each acceptance test `AT-<n>`. It writes `.scratch/<slug>/VERDICTS.md`. The check `verdict` reads that file (ADR 0026).

The orchestrator built the work, so it never writes a Test verdict of its own in `VERDICTS.md`. It only copies the lines of the Judge. The Judge did not build the work. It reads only the acceptance tests and the evidence.

## Before the first round

1. Start after the evidence commit of stage 3. Run `git status --short .scratch/<slug>`. It must show no change.
2. Get the blob SHA of each file that the Judge reads:
   - `git hash-object .scratch/<slug>/ACCEPTANCE.md`
   - `git hash-object .scratch/<slug>/EVIDENCE.md`
3. Put the two SHAs in the brief below. The check `verdict` compares them with the files at the PR head.

## Start the Judge

Start a fresh subagent with the strong model. A fresh subagent gets none of the context of the build.

Give it the brief below, word for word, with the slug, the absolute path of the Spec worktree, and the two SHAs filled in. Add nothing to the brief. Give it no diff, no ticket, no PRD, no build note, and no summary of the work.

````text
You are the Judge of the acceptance tests of one spec. You did not build the work. Give each test a Test verdict from its evidence only.

Read only these paths:

- <worktree>/.scratch/<slug>/ACCEPTANCE.md
- <worktree>/.scratch/<slug>/EVIDENCE.md
- <worktree>/.scratch/<slug>/evidence/

Read no other file. Run no git command. Read no code, no diff, no ticket, and no PRD.

For each test AT-<n> of ACCEPTANCE.md:

1. Skip a test with the word Retired in its title. It gets no line.
2. Read its Then line in ACCEPTANCE.md.
3. Read its entry in EVIDENCE.md.
4. Open each file that the entry lists, under evidence/AT-<n>/. Look at each image. Read each text file.
5. Give PASS only if the files show that the Then line is true.
6. Give FAIL if a file is missing, if the files do not cover the Then line, or if the files show something else.
7. Give FAIL if the Observation says something that the files do not show. Trust the files, not the Observation.

A FAIL gets one sentence of reason. Name the line of the test and what the files show.

Write <worktree>/.scratch/<slug>/VERDICTS.md with exactly this shape, and nothing else:

ACCEPTANCE.md: <ACCEPTANCE.md SHA>
EVIDENCE.md: <EVIDENCE.md SHA>

Test verdicts
AT-1: PASS
AT-2: FAIL <reason>

Write one line for each test that is not Retired, in the order of ACCEPTANCE.md. Copy the two SHA lines as they are. Write no other word, heading, or note.

Then reply with the full text of VERDICTS.md.
````

## Check and commit a round

1. Run the check of the file:

   ```sh
   python3 scripts/verdict.py .scratch/<slug>/ACCEPTANCE.md --verdicts .scratch/<slug>/VERDICTS.md --evidence .scratch/<slug>/EVIDENCE.md
   ```

2. Commit the file alone: `git add .scratch/<slug>/VERDICTS.md`, then `git commit -m "Record the Test verdicts of the Judge"`. The hook must pass.
3. Run `git show --stat HEAD`. The commit must change only `VERDICTS.md`.

Each round is one new commit, so each change to a Test verdict leaves a trace. Never amend a round. Never write a Test verdict by hand. In a round on some tests only, copy the lines of the Judge, as "Some tests only" shows.

The check reads each offense:

- `0 offenses.` Each test has PASS. Go to stage 5.
- `verdict/not-pass` names a test with FAIL. In the first round, do the fix round below. After the fix round, stop, as "The hard stop" shows.
- `verdict/missing`, `verdict/unknown`, `verdict/duplicate`, or `verdict/no-verdicts` means the Judge broke the shape. Start a fresh Judge on those tests, with the lines of "Some tests only". This is not a FAIL round.
- `verdict/stale-acceptance` or `verdict/stale-evidence` means a file changed after you got its SHA. Get the SHAs again, and start a fresh Judge on each test.

## The fix round

A FAIL gets one fix round. There is never a second fix round.

1. Read the reason of the Judge for each failed test.
2. Fix the cause on the Spec branch, in its own commit. Use `tdd` when the fix changes behavior. The hook must pass.
3. Run `make check-fast BASE=main` in the Spec worktree.
4. Record the evidence of each failed test again with [`evidence.md`](evidence.md). Change only the entries of those tests in `EVIDENCE.md`.
5. Commit `EVIDENCE.md` and the changed files of `evidence/` with the message `Record the evidence of <slug> again`. The hook must pass.
6. Get the two SHAs again with `git hash-object`.
7. Start a fresh Judge. Never send the brief to the first Judge again. Give it the brief of the first round, with the new SHAs. Add the lines of "Some tests only" at its end, then the line of "After a fix".
8. Copy the reply of the Judge into `VERDICTS.md`, as "Some tests only" shows.
9. Check and commit the round, as above.

### Some tests only

Add these lines to the brief when the Judge checks only some tests:

````text
Judge only these tests: AT-<n>, AT-<m>. These lines replace the steps above where they differ.

Write no file. Reply with only the line AT-<n>: ... of each test above, in the order of ACCEPTANCE.md. Write no other word.
````

The Judge of such a round does not see the old lines of `VERDICTS.md`, so an old FAIL reason does not steer it. The orchestrator writes its reply into the file:

1. Copy each line `AT-<n>: ...` of the reply word for word into `VERDICTS.md`. Replace the line of that test.
2. Set the two SHA lines to the new SHAs.
3. Change no other line.
4. Run `git diff -U0 .scratch/<slug>/VERDICTS.md`. Only the two SHA lines and the lines of the named tests may change.

### After a fix

Add this line too when the tests had a FAIL and got a fix. A second FAIL then shows as BLOCKED:

````text
A test above that does not pass gets BLOCKED, not FAIL, with one sentence of reason.
````

### The hard stop

After the fix round, a test that does not have PASS stops stage 4. If the Judge wrote FAIL, not BLOCKED, treat the test as BLOCKED all the same:

1. Push nothing.
2. Open no PR.
3. Tell Brian the test and the reason of the Judge, quoted from `VERDICTS.md`.

Never change `ACCEPTANCE.md` to make a test pass. An acceptance test changes only with `4ag:to-acceptance` and Brian.

A test that `evidence.md` skipped, because its ticket is `blocked`, gets no fix round. Its FAIL stays until the ticket builds. Then [`pr.md`](pr.md#a-second-start) runs the Judge on it.

**Stop rule of stage 4.** Go to stage 5 when each test has PASS, or when each FAIL names a test of a `blocked` ticket. If a test has no PASS after the fix round, stop, even if the Judge wrote FAIL. Push nothing and open no PR. Tell Brian each such test and the reason of the Judge, quoted from `VERDICTS.md`.
