# The quick Judge

Step 7 of `4ag:quick`. A fresh subagent, the quick Judge, gives the Test verdict of each item of a quick run (ADR 0033). It did not build the work. It sees only the done conditions and the Red and Green blocks, and the image files that they name.

The common miss of an agent bug fix is a loop that does not match the bug. The loop fails for some other cause, then it passes, and the real bug stays. The builder wrote both halves, so it cannot see this. The quick Judge asks two questions per item to catch it.

## Which items

1. Read the `Method:` line of each item in the quick file.
2. Set `Test verdict: none` on each item with `Method: text only`. It gets no Judge.
3. Each other item goes to the Judge. If no item is left, skip the Judge and go to step 8 of the skill.

## The items of the brief

For each item that goes to the Judge, copy these lines from the quick file, word for word:

````text
### Item <n>: <item title>

Done condition: <the line, word for word>

Red: <the Red block, word for word, with its output>

Green: <the Green block, word for word, with its output>
````

Copy nothing else. Leave out the `Method:`, `Cause:`, and `Test verdict:` lines, the `Boundary:` line, and the comments. Leave out each text-only item.

## Start the Judge

Start a fresh subagent with the strong model. A fresh subagent gets none of the context of the build.

Give it the brief below, word for word. Fill in question 1 for the kind of the run, and the items. Add nothing else. Give it no path, no diff, no code, no cause, and no summary of the work.

Question 1 for a run of Bugs:

```text
Does the red evidence show the bug of the done condition, and not some other failure?
```

Question 1 for a run of Quick wins:

```text
Does the red evidence show the old behavior that the done condition names, and not some other failure?
```

The brief:

````text
You are the quick Judge of one quick run. You did not build the work. Give each item a Test verdict from its evidence only.

Run no command. Read no code, no diff, and no git history. Read no file, with one exception: open an image file that a Red block or a Green block names, to see its screenshot. Open no other file. The items below are all that you judge.

For each item, answer two questions:

1. <question 1>
   A failure of another cause is a no: an import error, a syntax error, a missing file, a missing fixture, a typo, or a failed assertion on some other value.
2. Does the green evidence come from the same loop, at the fixed commit?
   The command of Green must match the command of Red, character for character.
   Green must name a commit other than the commit of Red.
   The output of Green must show a pass.

Give PASS only if the answer to both questions is yes.
Give FAIL if one answer is no. Give one sentence of reason. Name the question, and say what the evidence shows.

Reply with exactly one line per item, in the order below, and no other word:

Item 1: Test verdict: PASS
Item 2: Test verdict: FAIL <reason>

The items:

<the items>
````

## Copy and commit the reply

1. For each line `Item <n>: Test verdict: ...` of the reply, copy the text from `Test verdict:` to the end of the line, word for word. It replaces the `Test verdict:` line of item `<n>` in the quick file.
2. Change no other line.
3. Run `git diff -U0 <path of the quick file>`. Only the `Test verdict:` lines may change.
4. Commit the file alone, with the message `Record the Test verdicts of the quick Judge`. The hook must pass.

Each round is one new commit. Never amend a round. Never write a Test verdict by hand.

## The fix round

A FAIL gets one fix round. There is never a second fix round.

1. Read the reason of the Judge for each failed item.
2. Start a fresh subagent of the item, with the brief of its kind in the skill. Add the reason of the Judge at the end of the brief.
3. The subagent writes a new Red and Green block. Check them as step 6 of the skill does.
4. Start a fresh quick Judge. Never send the brief to the first Judge again. Give it the brief with only the failed items. Add this line at the end of the brief:

   ```text
   An item above that does not pass gets BLOCKED, not FAIL, with one sentence of reason.
   ```

5. Copy and commit the reply, as above.

## The hard stop

After the fix round, an item that does not have PASS stops the run. If the Judge wrote FAIL, not BLOCKED, treat the item as BLOCKED all the same.

1. Set `Status: blocked` in the quick file. Add one comment under `## Comments` with the item and the reason of the Judge. Commit.
2. Run `python3 scripts/queue.py push <path of the quick file>`.
3. Push nothing. Open no PR.
4. Tell Brian the item and the reason of the Judge, quoted from the quick file.

Never change a done condition to make an item pass. A done condition changes only with Brian.
