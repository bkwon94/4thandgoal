# 05 notes: the host and the URL of the second site
Ticket: .scratch/clients/decisions/05-research-the-second-site-host.md

Research date: 2026-11-03. Each claim cites its primary source. A claim marked **Local check** comes from a command in this repo, not from a doc.

## Two local facts that change the answer

1. **Local check:** `dig +short NS cpcfantasy.com` returns `rohin.ns.cloudflare.com` and `fish.ns.cloudflare.com`. The DNS of `cpcfantasy.com` is already a Cloudflare zone. The apex A records point to the GitHub Pages IPs `185.199.108-111.153`.
2. **Local check:** `apps/site/public/` holds 130 files and 3.7 MB. The site is far below every file limit below.
3. A Pages site from a custom workflow ignores `apps/site/public/CNAME`. The domain of CPC comes from the Pages settings of the repo. Source: https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site

Fact 1 matters for Cloudflare Workers. A Workers Custom Domain needs an active Cloudflare zone, and this zone exists. A subdomain such as `norcal.cpcfantasy.com` can point to any of the three hosts, while the apex stays on GitHub Pages.

## 1. Cloudflare: a Pages project, or a Worker with static assets

### Which product

The Pages docs carry a banner that advises against Pages for new projects: "Workers supports most Pages use cases and offers a broader feature set." Source: https://developers.cloudflare.com/pages/

Both products serve a folder of prebuilt files. The notes below cover both.

### Cost and free-tier limits

Pages, Free plan:

- 500 builds a month, and one build at a time for each account. Source: https://developers.cloudflare.com/pages/platform/limits/
- 20,000 files for each site, and 25 MiB for each file. Source: https://developers.cloudflare.com/pages/platform/limits/
- 100 projects for each account, and 100 custom domains for each project. Source: https://developers.cloudflare.com/pages/platform/limits/
- "On both free and paid plans, requests to static assets are free and unlimited." Source: https://developers.cloudflare.com/pages/functions/pricing/
- The limits page states no bandwidth cap. Source: https://developers.cloudflare.com/pages/platform/limits/

Workers with static assets, Free plan:

- "Requests to static assets are free and unlimited." Source: https://developers.cloudflare.com/workers/static-assets/billing-and-limitations/
- 20,000 files for each Worker version on Free, 100,000 on Paid, and 25 MiB for each file. Source: https://developers.cloudflare.com/workers/platform/limits/
- 100 Workers for each account. The 100,000 requests a day limit applies to requests that run Worker code. Source: https://developers.cloudflare.com/workers/platform/limits/

Cost for one small static site: $0 on either product.

### Deploy step from GitHub Actions

- The official action is `cloudflare/wrangler-action@v4`. It takes the inputs `apiToken` and `accountId` from secrets. Source: https://github.com/cloudflare/wrangler-action
- For Pages, the command is `pages deploy <dir> --project-name=<name>`. The job also sets `deployments: write` if `gitHubToken` is given. Source: https://github.com/cloudflare/wrangler-action
- The secrets are `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID`. Source: https://developers.cloudflare.com/workers/ci-cd/external-cicd/github-actions/
- The Pages token needs Account > Cloudflare Pages > Edit. Source: https://developers.cloudflare.com/pages/how-to/use-direct-upload-with-continuous-integration/
- The Workers token uses the "Edit Cloudflare Workers" template. Source: https://developers.cloudflare.com/workers/ci-cd/external-cicd/github-actions/
- Create a Pages project for CI with `wrangler pages project create`. "If you choose Direct Upload, you cannot switch to Git integration later." Source: https://developers.cloudflare.com/pages/get-started/direct-upload/
- On Workers, the default `assets.html_handling` is `auto-trailing-slash`. It serves `foo/index.html` at `foo/`, which fits `trailingSlash: true`. Source: https://developers.cloudflare.com/workers/static-assets/routing/advanced/html-handling/

### Custom domain and free URL

