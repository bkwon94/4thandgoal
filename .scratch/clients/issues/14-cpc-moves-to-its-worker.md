# 14: CPC moves to its Worker

Spec: `.scratch/clients/PRD.md`. Acceptance tests AT-3, AT-4, and AT-28.

**App:** both

**What to build:** CPC serves at `cpc.4thandgoal.app` from its own Cloudflare Worker. Old `cpcfantasy.com` links redirect there, and the API serves at `api.4thandgoal.app`.

**Blocked by:** 08, 10, 11, 12, 13

**Needs Brian:** manual steps 1, 2, 4, and 5 of the spec, and step 3 for `cpc.4thandgoal.app`. `cpc:implement` stops here and gives Brian the dashboard page, each value, and the check.

**Status:** ready-for-agent

- [x] One workflow deploys each client to its Worker with `wrangler-action` on each green push to `main`.
- [x] The GitHub Pages deploy goes away.
- [ ] The CPC week 8 page at `cpc.4thandgoal.app` matches the screenshots from before the move (AT-3).
- [ ] `cpcfantasy.com/2026/week-08/` answers a 301 to `cpc.4thandgoal.app/2026/week-08/` (AT-4).
- [ ] The default API URL is `https://api.4thandgoal.app`. `api.cpcfantasy.com/teams` still lists the CPC teams (AT-28).
