# 13: The analyzer package and the API per client

Spec: `.scratch/clients/PRD.md`. Acceptance tests AT-27, AT-29, AT-30, and AT-34.

**App:** both

**What to build:** The trade analyzer and the finder move into the `analyzer` package, with their prompts and their API routes. The API serves each client with the client in the path.

**Blocked by:** 06, 07

**Status:** ready-for-agent

- [x] The `analyzer` package holds the modules of decision 01, its prompts, and its API routes.
- [x] The API answers `/clients/<slug>/teams`, `/analyze`, `/find`, and `/refresh` for each client. `/clients/cpc/teams` lists the CPC teams (AT-27).
- [x] The old paths with no client answer as `cpc`.
- [x] The grade limit counts per client and per address (AT-29). The name of the request address no longer uses the word client.
- [x] A bad `client.toml` stops the API at start with the file and the key (AT-30).
- [ ] Each client has its own passphrase in `CORNERSTONE_PASSPHRASE_<SLUG>`. A wrong passphrase gets 401, and a missing one stops the API at start (AT-34).
- [x] `finder` is a package value of `analyzer`, and the site calls the API with the client in the path.
- [x] The CPC golden diff is empty (AT-1).
