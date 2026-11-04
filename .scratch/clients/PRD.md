# Clients: one structure for many leagues

Status: ready-for-agent
Date: 2026-11-04
Apps: both. The pipeline and the API read `client.toml` and move their domain code into packages. The site build selects one client, generates its routes, and applies its brand. The API moves to its own app.
Spec branch: `clients`.
Source: the map `.scratch/clients/MAP.md` and decision tickets 01 to 09. ADRs 0019, 0022, and 0023.
Tickets: 01 to 15, in `issues/`.

## Problem Statement

The code serves one league, CPC. The League config, the brand colors, the site name, the menu, and the published data all sit in the two apps as CPC values. Two env flags hide the waiver board and the finder.

Brian wants a second league on the same code. Today that means a fork, or a flag for each difference. A fork drifts. A flag ships each feature to each league and hides it. Neither one grows to ten leagues.

The CPC site lives on GitHub Pages, and one GitHub repo serves one Pages site only. So a second site has no host today.

## Solution

The repo takes the One structure. The code splits into eight packages, one per domain, each in both languages. The apps become thin: they hold the build config, the routes, and the wire code. Each league is one client folder at `clients/<slug>/` with its values and no code.

A client chooses at two levels: its package list, and the package values in each package README. The brand, the copy, the menu, and the voice are values of the client too. The site build reads `clients/$CLIENT/client.toml`, and it generates the routes and the import lines of that client only. An omitted package is then absent from the bundle.

Each client deploys as one Cloudflare Worker at `<slug>.4thandgoal.app`. CPC moves from GitHub Pages to `cpc.4thandgoal.app`, and `cpcfantasy.com` redirects there. The API serves each client at `api.4thandgoal.app`, with the client in the path.

The proof is two numbers. The CPC week 8 rebuild has an empty golden diff, except the removed key `is_brian`. The second client, NorCal Apex 6, builds its own week from the same code, with its own packages, brand, and menu.

## User Stories

### Brian as the operator of the service

1. As Brian, I want each league in one folder `clients/<slug>/`, so that I add a league with no change to the code.
2. As Brian, I want one `client.toml` that the pipeline, the API, and the site build all read, so that the three readers never disagree.
3. As Brian, I want a build with no client name to fail with a plain message, so that no build ships the wrong league.
4. As Brian, I want a client to take or omit a package with one line, so that a league gets only the features it wants.
5. As Brian, I want each package value to have a default in the package README, so that a client sets only what differs.
6. As Brian, I want an unknown key in `client.toml` to fail the check, so that a typo never passes as a default.
7. As Brian, I want a stale exported JSON Schema to fail the check, so that the site and the pipeline check against the same rules.
8. As Brian, I want the league sizes to come from the provider, so that a typed size never disagrees with the real league.
9. As Brian, I want each client to deploy to its own Worker at `<slug>.4thandgoal.app`, so that each league has its own URL at no cost.
10. As Brian, I want the check to build each client, so that a change to a shared part cannot break a second client unseen.
11. As Brian, I want the weekly `publish` to write into `clients/<slug>/published/`, so that the data of each client stays in its folder.
12. As Brian, I want the CPC week 8 rebuild to have an empty golden diff, so that I know the move changed no CPC output.
13. As Brian, I want each manual step to come to me with its exact values and its check, so that I do it once and right.
14. As Brian, I want one shared returns file for the NFL, so that I keep the return weeks in one place for every league.
15. As Brian, I want one API deploy for each client, so that I run and pay for one Fly app.
16. As Brian, I want a rate limit per client on the API, so that one league cannot use up the grades of another.
17. As Brian, I want the API to fail at start on a bad `client.toml`, so that a bad value never reaches a reader.

### Brian as the developer

