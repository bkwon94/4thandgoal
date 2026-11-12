# 05: What does a Todoist task hold?

Map: `.scratch/todoist-queue/MAP.md`.

**Kind:** spec

**Blocked by:** none

**Status:** done

## Question

Each task needs a title format, a description, maybe a link to the ticket file on GitHub, a priority default, and maybe an app label such as `site` or `pipeline`. The repo is public, so a link to a file on `main` works. A file on a local spec branch has no link until the push. The spec records these small choices.

## Decision

The spec records the choice under "The task content (decision ticket 05)" in `.scratch/todoist-queue/PRD.md`. Brian approved the spec on 2026-11-12.

- A ticket task has the title `<NN> <title>`. A decision task has `Decision <NN>: <question>`. A wait task has `Approve PRD`, `Approve ACCEPTANCE`, `Approve tickets`, or `Merge PR #<N>`.
- The description holds the key line, the app, the blockers, a GitHub link for a file on `main` only, and a summary of up to 500 characters.
- A push never sets or changes the priority or the order. It keeps every label outside the flow.
- The app label comes from the subfolder, else the row in `docs/agents/state.md`, else the Apps line of the PRD.
