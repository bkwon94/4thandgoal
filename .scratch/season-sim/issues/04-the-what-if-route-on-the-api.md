# 04: The What-if route on the API

Spec: `.scratch/season-sim/PRD.md`. Acceptance tests AT-14 to AT-21, AT-67, and AT-68. Decisions 01, 03, and 07.

**App:** api

**What to build:** Each client has one What-if route. It takes Your team and a list of set results, and it answers with `schema_version`, `season`, `week`, `runs`, `effective_runs`, `you`, `set`, `teams`, `sample`, and one `page` block. It runs on the inputs of the latest published `week-NN/sim.json`, so it never calls Sleeper. It needs no passphrase, and it has its own rate limit for each address, apart from the other routes. The route is a sync route. The sim stops the work of a call whose client went away. The API sends gzip, and its image holds the sim package. The machine stays `shared-cpu-1x` with 1 GB.

**Blocked by:** 03.

**Status:** done

- [x] A post of Bo Girds and one set result with no passphrase answers 200 with each key of the spec (AT-14).
- [x] A post with no set result answers the page of Bo Girds in `week-10/sim.json`, equal by a diff (AT-15).
- [x] With each request to Sleeper blocked, the route still answers 200, and the log shows no Sleeper request (AT-16).
- [x] A call past the limit gets 429 with a retry-after, and `/health` and the analyzer still answer for that address (AT-17).
- [x] An answer with `Accept-Encoding: gzip` is gzip and under 60 KB (AT-18).
- [x] A client that goes away after 100 ms stops the sim before 10,000 runs, as the log shows (AT-19).
- [x] A set result for week 3 answers 422 with a message that names the week (AT-20).
- [x] `fly.toml` keeps `shared-cpu-1x` with 1 GB (AT-21).
- [x] No route reads or writes an Announcement (AT-67), and two equal posts run the sim twice (AT-68).
- [x] The API image builds with the sim package.
- [x] `make check-fast` passes.

## Comments

- 2026-11-18: The box "The API image builds with the sim package" stays open. The Docker daemon on the Mac hangs. Run `make image` in `apps/api` after a restart of Docker Desktop.
- 2026-11-18: `make image` built `cpcfantasy-api` (sha256:292cc15d) from the Spec branch at 3a40a99d. In the image, `/opt/venv/bin/python` imports `sim.season`, `sim.page`, `cornerstone_api.what_if`, and `cornerstone_api.app`.

Closes with the squash merge of the spec PR: `season-sim-04` (`bd4f5164`) merged into `season-sim` as a fast-forward on 2026-11-18.
AT-14 to AT-21, AT-67, and AT-68 have PASS in `.scratch/season-sim/VERDICTS.md`.
The builder did not count the files it read; the ticket commits changed 14 files, and the main ones are: apps/api/Dockerfile, apps/api/Dockerfile.dockerignore, apps/api/pyproject.toml, apps/api/src/cornerstone_api/app.py, apps/api/src/cornerstone_api/what_if.py, packages/sim/python/src/sim/season.py, packages/sim/python/src/sim/tunables.py, apps/api/src/cornerstone_api/README.md.
