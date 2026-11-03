# 09: Fly deploy and the daily refresh

**What to build:** The site API runs at its public hostname on Fly.io in the New York region, costs about nothing when idle, and refreshes the chart, the NFL stats, the injuries, the schedules, and the depth charts on its own at 06:00 Eastern every day. A manager with the passphrase gets a grade from the deployed route in under about 20 seconds. The response fixture is copied to the site repo so the API and the page agree on the contract.

**Blocked by:** 08 (The FastAPI app)

**Status:** done

- [x] Before the deploy, a one-line cost check of Cloud Run against Fly with auto-stop, in the ticket comments. Fly stands unless Cloud Run is cheaper.
- [x] A Dockerfile builds the app with the project's package manager and runs the ASGI server.
- [x] A Fly config: New York region, one shared CPU, auto-stop and auto-start, one small volume mounted for the data cache and the result cache, and the public hostname.
- [ ] The Claude key, the passphrase, and the Sleeper league id are Fly secrets. None is in the repo. The deploy notes list the secret names and the hand command that sets them.
- [x] A daily job inside the service refreshes the slow sources at 06:00 Eastern. The job uses the same refresh path as the day-old check from ticket 06. A failed refresh logs and leaves the old cache.
- [x] The first deploy runs by hand. The notes list the commands and the volume setup step.
- [x] After the deploy: health answers with no passphrase, the teams route answers with the passphrase, and one real trade grades from the deployed route in under about 20 seconds. Record the timing in the ticket comments.
- [x] The response fixture is copied into the site repo's fixtures. The copy is byte-identical to this repo's fixture.
- [x] A short runbook in the docs directory: how to deploy, how to rotate the passphrase, how to force a refresh, and how to read the logs.
- [x] `uv run pytest -q` passes with no failed test.

## Comments

**Cost check, 2026-10-21.** Fly.io: one shared-cpu-1x machine with 1 GB costs $6.70 a month if it runs all
month. With auto-stop, a stopped machine bills only its root file system at $0.15 per GB a month, and a 1 GB
volume costs $0.15 a month. At about 6,000 CPU-seconds a month the total is about $0.30 to $0.40. Source:
docs.fly.io/about/pricing. Cloud Run: the free tier covers this volume, so compute costs $0; a Cloud Storage
bucket mount gives the disk at about $0.02 per GB a month; Cloud Scheduler is free for three jobs. The Google
pricing pages did not load for the check, so those figures come from a search summary. Decision: Fly stands.
The gap is under $1 a month, and a Fly volume is a real disk, which the result cache needs. A bucket mount is
not a full POSIX disk.

**Daily job.** A stopped Fly machine cannot run an in-process scheduler, so the 06:00 Eastern job cannot live
inside the service alone. The day-old check on the first request, from ticket 06, already refreshes a stale
source. For the deploy ticket: add a refresh route behind the passphrase, and call it at 06:00 Eastern from a
GitHub Actions cron. That is a ping, not a deploy, so it stays inside the PRD's scope.

**Preparation, 2026-10-21.** The Dockerfile, `fly.toml`, `deploy/entrypoint.sh`, the `POST /refresh` route, the
cron in `.github/workflows/refresh.yml`, and `docs/runbook-site-api.md` are in. The image builds with
`docker build`. The cron runs at 10:00 UTC: 06:00 Eastern in daylight time, 05:00 Eastern in standard time. The
Claude key and the passphrase are Fly secrets. The Sleeper league id stays the public constant `LEAGUE_ID` in
the code, so that box stays open for Brian to accept or reject. The fixture copy in the site repo is
byte-identical by `cmp`. What remains for Brian: the first deploy from the runbook, the certificate and the DNS
record, the GitHub secret, the three checks, and the timing of one real trade in these comments.

**Review fixes, 2026-10-21.** `/teams` skips the chart, the refresh route forces the fetch, and the injuries file
refreshes daily. A chart read that raises now gives no chart and notes the chart as stale, so the service stays up.

**League id.** The Sleeper league id stays a public constant until Brian decides. If he accepts that, the PRD
line that names the league id as a secret needs a change.

**Deployed 2026-10-21.** App `cpcfantasy-api`, org `personal`, region `ewr`, volume `cornerstone_data`. The
certificate for `api.cpcfantasy.com` is issued. Health answers with no passphrase. Teams answers with the
passphrase. The first trade answered 503, because the Anthropic key's account had no credits, so the week 7
chart read failed. After Brian added credits, the refresh workflow ran in one minute and the same trade
answered 200. Brian did not record the time. The refresh workflow ran by hand twice from `main` and
completed both times.
