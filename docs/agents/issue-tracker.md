# Issue tracker: Local Markdown

Issues and PRDs for this repo live as markdown files in `.scratch/`, the same convention as the
pipeline repo `cornerstone-fantasy-sleeper-weekly-report`.

- One feature per directory: `.scratch/<feature-slug>/`
- The PRD is `.scratch/<feature-slug>/PRD.md`
- Issues are `.scratch/<feature-slug>/issues/<NN>-<slug>.md`, numbered from `01`
- Triage state is a `Status:` line near the top of each file
- Comments append under a `## Comments` heading

## The close comment

A ticket closes with one comment under `## Comments`. Each line is one sentence.

1. The merge: the branch, the commits, and the date.
2. The proof: the test count, and the golden diff if one exists.
3. The notes for a later ticket, if any.
4. The files read: "Read N files: path, path, path." Paths are relative to the repo root.

The files-read line is the measure of the One vision test: an agent changes the repo without a read of most of
it. Count every file the agent read to build the ticket: source, tests, tickets, ADRs. A file the agent only wrote
does not count. A folder that three close comments in a row list is the next README or the next split. Note it
under Further Notes in the PRD of the feature.
