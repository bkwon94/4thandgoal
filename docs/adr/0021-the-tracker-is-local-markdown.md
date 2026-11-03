# The tracker is local markdown

The repo is public, and the notes name league managers. A GitHub issue is public too, so it
cannot hold those notes. We decided that the tracker is local markdown under `.scratch/<feature>/`.
GitHub holds only the pull requests, and a pull request names no manager.

## The shape of a feature

A new feature has this shape:

- `MAP.md`: the map, with the headings DESTINATION, DECISIONS SO FAR, NOT YET SPECIFIED, and
  OUT OF SCOPE. The map is optional.
- `decisions/<NN>-<kind>-<slug>.md`: one file for each decision. The kind is `grill`, `research`,
  `prototype`, or `spec`.
- `PRD.md`: the spec in prose.
- `ACCEPTANCE.md`: the acceptance tests, each named `AT-<n>`.
- `issues/`: the tickets.

Old features keep the shape they have. The nine features that touched both repos keep `site/` and
`pipeline/` subfolders, with no renumbering.

## The cost

The tracker has no native blocked-by link and no board. A ticket names its blockers as text, and
`docs/agents/state.md` is the only list of open work. The tracker rule test keeps that list true.
We accept this cost because a private note in a public repo is worse.

We rejected three alternatives:

- **GitHub issues.** They are public and would leak manager names.
- **A private issue tracker.** It adds an account and a second place to look, for one person.
- **A private repo for the notes.** It splits the tickets from the code and breaks the worktree flow.
