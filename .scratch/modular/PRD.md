# Modular: one config, typed edges, six layers, and a sheet in chapters

Status: ready-for-agent
Date: 2026-10-31
Repos: the pipeline `cornerstone-fantasy-sleeper-weekly-report`. The site has its own `.scratch/modular/PRD.md` for the same feature name. The two ship on separate schedules.
Glossary: **League config**, **Provider**, **Bundle**, **Published file** in the pipeline `GLOSSARY.md`. **Fact**, **Fact sheet**, **Chapter** as before.
ADRs: 0007 rules the six layers and the import direction. 0008 rules that the pipeline owns the published shape.
Follows: `.scratch/manager-pages/PRD.md`. This PRD closes pipeline ticket 14. It also closes the handoff items for atomic writes and `ruff`.

## Problem Statement

The pipeline works, and every week it builds a page. But the code follows features, not shape. The
orchestrator holds the league id. A default argument holds the owner's username. Five modules name
the timezone. The tunables hold the twelve-team numbers, with comments. Raw Sleeper data travels as
`dict` from the HTTP call to the parser.

The sheet is one module of 1,787 lines. It is both the base every fact module imports and the
assembly of every chapter. One direct import cycle and two indirect ones exist. The model module
imports a logic module. A library module imports the orchestrator. Three round functions exist, and
nine copies of the week label. No test compares a whole built file. A refactor has no proof that
nothing moved.

Brian wants a modular pipeline. It needs one config, typed inputs, named layers, one job per module,
and one module per shared function. Nothing on the page may change.

## Solution

The entry points build one **league config** object in Python and pass it down as a parameter.
It holds the slug, the display name, the provider, the provider id per season, the owner's username, the
timezone, the league-sized limits, and the prompts folder. The passphrase stays in the env.

The **provider** gets a protocol with five methods and one implementation, Sleeper. The raw shapes become
pydantic models at the HTTP call, and the parser reads those. Sleeper field names stay in the adapter.

The sheet becomes a package: a base with the shared pieces, one module per chapter with one function of
one shape, and an assembly. Every module outside the sheet imports only the base.

Each shared function gets one module: one for the round functions and plurals, one for every
directory and label. No behavior changes. The three cycles break. We name six layers. A test over the
import graph fails any upward import.

Four golden files from the week 6 fixtures fix the output before the first code change. Every ticket
checks its work against them.

## User Stories

1. As Brian, I want one object that names the league, so that a league constant has one module.
2. As Brian, I want the config passed as a parameter, so that a test can run with a different league in one line.
3. As Brian, I want the owner's username in the config, so that `is_brian` is not a field name.
4. As Brian, I want the timezone in the config, so that five modules do not each name it.
5. As Brian, I want the twelve-team numbers in the config, so that the tunables hold only algorithm settings.
6. As Brian, I want the raw Sleeper data typed at the HTTP call, so that a wrong field name fails at parse time, not in a fact.
7. As Brian, I want a provider protocol, so that the fake fetcher in the tests and Sleeper share one contract.
8. As Brian, I want the fixtures to load through the raw models, so that the contract test needs no extra work.
9. As Brian, I want Sleeper field names to stay in the adapter, so that the rest of the pipeline reads only the models.
10. As Brian, I want the sheet split by chapter, so that a change to one chapter touches one module.
11. As Brian, I want every chapter to be one function of one shape, so that a new chapter copies a form and not a file.
12. As Brian, I want the sheet base in one module, so that the waiver and the verifier import a base and not an assembly.
13. As Brian, I want one module for the round functions, so that a number formats the same way from every chapter.
14. As Brian, I want no rounding behavior to change in this feature, so that the golden files stay green.
15. As Brian, I want one module for every directory and label, so that a layout change touches one module.
16. As Brian, I want the waiver cycle broken, so that the import graph is a tree.
17. As Brian, I want the model module to import no logic module, so that the layers hold.
18. As Brian, I want the live module to import nothing from the orchestrator, so that the API does not depend on the orchestrator.
19. As Brian, I want the API to import nothing from the render module, so that the API imports no page code.
20. As Brian, I want six named layers, so that a reader knows where a module belongs.
21. As Brian, I want a test over the import graph, so that an upward import fails the build and not the review.
22. As Brian, I want the season inputs built once, so that the raw week loads once and not three times.
23. As Brian, I want the tuple of four through the grade to be one object, so that a new input touches one signature.
24. As Brian, I want the projections ahead to have a name, so that six signatures share one named type.
25. As Brian, I want four golden files from the week 6 fixtures, so that a refactor proves nothing moved.
26. As Brian, I want a `make golden` target, so that a change on purpose rewrites the files and shows in review.
27. As Brian, I want the golden page built with template blurbs, so that the golden test makes no Claude call.
28. As Brian, I want atomic writes in history and render, so that a killed build leaves no half file.
29. As Brian, I want `ruff` pinned in the development dependencies, so that lint runs the same version on every machine.
30. As Brian, I want `pyright` in basic mode with a make target, so that the pipeline has a type check like the site.
31. As Brian, I want every published shape unchanged, so that the site needs no release for this feature.
32. As Brian, I want nothing merged before the week 8 build, so that the Tuesday build runs from a known `main`.
33. As an agent, I want each ticket to name its golden check, so that I know when I am done.
34. As an agent, I want the layer map in a test, so that I can place a new module without a question.
35. As a reader of the site, I want the page to look the same after this feature, so that I never know it happened.

