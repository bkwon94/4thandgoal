# 03 notes: where each old name is wired, and one cutover order

Ticket: `decisions/03-research-the-cutover.md`. Map: `MAP.md`. Checked: 2026-11-11.

## Scope

- The old names are `4thandgoal`, `cpcfantasyfootball`, `cpcfantasy.com`, `cpcfantasy`, and the plugin name `cpc`.
- The new names are not chosen. These notes write `<newdomain>`, `<newrepo>`, and `<plugin>`.
- The inventory uses `git grep` on the `rebrand` branch at `b450624c`. It excludes `.scratch/`, because old evidence stays as written.
- The client slug `cpc`, the folder `clients/cpc/`, and secrets such as `CORNERSTONE_PASSPHRASE_CPC` are a client name, not the product name. They stay.
- The `cornerstone_api` package, the `cornerstone` package, the `@cpc/*` npm names, and the `cpc-*` Python names stay. The map puts them out of scope.
- The GoatCounter code `cpcfantasy` is the usage code of the client `cpc`. It stays. A change resets the counts of the client.

Kinds: **D** is a domain. **R** is a repo name. **F** is a folder path. **P** is a plugin name. **A** is the Fly app name. **K** is a package name.

## Part 1: the inventory

Totals: 35 files hold `4thandgoal` or `cpcfantasy`. 22 files hold the plugin name. 54 files hold one or the other.
The count is lines with a match, per `git grep -c`.

### Site

| File | Lines | Kind | Note |
| --- | --- | --- | --- |
| `apps/site/src/lib/config.ts` | 1 | D | Default `NEXT_PUBLIC_API_URL` is `https://api.4thandgoal.app`. The deploy sets no value, so this default ships. |
| `apps/site/src/lib/config.test.ts` | 1 D, 2 usage code | D | The usage code `cpcfantasy` stays. |
| `apps/site/scripts/client-build.mjs` | 1 | D | Comment on the Custom Domain. |
| `apps/site/scripts/client-build.test.mjs` | 1 | usage code | Stays. |
| `apps/site/e2e/evidence-rules.spec.ts` | 1 | D | |
| `apps/site/README.md` | 3 | D | Lines 3, 68, 86. |
| `apps/site/docs/runbook-site-host.md` | 16 `4thandgoal`, 12 `cpcfantasy.com`, 1 folder | D, R, F | Lines 49, 100, 101, 104 name `bkwon94/4thandgoal`. Line 70 is quoted wrangler output with the old folder. Keep line 70. |
| `apps/site/package.json` | 1 | K, R | Name `cpcfantasyfootball-site`. `scripts/test_changed_apps.py` names it too. |

### Pipeline

| File | Lines | Kind | Note |
| --- | --- | --- | --- |
| `apps/pipeline/src/cornerstone/publish.py` | 1 | D | `SITE_DOMAIN = "4thandgoal.app"`. It builds each page URL and midseason URL. |
| `apps/pipeline/tests/test_pipeline.py` | 2 | D | |
| `apps/pipeline/tests/test_client.py` | 1 | usage code | Stays. |
| `apps/pipeline/README.md` | 2 | D | |
| `apps/pipeline/docs/runbook-site-api.md` | 13 `4thandgoal`, 11 `cpcfantasy.com`, 21 `cpcfantasy` | D, A, R | Lines 92, 302, 312 name the repo. Many lines name the Fly app `cpcfantasy-api`. |
| `apps/pipeline/bin/cornerstone-build` | 1 | F | `REPO_DIR="$HOME/repos/cpcfantasyfootball/apps/pipeline"`. |
| `apps/pipeline/launchagents/com.briankwon.cornerstone-weekly.plist` | 1 | F | The installed copy in `~/Library/LaunchAgents/` holds the same path. See outside places. |

### API

