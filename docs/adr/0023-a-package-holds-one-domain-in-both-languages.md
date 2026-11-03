# A package holds one domain in both languages

A package is one domain of the league, such as the waiver board or the rankings. It lives at
`packages/<domain>/` and holds each part of that domain: the Python that computes it, the React that
renders it, and the README with the headings Knows, Ports, and Does not do. This follows One
ADR-0001.

```
packages/waiver/
  python/    the buckets, the price, the drops: it writes the waiver board
  site/      the route screen and the parts that render the board
  README.md
```

A client takes a package or omits it as a whole, with one line of `client.toml` (ADR 0022). The
parts and the primitives that each package uses sit in one design-system package. The published
file stays the seam between the two languages, and the pipeline owns its shape (ADR 0011).

## Why

The goal is that a client can take any feature or omit it. With one package per domain, that is one
choice per feature, in one line, and one spec of a feature touches one folder.

## The cost

`uv` and `pnpm` must each find their code under `packages/`, and the check must run each language
for each package. We pay that cost one time.

## Rejected

- **A package per app**, such as `apps/pipeline/packages/waiver/` and `apps/site/packages/waiver/`.
  Each app keeps one toolchain, but a client lists each feature two times.