18. As Brian, I want one package per domain at `packages/<domain>/`, so that one spec of a feature touches one folder.
19. As Brian, I want each package to hold both languages, so that a client lists each feature one time.
20. As Brian, I want one root uv workspace and one root pnpm workspace, so that each language has one lock file.
21. As Brian, I want an undeclared import between packages to fail the check, so that the dependency order holds.
22. As Brian, I want a diff to check each touched package in both languages plus its dependents, so that a Python change cannot break the site unseen.
23. As Brian, I want a change to a root file to run the full check, so that a change to the workspace is never under-tested.
24. As Brian, I want each package to own its `tunables`, so that a number lives beside the rule that reads it.
25. As Brian, I want each package to write its own published file, so that its site side reads it with its own schema.
26. As Brian, I want the week to take chapters through a chapter port, so that a client with no rankings gets a week with no rankings chapter.
27. As Brian, I want the color tokens to take role names, so that a brand with a blue accent has no class `bg-red`.
28. As Brian, I want the provider port to take ESPN and Yahoo later, so that a later spec adds a provider with no change to the packages.
29. As Brian, I want the generated site files out of git, so that a review shows only the source.

### A manager of a league, as a reader of the site

30. As a manager of CPC, I want the CPC site to look and read the same after the move, so that nothing I know changes.
31. As a manager of CPC, I want my old `cpcfantasy.com` links to keep working, so that a bookmark or a group chat link still opens the page.
32. As a manager of NorCal, I want a site with the name and the colors of my league, so that it reads as our site.
33. As a manager of NorCal, I want the week to show no Median Game chapter, so that the page matches our league, which has no median game.
34. As a manager of NorCal, I want the standings and the odds to count one game a week, so that the numbers match Sleeper.
35. As a manager of NorCal, I want the pool and the leaders to have no DEF, so that the page shows only positions that my league starts.
36. As a manager of NorCal, I want the full PPR projections, so that the projections match my scoring.
37. As a manager of NorCal, I want the trade finder, so that I can find a trade with no guesswork.
38. As a manager of NorCal, I want a menu bar, so that each page is one tap away.
39. As a manager of NorCal, I want a dark site with no theme button, so that the brand of my league always shows.
40. As a manager of CPC, I want the theme button to stay, so that I can still choose light or dark.
41. As a reader with low vision, I want each text pair of each brand to pass WCAG AA, so that I can read each page.
42. As a manager of a league with no logo, I want the masthead to show the site name as text, so that the page still has a title.

## Implementation Decisions

### The structure

- A **Client** is one league and its site, over every season, with one provider per season (ADR 0022). Its folder holds `client.toml`, `brand.toml`, `copy.toml`, an optional `prompts/`, `assets/`, `data/`, and `published/`. The folder holds values and no code.
- `clients/<slug>/data/<season>/` holds the history and the raw weeks of the client, which `apps/pipeline/data/` holds today. ADR 0022 adds `data/` to its tree.
- The shared NFL data sits at the root `data/nfl/`, outside each client: the caches, which git ignores, and the **Returns file** at `data/nfl/<season>/returns.json`.
- A **Package** is one domain in both languages at `packages/<domain>/`, with `python/`, `site/`, or both, and a README with the headings Knows, Ports, and Does not do (ADR 0023).
- The Python package is `cpc-<domain>` and imports as `<domain>`. The npm package is `@cpc/<domain>`. A package has no build step. Each package with TSX lists `react` as a peer dependency and `@types/react` as a dev dependency.
- The **Apps** are `apps/pipeline/`, `apps/api/`, and `apps/site/`. An app holds the build config, the routes, and the wire code, and no rule of a domain. The API moves out of `apps/pipeline/` into `apps/api/`.

### The eight packages

Decision 01 maps each module. The dependency order is `league`, then `facts`, then the five core packages. `design` sits under each site side.

| Package | Role | Holds |
| --- | --- | --- |
| `league` | Shared kernel | The models, the provider port and the Sleeper adapter, the paths, the history, nflverse, the snapshot, the chart, the Claude port, the lineup, the standings table, and the shared tunables. Every outside service enters here. Site: `headshot`, `avatar`. |
| `facts` | Generic subdomain | The fact tokens, the writer, the verifier, the names, the default voice. |
| `week` | Core | The sheet chapters except rankings, the league and matchup facts, the page writer, the chapter port, the median text. |
| `rankings` | Core | The power rankings, the odds, its chapter, its published file. |
| `managers` | Core | The managers and its published file. |
| `waiver` | Core | The waiver board, `rank_score`, the research prompt, its published file. |
| `analyzer` | Core | The rubric, the criteria, the analysis, the finder, the analyzer routes of the API, its prompts. Site: the form, `api`, `passphrase`, `teams-store`, `team-pick`. |
| `design` | Presentation | The primitives, the parts, the shell with its three menu layouts, the theme, motion, format, the code that applies a brand, and the usage count. |