- Pages gives a free `<project>.pages.dev` URL. Source: https://developers.cloudflare.com/pages/configuration/custom-domains/
- For a Pages subdomain, add the domain in the dashboard first. Then add a CNAME to `<project>.pages.dev`. A CNAME added before the dashboard step fails with a 522 error. The subdomain does not need to be a Cloudflare zone. Source: https://developers.cloudflare.com/pages/configuration/custom-domains/
- Workers gives a free `<worker>.<account-subdomain>.workers.dev` URL. Source: https://developers.cloudflare.com/workers/configuration/routing/workers-dev/
- A Workers Custom Domain needs "An active Cloudflare zone" that you own. It cannot go on a hostname with an existing CNAME record. Source: https://developers.cloudflare.com/workers/configuration/routing/custom-domains/
- `cpcfantasy.com` is already a Cloudflare zone, so `norcal.cpcfantasy.com` works on both products. See the local check above.

### Can one repo deploy two sites

Yes. Each deploy names its target: `--project-name` for Pages, or the Worker name in its config. One token for each account deploys every project in the account. Ten clients need ten projects, inside the 100 limit. Sources: https://github.com/cloudflare/wrangler-action and https://developers.cloudflare.com/pages/platform/limits/

## 2. A second GitHub repo that serves GitHub Pages

### Cost and free-tier limits

- GitHub Free gives "GitHub Pages in public repositories". Source: https://docs.github.com/en/get-started/learning-about-github/githubs-plans
- "GitHub Actions usage is free for standard GitHub-hosted runners in public repositories". Source: https://docs.github.com/en/get-started/learning-about-github/githubs-plans
- A published site is 1 GB or less. The soft bandwidth limit is 100 GB a month. A deploy times out after 10 minutes. The soft limit of 10 builds an hour does not apply to a custom Actions workflow. Source: https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits

Cost: $0.

### One site for each repo

The docs state: "Maximum of one pages site per repository." The default URL of a project site is `<owner>.github.io/<repositoryname>`. Source: https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages

### Deploy step from GitHub Actions

- The official actions are `actions/upload-pages-artifact` and `actions/deploy-pages`. The deploy job needs `pages: write` and `id-token: write`. The `token` input defaults to `github.token`. Source: https://github.com/actions/deploy-pages
- The README of `deploy-pages` says nothing about a deploy to another repo. Source: https://github.com/actions/deploy-pages
- The REST call under `deploy-pages` takes an artifact and an `oidc_token` "issued by GitHub Actions certifying the origin of the deployment". The artifact belongs to the target repository. Source: https://docs.github.com/en/rest/pages/pages#create-a-github-pages-deployment
- So repo A cannot use `deploy-pages` to deploy to the Pages of repo B. This is an inference from the REST doc, not a direct GitHub statement.
- The other publishing source is "publish from a branch". Source: https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site
- A cross-repo deploy therefore means a push of `out/` to a branch of repo B. That push needs a token with write access to repo B, such as a fine-grained PAT with Contents: write on repo B, stored as a secret in repo A. No first-party action does this push. **Inference**, from the two sources above.

### Custom domain and free URL

- Free URL: `<owner>.github.io/<repo>`. With `basePath` from config, the build must set the base path to `/<repo>` for this URL. Source: https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages
- For a subdomain, set the domain in Settings > Pages. Then add a CNAME to `<owner>.github.io`, without the repo name. Source: https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site
- With a custom Actions workflow, "no CNAME file is created, and any existing CNAME file is ignored and is not required." Source: https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site
- A repo-level domain overrides the account default. So repo B can serve `norcal.cpcfantasy.com`, while this repo keeps the apex. Source: https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/about-custom-domains-and-github-pages

### Can one repo deploy two sites

Not with the first-party Pages actions. This repo serves one site, and each new client needs a new repo, a new PAT secret, and a push step. Ten clients mean ten repos and ten tokens to rotate.

## 3. A static deploy on Fly.io

### Cost and free-tier limits

- No free tier. A new org gets a trial of 2 hours of Machine runtime or 7 days. Source: https://docs.fly.io/about/pricing
- The smallest `shared-cpu-1x` 256 MB Machine is $2.19 a month at full runtime. Source: https://docs.fly.io/about/pricing
- Outbound data costs $0.02 a GB in North America and Europe, with no free allowance. Source: https://docs.fly.io/about/pricing
- A stopped Machine costs $0.15 a GB a month of rootfs. Source: https://docs.fly.io/about/pricing
- Shared IPv4 and IPv6 are free. A dedicated IPv4 is $2 a month. Source: https://docs.fly.io/about/pricing
- The first 10 single-hostname certificates of each org are free. Then each costs $0.10 a month. Source: https://docs.fly.io/about/pricing
- `auto_stop_machines` (default `"off"`) can stop an idle Machine, and `auto_start_machines` (default `true`) starts it on a request. Source: https://docs.fly.io/reference/configuration
- `[[statics]]` serves files from a `guest_path` in the image, with up to 10 mappings for each app. Source: https://docs.fly.io/reference/configuration
- There is no file count limit like Cloudflare's. The site is files inside an image, such as nginx or Caddy.

