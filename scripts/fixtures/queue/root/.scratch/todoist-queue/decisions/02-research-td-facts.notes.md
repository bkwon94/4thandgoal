# 02: Research notes on the Todoist CLI `td`

Ticket: `02-research-td-facts.md`. Date: 2026-11-12.

The installed CLI is `@todoist/cli` 6.1.0. It uses `@todoist/sdk` 19.0.0 and the Todoist API v1.
In these notes, `CLI/` means `/Users/brian.kwon/.nvm/versions/node/v24.15.0/lib/node_modules/@todoist/cli/`.
`SDK/` means `CLI/node_modules/@todoist/sdk/dist/esm/`. `DOCS` means https://developer.todoist.com/api/v1/.

No command in this research wrote to Todoist. Each run was a `--help`, a `--dry-run`, or a read.

## 1. How does `td` find a task by a line in its description?

There is no documented filter for the task description. The sync must list the project and match the key line locally.

- `td task list` has no description flag. It has `--project`, `--label`, `--filter <query>`, `--all`, and `--json` (`td task list --help`).
- `--filter` goes to `GET /api/v1/tasks/filter?query=` (`CLI/dist/lib/task-list.js` line 212, `api.getTasksByFilter`). DOCS, "Get Tasks By Filter": the query is "any supported filter", 1 to 1024 characters, page size up to 200.
- The filter keyword is `search:`. The help article "Introduction to search" (`td hc view id:360000394949`) says only "search: report Shows all tasks that contain the word "report"". It does not say if `search:` reads the description.
- The app search UI has a separate "Task descriptions" tab (same article). The completed-task search "only matches words in a task's name or description" (same article). Neither fact covers the `search:` filter.
- The article "Introduction to filters" (https://www.todoist.com/help/articles/introduction-to-filters-V98wIH) also does not name the fields of `search:`. It says "Todoist filters can't access comment content."
- `search:` matches words. A path such as `.scratch/x/issues/01-a.md` does not make one clean word, so an exact match through `search:` is not reliable.
- A name ref in `td` also uses `search:`, on the task content (`CLI/dist/lib/refs.js` line 209, `getName = t.content`). Always pass `id:<id>` to the commands that take a ref.

The local match is cheap. `td task list --project id:6j222rQrr58wHx9G --json --all` returns `{"results": [...], "nextCursor": null}`. The default JSON fields include `id`, `content`, `description`, `sectionId`, `labels` (`CLI/dist/lib/output.js` line 196, `TASK_ESSENTIAL_FIELDS`). A run now returns `"results": []` with exit 0.

`td task list` returns open tasks only (`api.getTasks`, `GET /api/v1/tasks`). A completed task needs `td completed list --project <p> --search <q> --json` (`td completed list --help`). Its `--since` and `--until` range is 3 months at most. It calls `api.searchCompletedTasks` (`CLI/dist/commands/completed/list.js` line 83).

## 2. How does `td` make, update, complete, and uncomplete a task?

| Action | Command | JSON out | API call (source) |
| --- | --- | --- | --- |
| Make | `td task add "<title>" --project id:<p> --section id:<s> --labels a,b --description "<text>"` or `--stdin` for the description | `--json` | `api.addTask` (`commands/task/add.js` line 104) |
| Update | `td task update id:<t> --content .. --labels a,b --description ..` | `--json` | `api.getTask`, then `api.updateTask` (`commands/task/update.js` line 87) |
| Change section | `td task move id:<t> --section id:<s>`, or `--no-section` | `--json` | `api.moveTask` (`commands/task/move.js` line 47) |
| Complete | `td task complete id:<t>` | `--json` | `api.closeTask` (`commands/task/complete.js` line 33) |
| Uncomplete | `td task uncomplete id:<t>` (help: "requires id:xxx") | `--json` | `api.getTask`, then `api.reopenTask` (`commands/task/uncomplete.js`) |
| Read one | `td task view id:<t> --json` | `--json` | `api.getTask` |

Facts from the help and the source:

- `td task update` has no `--section` flag (`td task update --help`). A change of section is a separate `td task move` call.
- `--labels` on update "replaces existing" labels. `--no-labels` removes all (`td task update --help`). The push can send the full label set each time.
- `td task add --section <name>` needs a section that exists. A dry run gave `{"error":{"code":"SECTION_NOT_FOUND","message":"Section \"todoist-queue\" not found in project."}}` with exit 1. So `--dry-run` on `task add` still reads the API.
- Each of these commands has `--dry-run`.
- `td --help` says "Use --json or --ndjson flags for unambiguous, parseable output" and "Use --quiet to suppress success messages (create commands still print the ID)".
- A label name that does not exist yet: DOCS says only that `labels` is "a list of names that may represent either personal or shared labels". I found no doc line that says the API makes a missing label. I did not test it, because a test writes to Todoist. Brian has 0 personal labels now (`td label list --json --all`, `results` has 0 items).

## 3. How does `td` create and archive a section, and create the labels?

| Action | Command | API call (source) |
| --- | --- | --- |
| List sections | `td section list --project id:<p> --json` | `api.getSections` (`commands/section/list.js` line 27) |
| Create a section | `td section create --name <n> --project id:<p> --json` | `api.addSection` (`commands/section/create.js` line 29) |
| Archive a section | `td section archive id:<s> --json` | `api.getSection`, then `api.archiveSection` (`commands/section/archive.js`) |
| Unarchive a section | `td section unarchive id:<s>` | (help only) |
| List labels | `td label list --json --all` | |
| Create a label | `td label create --name <n> --color <c> --json` | `api.addLabel` (`commands/label/create.js` line 15) |

- DOCS, Sync command `section_archive`: "Archive a section and all its child tasks." Archive of a feature section also archives its open tasks.
- `td label create` does no check for a label that exists. It calls `api.addLabel` directly (`commands/label/create.js`). An idempotent setup must list the labels first.
- `td task add-many` makes a missing section by name. Its schema says: "Section name, reused if the project has one by that name (ignoring case) and created otherwise" (`td task add-many --schema`). A dry run showed `New section: todoist-queue`, exit 0.
- `td section archive id:abc --dry-run` called the API and failed with `API_ERROR` "Non-base32 digit found", exit 1. The dry run of archive also reads the section first.
- The project `4thandgoal` has 0 sections now (`td section list --project id:6j222rQrr58wHx9G --json`).

## 4. Limits of `td task add-many` and the API rate for about 100 tasks

`td task add-many`:

- It reads a JSON array from `--stdin` or `--file`. Each item takes `content`, `description`, `labels`, `section`, `priority`, `due`, `subtasks`, and more (`td task add-many --help`, `--schema`). The schema sets `minItems: 1` and no maximum.
- It sends Sync API `item_add` and `section_add` commands, at most 100 commands per request (`commands/task/add-many.js`, `MAX_COMMANDS_PER_REQUEST = 100`). About 100 tasks plus some new sections is 2 Sync requests. The pre-reads are the project and its sections.
- A partial failure does not undo the rest. It lists the failures on stderr and exits with code `PARTIAL_FAILURE` (`td task add-many --help`; `add-many.js` line 294). With `--json`, stdout has `projectId`, `sections`, `tasks` (each `id`, `content`, `sectionId`, `parentId`), and `failures` (`add-many.js` lines 222 to 248).
- An item can end as `unknown` if a request fails after it is sent. The hint says "check the project before re-running them" (`add-many.js`).
- It cannot update a task. It only makes tasks.

The API, from DOCS "Request limits":

- "For each user, you can make a maximum of 1000 partial sync requests within a 15 minute period."
- "For each user, you can make a maximum of 100 full sync requests within a 15 minute period."
- "The maximum number of commands is 100 per request."
- "There is a 1MiB HTTP request body limit on POST requests." The standard request timeout is 15 seconds.
- The error body can carry `retry_after`, "Seconds to wait before retrying" (DOCS, error fields).
- I found no separate REST limit in DOCS. The REST endpoints answer `429 Rate limit exceeded` and `503 Rate limiter temporarily unavailable`.

Cost of a push of one task at a time, from the source: `td task update id:<t>` does `getTask` plus `updateTask`, so 2 requests. A `td task move` adds more. 100 updates is about 200 to 300 requests. That is below 1000 per 15 minutes, if the REST calls count against the same cap. DOCS does not say if they do.

`td` does not retry a 429. The SDK retries only network errors (see question 6). A 429 maps to `RATE_LIMITED` with the hint "Wait a moment and retry" (`CLI/dist/lib/api/core.js` line 298).

## 5. How does a skill, a subagent, and the Codex flow call `td`?

`td` is not on the PATH of any shell that a tool starts. It is also not on the PATH of an interactive shell.

| Command run | Result |
| --- | --- |
| `env -i HOME=$HOME /bin/zsh -c 'command -v td'` | not found, rc=1; PATH is `~/.cargo/bin:/bin:/usr/bin:/usr/ucb:/usr/local/bin` |
| `env -i HOME=$HOME /bin/zsh -l -c 'command -v td'` | not found, rc=1 |
| `env -i HOME=$HOME /bin/zsh -i -c 'command -v td'` | not found, rc=1 |
| `command -v td` in the Claude Code Bash tool | not found |

- `~/.zshenv`, `~/.zprofile`, and `~/.profile` do not add the nvm `bin` directory. `~/.profile` line 13 adds only `~/.brv-cli/bin`.
- `~/.zshrc` lines 195 to 205 lazy-load nvm. They define shell functions `nvm`, `node`, `npm`, `npx`. They do not put the nvm `bin` on the PATH, so `td` stays missing until a call to `node` loads nvm.
- The file `td` starts with `#!/usr/bin/env node`. A call by the absolute path needs a `node` on the PATH.
  - `env -i HOME=$HOME PATH=/usr/bin:/bin <nvm-bin>/td --version` gives `env: node: No such file or directory`, rc=127.
  - With `/opt/homebrew/bin` first, the absolute path runs under Homebrew node 22.17.0 and prints `6.1.0`. The package sets `"engines": {"node": ">=24"}` (`CLI/package.json` line 48). A run under node 22 is outside the supported range.
- These two forms work from a clean environment, each with rc=0:
  - `PATH=/Users/brian.kwon/.nvm/versions/node/v24.15.0/bin:$PATH td ...`
  - `/Users/brian.kwon/.nvm/versions/node/v24.15.0/bin/node /Users/brian.kwon/.nvm/versions/node/v24.15.0/bin/td ...`
- The login works from a clean environment. `env -i HOME=$HOME PATH=<nvm-bin>:/usr/bin:/bin td section list --project id:6j222rQrr58wHx9G --json` returned `{"results": [], "nextCursor": null}`, rc=0. The token sits in the macOS keychain, service `todoist-cli` (`CLI/dist/lib/auth-store.js` lines 13 and 92, credential store `system`).
- `TODOIST_API_TOKEN` overrides the stored token (`auth-store.js` line 15). `TD_USER` names a stored account (`auth-store.js` line 21).
- A subagent in a worktree runs the same Bash tool as its parent, so it needs the same PATH prefix. Neither `~/.claude/settings.json` nor the repo `.claude/settings*.json` sets an `env` PATH.
- Codex: the profile `4ag` on branch `codex-flow` sets `[permissions.4ag.network] enabled = true` (`git show codex-flow:.codex/config.toml`). This file is not on `main` yet. I did not test a keychain read from inside the Codex sandbox. `TODOIST_API_TOKEN` avoids the keychain if that read fails.
- `~/.codex/config.toml` does not set a PATH that holds the nvm `bin`.

## 6. Does a call fail with a clear exit code without the login or the network?

Every failure exits 1. The kind of failure is in the error code, not in the exit code.

- The entry point catches each error in `reportFatal`, prints it to stderr, and calls `process.exit(1)` (`CLI/dist/index.js` lines 21 to 31 and the `parseAsync().catch` at the end).
- With `--json` or `--ndjson`, stderr gets one JSON line: `{"error":{"code":..,"message":..,"hints":[..]}}` (`formatErrorJson`). Stdout stays empty.
- Bad token, run: `TODOIST_API_TOKEN=invalid td task list --project id:6j222rQrr58wHx9G --json` printed `{"error":{"code":"AUTH_ERROR","message":"HTTP 401: Unauthorized","hints":["Check your API token: td auth status"]}}` and gave exit 1. With `2>/dev/null`, stdout was empty and the exit was 1.
- No token at all: the code is `NO_TOKEN`, "No API token found. Set TODOIST_API_TOKEN or run `td auth login`" (`CLI/dist/lib/auth.js` line 10). I did not run this case, because it needs the keychain entry removed.
- HTTP status to code (`CLI/dist/lib/api/core.js` lines 274 to 302): 401 or 403 gives `AUTH_ERROR`. 404 gives `NOT_FOUND`. 429 gives `RATE_LIMITED`. A 403 with a scope tag gives `MISSING_SCOPE`. A 403 with `PREMIUM_ONLY` gives `PREMIUM_REQUIRED`. Any other status gives `API_ERROR`.
- No network, from the source only: the SDK retries a network error 3 times, with delays of 0 ms, 500 ms, and 500 ms (`SDK/transport/http-client.js` lines 34 and 70). Each request has a 30000 ms timeout. A timeout counts as a network error (`SDK/types/http.js` line 4). After the last retry, the SDK wraps the error as a `TodoistRequestError` with no HTTP status (`SDK/transport/http-client.js` lines 37 to 58). `td` maps that to `API_ERROR` (`core.js` line 301). The exit is 1. A worst case of a hung network is about 4 times 30 s plus 1 s, so about 2 minutes per call.
- A name that matches no task gives `TASK_NOT_FOUND`. More than one match gives `AMBIGUOUS_TASK` (`CLI/dist/lib/refs.js` lines 197 to 207).
- `td task add-many` exits 1 with `PARTIAL_FAILURE` when some items fail (question 4).

## What this means for decision 04

Facts only. No decision here.

1. No documented filter finds a task by its description. One `td task list --project id:<p> --json --all` returns every open task with its `description`, so a local match on the key line costs one paginated read.
2. Open tasks and completed tasks come from two commands. `td completed list` covers 3 months at most per call.
3. A change of section needs `td task move`. `td task update` cannot do it. `--labels` on update replaces the full set.
4. `td task add --section` needs the section to exist first. `td task add-many` makes missing sections by name.
5. `td label create` and `td section create` do not check for a duplicate. The API docs do not say if a task with a missing label makes that label. Brian has 0 labels now.
6. Archive of a section also archives its open tasks (`section_archive` in DOCS).
7. `td task add-many` sends at most 100 commands per Sync request. It only makes tasks, and it reports partial failures with `PARTIAL_FAILURE`.
8. The documented cap is 1000 partial sync requests per user per 15 minutes. A one-task-at-a-time push is about 2 to 3 requests per task.
9. Each `td` call in a skill, a subagent, or Codex must put `/Users/brian.kwon/.nvm/versions/node/v24.15.0/bin` first on the PATH. A bare absolute path to `td` fails with rc 127 when no `node` is on the PATH.
10. Every failure exits 1. With `--json`, stderr names the cause as `AUTH_ERROR`, `NO_TOKEN`, `RATE_LIMITED`, `NOT_FOUND`, `API_ERROR`, or `PARTIAL_FAILURE`. A network failure shows as `API_ERROR` with no HTTP status, after up to about 2 minutes.
11. `td` does not retry a 429. It retries only network errors.