- `lib/usage.ts` moves into `design`. The shell and the analyzer both call `countEvent`, and `design` sits under both. The app layout reads `usage_code` from the client values.
- The rules of the map hold: a term belongs to one package, the kernel stays small, and each package owns its `tunables`. A number that three or more packages read goes into `league`.

### `client.toml`

The schema comes from decision 02. The file for CPC:

```toml
packages = ["week", "rankings", "managers", "analyzer"]
timezone = "America/New_York"
usage_code = "cpcfantasy"

[seasons.2026]
provider = "sleeper"
league_id = "1386167364424318976"

[values.analyzer]
finder = false

[menu]
layout = "hamburger"
items = [
  { page = "home", label = "Home" },
  { package = "week" },
  { package = "rankings", label = "Power Rankings" },
  { package = "managers", label = "Managers" },
  { package = "analyzer", label = "Trade Analyzer" },
]
```

- The list omits `league`, `facts`, and `design`, because each client takes them.
- Required: the seasons, with the provider and the league id of each, the timezone, and the package list. Optional: `usage_code`, the package values, and the menu.
- The values of a package sit in the table `[values.<package>]`. The key `packages` holds only the list, because TOML forbids one key as both an array and a table.
- Each package defines its **Package values** as one pydantic model. A step exports each model as a JSON Schema file into its package. The pipeline and the API check with the model. The site build checks with the JSON Schema and `ajv`. An unknown key fails, and a stale exported file fails.
- The menu is a closed set. An item names the home page or one package of the list, with an optional label. The layout is `hamburger`, `bar`, or `tabs`. With no `items`, the menu takes the home page, then the package list in its order. An item for an omitted package fails the check.
- The site values follow one rule: a value that changes with the league goes into `client.toml`, and a value that changes with the deploy stays an env value. `NEXT_PUBLIC_WAIVER` becomes `waiver` in the list. `NEXT_PUBLIC_FINDER` becomes `finder` of `analyzer`. `NEXT_PUBLIC_SEASON` derives from the latest season. `NEXT_PUBLIC_USAGE_CODE` becomes `usage_code`. `NEXT_PUBLIC_API_URL` stays an env value, and its default becomes `https://api.4thandgoal.app`. `NEXT_PUBLIC_BASE_PATH` goes away, because each client serves at the root.
- `client.toml` replaces the League config. Gone: the sizes, `owner_username`, `is_owner`, `display_name`, and `prompts_dir`. `seller_gap` moves into the tunables of `analyzer`. `shootout_top` moves into the tunables of `week`.
- The published key `is_brian` goes away. It is the one allowed line in the CPC golden diff.

### The League settings

- The Sleeper adapter maps the settings of each season into the **League settings**, a kernel model in `league`: the team count, the playoff spots, the roster slots, the weeks of the regular season, the reception points, and the **Median game** from `league_average_match`.
- The code derives the lines, the strength rank, and the star ranks from the roster slots and the team count. Each derived CPC value must equal the CPC value of the League config today.
- The reception points choose the points key: 0 gives `pts_std`, 0.5 gives `pts_half_ppr`, and 1 gives `pts_ppr`. Another value fails the build with a plain message.
- The roster slots set the position lists. A position with no slot, through a flex slot too, leaves the pool and the leaders. The ranked positions stay QB, RB, WR, and TE.
- With the median game off, each package honors it when it moves. The standings and the odds count one game a week. The power form drops the median weight. The week has no Median Game chapter. The managers points line has no median line.

### The provider port

- The Sleeper player ID is the one canonical player ID. The `league` README states the rule.
- `fetch_week`, `fetch_live`, and `fetch_players` drop the `players_cache` argument. The Sleeper adapter takes its cache dir in its constructor.
- The `league` README lists each Sleeper shape in the port as a duty of a later adapter.

