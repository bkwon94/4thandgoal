# 01: The route of a site question

Spec: `.scratch/site-answer/PRD.md`. Acceptance tests AT-9, AT-18, AT-20, AT-22.

**App:** api

**What to build:** The ask route takes the pages of the client from the site and routes a question about the site to the new route kind `site`, with the page it asks about. The request takes a `pages` field, and the Jev state gets `site_pages`. The one Jev request adds the Noul `n5` and the Choice `c1` of decision 01, with the options `all` and `missing` of the spec. A clear yes on the Noul routes to `site` right after the abuse row, and an unsure or a no falls through to the old table. The response holds `page`. A `site` route makes no Claude call, writes no entry in the miss log, and touches no cap. The live route eval holds the 40 questions of decision 01.

**Blocked by:** none.

**Status:** ready-for-agent

- [x] The live route eval routes at least 20 of the 22 site questions to `site` with the right key, keeps each of the 18 traps, and keeps the old bar (AT-9).
- [x] With the fake Jev, a `site` route returns `page`, makes no Claude call, writes no miss log entry, and leaves each cap count as it was (AT-18).
- [x] An unknown page key, or more than 12 pages, gets a 422 before any Jev request (AT-20).
- [x] "what's the weather" still routes to an honest miss (AT-22, api half).
- [x] An ask request with no `pages` field still routes as before, so the site of `main` keeps working until ticket 02.
