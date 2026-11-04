# 05: The host and the URL of the second site

Map: `.scratch/clients/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** done

## Question

Where is the second site hosted, and at what URL? The GitHub Pages of this repo serves one site, cpcfantasy.com. Each client builds its own site, so a second client needs a second host. Compare a second Cloudflare Pages project, a second GitHub repo for Pages, and a static deploy on Fly. Name the cost, the deploy step from CI, and the custom domain for each.

## Decision

Brian decided each item on 2026-11-03, from the notes in `05-research-the-second-site-host.notes.md`.

1. **The host is Cloudflare Workers with static assets.** Each client is one Worker, and the Worker name is the client slug. One repo deploys each Worker with `cloudflare/wrangler-action` and one API token. The cost is $0, and requests to static assets have no limit. A GitHub repo serves one Pages site only, and Fly has no free tier.
2. **NorCal uses the free URL for now.** The Worker `norcal` serves at `norcal.<account>.workers.dev`. The domain is a setting of the Worker, not code, so the build takes the client slug only.
3. **CPC stays on GitHub Pages at `cpcfantasy.com` in this spec.** `cpcfantasy.com` belongs to CPC alone, so no other client gets a subdomain of it.
4. **The end state is `<client>.<brand>.app`.** A later step buys one brand domain on Cloudflare and moves both clients there, CPC too. Brian has not chosen the brand name yet.

## Comments

- 2026-11-04: Brian chose the brand 4th and Goal and owns `4thandgoal.app`. The end state is `<client>.4thandgoal.app`. The move stays out of scope for this spec.
