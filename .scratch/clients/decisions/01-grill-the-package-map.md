# 01: The package map

Map: `.scratch/clients/MAP.md`.

**Kind:** grill

**Blocked by:** none

**Status:** done

## Question

Which domains become packages? The pipeline has about 60 flat modules in `apps/pipeline/src/cornerstone/`, and the site has its parts in `apps/site/src/components/`. Each package holds one domain in both languages (ADR 0023). The spec needs the list of packages, the module and the part that each one takes, and the name of the design-system package. A package is a word the league uses, not a technical shape. Survey the code before the grill, so each question rests on facts.

## Decision

Brian decided each item in the grill of 2026-11-03. The map follows domain-driven design: a package is a bounded context.

### The rules

1. A term belongs to one package. If two packages use it, it goes into the league package, or one package publishes it to the other.
2. The league package stays small. A rule of one package does not go into it only because another package imports it.
3. Every outside service enters through the league package: Sleeper, nflverse, the trade value chart, and Claude.
4. Each package writes its own published file, and its site side reads that file with its own schema (ADR 0011).
5. Each package owns its own `tunables` module. The numbers that three or more packages read go into the league package.

### The packages

| Package | DDD role | Python | Site |
| --- | --- | --- | --- |
| `league` | Shared kernel | `models`, `parse`, `provider/`, `config`, `paths`, `files`, `numbers`, `player_ids`, `history`, `nflverse*`, `slow_sources`, `points_allowed`, `snapshot`, `live`, `season_inputs`, `standings_table`, `trades`, `ranks`, `chart`, `claude_port`, `claude_errors`, the lineup from `adjusters`, `head_to_head` from `facts_league`, the shared tunables | `headshot`, `avatar` |
| `facts` | Generic subdomain | the fact tokens from `sheet/base.py`, `writer`, `verifier`, `names` | none |
| `week` | Core | `sheet/*` except the rankings chapter, the rest of `facts_league`, `facts_matchup`, `facts_nflverse`, the page writer, the chapter port | `components/week/`, its data, schema, and types |
| `rankings` | Core | `power_rankings`, `odds`, `sheet/rankings.py` as its chapter, the rankings file writer | `components/rankings/`, its data, schema, and types |
| `managers` | Core | `managers`, `manager_*`, the managers file writer | `components/managers/`, its data, schema, and types |
| `waiver` | Core | `waiver*`, `rank_score`, the waiver file writer | `components/waiver/`, its data, schema, and types |
| `analyzer` | Core | `rubric`, the criteria and `Side` from `adjusters`, `analysis`, `trade_facts`, `finder`, `finder_reasons`, the analyzer routes of the API | `components/analyzer/`, `api`, `passphrase`, `teams-store`, `team-pick` |
| `design` | Presentation | none | `components/ui/`, `parts/`, `shell/`, `theme`, `motion`, `format/`, `utils` |

The dependency order is `league`, then `facts`, then the five core packages. `design` sits under each site side. Each client takes `league`, `facts`, and `design`.

### The choices and the reasons

- **The kernel is `league`, not `core`.** A package name is a word the league uses. `core` names a shape and has no edge.
- **The shell goes into `design`.** Three menu layouts are code that each client needs. In the app, they break the App term. As a package, they give no choice.
- **`design` is the one name that is not a league word.** The package holds no rule of the league. ADR 0023 records the exception.
- **`facts` is its own package.** In `league`, the kernel holds two ideas. In `week`, the waiver board and the analyzer depend on the week.
- **The lineup moves into `league`.** The waiver board, the managers, and the week import only the lineup from `adjusters`, not the trade criteria.
- **The week defines a chapter port.** The rankings gives its chapter through it. A client that omits the rankings gets a week with no rankings chapter.
- **The analyzer holds the finder.** The finder calls the rubric, so a separate package cannot stand alone. `trades` is the kernel word for a Sleeper transaction.
- **The chart and the Claude port go into `league`.** The kernel snapshot holds the chart, and two packages read it. The chart read needs Claude, and the kernel cannot import from `facts`.
- **Claude gets no package.** It is a port with no league rule, and no client can omit it. A second AI service is a second adapter behind the Writer port.
- **Each package writes its own file.** One spec of a package then touches one folder.

### Left for other tickets

- `cornerstone_api` lives in `apps/pipeline/` today, but the glossary calls the API its own app. Decision 07 decides its folder.
- `config.py` is the League config, which `client.toml` replaces. Decision 02 decides its shape.
- `lib/usage.ts` has no home yet. The spec places it after a read of the file.
- If the README sentence of `league` stops being true, split the outside services into a second kernel package. The four services make it the first package to watch.
