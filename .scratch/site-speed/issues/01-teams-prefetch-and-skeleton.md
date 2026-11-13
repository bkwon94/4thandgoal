# 01: The analyzer form fills at once

**What to build:** When a passphrase is stored, the home page fetches the teams in the background and keeps them in session storage. The analyzer reads session storage first, then fetches. The "Loading teams" line becomes skeleton rows in the two picker shapes, tokens only, with any pulse under `useMotionOff`.

**Why:** The commissioner sees "Loading teams" for many seconds on an almost blank page. The API side, ticket 19 in the pipeline repo, makes the route itself fast. This ticket hides the rest.

**Blocked by:** None. The API cache lands on its own.

**Status:** done

- [x] `src/app/page.tsx`: when `cpc.passphrase` is in local storage, fetch the teams for the current season and store the JSON in session storage under one key with the season and the time.
- [x] `src/components/analyzer.tsx`: read that key first. Use it if it is under 5 minutes old, then fetch in the background and replace it. With no key, fetch as today.
- [x] Skeleton rows for both picker shapes, with the tokens from `src/lib/utils.ts`. Teach the `cn` helper every new token name. The skeleton uses only existing token names, so `cn` needs no new entry.
- [x] A 429 with `Retry-After` over an hour reads "Try again in N hours." in `src/lib/api.ts`.
- [x] Tests read the screen: the skeleton shows before the teams, the stored teams show at once, the hours text.
- [x] Check at 390 wide with `agent-browser`, with and without `reduced-motion`.
- [ ] `pnpm test` passes with no failed test. Push to main deploys. The tests pass on branch `teams-prefetch`; the push to main is still open.

## Comments

Closes as done in the audit of `todoist-queue` on 2026-11-12. The work merged in 590268f8.
Proof: The commit merged in 84d3fabb on `main`, and `packages/analyzer/site/lib/teams-store.ts` and `waitText` in `api.ts` hold the behavior now.
Read 1 file: .scratch/todoist-queue/audit.md.
