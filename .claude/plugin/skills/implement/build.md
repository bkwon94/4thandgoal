# The build and the review

Stages 1 and 2 of `4ag:implement`. The main checkout is the repo root on `main`. Run each `git worktree` command there.

## The setup of a worktree

A new worktree has no `node_modules` and no `.venv`, and the hook installs nothing. Run these two commands in each new worktree:

1. `pnpm install --frozen-lockfile` at the root of the worktree.
2. `uv sync --all-packages` at the root of the worktree.

## Stage 1: the build

### The Spec branch

1. If the branch `<slug>` exists, reuse it. Find its worktree with `git worktree list`. If it has no worktree, run `git worktree add .claude/worktrees/<slug> <slug>`.
2. Otherwise run `git worktree add .claude/worktrees/<slug> -b <slug> main`.
3. Do the setup of the worktree.
4. If `main` has commits that the Spec branch does not have, run `git merge --no-edit main` in the Spec worktree. A conflict stops the build: tell Brian.
5. Run `python3 scripts/queue.py pull <slug>` in the Spec worktree. Commit each changed `Status:` line.

### The frontier

The frontier is each ticket whose Status is not `done`, `in-review`, `blocked`, or `wontfix`, and whose blockers are each `done` or `in-review`. Read the lines with `grep -H '^\*\*' .scratch/<slug>/issues/*.md` in the Spec worktree.

If the frontier is empty and no ticket is `ready-for-agent`, go to stage 2.

### Build one ticket

For each ticket `<NN>` of the frontier:

1. Run `git worktree add .claude/worktrees/<slug>-<NN> -b <slug>-<NN> <slug>` in the main checkout.
2. Do the setup of the worktree.
3. Start one subagent with the Agent tool. Give it the brief below. Start the subagents of one frontier in one message, so they run in parallel.

The brief of the subagent:

```text
Build ticket <NN> of the feature <slug> in the 4thandgoal repo.

Work only in the worktree <absolute path of .claude/worktrees/<slug>-<NN>>, on the branch <slug>-<NN>.
Read CLAUDE.md, the CLAUDE.md of each app you change, .scratch/<slug>/PRD.md, .scratch/<slug>/ACCEPTANCE.md,
and .scratch/<slug>/issues/<NN>-*.md.

1. Call the Skill tool for `tdd`. Build the behavior of the ticket test-first, with real data and no mock.
2. Tick each box of the ticket that a test or a real run proves. Leave the Status line as it is.
3. Run `make check-fast BASE=<slug>` at the root of the worktree. It must pass.
4. Commit with a plain `git commit`. The hook must pass. Never use --no-verify.
5. Push nothing. Start no dev server: the evidence stage runs after the merge.
6. Report the commit ids and the test count.

If you cannot make the ticket true, put back each file that you changed, and return
`STUCK: <what I tried / what failed / what I need>`.

Write all output in Simplified Technical English. Rules: `~/.claude/rules/communication/simplified-technical-english.md`.
Active voice, present tense, one instruction per sentence, 20 words or fewer, no `-ing` as a verb, plain words.
Code, technical names, and quoted output are exempt. Refer to Brian by name.
```

### Merge one ticket

Merge one ticket at a time, in the Spec worktree. The other subagents continue meanwhile. This is the merge rule. Stage 2 uses it for each fix branch too.

