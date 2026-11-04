# 08: The site build that selects one client

Map: `.scratch/clients/MAP.md`.

**Kind:** prototype

**Blocked by:** 02, 07

**Status:** done

## Question

How does the Next.js build select one client from `client.toml`? A build with no client name fails, and a package not in the list is not in the bundle. Try two ways: a generated file of import lines, and an alias that points at the client folder. Show that the bundle of a client that omits a package holds none of its code. Then delete the prototype.

## Decision

Brian decided each item on 2026-11-04, from a throwaway workspace on Next 16.4.5 with Turbopack and a static export. The workspace held the clients `cpc`, with `week`, and `norcal`, with `week` and `waiver`. It built each client two ways. The prototype is deleted.

### What the prototype showed

| Test | Generated file of imports | Alias, with route files in git |
| --- | --- | --- |
| A build with no `CLIENT` fails with a plain message | Yes | Yes |
| The `cpc` export has no waiver route and no waiver code | Yes | Yes |
| The `norcal` export has `/waiver/` and the site name "NorCal Apex 6" | Yes | Yes |
| A shared page imports a client component of `waiver` | No leak: the `cpc` registry has no import line for it | Leak: the `cpc` export holds the waiver JS |

The alias way leaked under a runtime guard and under a compile-time `env` constant. A server component did not leak in either way, because its code runs at build time only. The chapter port of the week and the menu are shared parts, so only a generated import list keeps an omitted package out of the bundle.

Three smaller findings:

- Each package with TSX lists `react` as a peer dependency and `@types/react` as a dev dependency. Without them, the type check fails in the strict `node_modules` of pnpm.
- Turbopack does not resolve a file outside the app unless `turbopack.root` is the repo root. The generated way copies the client values and data into the app, so it needs no such import.
- An empty generated list needs an explicit type, or the type check fails for a client with no chapters.

### The decision

1. **The site build generates its imports from `client.toml`.** A `prebuild` script reads `clients/$CLIENT/client.toml`. It writes one route file per package, one registry of import lines for the chapters and the menu, and the client values. It copies only that client's published data into `public/`. The `pageExtensions` gate goes away.
2. **The generated files stay out of git.** Each one starts with a `GENERATED ... Do not edit.` line, and `.gitignore` lists each one.
3. **The check builds each client in `clients/`.** A change to a shared part then cannot break a second client unseen. Each build costs about 30 seconds in CI. The fast hook builds `cpc` only.
4. **The env value is `CLIENT`.** It holds the client slug. A build with no `CLIENT` fails.