| File | Lines | Kind | Note |
| --- | --- | --- | --- |
| `apps/api/fly.toml` | 2 | A, D | `app = "cpcfantasy-api"`. `CORNERSTONE_ALLOWED_ORIGINS` lists `cpc.4thandgoal.app`, `norcal.4thandgoal.app`, `cpcfantasy.com`. |
| `apps/api/src/cornerstone_api/settings.py` | 1 | D | `DEFAULT_ORIGINS`, the same three hosts. |
| `apps/api/Makefile` | 2 | A | Docker tag and `fly logs --app cpcfantasy-api`. |
| `apps/api/tests/test_api.py` | 2 | D | CORS tests. |
| `apps/api/tests/test_egg_drop.py` | 1 | D | |
| `packages/eggs/python/src/eggs/keys.py` | 1 | D | `API_URL = "https://api.4thandgoal.app"`. |

`cornerstone_api` stays as is.

### Workflows under `.github/workflows/`

| File | Lines | Kind | Note |
| --- | --- | --- | --- |
| `refresh.yml` | 1 | D | Live URL. The daily cron calls `https://api.4thandgoal.app/clients/${SLUG}/refresh`. |
| `deploy-api.yml` | 1 | R | Comment only. |
| `deploy-sites.yml` | 1 | D | Comment only. |
| `check.yml` | 1 | K | `--package cpc-api`. Out of scope. |

No workflow names the repo in a `uses:` line. `deploy-sites.yml` calls `./.github/workflows/check.yml` by a relative path.

### Root files and docs

| File | Lines | Kind | Note |
| --- | --- | --- | --- |
| `.claude-plugin/marketplace.json` | 4 | P, R | Marketplace `cpc-local`, plugin `cpc`, two description lines. |
| `.claude/plugin/.claude-plugin/plugin.json` | 2 | P, R | `"name": "cpc"`. |
| `.claude/settings.json` | 2 | P | `cpc-local` and `cpc@cpc-local`. |
| `.claude/plugin/skills/**` | 27 in 13 files | P, R | `implement/` 11, `plan/` 8, `review/` 5, `to-acceptance/` 3, `to-spec/` 4, `to-tickets/` 2. `implement/build.md` names the repo twice. |
| `CLAUDE.md` | 1 R, 6 P | R, P | Title and the `cpc:` skill list. No root `AGENTS.md` exists. |
| `docs/agents/issue-tracker.md` | 3 | P | |
| `docs/agents/triage-labels.md` | 1 | P | |
| `scripts/verdict.py` | 2 | P | `AGENT_MARKER = "<!-- cpc:agent -->"` and a `cpc:review` message. |
| `scripts/fixtures/verdict/**` | 2 | P | The marker in fixture comments. |
| `scripts/test_changed_apps.py` | 1 | K | `cpcfantasyfootball-site`. |
| `docs/adr/0017`, `0018`, `0022`, `0031` | 1 each | A, R, D, P | ADRs are records. Keep the text, like `.scratch/`. |

Warning: the `verdict` check reads `<!-- cpc:agent -->` in old PR comments. Keep the marker, or accept the old and the new marker. A change to the marker alone makes the check miss the agent comments on an open PR.

### Package names

| Name | Where | Count | Scope |
| --- | --- | --- | --- |
| `cpcfantasyfootball-site` | `apps/site/package.json` | 1 | In scope: it holds the repo name. |
| `@cpc/*` | 11 packages | 561 lines in 198 files | Out of scope. |
| `cpc-api`, `cpc-*` | 12 `pyproject.toml` | 128 lines in 41 files | Out of scope. |
| `cornerstone`, `cornerstone_api` | pipeline, API | many | Out of scope. |

### Outside places

