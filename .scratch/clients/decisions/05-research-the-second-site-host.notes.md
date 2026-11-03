# 05 notes: the host and the URL of the second site

Research for `05-research-the-second-site-host.md`. Read on 2026-11-03. Brian makes the decision.

## The current deploy

- `.github/workflows/deploy.yml` builds and deploys the site. It runs on a push to `main` that changes `apps/site/**`, and on a manual dispatch.
- The build job runs `pnpm check` in `apps/site`, then `actions/configure-pages@v5` and `actions/upload-pages-artifact@v3` with the path `apps/site/out`.
- The deploy job runs `actions/deploy-pages@v4` with `pages: write` and `id-token: write`, in the `github-pages` environment.
- `apps/site/next.config.ts` sets `output: "export"`, `trailingSlash: true`, and `basePath`.
- `apps/site/src/lib/config.ts` reads `basePath` from `NEXT_PUBLIC_BASE_PATH`. The default is empty, because the site is at the domain root.
- `apps/site/public/CNAME` holds `cpcfantasy.com`. A site from a custom workflow ignores this file. The domain comes from the Pages settings of the repo. Source: https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site
- The repo is `bkwon94/cpcfantasyfootball` (`git remote -v`).
- DNS: `dig` shows that `cpcfantasy.com` uses the Cloudflare nameservers `fish` and `rohin`. Its apex A records are the four GitHub Pages IPs, `185.199.108.153` to `185.199.111.153`. So the domain is already a Cloudflare zone.
- The API is a separate Fly app, `cpcfantasy-api` in `apps/pipeline/fly.toml`. `.github/workflows/deploy-api.yml` runs `superfly/flyctl-actions/setup-flyctl@v1` and `flyctl deploy --remote-only`.

## The hard limit on GitHub Pages

- A repo has a maximum of one Pages site. Source: https://docs.github.com/en/pages/getting-started-with-github-pages/about-github-pages
- `actions/deploy-pages` has no input for a target repo. It deploys an artifact to the Pages site of the repo that runs the workflow. Source: https://github.com/actions/deploy-pages
- So this repo cannot serve a second site on GitHub Pages. A second GitHub Pages site needs a second repo.

## Option A: a second Cloudflare Pages project

1. Cost: free. "On both free and paid plans, requests to static assets are free and unlimited." Source: https://developers.cloudflare.com/pages/functions/pricing/
2. Deploy step: a direct upload from GitHub Actions with `cloudflare/wrangler-action@v4`. The command is `pages deploy apps/site/out --project-name=<project>`. Source: https://developers.cloudflare.com/pages/how-to/use-direct-upload-with-continuous-integration/
   - Secrets: `CLOUDFLARE_API_TOKEN`, a custom token with "Account, Cloudflare Pages, Edit". Also `CLOUDFLARE_ACCOUNT_ID`.
   - The job grants `contents: read` and `deployments: write`.
   - A matrix over the client slugs can build and deploy each client in one workflow, one project per client.
3. Default URL: `<project>.pages.dev`. You choose the name when you create the project. Source: https://developers.cloudflare.com/pages/configuration/custom-domains/
   - Custom domain: a subdomain needs only a CNAME to `<project>.pages.dev`. If the zone is on Cloudflare, Cloudflare adds the CNAME for you. Add the domain in the Pages dashboard first, or a 522 error can occur.
   - An apex domain must be a Cloudflare zone on the same account. Same source.
   - `cpcfantasy.com` is already a Cloudflare zone, so `<slug>.cpcfantasy.com` is a one-step setup.
4. Limits on the Free plan: 100 projects per account, 20,000 files per site, 25 MiB per file, 500 builds per month, 100 custom domains per project. Source: https://developers.cloudflare.com/pages/platform/limits/
   - Check the file count. Each week adds files, and the limit is per site, not per repo.
   - A direct upload from Actions does not use the Cloudflare build system. The docs do not say if the 500-build limit counts direct uploads.

## Option B: a second GitHub repo for Pages

1. Cost: free for a public repo. On GitHub Free, the repo must be public. Source: https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site
2. Deploy step: `actions/deploy-pages` cannot deploy from this repo to the second repo (see the hard limit above). Two paths exist:
   - The second repo has its own workflow. It checks out this repo, builds with the client name, and deploys with `actions/deploy-pages@v4`. The trigger then lives in the second repo, not in this one.
   - This repo builds, then pushes `out/` to a branch of the second repo. That needs a deploy key or a token with write access. The second repo publishes from that branch. Source for branch publish: https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site
