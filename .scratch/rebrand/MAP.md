# Rebrand: map

App: both, plus the API.
Spec branch: `rebrand`.

## DESTINATION

The product has one Product name. Each client serves at `<client>.<newdomain>`, the API serves at `api.<newdomain>`, and the old `4thandgoal.app` addresses redirect to the new ones. The GitHub repo, the local folder, and the plugin carry the Product name.

## DECISIONS SO FAR

These came from the Stage 1 grill of 2026-11-11. Brian decided each one.

- The goal is both: a name that sells a fantasy AI expert to any league and any manager, and one name for us everywhere. Front door is the first version of that product, and the name reflects it.
- The **Product name** is the one name of the app across all clients. **Brand** keeps its meaning: the identity of one client in `brand.toml`. `GLOSSARY.md`, **Product name**.
- The plan, the name search, and the domain purchase run now. `cpc:implement rebrand` starts after `front-door` merges to `main`, because a rename of the folder and the plugin breaks the open worktrees of front door.
- "Fantasy Bot" and "Commish Bot" are taken by live AI fantasy products. The top 5 free names are Ask Huddle, Huddle Sage, Pocket OC, League Oracle, and Grid Genie. `decisions/01-research-name-candidates.md`.
- 54 files hold an old name. The Workers keep their slug names. The folder move runs last and needs a fix of the venv, the LaunchAgent, the plugin path, the memory folder, and the worktrees. `decisions/03-research-the-cutover.md`.
- The rename covers each name a person types or sees: the domain, the GitHub repo, the local folder, the plugin, the Fly app, and the Worker names.

## NOT YET SPECIFIED

- What is the Product name? `decisions/02-grill-the-product-name.md`.
- Does the API move to a new Fly app, or keep `cpcfantasy-api`? `decisions/07-grill-the-fly-app.md`.
- How long do `4thandgoal.app` and `cpcfantasy.com` redirect, and do we renew them? `decisions/04-spec-the-old-domains.md`.
- Is the plugin the full Product name or a short form? `decisions/05-spec-the-plugin-name.md`.
- The spec. `decisions/06-spec-rebrand.md`.

## OUT OF SCOPE

- A product brand on the page, such as a logo, a footer, or a title. The league owns the page today, and front door may own this design work.
- A landing page at the bare domain for new leagues. It is a growth feature, not a rename.
- A rename of `cornerstone_api` and the other package names. It touches every import for no user gain. It can be its own ticket later.
- A rewrite of old text under `.scratch/`. Evidence is a record of what happened.
