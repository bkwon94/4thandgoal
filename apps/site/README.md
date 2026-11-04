# Cornerstone League Weekly

The Cornerstone League Weekly site, at cpcfantasy.com. This repo holds the Next.js source. The
Python pipeline in `apps/pipeline` publishes each week's `page.json` and images into `clients/<slug>/published/`. The build
copies the published data of one client into `public/`. The site renders every page, the home page included, from that JSON.

## Install

Use Node 22 or newer. The `.nvmrc` pins 22.

```
pnpm install
```

Install the commit hook one time per clone with `prek install`, or `pnpm hook:install`. Each worktree then reads its own branch's `.pre-commit-config.yaml`.

## Run

```
CLIENT=cpc pnpm dev
```

## Build and export

`pnpm build` writes the static export of one client to `out/`. The export has trailing slashes and no server.
The env value `CLIENT` names the client folder under `clients/`. A build with no `CLIENT` fails.

```
CLIENT=cpc pnpm build
CLIENT=cpc pnpm check:export
```

The `prebuild` step runs `scripts/client-build.mjs`. It checks `clients/$CLIENT/client.toml` against the JSON Schema
that the pipeline exports, with `ajv`. Then it writes the route file of each package of the client, the registry,
and the client values, and copies the client's `published/` into `public/`. Git ignores each generated file.

`pnpm check:export` runs after the build. It checks that every file under `public/` exists in
`out/` with the same bytes, and that the export holds no route and no code of a package that the client omits.
It exits 1 and names the first mismatch. `pnpm check` builds and checks each client under `clients/`.

To look at the export, serve `out/`:

```
python3 -m http.server --directory out
```

## Test

```
pnpm test
pnpm typecheck
```

`pnpm check` runs typecheck, test, build, and `check:export`. CI runs it on every push. `pnpm check:fast` runs typecheck and test. The commit hook runs it. The hook does not run `pnpm install`. If the hook fails in a worktree with no `node_modules`, run `pnpm install`.

## Schema version

The week pages read `page.json` at schema version 2. The build fails loud on any other version.
Ship the reader of the site for a new version before the pipeline bumps the version.

## Config

All values are build-time. Only `src/lib/config.ts` reads them.

| Variable | Default | Meaning |
| --- | --- | --- |
| `NEXT_PUBLIC_API_URL` | `https://api.cpcfantasy.com` | Base URL of the site API. |
| `NEXT_PUBLIC_BASE_PATH` | empty string | Pages base path. Empty because the site lives at the domain root. |
| `CLIENT` | none | The slug of the client folder under `clients/`. The build fails with no value. |

A value that changes with the league comes from `client.toml`: the package list, the finder, the usage code, and the
season, which is the latest season of the client.

## Deploy

A push to `main` builds the site and deploys it. The workflow is `.github/workflows/deploy.yml`.
It installs the packages and runs `pnpm check`. That script checks the types, runs the tests, builds the export,
and checks the export. A failed step stops the deploy.

The Pages source is GitHub Actions. The `CNAME` file in `public/` keeps the custom domain.

The Python publish in `apps/pipeline` writes the week folder, with `page.json` and the images, into `clients/cpc/published/` and pushes to
`main`. That push starts the deploy.