| Place | What holds an old name | Read on 2026-11-11 |
| --- | --- | --- |
| GitHub repo `bkwon94/4thandgoal` | Repo name. Public. | `gh repo view` |
| Actions secrets | `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_TOKEN`, `CORNERSTONE_PASSPHRASE`, `CORNERSTONE_PASSPHRASE_CPC`, `CORNERSTONE_PASSPHRASE_NORCAL`, `FLY_API_TOKEN`. None holds a URL. `FLY_API_TOKEN` is a deploy token for the app `cpcfantasy-api` only (ADR 0017). | `gh secret list` |
| Actions variables | None set. `CORNERSTONE_SEASON` falls back to `2026` in `refresh.yml`. | `gh variable list` |
| Webhooks, Pages | No webhooks. Pages is off (404). An environment `github-pages` remains. | `gh api` |
| Local git remote | `ssh://git@ssh.github.com:443/bkwon94/4thandgoal.git` | `git remote -v` |
| Cloudflare zone `4thandgoal.app` | Active on Cloudflare name servers. | `dig NS` |
| Workers `cpc` and `norcal` | Worker names are the client slugs, so they hold no old product name. Custom Domains `cpc.4thandgoal.app` and `norcal.4thandgoal.app` answer 200. | `curl -sI` |
| Cloudflare zone `cpcfantasy.com` | Redirect Rule "cpc to 4thandgoal". `https://cpcfantasy.com/rankings/?a=1` answers 301 to `https://cpc.4thandgoal.app/rankings/?a=1`. Also the record `api.cpcfantasy.com`. | `curl -sI` |
| DNS `api.4thandgoal.app` | `CNAME` to `cpcfantasy-api.fly.dev`, DNS only (runbook). | runbook |
| Fly app `cpcfantasy-api` | Org `personal`, region `ewr`, one machine, volume `cornerstone_data` (`vol_r68588x1momoxlj4`, 1 GB, holds the eggs SQLite and the caches). Certs `api.cpcfantasy.com` and `api.4thandgoal.app`, both Issued. | `fly status`, `fly certs list`, `fly volumes list` |
| GoatCounter `cpcfantasy.goatcounter.com` | Usage code of the client `cpc`. Stays. | code |
| Local folder `~/repos/cpcfantasyfootball` | The main checkout. Root `.venv` scripts have the absolute path in the shebang. | `head -1 .venv/bin/pytest` |
| Git worktrees | 45 linked worktrees: 44 under `.claude/worktrees/`, and 1 at `/private/tmp/claude-503/.../scratchpad/main-before`. 25 belong to `front-door`. | `git worktree list` |
| LaunchAgent `com.briankwon.cornerstone-weekly` | Loaded. The plist in `~/Library/LaunchAgents/` runs the old folder path. | `launchctl list` |
| Claude project folders | 5 folders under `~/.claude/projects/` start with `-Users-brian-kwon-repos-cpcfantasyfootball`. The main one holds `memory/` with 51 files and the session transcripts. | `find` |
| `~/.claude/settings.json` | `extraKnownMarketplaces.cpc-local.source.path` is the old folder. Two `autoMode.environment` lines name the old folder and `bkwon94/cpcfantasyfootball`. That repo name is already out of date. | `grep` |
| `~/.claude.json` | 3 mentions, with one project entry for the old folder. | `grep` |

## Part 2: how each rename behaves

### 1. A GitHub repo rename

- Web URLs redirect: "all existing information, with the exception of project site URLs, is automatically redirected to the new name." [GH-rename]
- Git remotes redirect: "operations targeting the previous location will continue to function as if made on the new location." GitHub still tells you to run `git remote set-url origin NEW_URL`. [GH-rename]
- Pages project sites do not redirect. [GH-rename] Pages is off here, so this has no effect.
- An action in a renamed repo does not redirect: "GitHub will not redirect calls to an action hosted by a renamed repository." [GH-rename] No other repo calls an action from this repo, so this has no effect.
- A new repo with the old name breaks the redirects. Do not make a new `bkwon94/4thandgoal`. [GH-rename]
- The API: the rename page does not cover it. The REST guide says a `301` is a permanent move, and a client must follow it. [GH-rest-redirects] `gh` follows it, but change each `--repo bkwon94/4thandgoal` to the new name.
- Secrets and webhooks: no GitHub page says what a rename does to them. [GH-rename] [GH-secrets] Check with `gh secret list --repo bkwon94/<newrepo>` after the rename.

### 2. A Fly app rename

