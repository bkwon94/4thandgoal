# 04: The What-if route on the API

Spec: `.scratch/season-sim/PRD.md`. Acceptance tests AT-14 to AT-21, AT-67, and AT-68. Decisions 01, 03, and 07.

**App:** api

**What to build:** Each client has one What-if route. It takes Your team and a list of set results, and it answers with `schema_version`, `season`, `week`, `runs`, `effective_runs`, `you`, `set`, `teams`, `sample`, and one `page` block. It runs on the inputs of the latest published `week-NN/sim.json`, so it never calls Sleeper. It needs no passphrase, and it has its own rate limit for each address, apart from the other routes. The route is a sync route. The sim stops the work of a call whose client went away. The API sends gzip, and its image holds the sim package. The machine stays `shared-cpu-1x` with 1 GB.

**Blocked by:** 03.

**Status:** ready-for-agent

- [ ] A post of Bo Girds and one set result with no passphrase answers 200 with each key of the spec (AT-14).
- [ ] A post with no set result answers the page of Bo Girds in `week-10/sim.json`, equal by a diff (AT-15).
- [ ] With each request to Sleeper blocked, the route still answers 200, and the log shows no Sleeper request (AT-16).
- [ ] A call past the limit gets 429 with a retry-after, and `/health` and the analyzer still answer for that address (AT-17).
- [ ] An answer with `Accept-Encoding: gzip` is gzip and under 60 KB (AT-18).
- [ ] A client that goes away after 100 ms stops the sim before 10,000 runs, as the log shows (AT-19).
- [ ] A set result for week 3 answers 422 with a message that names the week (AT-20).
- [ ] `fly.toml` keeps `shared-cpu-1x` with 1 GB (AT-21).
- [ ] No route reads or writes an Announcement (AT-67), and two equal posts run the sim twice (AT-68).
- [ ] The API image builds with the sim package.
- [ ] `make check-fast` passes.
