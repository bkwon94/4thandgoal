# 09: Fly deploy and the daily refresh

**What to build:** The site API runs at its public hostname on Fly.io in the New York region, costs about nothing when idle, and refreshes the chart, the NFL stats, the injuries, the schedules, and the depth charts on its own at 06:00 Eastern every day. A manager with the passphrase gets a grade from the deployed route in under about 20 seconds. The response fixture is copied to the site repo so the API and the page agree on the contract.

**Blocked by:** 08 (The FastAPI app)

**Status:** ready-for-agent

- [ ] Before the deploy, a one-line cost check of Cloud Run against Fly with auto-stop, in the ticket comments. Fly stands unless Cloud Run is cheaper.
- [ ] A Dockerfile builds the app with the project's package manager and runs the ASGI server.
- [ ] A Fly config: New York region, one shared CPU, auto-stop and auto-start, one small volume mounted for the data cache and the result cache, and the public hostname.
- [ ] The Claude key, the passphrase, and the Sleeper league id are Fly secrets. None is in the repo. The deploy notes list the secret names and the hand command that sets them.
- [ ] A daily job inside the service refreshes the slow sources at 06:00 Eastern. The job uses the same refresh path as the day-old check from ticket 06. A failed refresh logs and leaves the old cache.
- [ ] The first deploy runs by hand. The notes list the commands and the volume setup step.
- [ ] After the deploy: health answers with no passphrase, the teams route answers with the passphrase, and one real trade grades from the deployed route in under about 20 seconds. Record the timing in the ticket comments.
- [ ] The response fixture is copied into the site repo's fixtures. The copy is byte-identical to this repo's fixture.
- [ ] A short runbook in the docs directory: how to deploy, how to rotate the passphrase, how to force a refresh, and how to read the logs.
- [ ] `uv run pytest -q` passes with no failed test.
