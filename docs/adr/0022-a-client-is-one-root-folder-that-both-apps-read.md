# A client is one root folder that both apps read

A client is one league and its site. Each client has one folder at the root, `clients/<slug>/`, and
its file `client.toml` holds the package list and the values of the client. The pipeline, the API,
and the site build all read the same file. The client folder holds values and no code.

```
clients/cpc/
  client.toml   the league, the provider per season, the package list, the values, the menu
  brand.toml    the color roles of the brand, a light set and a dark set (ADR 0024)
  copy.toml     the site name, the masthead text, the tagline
  prompts/      the voice of the writer for this league
  assets/       the logo and the favicon
  data/         the history and the raw weeks of the league, by season, with the league file of each season
  published/    the published files, by season and week
```

The shared NFL data sits at the root `data/nfl/`, outside each client: the caches, which git ignores, and the
Returns file at `data/nfl/<season>/returns.json`. A return week is the same in each league, so no client owns it.

Each client builds its own site at its own URL. A site build with no client name fails, so no site
build has a default client. The site build copies only the published files of its client.

One API deploy serves all clients, with the client in the path, such as `/clients/<slug>/teams`. The
old paths with no client answer as `cpc`, so an old page that calls `api.cpcfantasy.com` still works.
`cpc` is the one default client, and only for those old paths.

`client.toml` replaces the League config. A client chooses at two levels: the packages in its list,
and the values that each package names in its README. A client does not choose a part.

## How three readers agree

Each package defines its package values as one pydantic model, and a step exports it as a JSON Schema file into
the package. The pipeline and the API check `client.toml` with the model. The site build checks it with the JSON
Schema. A stale exported file fails the check, and an unknown key in `client.toml` fails it too. The league sizes are
not in `client.toml`: the provider gives them per season. `.scratch/clients/decisions/02-grill-the-client-toml-schema.md`
holds the file for CPC.

Rejected: a pydantic model and a Zod schema per package, which are two sources of truth. Also rejected: a checked
`client.json` that Python writes for the site, which makes the site build run Python.

## How the site selects a client

The site build reads `clients/$CLIENT/client.toml` and generates its route files and its registry of
import lines before `next build`. Only a generated list keeps an omitted package out of the bundle:
an import in source code ships each client component of the package, under any guard. The generated
files stay out of git. `.scratch/clients/decisions/08-prototype-the-client-build.md` records the proof.

## Why we break from One

One puts a client under its app, at `apps/<app>/clients/<owner>/`, and the import lines of
`client.ts` are its package list (One ADR-0009). That works for One because the portal has one
language. Our one product has two apps in two languages. Python cannot read a TypeScript import,
and a list per app lets the two lists disagree: the pipeline omits the waiver board while the site
still renders its route. So the list is TOML that both apps read, in one place.

## The word "shell"

One names the thin source code of an app its shell (One ADR-0008). Our glossary already uses
**Shell** for the frame of each page. We keep our meaning, and we say **app** for the meaning of
One. The rule of One ADR-0008 holds: an app holds no rule of a domain.

## Rejected

- **A client folder per app.** Two lists per client, which can disagree.
- **A client folder with its own code.** Ten clients become ten shells that nobody keeps in step.
- **One site for each league, under a path.** Each build then carries each package and each brand,
  and a flag hides what a client omits.