1. Write down the head of the Spec branch: `git rev-parse HEAD`. This is the head before the merge.
2. Run `git merge --no-edit <slug>-<NN>`.
3. If the merge has a conflict, resolve it yourself in the Spec worktree. Call the Skill tool for `resolving-merge-conflicts`. Start no subagent for the conflict: a send-back costs 10 to 40 minutes per ticket. Commit the merge with the hook. If the hook fails, go to step 5 with its output.
4. Run `make check-fast BASE=main`. It takes about 1 minute. The full check runs in CI on the PR, so no ticket merge waits for it.
5. If the check fails, run `git reset --hard <head before the merge>`. Only then send the failure to the subagent of the ticket, with the conflicted files and the red output. A red check never stays on the Spec branch.
6. If the check passes, set the Status of the ticket to `in-review` in the Spec worktree. Commit it with the message `Mark <slug> <NN> in-review`. Then run `python3 scripts/queue.py push <path of the ticket>`.
7. Remove the ticket worktree: `git worktree remove .claude/worktrees/<slug>-<NN>`.
8. In the Spec worktree, delete the branch: `git branch -d <slug>-<NN>`. The `-d` checks the merge into the Spec branch there.
9. Find the frontier again, and build each new ticket.

### A blocked ticket

If a subagent returns `STUCK`, or a ticket conflicts with the spec or an ADR:

1. Set the Status of the ticket to `blocked` in the Spec worktree. Add the reason as a comment under `## Comments`. Commit. Then run `python3 scripts/queue.py push <path of the ticket>`.
2. Remove the ticket worktree with `git worktree remove --force`. Keep the branch for a second start.
3. Continue with each ticket that the blocked ticket does not block.

**Stop rule of stage 1.** Go to stage 2 when the frontier is empty and no subagent works. Each ticket is then `in-review`, `blocked`, or behind a `blocked` ticket. If no ticket is `in-review`, stop. Tell Brian which tickets are blocked and why.

## Stage 2: the review

1. In the Spec worktree, call the Skill tool for `code-review`. The fixed point is `main`. The spec is `.scratch/<slug>/PRD.md`.
2. If you do not fix a finding, write down its id and the reason, such as a conflict with an ADR. The PR body lists it.
3. List the files that each finding to fix changes.
4. Sort the findings into groups that share no file. Two findings that share a file go in the same group. Give each group a letter: `a`, `b`, and so on.
5. Check that no two groups share a file. Write the table of the groups, with the findings and the files of each.
6. For each group, run `git worktree add .claude/worktrees/<slug>-fix-<letter> -b <slug>-fix-<letter> <slug>` in the main checkout. Do the setup of the worktree.
7. Start one subagent per group with the Agent tool, all in one message, so they run in parallel. Give each one the brief below.
8. Merge each fix branch into the Spec branch under the merge rule of stage 1, one at a time. Read `<slug>-fix-<letter>` for `<slug>-<NN>`. Skip steps 6 and 9, the Status and the frontier.
9. Run `make check-fast BASE=main` again. The CI check `Check` on the PR runs the full check.

The brief of a fix subagent:

```text
Fix the review findings of group <letter> of the feature <slug> in the 4thandgoal repo.

Work only in the worktree <absolute path of .claude/worktrees/<slug>-fix-<letter>>, on the branch <slug>-fix-<letter>.
Read CLAUDE.md, the CLAUDE.md of each app you change, and .scratch/<slug>/PRD.md.

The findings, each with its id, its text, and its files:
<the findings of the group>

1. Fix each finding in its own commit. Name the finding id in the commit message.
2. Change only the files of the group. If a fix needs another file, stop and report it.
3. Run `make check-fast BASE=<slug>` at the root of the worktree before each commit. It must pass.
4. Commit with a plain `git commit`. The hook must pass. Never use --no-verify.
5. Push nothing. Start no dev server.
6. Report the commit id of each finding.

If you cannot fix a finding, put back each file that it changed, and report
`STUCK: <finding id> / <what I tried / what failed / what I need>`.

Write all output in Simplified Technical English. Rules: `~/.claude/rules/communication/simplified-technical-english.md`.
Active voice, present tense, one instruction per sentence, 20 words or fewer, no `-ing` as a verb, plain words.
Code, technical names, and quoted output are exempt. Refer to Brian by name.
```

**Stop rule of stage 2.** If the check fails after the fixes, stop. Tell Brian the failed rule and the commit that broke it.
