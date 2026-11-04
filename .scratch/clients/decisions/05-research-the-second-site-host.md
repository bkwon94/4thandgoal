# 05: The host and the URL of the second site

Map: `.scratch/clients/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** done

## Question

Where is the second site hosted, and at what URL? The GitHub Pages of this repo serves one site, cpcfantasy.com. Each client builds its own site, so a second client needs a second host. Compare a second Cloudflare Pages project, a second GitHub repo for Pages, and a static deploy on Fly. Name the cost, the deploy step from CI, and the custom domain for each.

## Decision

Brian decided items 1 to 3 on 2026-11-03, from the notes in `05-research-the-second-site-host.notes.md`. Brian changed items 2 to 4 on 2026-11-04, after he bought `4thandgoal.app`.

1. **The host is Cloudflare Workers with static assets.** Each client is one Worker, and the Worker name is the client slug. One repo deploys each Worker with `cloudflare/wrangler-action` and one API token. The cost is $0, and requests to static assets have no limit. A GitHub repo serves one Pages site only, and Fly has no free tier.
2. **Each client serves at `<client>.4thandgoal.app`, at the root.** The subdomain is the client slug: `cpc.4thandgoal.app` and `norcal.4thandgoal.app`. The site has no base path. Each Worker takes its subdomain as a Custom Domain on the `4thandgoal.app` zone.
3. **CPC moves from GitHub Pages to its own Worker in this spec.** Each client then deploys the same way, and the GitHub Pages deploy goes away. One Cloudflare Redirect Rule sends `cpcfantasy.com/<path>` to `cpc.4thandgoal.app/<path>` with a 301, so old links keep working.
4. **The API serves at `api.4thandgoal.app`.** The Fly app takes a second cert with `fly certs add`. `api.cpcfantasy.com` keeps its cert, so an old page that calls it still works. The default of `NEXT_PUBLIC_API_URL` changes to the new URL.
5. **The CPC site name stays "Cornerstone Fantasy Football League".** It goes into `clients/cpc/copy.toml`, as the page titles and the masthead show it today.
6. **The bare `4thandgoal.app` is a later landing page.** It is a marketing page for sign-ups, and it is out of scope for this spec.

## Comments

- 2026-11-04: Brian chose the brand 4th and Goal and owns `4thandgoal.app`. The end state is `<client>.4thandgoal.app`. The move stays out of scope for this spec.
- 2026-11-04: Brian moved both clients to `4thandgoal.app` in this spec, with a redirect from `cpcfantasy.com` and the API at `api.4thandgoal.app`. He chose no `/fantasy` base path, because each league on the service is a fantasy league. Items 2 to 6 above record it.
