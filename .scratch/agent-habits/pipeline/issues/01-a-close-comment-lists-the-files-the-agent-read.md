# 01: A close comment lists the files the agent read

Spec: `.scratch/agent-habits/pipeline/PRD.md`, part 1.

**What to build:** `docs/agents/issue-tracker.md` gains a section "The close comment". A close comment ends with one line: the
count of files the agent read to build the ticket, and their paths. The count is the measure of the vision test
in One's VISION.

**Blocked by:** none.

**Status:** done

- [x] `docs/agents/issue-tracker.md` gains "The close comment": the merge line, the test count, the golden diff, and the files-read
  line. Each line is one sentence.
- [x] The files-read line reads "Read N files: path, path, path." Paths are relative to the repo root. Test files,
  tickets, and ADRs count too, because the agent read them.
- [x] Choice: a file the agent only wrote does not count. The measure is the read cost, not the diff.
- [x] Choice: no token count. A file count is a claim the agent can make without a tool, and the trend shows.
- [x] The first ticket closed after this one carries the line. Its close comment names this ticket.
- [x] A folder that three close comments in a row list is a note in `.scratch/agent-habits/pipeline/PRD.md` under Further
  Notes, as the next README or the next split.

## Comments

- 2026-11-02: built on `main` in one commit, no branch, because the change is one doc section. `docs/agents/issue-tracker.md` gains "The close comment" with four lines: the merge, the proof, the notes, and the files read. This comment is the first one that carries the line, so the fifth box closes here. No test runs on a doc. Read 6 files: docs/agents/issue-tracker.md, .scratch/rules-as-checks/pipeline/PRD.md, .scratch/rules-as-checks/site/issues/02-no-suppression-comments.md, ~/repos/zero/docs/VISION.md, ~/repos/zero/docs/adr/0014-a-merge-request-merges-on-the-verdicts-of-its-acceptance-tests.md, docs/agents/triage-labels.md.
