# Rebrand: map

App: both, plus the plugin and the local setup.
Spec branch: `rebrand`.

## DESTINATION

The local folder is `~/repos/4thandgoal`, so it matches the GitHub repo `bkwon94/4thandgoal`. The plugin is `4ag`. The memory, the worktrees, the venv, the LaunchAgent, and the plugin load all work from the new folder. The domain `4thandgoal.app` stays.

## DECISIONS SO FAR

These came from the grill of 2026-11-11. Brian decided each one.

- The long-term goal is a name that sells a fantasy AI expert to any league. Front door is the first version of that product.
- The **Product name** is the one name of the app across all clients. **Brand** keeps its meaning: the identity of one client in `brand.toml`. `GLOSSARY.md`, **Product name**.
- `cpc:implement rebrand` starts after `front-door` merges to `main`, because a rename of the folder and the plugin breaks the open worktrees of front door.
- "Fantasy Bot" and "Commish Bot" are taken by live AI fantasy products. Five names had free domains. `decisions/01-research-name-candidates.md`.
- 54 files outside `.scratch/` hold an old name. 10 of them name the folder path, and 22 name the plugin. The folder move needs a fix of the venv, the LaunchAgent, the plugin path, the memory folder, and the worktrees. `decisions/03-research-the-cutover.md`.
- The Product name stays 4th & Goal at `4thandgoal.app` for now. A new domain costs too much for two leagues. `decisions/02-grill-the-product-name.md`.
- No old domain redirects, because no domain changes. `decisions/04-spec-the-old-domains.md`.
- The Fly app keeps the name `cpcfantasy-api`. `decisions/07-grill-the-fly-app.md`.
- The plugin is `4ag`, with the marketplace `4ag-local`. The verdict marker `<!-- cpc:agent -->` stays. `decisions/05-spec-the-plugin-name.md`.
- The spec is `PRD.md`. The weekly build script finds the repo from its own path, and a runbook holds the folder move. `decisions/06-spec-rebrand.md`.

## NOT YET SPECIFIED

None.

## OUT OF SCOPE

- A new Product name and domain. Choose it when front door serves a league that we do not know. The candidates are in `decisions/01-research-name-candidates.notes.md`.
- A new Fly app. Fly has no rename, and a move risks the eggs SQLite and the API certificate.
- A product brand on the page, such as a logo, a footer, or a title. The league owns the page today.
- A landing page at the bare domain for new leagues. It is a growth feature, not a rename.
- A rename of `cornerstone_api`, the `@cpc/*` npm names, and the other package names. It touches every import for no user gain.
- A rewrite of old text under `.scratch/`. Evidence is a record of what happened.
- The same skills in Codex. 11 of 14 skill files call Claude-only tools, so the port is its own spec, `codex-skills`, after this one. Brian chose it on 2026-11-11.
