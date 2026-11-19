# Free ports: two smoke runs at the same time

This run shows that two smoke runs in two worktrees run at the same time, each with its own site server and its own local API on free ports. Both runs are green. Each API gets only the calls of its own site. After the runs, no process holds a port of either run.

Head: `8e3baa6d` in both worktrees. Date: 2026-11-19.

## The commands

1. `git worktree add --detach <scratch>/tg-second HEAD`
2. In `<scratch>/tg-second`: `pnpm install --frozen-lockfile`, then `uv sync --all-packages`.
3. Start both runs in the background, one second apart. `run-smoke.sh` beside this file runs each one:
   - Spec worktree: `sh run-smoke.sh ~/repos/4thandgoal/.claude/worktrees/trusted-green <scratch>/proof/spec-smoke <scratch>/proof/spec-console.log`
   - Second worktree: `sh run-smoke.sh <scratch>/tg-second <scratch>/proof/second-smoke <scratch>/proof/second-console.log`
   - Each one runs `pnpm --dir apps/site smoke --out <smoke folder> "Week report" "Passphrase"`.
4. `lsof -nP -i :<port>` for each of the four ports, and `pgrep` for uvicorn, make api-evidence, and the smoke project. See `ports-after.txt`.
5. `git worktree remove <scratch>/tg-second`

## The ports

| Run | Site server | API | Allowed origin of the API | Repo of the API |
| --- | --- | --- | --- | --- |
| Spec worktree | 127.0.0.1:61066 | 127.0.0.1:61067 | http://127.0.0.1:61066 | the Spec worktree |
| Second worktree | 127.0.0.1:61098 | 127.0.0.1:61099 | http://127.0.0.1:61098 | `<scratch>/tg-second` |

## What the files show

- `spec-times.txt` and `second-times.txt`: the first try of each run stopped on the known Next.js `SecurityFatalError` of an agent session. The script tried once more. The second tries ran from 12:20:37 to 12:21:21 and from 12:20:51 to 12:21:29, so they ran at the same time for 30 s.
- `spec-console.log` and `second-console.log`: the output of the second try. The first line names the site URL, the API URL, and the path of `api.log`.
- `spec-smoke.log` and `second-smoke.log`: each ends with "Smoke run: 2 flows, 2 passed, 0 failed".
- `spec-api.log` and `second-api.log`: each API printed "Uvicorn running on" its own port, and allowed only the origin of its own site server. Each one got 6 calls of `GET /clients/cpc/eggs/board`, one for each flow size of its run, and no call of the other run.
- `ports-after.txt`: no process holds a port of either run, and no API process runs. No smoke folder keeps an `api.pid`, because each run stopped its API.

The flows have `"claude": false`, so the runs need no key.
