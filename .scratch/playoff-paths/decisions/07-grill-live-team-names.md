# 07: How does The Race show live team names?

Map: `.scratch/playoff-paths/MAP.md`.

**Kind:** grill

**Blocked by:** none

**Status:** done

## Question

The weekly build fetches `users.json` on Tuesday, so a team renamed after the fetch shows its old name for up to a week. Brian wants live names as part of this spec. Decide the source and the scope:

- The source: the browser reads the public Sleeper users endpoint, the API serves the names, or the build fetches them again at publish. A fact from 2026-11-24: `GET https://api.sleeper.app/v1/league/<id>/users` answers with `access-control-allow-origin: *` and a CDN cache of 300 s, so a browser can read it.
- The fallback: the published name shows first, and when the live call fails.
- The scope: The Race only, or every page with a team name.
- The avatar: if it changes too.

## Decision

Brian decided on 2026-11-24, in 4 questions.

1. **Scope:** every page with a team name gets live names: the week page, rankings, managers, the front door, the analyzer, and The Race. One shared part swaps the names after the page loads. The midseason report keeps its published names, because it is a record of one week.
2. **Source:** the browser reads 2 public Sleeper calls, `GET /v1/league/<id>/rosters` for `roster_id` to `owner_id`, and `GET /v1/league/<id>/users` for `metadata.team_name` and the avatar. Both answer with `access-control-allow-origin: *`. The API does not change.
3. **Text:** live names fill the name slots: rows, cards, and headers. The page also swaps the full old name for the live one in the text of the build, such as blurbs, facts, and front door Answers. The swap happens only for a team that the live call shows as renamed, and only on the full old name.
4. **Timing and fallback:** the page shows the published name first, then swaps each renamed team in place with no animation. The browser keeps the live names for 5 minutes in `sessionStorage`, the time of Sleeper's CDN cache. On a failed call or a wait over 3 seconds, the page keeps the published names and shows no error. Tests stub `fetch` for both calls.
5. **Avatar:** when the live `avatar_url` differs from the published one, the page loads the new image from Sleeper's CDN. It keeps the local image until the new one loads.

The case that found the gap: cpc roster 5 shows "Puka Deez..." in the week 11 build, and Sleeper says "Teez Nuts".