### The chart, the prompts, and the voice

- `chart` is a package value of `league`. The default is no chart, and then each chart value is 0. CPC sets the chart that it reads today. NorCal sets `1QB1.0PPR4pt`.
- Each rule prompt moves into the package that owns it: `writer` and `verifier` into `facts`, `analysis`, `finder`, and `rubric` into `analyzer`, and `research` into `waiver`.
- `tone.md` and `vocabulary.md` move into `facts` as the default voice. A client `prompts/` folder can override only those two files. CPC keeps its voice in `clients/cpc/prompts/`.
- The median text moves into `week`. The build adds it only when the median game is on.

### The brand

The schema comes from decision 03. A **Brand** is `brand.toml`: the two radii, two font stacks, and one or two color sets.

- Each set has the six **Base roles**: `accent`, `band`, `page`, `card`, `text`, and `muted`. A missing base role or an unknown role fails the check. The design package exports a JSON Schema for the file.
- The brand file decides the set count. With no `[dark]` table, the site paints light and has no theme button. With no `[light]` table, it paints dark and has no theme button. A two-set brand defaults to light (ADR 0007).
- The build writes the CSS custom properties from the brand. Font files go in `assets/fonts/`, and the design package loads them with `@font-face`. The build fetches no font from an outside host.
- The spacing, the type scale, the breakpoints, the tracking, `move-up`, and `move-down` stay in the design package.
- The color tokens take role names in one mechanical ticket, before the design package moves, with no change to the CPC look. The CSS tokens are below. `ink` and `mute` keep their names, as decision 03 renames only four tokens.

| Today | Token | Kind | Formula, for a brand with no override |
| --- | --- | --- | --- |
| `red` | `accent` | base | `accent` |
| `blk` | `band` | base | `band` |
| `wht` | `page` | base | `page` |
| `gry` | `card` | base | `card` |
| `ink` | `ink` | base | `text` |
| `mute` | `mute` | base | `muted` |
| `red-lt` | `accent-text` | derived | `accent` |
| `red-ink` | `accent-ink` | derived | `accent` |
| `red-glow` | `accent-glow` | derived | `accent` 45% over transparent |
| `pick` | `pick` | derived | `accent` 10% over `page` |
| `card-blk` | `card-band` | derived | `band` |
| `ink-2` | `ink-2` | derived | `text` 85% over `page` |
| `rule` | `rule` | derived | `text` 10% over `page` |
| `divider` | `divider` | derived | `text` 20% over `page` |
| `bar-off` | `bar-off` | derived | `text` 20% over `page` |
| `on-dark` | `on-dark` | derived | the `page` of the light set, else `text` |
| `on-dark-2` | `on-dark-2` | derived | `on-dark` 80% over `band` |
| `on-dark-muted` | `on-dark-muted` | derived | `on-dark` 60% over `band` |
| `rule-dark` | `rule-dark` | derived | `on-dark` 15% over `band` |
| `chip-dark` | `chip-dark` | derived | `on-dark` 10% over `band` |

- Each **Derived role** has its formula in the design package as a `color-mix`, and a brand can override it under `[light.derived]` or `[dark.derived]`.
- `clients/cpc/brand.toml` overrides each derived role whose formula does not give today's CPC value. The test of the brand pins each CPC value.
- The shadcn tokens `card` and `accent` take the brand roles of the same name. A shadcn use with another meaning, such as the focus fill of the select item, moves to the role with that meaning.

### The copy

- `copy.toml` holds the site name, the masthead text, and the tagline. CPC: "Cornerstone Fantasy Football League". NorCal: "NorCal Apex 6".
- The logo is optional. With no logo in `assets/`, the masthead shows the site name as text.

### The site build

The design comes from decision 08.

