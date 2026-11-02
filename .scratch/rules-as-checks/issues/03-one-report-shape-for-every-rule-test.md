# 03: One report shape for every rule test

Spec: `.scratch/rules-as-checks/PRD.md`, part 4 and "The report shape". One 0013, "The report of an offense".

**What to build:** A small helper in `src/rule-report.ts` prints each offense in the house shape. The two
rule tests of today, `src/component-rule.test.ts` and `src/lib/data/published-files.test.ts`, change to it.
Tickets 02 and 04 use it for their rules. The pipeline's `tests/test_layers.py` is the model.

**Blocked by:** 01 (ADR 0006).

**Status:** ready-for-agent

- [x] The exact shape, one offense:

```text
src/components/week/standings.tsx:4  components/no-loader
  standings.tsx imports @/lib/data/week-data.
  Rule: a component takes data and returns markup (docs/adr/0004-a-component-takes-data-and-returns-markup.md).
  Fix: call the loader in src/app/ and pass the value to the component as a prop.
```

- [x] Line 1: the path from the repo root, a colon, the line, two spaces, the rule id. Lines 2 to 4 start with two spaces.
- [x] `src/rule-report.ts` exports a type `Offense` with `path`, `line`, `ruleId`, `what`, `rule`, `adr`, `fix`, and a function `report(offenses)`. It starts with the count, such as "2 offenses.", then each offense, with a blank line between.
- [x] Choice: the helper sits in `src/` beside the rule tests. It imports no app code, so the build never bundles it.
- [x] Choice: the rule id is `<topic>/<name>`. The topics: `components`, `published`, `suppression`, `readme`.
- [x] `component-rule.test.ts` ids: `components/no-fs`, `components/no-config`, `components/no-loader`, `components/no-env`. ADR 0004. Each has a fix sentence.
- [x] `published-files.test.ts` id: `published/shape`. ADR `docs/adr/0005-the-published-shape-has-one-owner.md`. The fix: "Change the schema in src/lib/schemas/ and the pipeline's writer together, or republish the file."
- [x] Choice: a JSON parse gives no line, so a `published/shape` location is the file and the field path, such as `public/2026/week-07/page.json:games.0.byes`. Line 2 holds the Zod message.
- [x] Both tests still find at least one file, as today, so an empty tree cannot pass.
- [x] A test of the helper compares `report` of one offense with the text above, byte for byte.
- [x] A test runs the component rule on one source string that imports `@/lib/data/week-data`, and reads one `components/no-loader` offense with line 1.
- [ ] `docs/adr/0006-the-rules-are-checks.md` gains "The report of an offense", with the example above.
- [ ] `pnpm check` passes.
