# packages/design: the primitives, the parts, and the shell of each client site

## Knows

- The shadcn primitives in `site/ui/`, the shared parts in `site/parts/`, and the shell in `site/shell/`.
- The three menu layouts of the shell: `hamburger`, `bar`, and `tabs`.
- The theme store and its boot script, the motion timings and hooks, the pure number formats, and the `cn` helper.
- The usage count: the count script tag and the event call.
- It holds no rule of the league. It is the one package name that is not a league word (ADR 0023).

## Ports

- The theme choice in local storage, through `site/lib/theme.ts`.
- GoatCounter, through `site/lib/usage.ts`.

## Does not do

- It reads no file, no env, and no config. The app passes each value as a prop (ADR 0012).
- It imports nothing from an app. Each app and each package imports it, through `@cpc/design/<folder>/<file>`.
- It builds no menu link. The app builds the destinations from `[menu]` of `client.toml`.
- It holds no Python. The site build compiles its TSX source, so it has no build step.