- The env value `CLIENT` holds the client slug. A build with no `CLIENT` fails with a plain message.
- A `prebuild` script reads `clients/$CLIENT/client.toml` and checks it. It writes one route file per package, one registry of import lines for the chapters and the menu, the client values, and the brand CSS. It copies only that client's `published/` into `public/`.
- Each generated file starts with a `GENERATED ... Do not edit.` line, and `.gitignore` lists each one. An empty generated list has an explicit type.
- The `pageExtensions` gate goes away.
- Only the generated list keeps an omitted package out of the bundle. A source import of a client component ships it, under any guard.

### The workspaces and the check

The design comes from decision 07.

- One root `pyproject.toml` holds a uv workspace over `apps/pipeline`, `apps/api`, and `packages/*/python`, with one root `uv.lock`.
- One root `pnpm-workspace.yaml` holds `apps/site` and `packages/*/site`, with one root `pnpm-lock.yaml`. `transpilePackages` in the site config compiles each package.
- The check runs each Python member with `uv run --exact --package <name>`, so an undeclared import fails.
- A change in `packages/<domain>/` checks both languages of that package, plus each package and app that depends on it. pnpm selects with `--filter "...[<ref>]"`. A short script reads the uv workspace sources for the Python side.
- A change to a root file runs the full check. The root files are the workspace files, the lock files, the root `Makefile`, and `.github/`.
- The full check builds each client in `clients/`. The fast hook builds `cpc` only.

### The published data and the publish

- The data of each client lives in `clients/<slug>/published/<season>/week-NN/`. The CPC data moves there from `apps/site/public/<season>/`.
- The publish exception of ADR 0019 changes: `publish` may push to `main`, and it may stage only `clients/<slug>/published/<season>/`. The root `CLAUDE.md` changes with it.
- The pipeline takes the client slug as an argument. With no slug, it fails with a plain message.

### The API

- One shared API serves each client, with the client in the path: `/clients/<slug>/teams`, `/clients/<slug>/analyze`, `/clients/<slug>/find`, and `/clients/<slug>/refresh`. `/health` stays at the root.
- The rate limit of the grades counts per client and per address.
- The API reads each client folder at start and fails at start on a bad `client.toml`.
- The old paths with no client answer as `cpc`, so an old page that calls `api.cpcfantasy.com` still works.
- The API serves at `api.4thandgoal.app`, with a second Fly cert. `api.cpcfantasy.com` keeps its cert.

### The host

The design comes from decision 05.

- Each client is one Cloudflare Worker with static assets, named by the client slug, at the Custom Domain `<slug>.4thandgoal.app`. The site has no base path.
- One workflow deploys each client with `cloudflare/wrangler-action` and one API token, on each green push to `main`.
- CPC moves to `cpc.4thandgoal.app` in this spec, and the GitHub Pages deploy goes away. One Redirect Rule sends `cpcfantasy.com/<path>` to `cpc.4thandgoal.app/<path>` with a 301.

### The second client

NorCal Redraft Apex #6, Sleeper league `1402948824305049600`, slug `norcal`. Decision 04 holds its files.

- It takes the same package list as CPC. It differs at the second level: `finder = true`, the chart `1QB1.0PPR4pt`, the menu layout `bar`, and a dark brand with one set.
- Its brand: accent `#c2410c`, band `#0a0a0a`, page `#141414`, card `#232323`, text `#f5f0e6`, muted `#a8a29a`, and the accent text `#e0a526`. Each text pair passes WCAG AA. A ticket can tune a value with the same contrast check.
- It has no logo and no `prompts/`, so it gets the site name as text and the default voice.
- Its known gap: each NorCal projection uses 4-point passing touchdowns, so each QB projection is 2 points low for each passing touchdown. The matchup scores stay exact.

### The order of the work

1. The client folder of CPC, the client build, and the check of `client.toml`. The CPC values move out of the League config.
2. The root workspaces and the move of the API to `apps/api/`.
3. The rename of the color tokens to role names.
4. One package per ticket, in the dependency order: `league`, `facts`, `design`, `week`, `rankings`, `managers`, `waiver`, `analyzer`. Each ticket has an empty CPC golden diff, and each core package ticket adds a test with the median off.
5. The brand and the copy files, and the move of CPC to its Worker.
6. The second client last.

### The manual steps of Brian

