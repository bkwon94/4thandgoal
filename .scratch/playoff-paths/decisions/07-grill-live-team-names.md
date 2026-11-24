# 07: How does The Race show live team names?

Map: `.scratch/playoff-paths/MAP.md`.

**Kind:** grill

**Blocked by:** none

**Status:** open

## Question

The weekly build fetches `users.json` on Tuesday, so a team renamed after the fetch shows its old name for up to a week. Brian wants live names as part of this spec. Decide the source and the scope:

- The source: the browser reads the public Sleeper users endpoint, the API serves the names, or the build fetches them again at publish. A fact from 2026-11-24: `GET https://api.sleeper.app/v1/league/<id>/users` answers with `access-control-allow-origin: *` and a CDN cache of 300 s, so a browser can read it.
- The fallback: the published name shows first, and when the live call fails.
- The scope: The Race only, or every page with a team name.
- The avatar: if it changes too.

## Decision

None yet.
