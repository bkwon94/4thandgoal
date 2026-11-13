# 02: What can the Todoist CLI do for the sync?

Map: `.scratch/todoist-queue/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** done

## Question

The sync calls the Todoist CLI `td`. The spec needs these facts before it picks the shape of the tool:

1. How does `td` find a task by a line in its description? Is there a search or a filter for it, or must the sync list the project and match locally?
2. How does `td` make, update, complete, and uncomplete a task with labels, a section, and a description? Which calls return JSON?
3. How does `td` create and archive a section, and create the labels?
4. What are the limits of `td task add-many` and of the Todoist API rate for an import of about 100 tasks?
5. `td` lives at `/Users/brian.kwon/.nvm/versions/node/v24.15.0/bin/td`, which is not on the default PATH. How does a skill, a subagent in a worktree, and the Codex flow call it?
6. Does a call fail with a clear exit code when the login or the network is missing, so the soft fail can catch it?

## Decision

The facts are in `decisions/02-research-td-facts.notes.md`, from a research agent on 2026-11-12. Each fact cites a `td --help` output, the package source, or the Todoist API docs. No call wrote to Todoist.

1. No filter reads the description. The sync reads the open tasks of the project once with `td task list --project id:<p> --json --all` and matches the key line locally. Completed tasks need `td completed list`, which covers 3 months at most per call.
2. `task add`, `update`, `complete`, `uncomplete`, and `view` take `--json` and `--dry-run`. `task update` cannot change the section, so the sync uses `td task move`. `--labels` replaces the full set of labels.
3. `section create`, `section archive`, and `label create` exist, with no check for a duplicate. The archive of a section also archives its open tasks.
4. `add-many` sends at most 100 commands per request and reports `PARTIAL_FAILURE`. The cap is 1000 sync requests per 15 minutes. `td` does not retry a 429.
5. `td` is on no shell PATH, because nvm loads lazily in `~/.zshrc`. Each call must put `/Users/brian.kwon/.nvm/versions/node/v24.15.0/bin` first on the PATH. The keychain login works from a clean environment. `TODOIST_API_TOKEN` is the fallback for a sandbox.
6. Every failure exits 1. With `--json`, stderr names the cause, such as `AUTH_ERROR` or `API_ERROR`. A network failure can take about 2 minutes per call before it fails.

Two facts change later decisions. The 2-minute hang means the soft fail of decision 01 needs a timeout. The archive of a section must wait until each task in it is complete.