## Implementation Decisions

- A config module builds the config as a frozen pydantic model from literals. This feature adds no TOML file. A second league turns the literals into a file then.
- The config holds the identity: the slug, the display name, the provider name, and the provider league id per season. It holds the owner's username, the timezone, and the prompts folder. It holds the league-sized limits: the playoff spots, the bye count, the last regular and season weeks, the return-by week, the star and line ranks, the strength rank, and the seller gap.
- The API settings read the passphrase from the environment, as today.
- The config is a parameter. The CLI and the API entry build it once and pass it down. No module reads a global.
- The tunables keep the algorithm settings: the trade bands, the simulation runs, the weights, the waiver sizes, and the API limits. A number moves to the config only if it would change with a different league.
- The provider package has a base module with a protocol of five methods: fetch the week, fetch live, fetch a past leg, fetch the players, fetch the projections. The Sleeper module implements it. The no-network fetcher in the test conftest satisfies it.
- The raw Sleeper shapes are pydantic models in the Sleeper module, such as a raw roster, a raw matchup, a raw user, a raw transaction. The parser takes the models. The fixture raw files load through them.
- The models module keeps `roster_id` as the team key, because every published file and the manager route use it. `is_brian` becomes `is_owner`. `owner_id` and `matchup_id` stay. No published file changes a field name.
- The sheet becomes a package: a base module with `Nums`, `fact`, `fmt`, `Context`, and the tokens; one module per chapter; an assembly module with `chapters` and `build_bundle`. The package re-exports the names callers use today. No caller changes in the split ticket.
- Each chapter module exports one function, `facts(bundle, config)`, that returns a list of facts. It reads no file, no environment variable, and no global. The league facts and the trade facts modules move under the sheet as chapters of the same shape.
- One numbers module in the model layer holds `r2`, `round_half_up`, `one_decimal`, `ordinal`, and `plural`. The three round functions keep their behavior and names, each with a comment that says when to use it.
- One paths module in the model layer holds `week_label`, `week_dir`, `raw_dir`, `history_dir`, `site_week_dir`, `season_dir`, and the chart paths. The config and the repo root build them.
- Cycles: the odds result model moves into the model module. The league id and the nflverse cache directory leave the orchestrator. The live module then no longer imports it. The two waiver modules get a shared third module. The two indirect cycles stay until the layer test flags them.
- The API no longer imports render. The headshot URL and the defense check move into a model-layer module beside the player models.
- Six layers: model, provider, load, facts, write, output. The model layer is lowest because the provider returns the models. The layer test holds the map as a dict of module name to layer. It fails on any import from a higher layer. The API imports model, load, facts, and write. In this feature the map is a test, not a folder move.
- A frozen `SeasonInputs` dataclass holds the snapshot, the projections ahead, the history, and the chart. The build saves the week. Then it makes `SeasonInputs` once and passes it to the rankings and the managers writers. `ProjectionsAhead` is a type alias for the dict shape and nothing more.
- History and render use the atomic write helper.
- Pin `ruff` in the development dependencies. `pyright` runs in basic mode with a make target. Only the modules a ticket touches must pass.
- Every `schema_version` stays as it is.
- Extract a helper on its second use. It stays beside its one caller until a second caller appears. No `utils` module.

## Testing Decisions

- A good test reads a built file or calls a public function. It compares the output. It never reads a private name or a module's internals. The import-graph test is the one exception. It reads only module names.
- The seam is `run_build` over the week 6 fixtures with the template fallback and the no-network fetcher. Four golden files under the fixtures lock `facts.json`, `page.json`, `rankings.json`, and `managers.json`. One test per file compares bytes. `make golden` rewrites them.
- The golden tests are the first ticket. Merge no code change before they are green on `main`.
- The layer test reads the import graph of the package and the API. It fails on an upward import. It lives beside the other tree-level tests.
- The fake fetcher in the conftest must satisfy the provider protocol.
- The fixture raw files must load through the raw models.
- Prior art: the pipeline tests that build from the fixture raw dir and history root through the conftest, the render tests that read a written page, and the CLI tests that run a build with a fake Claude call.
- Run the full suite before each merge. It takes about 3 minutes. It must show 1,455 or more tests.

## Out of Scope

- A league segment in any path or route. Every directory layout stays as it is. One module builds every path.
- API tenancy, a passphrase per league, or caches keyed by league.
- Live chapters, a publish route on the API, or any change to what the API serves.
- A second league, a second provider, or ESPN.
- A TOML config file.
- A change to any rounding behavior.
- The adjusters module. Do not split it.
- The overlap between the CLI and the API in as-of lines, team lists, and analysis output.
- Folders that match the six layers. Do not move files between folders.
- Any change to a published shape or a `schema_version`.

## Further Notes

- The week 8 build runs Tuesday 2026-11-03 at 08:00 ET from `main`. Nothing from this feature merges before it.
- Build in a scratchpad worktree. Merge from the main checkout with `--no-ff`. Get two reviews before each merge.
- Write every comment, docstring, and commit in Simplified Technical English. Never remove a comment unless it is false. Make the smallest change.
- The site has a matching PRD under the same feature name. The two share only the shape-owner ADR.
