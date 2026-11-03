# Clients: map

App: both.
Spec branch: `clients`.

## DESTINATION

The repo takes the One structure: thin apps, one package per domain, and one folder per client. Brian's second Sleeper league builds its own site from the same code, with its own packages, brand, and menu, and the CPC week 8 rebuild has an empty golden diff.

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

## NOT YET SPECIFIED

- Which domains become packages, from the pipeline modules and the site parts? `decisions/01-grill-the-package-map.md`.
- What sections and values does `client.toml` hold? `decisions/02-grill-the-client-toml-schema.md`.
- Which tokens does a brand give: which colors, fonts, and radii? `decisions/03-grill-the-brand-tokens.md`.
- What does the second league need to build a week: its history, its prompts, its voice? `decisions/04-grill-the-second-league-week.md`.
- Where is the second site hosted, and at what URL? `decisions/05-research-the-second-site-host.md`.
- Can the provider port take the ESPN API and the Yahoo API later? `decisions/06-research-the-espn-and-yahoo-apis.md`.
- How do `uv` and `pnpm` find the code of a package, and how does the check run per package? `decisions/07-prototype-one-workspace-two-languages.md`.
- How does the Next.js build select one client from `client.toml`? `decisions/08-prototype-the-client-build.md`.
- The spec. `decisions/09-spec-clients.md`.

## OUT OF SCOPE

- The ESPN provider and the Yahoo provider. Each is a later spec that plugs into the provider port. Two seams in one spec breaks the One test.
- A client that swaps one part for its own code. The client folder holds values and no code, so ten clients do not become ten shells.
- A deploy of the API per client. The client choice is data, so a later spec can run the same image as a second Fly app with one env var.