- Fly has no rename. The `fly apps` commands are `create`, `destroy`, `errors`, `list`, `move`, `open`, `releases`, and `restart`. `move` changes the org, not the name. [Fly-apps]
- Fly staff say the name builds the `fly.dev` hostname, so a rename is not possible. A new name means a new app. [Fly-community] This is a forum post, not the docs.
- A new app needs a new volume. `fly volumes fork` takes only a volume ID, and its docs do not say it can fork into another app. [Fly-fork] The data copy goes through `fly ssh sftp get` and `put`. [Fly-sftp]
- A certificate: run `fly certs add <host>`, set the DNS records it gives, and check with `fly certs check <host>`. [Fly-domain]
- For a subdomain, a `CNAME` to the `.fly.dev` host works. To issue a cert before traffic moves, set the `_acme-challenge` `CNAME` (DNS-01). [Fly-domain]
- Behind the Cloudflare proxy, verify with a `_fly-ownership` TXT record, and use SSL mode "Full" or "Full (Strict)". HTTP-01 can fail behind the proxy. [Fly-domain]
- Two hostnames at once: `fly certs` "manages the certificates associated with a deployed application". [Fly-domain] The app has two Issued certs now (`api.cpcfantasy.com`, `api.4thandgoal.app`), so a third for `api.<newdomain>` serves beside them.
- The docs do not say if one hostname can have a cert on two apps at once. So a move of `api.4thandgoal.app` to a new app has an unknown gap.

### 3. Cloudflare Workers and redirects

- A Worker takes more than one Custom Domain: "You can add multiple Custom Domains." [CF-custom-domains]
- Add one in Workers & Pages, the Worker, Settings, Domains & Routes, Add, Custom Domain. Cloudflare makes the DNS record. [CF-custom-domains]
- A Custom Domain needs an active zone that you own. It fails on a hostname with an existing `CNAME` record. [CF-custom-domains]
- A Single Redirect needs proxied traffic: "Single Redirects require that the incoming traffic for the hostname referenced in visitors' requests is proxied." [CF-redirect-dashboard]
- A whole zone redirects with one wildcard rule: Request URL `http*://example.com/*`, Target URL `https://example.net/${2}`, 301, Preserve query string on. [CF-redirect-domain] A host wildcard, `https://*.4thandgoal.app/*` to `https://${1}.<newdomain>/${2}`, follows the same pattern syntax. [CF-redirect-settings] No doc page shows that exact form, so test it.
- Single Redirects run first in the order of Rules features. [CF-url-forwarding] The docs do not place Workers in that order. Test that the rule fires on a host with a Custom Domain.
- Bulk Redirects also work. They have "Include subdomains", "Subpath matching", "Preserve path suffix", and "Preserve query string". [CF-bulk-params] A Single Redirect is enough for two clients.
- A Worker rename: the wrangler `name` is "The name of your Worker". [CF-wrangler] The docs do not say what a change does. Our Worker names are the slugs, so no rename is needed.
- A redirect-only host with no origin uses a proxied `AAAA` record to `100::`. Only community and mirror pages say this, not the main docs. [CF-community-100]

### 4. `git worktree` when the main folder moves

- `git worktree move` cannot move the main worktree. [git-worktree]
- After a manual move: "If both the main worktree and linked worktrees have been moved or copied manually, then running `repair` in the main worktree and specifying the new `<path>` of each linked worktree will reestablish all connections in both directions." [git-worktree]
- Our worktrees sit inside the main folder, so one `mv` moves all 44 of them. The one in `/private/tmp` stays, and `repair` in the main worktree fixes its link back. [git-worktree]
- `worktree.useRelativePaths` links worktrees by relative paths, "useful for setups where the repository and worktrees may be moved". It turns on `extensions.relativeWorktrees`, so older Git cannot read the repo. [git-worktree]
- A Python venv does not move: "If you move an environment because you moved a parent directory of it, you should recreate the environment in its new location." [py-venv] Run `uv sync --all-packages` again. Run `pnpm install` again too, for its bin shims.

### 5. Claude Code and the folder path

