# 04: A README in each package folder

Spec: `.scratch/rules-as-checks/PRD.md`, part 5. One 0001 and 0007.

**What to build:** Each package folder holds a `README.md` with three headings: Knows, Ports, Does not do.
`src/readme-rule.test.ts` fails on a package folder with no README, a missing heading, 25 lines or more,
or a tracked `CLAUDE.md` other than the root one.

**Blocked by:** 03 (the report shape and its helper).

**Status:** ready-for-agent

- [x] A package folder is each folder directly under `src/components/` and under `src/lib/`, plus `src/lib/` and `src/hooks/`. Today that is 13 folders.
- [x] The list: `components/analyzer`, `managers`, `parts`, `rankings`, `shell`, `ui`, `waiver`, `week`; `lib`, `lib/data`, `lib/format`, `lib/schemas`; `hooks`.
- [x] Choice: the rule finds the folders. It does not hold a list, so a new folder needs a README on its first day. The PRD named seven of the 13. The other six follow from the rule.
- [x] Choice: `src/app/` gets no README. It is the app layer, and One 0007 says an app needs none. `src/pages/` holds only the 404 page. `src/fixtures/` holds test data.
- [x] The headings are exactly `## Knows`, `## Ports`, and `## Does not do`, in that order. A folder with no port writes "None." under Ports.
- [x] **Knows**: what the folder knows, in the terms of `GLOSSARY.md`. Do not define a term again.
- [x] **Ports**: the outside systems the folder reaches. `lib/` lists the API client in `lib/api.ts`. `lib/data/` lists the reads of `public/`.
- [x] **Does not do**: the lines that let an agent stop the search. For example, a component folder reads no file and builds no route (ADR 0004). `lib/schemas/` owns no shape, because the pipeline owns it (ADR 0005). `ui/` knows no league term.
- [x] Each README is under 25 lines, in STE.
- [x] Rule ids: `readme/missing`, `readme/headings`, `readme/length`, `readme/no-claude-md`. ADR: `docs/adr/0006-the-rules-are-checks.md`.
- [x] The `CLAUDE.md` rule reads `git ls-files`, so `node_modules` does not count. One 0007 says why: a nested `CLAUDE.md` loads by itself, and the agent must choose to read.
- [x] A test runs the rule on a temporary folder with one source file and no README, and finds one offense.
- [x] `docs/adr/0006-the-rules-are-checks.md` gains "A README in each package folder".
- [x] `pnpm check` passes. `pnpm check:export` still passes, because no README lands in `public/`.
