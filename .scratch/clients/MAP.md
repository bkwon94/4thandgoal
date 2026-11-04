# Clients: map

App: both.
Spec branch: `clients`.

## DESTINATION

The repo takes the One structure: thin apps, one package per domain, and one folder per client. Brian's second Sleeper league builds its own site from the same code, with its own packages, brand, and menu, and the CPC week 8 rebuild has an empty golden diff, except the removed key `is_brian`.

## DECISIONS SO FAR

These came from the Stage 1 grill of 2026-11-03. Brian decided each one.

- A client is one league and its site, over every season, with one provider per season. Each client builds its own site at its own URL, and a build with no client name fails. `GLOSSARY.md`, **Client**.
- The proof client is Brian's second Sleeper league. It is public, and Brian is a member, not the commissioner. Its data in this public repo is fine.
- A package holds one domain in both languages, at `packages/<domain>/`. ADR 0023.
- One root folder `clients/<slug>/` per client. Both apps read its `client.toml`, which replaces the League config. ADR 0022.
- A client chooses at two levels: the package list, and the values that each package names in its README. The parts and the primitives sit in one design-system package, and a client does not choose them.
- `client.toml` sets the menu items, their order, their labels, and one layout from a closed set, such as `hamburger`, `bar`, or `tabs`. By default the menu items come from the package list.
- The **Brand** is the look of a client, with a light set, a dark set, or one set only. **Theme** stays the reader's choice of light or dark. `GLOSSARY.md`.
- **Shell** stays the frame of each page. We say **app** for the thin code of One over the packages. `GLOSSARY.md`.
- One shared API serves each client, with the client in the path and a rate limit per client. The API fails at start on a bad `client.toml`.
- Each client's data lives in `clients/<slug>/published/<season>/week-NN/`. The site build copies only the selected client's data. The publish exception of ADR 0019 changes to that folder.
- Every feature moves into a package. The order: the client folder and its build first, then one package per ticket with an empty CPC golden diff, then the second client last.
- Eight packages, as bounded contexts: the kernel `league`, then `facts`, then `week`, `rankings`, `managers`, `waiver`, and `analyzer`, with `design` under each site side. The week takes chapters through a chapter port. `decisions/01-grill-the-package-map.md`.
- `client.toml` holds the package list, the seasons, the timezone, the usage code, the package values, and the menu. The sizes come from the provider. Each package exports one JSON Schema, and an unknown key fails the check. `decisions/02-grill-the-client-toml-schema.md`.
- A brand is `brand.toml`: six base color roles per set, two fonts, and two radii. The other colors derive, with an override. A brand with one set has no theme button. The color tokens take role names. `decisions/03-grill-the-brand-tokens.md`.
- The second league is NorCal Apex 6: full PPR, no median game, no DEF, a dark brand. The League settings carry the median game and the positions, the chart is a value, the returns file is shared, and a client can override only the voice. `decisions/04-grill-the-second-league-week.md`.
- The host is Cloudflare Workers with static assets, one Worker per client, named by the client slug. Each client serves at `<client>.4thandgoal.app`, and CPC moves off GitHub Pages. `cpcfantasy.com` redirects to `cpc.4thandgoal.app`, and the API serves at `api.4thandgoal.app`. `decisions/05-research-the-second-site-host.md`.
- The provider port can take ESPN and Yahoo later. The Sleeper player ID is the canonical ID, the cache path moves into the adapter, and the `league` README lists each Sleeper shape as an adapter duty. `decisions/06-research-the-espn-and-yahoo-apis.md`.
- One root uv workspace and one root pnpm workspace, each with one lock file. The API moves to `apps/api/`. A diff checks each touched package in both languages plus its dependents, with `uv run --exact`. A root file runs the full check. `decisions/07-prototype-one-workspace-two-languages.md`.
- A `prebuild` script reads `clients/$CLIENT/client.toml` and generates the routes, a registry of import lines, and the client values, outside git. A source import leaks a client component, so only a generated list keeps a package out. The check builds each client. `decisions/08-prototype-the-client-build.md`.
- The spec is `PRD.md`, approved 2026-11-04. It adds the client `data/` folder, the shared `data/nfl/` folder, `usage` in `design`, the derived role names, and the old API paths as `cpc`. `decisions/09-spec-clients.md`.

## NOT YET SPECIFIED

None.


## OUT OF SCOPE

- Player points computed from `scoring_settings`. It makes the 6-point passing touchdowns of NorCal exact, but it changes how CPC computes its points. A later spec.
- A dark default for a two-set brand. ADR 0007 keeps light as the default, and no client asks for dark yet.
- A type scale per brand. Each change needs a check at three widths, so a later spec opens it with that check.
- A menu item that links outside the site. It needs a look in the shell, and a later spec can add a `link` kind to the closed set.
- An override of a provider size in `client.toml`. Add it when a real league needs one.
- The ESPN provider and the Yahoo provider. Each is a later spec that plugs into the provider port. Two seams in one spec breaks the One test.
- A client that swaps one part for its own code. The client folder holds values and no code, so ten clients do not become ten shells.
- A deploy of the API per client. The client choice is data, so a later spec can run the same image as a second Fly app with one env var.
- The landing page at the bare `4thandgoal.app`, a marketing page for sign-ups. It is a page of the service, not of a client, so a later spec builds it.
- The split of `Provider` into a league provider and an NFL data source. The ESPN spec does it, because NorCal is a Sleeper league and cannot test it.
- The move of the raw reads in the waiver modules, `snapshot.py`, `history.py`, `live.py`, and `pipeline.py` behind `parse.py`. It is real code with no second provider to need it yet, so it is a later ticket.