- Auto memory is at `~/.claude/projects/<project>/memory/`. "The `<project>` path is derived from the git repository, so all worktrees and subdirectories within the same repo share one auto memory directory." [CC-memory]
- Transcripts are at `~/.claude/projects/<project>/<session-id>.jsonl`. `<project>` "is your working directory path with non-alphanumeric characters replaced by `-`". [CC-sessions]
- No doc says Claude Code moves this folder when the repo folder moves. A new path gives a new, empty `<project>` folder. So a `mv` of the folder under `~/.claude/projects/` carries the memory and the sessions.
- `autoMemoryDirectory` in `settings.json` sets another place for auto memory. [CC-memory]
- `claude --resume <session-id>` searches every project on the machine. [CC-sessions] An old session stays reachable by ID.
- The marketplace path in `~/.claude/settings.json` points at the old folder, so the plugin does not load until Brian changes it.

## Part 3: one cutover order

Start: `<newdomain>` is bought, and `front-door` is merged to `main`. The rule: add the new name first, then redirect the old name. Never remove an old host in this order. Ticket 04 decides when the old names go.

1. **Brian.** Add the zone `<newdomain>` to the same Cloudflare account. Set its name servers at the registrar.
   Check: `dig +short NS <newdomain>` lists two `*.ns.cloudflare.com` names.
2. **Brian.** Add the Custom Domain `cpc.<newdomain>` to the Worker `cpc`. Add `norcal.<newdomain>` to the Worker `norcal`. Keep the old domains.
   Check: `curl -sI https://cpc.<newdomain>/ | head -1` and the same for `norcal` each print `HTTP/2 200`.
3. **Brian.** Add the cert to the current app: `fly certs add api.<newdomain> --app cpcfantasy-api`. Add `CNAME` `api` to `cpcfantasy-api.fly.dev`, DNS only.
   Check: `fly certs check api.<newdomain> --app cpcfantasy-api` says Issued, and `curl -s https://api.<newdomain>/health` prints `{"status":"ok"}`.
4. **Agent.** On the spec branch, change each in-scope file of Part 1. Add the new origins to CORS. Keep the old origins `cpc.4thandgoal.app`, `norcal.4thandgoal.app`, `cpcfantasy.com`, because an open tab still sends them.
   The PR also renames the plugin to `<plugin>` and keeps the verdict marker. It merges by the flow.
   Check: `curl -s -o /dev/null -w '%{http_code}\n' -H 'Origin: https://cpc.<newdomain>' -X OPTIONS -H 'Access-Control-Request-Method: GET' https://api.<newdomain>/health` prints `200`.
5. **Brian.** On the zone `4thandgoal.app`, add a Single Redirect. Request URL `https://*.4thandgoal.app/*`. Target URL `https://${1}.<newdomain>/${2}`. Status `301`. Preserve query string on.
   The record `api` is DNS only, so the rule never sees the API. The API keeps its old host.
   Check: `curl -sI 'https://cpc.4thandgoal.app/rankings/?a=1' | grep -iE '^(HTTP|location)'` prints `301` and `location: https://cpc.<newdomain>/rankings/?a=1`.
   If it prints `200`, the Worker answers first. Then remove the old Custom Domain from the Worker, and at once add a proxied `AAAA` `cpc` to `100::`. Do `norcal` the same way.
6. **Brian.** On the zone `cpcfantasy.com`, change the target of the rule "cpc to 4thandgoal" to `concat("https://cpc.<newdomain>", http.request.uri.path)`. This removes the second hop.
   Check: `curl -sI https://cpcfantasy.com/ | grep -i '^location'` prints `location: https://cpc.<newdomain>/`.
7. **Brian.** Rename the GitHub repo `bkwon94/4thandgoal` to `bkwon94/<newrepo>` in Settings. Never make a new repo with the old name.
   Check: `gh secret list --repo bkwon94/<newrepo>` lists the 6 secrets, and `gh workflow list --repo bkwon94/<newrepo>` lists 5 workflows.
