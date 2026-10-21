# Runbook: the site API on Fly.io

This runbook tells you how to deploy, check, and run the Cornerstone API at `api.cpcfantasy.com`.

## What runs where

The API is one FastAPI app in one Docker image on Fly.io, app `cpcfantasy-api`, region `ewr`. The machine
stops when no request comes, and the next request starts it again. A GitHub Actions cron calls `POST /refresh`
every day at 10:00 UTC, so the slow sources and the chart are fresh before the managers wake. The cron never
deploys. You deploy by hand from this runbook.

The data layout:

| Path in the machine | What it holds |
| --- | --- |
| `/app` | The repo root, `CORNERSTONE_REPO`. It holds `src/` and the link `data`. |
| `/app/data` | A link to `/data`, so every path helper lands on the volume with no change to the code. |
| `/data` | The volume `cornerstone_data`, 1 GB. It survives a restart and a deploy. |
| `/data/2026/history/`, `/data/2026/week-NN/raw/` | The tracked data. The live path also writes week N-1 here. |
| `/data/2026/returns.json` | The hand-kept returns file. |
| `/data/cache/` | The players, the nflverse files, the charts, and the result cache in `results/`. |
| `/app/seed/data` | The tracked `data/` from the image. It is the seed of the volume. |

At start, `deploy/entrypoint.sh` does two things:

1. On the first boot, it copies `/app/seed/data` onto the volume. Then it writes the marker `/data/.seeded`.
   A new Fly volume holds `lost+found`, so the script checks the marker and not an empty volume.
2. On every boot, it copies each `returns.json` from the image onto the volume. The service never writes that
   file, so a commit and a deploy are the only way it changes.

Other tracked files arrive only on the first boot. The live path fetches a missing history week from Sleeper,
so a new saved week does not need a deploy.

The settings:

- `fly.toml` holds the settings that are not secret: `CORNERSTONE_REPO`, `CORNERSTONE_RESULT_CACHE_DIR`, and
  `CORNERSTONE_ALLOWED_ORIGINS`.
- Fly secrets hold `ANTHROPIC_API_KEY` and `CORNERSTONE_PASSPHRASE`. No secret is in the repo.
- The Sleeper league id is the constant `LEAGUE_ID` in `src/cornerstone/pipeline.py`. It is public, so it is
  not a secret.

The rate limit counts each client address. On Fly every request comes through the proxy, so the app reads the
address from the `Fly-Client-IP` header.

The analyze route also has a grade limit. Each client address gets 5 grades per minute and 20 per day.
The day is a calendar day in Eastern time. A cached repeat of the same trade makes no Claude call, so it does not
count. The daily counts live in `/data/cache/results/grade-counts.json` on the volume, so a deploy keeps them.
The file holds only today. To clear the counts, delete the file. Past a limit the route answers `429` with a
`Retry-After` to the end of the minute or to midnight Eastern. The values are `GRADES_PER_MINUTE` and
`GRADES_PER_DAY` in `src/cornerstone/tunables.py`.

## First deploy

Run each command from the repo root. Each step takes about one minute, except the deploy.

1. Check the login. Expect `bkwon94@gmail.com`. If it differs, run `fly auth login`.

   ```sh
   fly auth whoami
   ```

2. Create the app from the existing `fly.toml`. `--copy-config` keeps the file. `--no-deploy` stops before the
   deploy.

   ```sh
   fly launch --no-deploy --copy-config --name cpcfantasy-api --org personal --region ewr \
     --no-db --no-redis --no-object-storage --no-github-workflow
   ```

   If `fly launch` offers to change the settings, answer no. Then check that `git diff fly.toml` is empty.

3. Create the volume. Fly warns that one volume has no copy. Accept the warning: the volume holds caches and
   a seed that the image can give again.

   ```sh
   fly volumes create cornerstone_data --app cpcfantasy-api --region ewr --size 1
   ```

4. Set the secrets. Do not put the real values in a file or in the shell history.
   Type one space before `fly`, so the shell keeps the line out of history.
   The shell does this only when `HIST_IGNORE_SPACE` is set.
   `--stage` stores the secrets with no restart, and the next deploy gives them to the machine.

   ```sh
    fly secrets set --app cpcfantasy-api --stage ANTHROPIC_API_KEY=<the key> CORNERSTONE_PASSPHRASE=<the passphrase>
   ```

5. Deploy. The first build takes about 3 minutes.

   ```sh
   fly deploy
   ```

6. Add the certificate for the public hostname.

   ```sh
   fly certs add api.cpcfantasy.com --app cpcfantasy-api
   ```

7. Brian adds the DNS record that the command gives, at the DNS host of `cpcfantasy.com`. That is a `CNAME`
   from `api` to `cpcfantasy-api.fly.dev`, or the `A` and `AAAA` records.

   DNS host: ____

8. Wait until the certificate shows as issued. This can take about 10 minutes.

   ```sh
   fly certs show api.cpcfantasy.com --app cpcfantasy-api
   ```