3. Default URL: `https://bkwon94.github.io/<repo>`. Source: https://docs.github.com/en/pages/getting-started-with-github-pages/about-github-pages
   - That URL has a path, so the build must set `NEXT_PUBLIC_BASE_PATH=/<repo>`. A custom domain removes the path.
   - Custom domain: a subdomain needs a CNAME to `bkwon94.github.io`. The domain is set in the Pages settings of the second repo. Source: https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site
4. Limits: 1 GB per site, a soft limit of 100 GB of bandwidth per month, and a timeout of 10 minutes per deploy. Pages is "not intended for or allowed to be used as a free web-hosting service to run your online business". Source: https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits
   - Each new client needs one more repo and one more token. Ten clients mean ten repos.

## Option C: a static deploy on Fly

1. Cost: not free. "New organizations don't have a free tier or a monthly free usage allowance." Source: https://docs.fly.io/about/pricing
   - The smallest Machine, `shared-cpu-1x` with 256 MB, costs $2.19 per month if it runs all the time.
   - A stopped Machine costs $0.15 per GB per month of rootfs. Outbound bandwidth in North America costs $0.02 per GB.
   - A shared IPv4 is free. The first 10 certificates per org are free, then $0.10 per month each.
   - Brian already pays for the org of `cpcfantasy-api`, so the extra cost is small but not zero.
2. Deploy step: a Dockerfile `FROM nginx:alpine` that copies the export into `/usr/share/nginx/html`. Set `internal_port = 80` in `fly.toml`. Run `flyctl deploy`. Source: https://docs.fly.io/languages-and-frameworks/static
   - In this repo, the step matches `deploy-api.yml`: `superfly/flyctl-actions/setup-flyctl@v1`, then `flyctl deploy --remote-only`, with one `fly.toml` per client site.
   - The example sets `auto_stop_machines = 'stop'` and `min_machines_running = 0`. An idle site stops, and the first visit then waits for a cold start. Same source.
3. Default URL: `<app>.fly.dev`. Same source.
   - Custom domain: run `fly certs add <domain>`, then add a CNAME from the subdomain to the app's `.fly.dev` target. An apex domain needs A and AAAA records. Source: https://docs.fly.io/networking/custom-domain/
4. Limits: a server to run and patch, with an nginx image per client. The other two options have no server.

## Other options checked

- Cloudflare Workers static assets: "Like Pages, requests for static assets on Workers are free." The docs do not mark Pages as deprecated. Workers has more features, but a static export does not need them. No clear advantage, so it is not a full option here. Source: https://developers.cloudflare.com/workers/static-assets/migration-guides/migrate-from-pages/

## Summary

| | A: Cloudflare Pages | B: second GitHub repo | C: Fly static |
| --- | --- | --- | --- |
| Cost | Free | Free (public repo) | About $0 to $2.19 per month, plus bandwidth |
| Deploy from this repo | `wrangler-action`, one project per client | Not direct; a second repo with a token or its own workflow | `flyctl deploy`, one app per client |
| Default URL | `<project>.pages.dev` | `bkwon94.github.io/<repo>` (needs a base path) | `<app>.fly.dev` |
| Custom subdomain | CNAME, auto on the Cloudflare zone | CNAME to `bkwon94.github.io` | `fly certs add`, then CNAME |
| Main limit | 20,000 files per site | 1 repo per client | Paid, cold start, a server |

## Recommendation

Choose Option A: a second Cloudflare Pages project, at `<slug>.cpcfantasy.com`, with `<project>.pages.dev` as the default URL.

- It is free, and static requests have no limit.
- The deploy stays in this repo. One `wrangler-action` step per client fits the plan of one build per client name.
- `cpcfantasy.com` is already a Cloudflare zone, so the subdomain needs no DNS work by hand.
- It needs no extra repo and no server, so client three costs one more project, not one more repo or app.
- Open question for Brian: does CPC stay on GitHub Pages, or move to Cloudflare Pages too? One host for each client keeps one deploy path.
- Check before the spec: the file count of a full season against the 20,000-file limit. `apps/site/public/` holds 130 files today, so the risk is low. The worktree has no `out/` to count.
