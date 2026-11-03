# 08: The site build that selects one client

Map: `.scratch/clients/MAP.md`.

**Kind:** prototype

**Blocked by:** 02, 07

**Status:** open

## Question

How does the Next.js build select one client from `client.toml`? A build with no client name fails, and a package not in the list is not in the bundle. Try two ways: a generated file of import lines, and an alias that points at the client folder. Show that the bundle of a client that omits a package holds none of its code. Then delete the prototype.

## Decision

None yet.