Brian does each step. The ticket that needs a step names it as a blocker. When `cpc:implement` reaches that ticket, it stops and gives Brian the dashboard page, each value, and the check that shows the step worked.

1. Add the zone `4thandgoal.app` to Cloudflare.
2. Make a Cloudflare API token for Workers, and add it and the account ID as GitHub secrets for `wrangler-action`.
3. Add the Custom Domain of each Worker: `cpc.4thandgoal.app` and `norcal.4thandgoal.app`.
4. Add the Redirect Rule on `cpcfantasy.com`.
5. Run `fly certs add api.4thandgoal.app`, and add its DNS record.

## Testing Decisions

A good test checks the behavior at a seam that a reader or a manager sees: a published file, a built export, or an API answer. It does not check the module layout. Each port has one fake (ADR 0015). No test calls Claude or the network.

The seams, from the highest:

1. **The CPC golden diff.** The golden test builds the four golden files from the week 6 fixtures, now through `clients/cpc/client.toml`. Every ticket that moves code keeps the diff empty, except the removed `is_brian`. The destination check rebuilds CPC week 8 and compares it with the published week 8. Prior art: `tests/golden.py` and `tests/test_golden.py` of the pipeline.
2. **The export of each client.** The check builds each client and reads its export. The `cpc` export has no waiver route and no waiver JS. The `norcal` export has the finder, the site name "NorCal Apex 6", and no theme button. A client with the list `["week"]` builds a week with no rankings chapter and no rankings route. Prior art: `scripts/check-export.mjs` of the site.
3. **The check of the client files.** A test feeds bad files to the check: an unknown key, a missing required value, a menu item for an omitted package, a bad layout, a missing base role, and a stale exported schema. Each one fails with a plain message. Prior art: the rule tests of the site, such as `readme-rule.test.ts`.
4. **The median game off.** Each core package ticket adds a fixture test with the League settings set to no median game. The test reads the published file of the package. Prior art: the fixture tests of the pipeline with `tests/fakes.py`.
5. **The brand CSS.** A test turns `clients/cpc/brand.toml` into the CSS custom properties and checks each CPC value against today's value. A second test checks each text pair of each brand for WCAG AA.
6. **The API.** The API tests call each route with the client in the path, call an old path as `cpc`, and check the rate limit per client. A bad `client.toml` fails the start. Prior art: `tests/test_api.py` of the pipeline.
7. **The dependency order.** The check runs each Python member with `uv run --exact`. pnpm blocks an undeclared import of a site package.

Brian checks that these seams match his intent with this spec.

## Out of Scope

- Player points computed from `scoring_settings`. It changes how CPC computes its points. A later spec.
- A dark default for a two-set brand. ADR 0007 keeps light as the default.
- A type scale per brand. Each change needs a check at three widths.
- A menu item that links outside the site. A later spec can add a `link` kind.
- An override of a provider size in `client.toml`. Add it when a real league needs one.
- The ESPN provider and the Yahoo provider. Each is a later spec behind the provider port.
- A client that swaps one part for its own code. The client folder holds values and no code.
- A deploy of the API per client. A later spec can run the same image as a second Fly app.
- The landing page at the bare `4thandgoal.app`.
- The split of `Provider` into a league provider and an NFL data source. The ESPN spec does it.
- The move of the raw reads in the waiver modules, `snapshot.py`, `history.py`, `live.py`, and `pipeline.py` behind `parse.py`.
- The removal of the old API paths with no client. A later ticket removes them when no page calls them.

## Further Notes

- The spec sets five values that no decision ticket set. Brian checks each one:
  1. The client folder holds `data/` for the history and the raw weeks, and ADR 0022 adds it.
  2. The shared NFL data and the returns file sit at `data/nfl/`.
  3. `lib/usage.ts` moves into `design`.
  4. The derived role names and formulas in the brand table.
  5. The old API paths answer as `cpc`.
- `league` is the first package to watch. If its README sentence stops being true, split the outside services into a second kernel package.
- In the API code, `client_address` names the address of a request, not a **Client**. The API ticket renames it to keep one word, one meaning.
- Each client build costs about 30 seconds in CI.