Cost: about $0 to $2.19 a month for each site, plus bandwidth. An eleventh certificate adds $0.10 a month.

### Deploy step from GitHub Actions

- The action is `superfly/flyctl-actions/setup-flyctl@master`. The command is `flyctl deploy --remote-only`. The secret is `FLY_API_TOKEN`. Source: https://docs.fly.io/launch/continuous-deployment-with-github-actions
- `fly tokens create deploy` makes a token for one app. `fly tokens create org` makes a token for every app in the org. Source: https://docs.fly.io/launch/continuous-deployment-with-github-actions
- The API already uses this flow. A site app needs its own `fly.toml` and a Dockerfile, such as nginx with `out/` copied in.

### Custom domain and free URL

- Free URL: `<app>.fly.dev`. Source: https://docs.fly.io/networking/custom-domain
- Run `fly certs add norcal.cpcfantasy.com`. Then add the CNAME that Fly shows. Source: https://docs.fly.io/networking/custom-domain
- A certificate needs one more proof: an AAAA record, a `_acme-challenge` CNAME, or a `_fly-ownership` TXT record. Source: https://docs.fly.io/networking/custom-domain

### Can one repo deploy two sites

Yes. Each app has its own name and `fly.toml`, and `flyctl deploy` takes a config path. One org token deploys all apps. Ten clients mean ten apps and ten Machines. Source: https://docs.fly.io/launch/continuous-deployment-with-github-actions

## Comparison

| Point | Cloudflare Workers or Pages | Second GitHub repo, Pages | Fly.io static app |
| --- | --- | --- | --- |
| Cost for one small site | $0 | $0 | $0 to $2.19 a month, plus $0.02 a GB out |
| Free-tier limits | 20,000 files, 25 MiB a file, static requests unlimited; Pages 500 builds a month | 1 GB a site, 100 GB a month soft, 10 min deploy | No free tier |
| Deploy action | `cloudflare/wrangler-action@v4` | `actions/deploy-pages@v4` only in its own repo; cross-repo needs a branch push | `superfly/flyctl-actions/setup-flyctl` |
| Secrets | `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID` | A PAT with write access to each target repo | `FLY_API_TOKEN`, which exists today |
| Free URL | `<name>.pages.dev` or `<worker>.<sub>.workers.dev` | `<owner>.github.io/<repo>` | `<app>.fly.dev` |
| `norcal.cpcfantasy.com` | Yes; the zone is on Cloudflare | Yes; CNAME to `<owner>.github.io` | Yes; `fly certs add` and a CNAME |
| One repo, two sites | Yes, by project name | No; one Pages site for each repo | Yes, by app name |
| Ten clients | 10 projects of 100; one token | 10 repos; 10 tokens | 10 apps; up to about $22 a month |
| A server to run | None | None | One Machine for each site |

## Recommendation

**This is a suggestion for Brian to decide.**

Host the second site, and each later client, as a Cloudflare Worker with static assets, at `<client>.cpcfantasy.com`.

The reasons:

1. One repo deploys many sites with one token and one action. Each deploy names its Worker.
2. The cost is $0, and static requests are unlimited.
3. The DNS of `cpcfantasy.com` is already on Cloudflare, so a Workers Custom Domain needs no new DNS host.
4. Cloudflare points new projects to Workers, not Pages. A Pages project is a fine fallback with the same cost and URL shape.

A second GitHub repo breaks the "one repo" constraint and needs a PAT for each client. Fly works, but it adds a Machine and a monthly cost for each site, with no gain for static files.

Open question for Brian: does the first site, `cpcfantasy.com`, also move to Cloudflare later, so that every client deploys the same way? This choice is outside ticket 05.