8. **Brian.** Move the folder. Do this on a day with no weekly build, and close each Claude session in the repo first. Do the steps in this order:
   1. Run `launchctl bootout gui/$(id -u)/com.briankwon.cornerstone-weekly`.
   2. Run `mv ~/repos/cpcfantasyfootball ~/repos/<newrepo>`.
   3. Run `cd ~/repos/<newrepo> && git worktree repair .claude/worktrees/* /private/tmp/claude-503/-Users-brian-kwon-repos-cpcfantasyfootball/fa1bf6f7-2ca2-49eb-b517-d84024187277/scratchpad/main-before`.
   4. Run `git remote set-url origin ssh://git@ssh.github.com:443/bkwon94/<newrepo>.git`.
   5. Run `mv ~/.claude/projects/-Users-brian-kwon-repos-cpcfantasyfootball ~/.claude/projects/-Users-brian-kwon-repos-<newrepo>`.
   6. In `~/.claude/settings.json`, set the marketplace key to `<plugin>-local` and its path to `/Users/brian.kwon/repos/<newrepo>`. Fix the two `autoMode` lines.
   7. Run `rm -rf .venv && uv sync --all-packages && pnpm install`.
   8. Copy the plist from `apps/pipeline/launchagents/` to `~/Library/LaunchAgents/`, then run `launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.briankwon.cornerstone-weekly.plist`.

   Check: `git worktree list | head -3` shows `/Users/brian.kwon/repos/<newrepo>` with no `prunable`, and `launchctl list | grep cornerstone` shows the job.
9. **Agent.** In a new session in the new folder, run one plugin skill to prove the load. Run `make check-fast` in `apps/pipeline`.
   Check: `/plugin` lists `<plugin>@<plugin>-local` as enabled, and the check passes.
10. **Brian, optional, the risky step.** A new Fly app for the name `<newrepo>-api`. It needs a new volume, a copy of the eggs SQLite with `fly ssh sftp`, each secret again, and a new deploy token in `FLY_API_TOKEN`.
    It then needs each of the three certs on the new app. The docs do not say if one hostname can hold a cert on two apps, so the API can go down between `fly certs remove` and the new cert.
    A claim written to the old volume after the copy is lost. The `fly.dev` name is the only place the old app name shows, and no manager sees it.
    The advice: keep `cpcfantasy-api` and skip this step, or do it in the off-season. Ticket 06 decides.

Why this order has no downtime: steps 1 to 3 add new hosts beside the old ones. Step 4 ships code that works on both hosts. Step 5 sends a manager to a host that already serves. The API keeps every old host, so an open tab still works.

## Sources

Each source was checked on 2026-11-11.

- [GH-rename] https://docs.github.com/en/repositories/creating-and-managing-repositories/renaming-a-repository
- [GH-rest-redirects] https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api
- [GH-secrets] https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions
- [Fly-apps] https://docs.fly.io/flyctl/apps
- [Fly-community] https://community.fly.io/t/deleting-and-or-renaming-apps/6967/2 (forum, not docs)
- [Fly-fork] https://docs.fly.io/flyctl/volumes-fork and `fly volumes fork --help`
- [Fly-sftp] `fly ssh sftp --help`
- [Fly-domain] https://docs.fly.io/networking/custom-domain and `fly certs --help`
- [CF-custom-domains] https://developers.cloudflare.com/workers/configuration/routing/custom-domains/
- [CF-redirect-dashboard] https://developers.cloudflare.com/rules/url-forwarding/single-redirects/create-dashboard/
- [CF-redirect-domain] https://developers.cloudflare.com/rules/url-forwarding/examples/redirect-all-another-domain/
- [CF-redirect-settings] https://developers.cloudflare.com/rules/url-forwarding/single-redirects/settings/
- [CF-url-forwarding] https://developers.cloudflare.com/rules/url-forwarding/
- [CF-bulk-params] https://developers.cloudflare.com/rules/url-forwarding/bulk-redirects/reference/parameters/
- [CF-wrangler] https://developers.cloudflare.com/workers/wrangler/configuration/
- [CF-community-100] https://community.cloudflare.com/t/http-and-https-redirect/594881 (community, not docs)
- [git-worktree] https://git-scm.com/docs/git-worktree
- [py-venv] https://docs.python.org/3/library/venv.html
- [CC-memory] https://code.claude.com/docs/en/memory
- [CC-sessions] https://code.claude.com/docs/en/sessions
