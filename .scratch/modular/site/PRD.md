# Modular: typed loaders, parts that take data, and one home per helper

Status: ready-for-agent
Date: 2026-10-31
Repos: the site `cpcfantasyfootball`. The pipeline has its own `.scratch/modular/pipeline/PRD.md` for the same feature name. The two ship on their own.
Glossary: **Part**, **Primitive**, **Shell**, **Published file**, **Loader** in the site `GLOSSARY.md`. **Chapter**, **Tier**, **Masthead**, **Menu** as before.
ADRs: 0004 rules that a component takes data and returns markup. 0005 rules that the published shape has one owner.
Follows: `.scratch/manager-pages/site/PRD.md`. Closes its site tickets 12 and 13.

## Problem Statement

The site renders well, and every page is static. But the code follows pages, not shape.

The masthead reads the public folder through its default props. Six components build their own hrefs with
the base path. Two send the season in API bodies. The shared parts sit in the week folder, and every
other folder imports them from there. Nine images of a player or a team are built by hand. The record
string is inline in five places and copied in two tests. Three functions named `metaLine` do three
things. Three components each build the logic that aborts a request when the component unmounts.

Every loader checks a version number and then casts the JSON to a type with no check of the shape.
`TradeSide` has three definitions and `Team` two.

Brian wants the site as modular as it can be: parts that take data and return markup, one home per
helper, and typed loaders and API calls. A folder names a layer or a page, never a mix. Nothing on
the page may change.

## Solution

Every **loader** parses its **published file** with a Zod schema, and the types come from the schemas.
A test parses every file under the public folder. A shape change from the pipeline then fails the
site test and not just the version check. The API responses get schemas too.

The lib splits by kind: data for the loaders, schemas, format for the pure helpers, and one route
builder for every href. Components may import schemas, format, and routes. Only the app layer imports
data. A test over the component tree enforces the rule.

The shared **parts** move out of the week folder into their own folder, one file per part. One `Avatar`
and one `Headshot` replace the hand-rolled images. One `PlayerChapter` replaces best adds and top
performers. The loose top-level components move into an analyzer folder and a **shell** folder. The
fixtures move to one folder.

The format module gets a record helper and one `count`. Two hooks move to a hooks folder, and one new
hook holds the abort logic. We rename the type clashes.

The seam is the static export. Each ticket diffs the export against a build of `main`. A pure move
shows no diff.

## User Stories

1. As Brian, I want every loader to parse its file with a schema, so that a wrong shape fails the build with a clear message.
2. As Brian, I want the types inferred from the schemas, so that a type and its check always match.
3. As Brian, I want a test that parses every file under the public folder, so that a pipeline shape change fails the site test.
4. As Brian, I want the API responses parsed with schemas, so that the analyzer trusts the API as little as the loaders trust the files.
5. As Brian, I want the loaders in one folder, so that a reader knows what runs at build time.
6. As Brian, I want only the app layer to call a loader, so that a component never reads a file.
7. As Brian, I want the masthead to take its links as props, so that it no longer reads the public folder through defaults.
8. As Brian, I want the home page to get its data from the app layer, so that the page file is only layout.
9. As Brian, I want one route builder for every href, so that a link change touches one module.
10. As Brian, I want every component that builds an href to take it as a prop, so that a component knows no route.
11. As Brian, I want the season to come from the app layer, so that no component imports the config.
12. As Brian, I want a test over the component tree, so that a component that reads a file, reads the env, or imports the config fails the build.
13. As Brian, I want the shared parts in their own folder, so that the week folder holds only week chapters.
14. As Brian, I want one file per part, so that a part has one job and one name.
15. As Brian, I want one `Avatar`, so that twelve team images built by hand become one part with a size.
16. As Brian, I want one `Headshot`, so that seven player images built by hand become one part with the fallback swap.
17. As Brian, I want one `PlayerChapter`, so that best adds and top performers share one body.
18. As Brian, I want the analyzer components in one folder, so that the top level holds no loose files.
19. As Brian, I want the shell components in one folder, so that the masthead, the menu, the compact bar, and the theme button sit together.
20. As Brian, I want the fixtures in one folder, so that a test finds its data in one place.
21. As Brian, I want a record helper, so that five inline strings and two test copies become one function.
22. As Brian, I want one `count`, so that two helpers with the same job have one home.
23. As Brian, I want `oneDecimal` in the format module, so that the manager parts format like the week parts.
24. As Brian, I want the standings points to go through the shared number format, so that every points value formats the same way.
25. As Brian, I want each `metaLine` to carry a name that says what it builds, so that each of three functions has its own name.
26. As Brian, I want the motion and hydration hooks in a hooks folder, so that a hook has one home.
27. As Brian, I want one request hook, so that three copies of the abort logic become one.
28. As Brian, I want the type clashes renamed, so that `Pick` and `Destination` each mean one thing.
29. As Brian, I want one team type per published file, so that a week team and a manager team stay distinct by schema.
30. As Brian, I want a helper to stay beside its one caller, so that no `utils` file grows.
31. As Brian, I want each ticket to diff the export against `main`, so that a pure move proves itself with no diff.
32. As Brian, I want the export check to pass after every ticket, so that the deploy never breaks.
33. As Brian, I want every published shape unchanged, so that the pipeline needs no release for this feature.
34. As an agent, I want the component rule in a test, so that I know the rule without a question.
35. As an agent, I want the fixtures typed by the schemas, so that a stale fixture fails at compile time.
36. As a reader of the site, I want the page to look the same after this feature, so that I never know it happened.

