# 09: The spec

Map: `.scratch/clients/MAP.md`.

**Kind:** spec

**Blocked by:** 01, 02, 03, 04, 05, 06, 07, 08

**Status:** open

## Question

The spec records the choices of tickets 01 to 08 and the map. It needs no session of its own. Run `cpc:to-spec clients` when each other ticket is done.

Brian does the manual steps of the spec himself, on 2026-11-04 terms: "When the time comes, let me know what I need to do specifically." So the spec lists each manual step, and the ticket that needs it names the step as a blocker. When `cpc:implement` reaches that ticket, it stops and gives Brian the exact steps: the dashboard page, each value to enter, and the check that shows the step worked. The known steps are the `4thandgoal.app` zone on Cloudflare, the Cloudflare API token and the GitHub secrets for `wrangler-action`, the Custom Domain of each Worker, the Redirect Rule on `cpcfantasy.com`, and `fly certs add api.4thandgoal.app` with its DNS record.

## Decision

None yet.
