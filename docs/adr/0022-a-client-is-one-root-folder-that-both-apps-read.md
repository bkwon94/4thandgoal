# A client is one root folder that both apps read

A client is one league and its site. Each client has one folder at the root, `clients/<slug>/`, and
its file `client.toml` holds the package list and the values of the client. The pipeline, the API,
and the site build all read the same file. The client folder holds values and no code.

```
clients/cpc/
  client.toml   the league, the provider per season, the package list, the values, the menu
  theme.css     the token values of the brand
  copy.toml     the site name, the masthead text, the tagline
  prompts/      the voice of the writer for this league
  assets/       the logo, the favicon, the fonts
  published/    the published files, by season and week
```

Each client builds its own site at its own URL. A build with no client name fails, so no default
client exists. The site build copies only the published files of its client. The API is one deploy
for each client, with the client in the path.

`client.toml` replaces the League config. A client chooses at two levels: the packages in its list,
and the values that each package names in its README. A client does not choose a part.

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