## Implementation Decisions

- Add Zod. Each of the four loaders parses its file with a schema. The type files become inferred exports from the schemas. The version check stays as the first check. Its message stays clear.
- The API client parses the responses of the teams, analyze, and find calls with schemas.
- The lib splits into four: data for the build-time loaders, schemas for the Zod schemas and inferred types, format for the pure helpers, and one routes module. The browser-only modules such as the passphrase, the teams store, the theme, and the usage stay where they are.
- The routes module exports a builder per destination: home, rankings, analyze, week, waiver, managers, and one manager. Each has the base path inside. The app layer calls them and passes hrefs down.
- Components may import schemas, format, and routes. Only the app layer imports data and the config. A test reads every file under the component tree. It fails when a file imports the node fs, the config module, or a data loader, or reads the process env.
- The masthead takes its week summaries and its links as required props. The home page and the layout get their data in the app layer.
- The two components that send the season in an API body take it as a prop from the app layer.
- Component folders go by layer or page. The ui folder stays the primitive layer. A parts folder holds every shared part, one file each. The parts now: chapter, label, tag, blurb, avatar, team name, who, headshot. The parts later: player row, points line, grade popover, swap strip. The page folders keep only the chapters one page owns. An analyzer folder and a shell folder take the loose top-level files.
- The avatar lookup by roster id moves beside the avatar helper in lib.
- `Avatar` and `Headshot` are client parts with the fallback swap on error and a size prop. Every image built by hand calls them. The managers player headshot moves into the headshot part.
- `PlayerChapter` takes an id, a title, an empty text, and the items. Best adds and top performers call it.
- The format module gains `record(wins, losses)`, `oneDecimal`, and one `count(n, one, many)`. The standings points go through `num`. The three `metaLine` functions stay local with names that say what each builds.
- The hooks folder holds the motion hook, the hydration hook, and a new request hook. The request hook holds the run id, the abort controller, and the unmounted guard. The focus on open and the open state stay inline.
- Type clashes: the trade form `Pick` becomes `PlayerPick`, and the trade side `Destination` becomes `SideChoice`. The analyzer `TradeSide` type and the week `TradeSide` type stay distinct, because they come from different schemas. No merge of shapes across files.
- The analyzer components move into the analyzer folder. They lose the duplicate type. They take hrefs as props. Do not split them by job.
- Fixtures move to one fixtures folder. The schemas type them.
- Every `schema_version` stays as it is.
- Extract a helper on its second use. No `utils`, `helpers`, or `common`.
- No catalog route in this feature.

## Testing Decisions

- A good test renders a part with data and reads the markup. Or it parses a file with a schema and reads the result. It never reads a class name, a private function, or a module's internals. The component rule test is the one exception, and it reads only import lines.
- The seam is the static export. Each ticket runs `pnpm build` on `main` and on the branch. It then diffs the two export folders. A pure move shows no diff. A ticket that changes markup on purpose names the pages that differ. `pnpm check:export` passes after every ticket.
- The schema test parses every file under the public folder with its schema. It lives beside the loaders.
- The component rule test reads every file under the component tree. It lives beside the other tree-level tests.
- The existing vitest tests stay. A test that copies a format string moves to the helper.
- Prior art: the page tests that render a route with a fixture, the reduced-motion test that reads the managers fixture, and the export check script.
- `pnpm typecheck` and `pnpm test` run before each merge.

## Out of Scope

- A league segment in any route or path.
- Any fetch of live data in the browser beyond the analyzer calls that exist today.
- A catalog route.
- A split of the trade form, the trade side, or the analyze result by job.
- A merge of the team or player shapes across published files.
- An npm package, a monorepo, or generic props.
- Any change to a published shape or a `schema_version`.
- Any change to the rendered markup, except where a ticket names it.

## Further Notes

- Commit every change before you publish. The publish step stages every file on `main`.
- Build in a scratchpad worktree. Merge from the main checkout with `--no-ff`. Get two reviews before each merge.
- Write every comment and commit in Simplified Technical English. Write labels in Title Case. No test reads a class name. Put a two-line docstring at the top of a file.
- The pipeline has a second PRD under the same feature name. The two share only the shape-owner ADR.
