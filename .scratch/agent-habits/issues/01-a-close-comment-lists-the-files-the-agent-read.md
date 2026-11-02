# 01: A close comment lists the files the agent read

Spec: `.scratch/agent-habits/PRD.md`, part 1.

**What to build:** `docs/agents/issue-tracker.md` gains a section "The close comment". A close comment ends with one line: the
count of files the agent read to build the ticket, and their paths. The count is the measure of the vision test
in One's VISION.

**Blocked by:** none.

**Status:** needs-triage

- [ ] `docs/agents/issue-tracker.md` gains "The close comment": the merge line, the test count, the golden diff, and the files-read
  line. Each line is one sentence.
- [ ] The files-read line reads "Read N files: path, path, path." Paths are relative to the repo root. Test files,
  tickets, and ADRs count too, because the agent read them.
- [ ] Choice: a file the agent only wrote does not count. The measure is the read cost, not the diff.
- [ ] Choice: no token count. A file count is a claim the agent can make without a tool, and the trend shows.
- [ ] The first ticket closed after this one carries the line. Its close comment names this ticket.
- [ ] A folder that three close comments in a row list is a note in `.scratch/agent-habits/PRD.md` under Further
  Notes, as the next README or the next split.