9. Call the refresh route once, and wait for the answer. Then the timed trade in the next step does not pay
   for the first downloads. The first refresh on a new volume takes a few minutes.

   ```sh
   curl --fail -s --max-time 600 -X POST -H 'X-League-Passphrase: <the passphrase>' \
     'https://api.cpcfantasy.com/refresh?season=2026'
   ```

10. Do the three checks. Use the real passphrase in place of `<the passphrase>`.

    ```sh
    curl -s https://api.cpcfantasy.com/health
    curl -s -H 'X-League-Passphrase: <the passphrase>' 'https://api.cpcfantasy.com/teams?season=2026' | head -c 300
    curl -s -o /dev/null -w '%{http_code} %{time_total}s\n' -X POST \
      -H 'X-League-Passphrase: <the passphrase>' -H 'Content-Type: application/json' \
      -d '{"season": 2026, "sides": [{"roster_id": 4, "gives": ["<player id>"]}, {"roster_id": 12, "gives": ["<player id>"]}], "asker": 4}' \
      https://api.cpcfantasy.com/analyze
    ```

    - Health answers `{"status":"ok"}` with no passphrase.
    - Teams answers with the 12 teams.
    - Analyze answers `200` in under about 20 seconds. Take the player ids from the teams answer. Record the time
      in the comments of ticket 09.

    The first request after a stop starts the machine, so it is slower. The first request of a new chart week also
    reads the chart with Claude.

11. Set up the GitHub secret for the cron. See the last section.

## Rotate the passphrase

Change the passphrase in two places, or the cron fails with `401`.

1. Set the new Fly secret. Fly restarts the machine with the new value.

   ```sh
    fly secrets set --app cpcfantasy-api CORNERSTONE_PASSPHRASE=<the new passphrase>
   ```

2. Set the GitHub secret `CORNERSTONE_PASSPHRASE` to the same value. Use the steps in the last section.
3. Tell the managers the new passphrase. The site asks for it again after a `401`.

## Force a refresh

Use one of the two ways:

- Run the workflow "Daily refresh" from the Actions tab of the source repo, with "Run workflow".
- Call the route with curl:

  ```sh
  curl --fail -s -X POST -H 'X-League-Passphrase: <the passphrase>' \
    'https://api.cpcfantasy.com/refresh?season=2026'
  ```

The route fetches every nflverse file again, whatever its age. The cron can start late, so a file 23 hours old
must still refresh. The live path of a request fetches only a file older than a day.

The answer is `{"refreshed": [...], "stale": [...]}`:

- `refreshed` lists the nflverse sources that the run fetched again and the history weeks that it saved.
- `stale` lists each source that is still older than a day, `history` when the history fetch failed, and
  `chart` when the trade window week has no good chart or the chart read failed.

A failed fetch keeps the old cache in place. A stale source is not an error, so the route still answers `200`.

## Read the logs

```sh
fly logs --app cpcfantasy-api
```

Add `--no-tail` to get only the logs in the buffer. A failed fetch logs a warning with the source and the error.

## The prompt cache

Every Claude call with a system prompt marks that prompt as a cache prefix. The chart read has no system
prompt, so it has no cache. The prompt files hold no date, week, or trade fact, so the prefix is the same
bytes on every call of one kind.

| Call | Lifetime | Why |
| --- | --- | --- |
| Analyzer, in the API and in `cornerstone analyze` | 1 hour | Trade requests come minutes apart. |
| Writer and verifier, in the weekly build | 5 minutes, the default | The build runs its calls back to back. |

The prices for Opus 5.5 are multiples of the input price:

- A five-minute cache write costs 1.25x.
- A one-hour cache write costs 2x.
- A cache read costs 0.05x.

Each call logs one info line with the kind and the three usage counts:

```text
INFO cornerstone.writer: AnalysisOut call: cache_creation_input_tokens=0 cache_read_input_tokens=4935 input_tokens=1949
```

A repeat call inside the lifetime shows `cache_read_input_tokens` above zero. A zero there on a repeat means
a changed prefix, or a prefix under the minimum size of the model.

## Update the returns file

1. Edit `data/<season>/returns.json`.
2. Commit the change.
3. Run `fly deploy`. The entrypoint copies the returns file onto the volume at start.

## GitHub secret for the cron

The cron reads the passphrase from the repository secret `CORNERSTONE_PASSPHRASE`.

1. Run this command. It asks for the value, so the value stays out of the shell history.

   ```sh
   gh secret set CORNERSTONE_PASSPHRASE --repo bkwon94/cornerstone-fantasy-sleeper-weekly-report
   ```

2. Merge the branch into `main`. GitHub runs a schedule only from the default branch.
3. Run the workflow once by hand from the Actions tab. Check that it is green.

The season is the workflow variable `CORNERSTONE_SEASON`, with `2026` as the default in the file. At the start
of a new season, change the default in the file, or set the repository variable:

```sh
gh variable set CORNERSTONE_SEASON --body 2027 --repo bkwon94/cornerstone-fantasy-sleeper-weekly-report
```

In the off-season, the refresh route answers `422` and the daily job fails until the season variable changes.

The cron runs at 10:00 UTC. That is 06:00 Eastern in daylight time, and 05:00 Eastern in standard time.
