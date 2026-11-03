# 02: No suppression comments

Spec: `.scratch/rules-as-checks/site/PRD.md`, part 3 and "The allow list is the one departure from One". One 0013.

**What to build:** `src/suppression-rule.test.ts` fails on any suppression comment in the site code. The
site has none today, so the test is a guard from the first day. The allow list starts empty.

**Blocked by:** 03 (the report shape and its helper).

**Status:** done

- [x] Rule id `suppression/comment`. Rule sentence: "no comment silences a rule".
- [x] Choice: the ticket gave two sentences for the rule and two for the fix. ADR 0016 gives one sentence each, so the one-sentence form won.
- [x] The test reads every `.ts`, `.tsx`, `.js`, and `.mjs` file under `src/` and `scripts/`, and the config files at the root: `next.config.ts`, `vitest.config.ts`, `postcss.config.mjs`.
- [x] It matches `@ts-expect-error`, `@ts-ignore`, `@ts-nocheck`, and `eslint-disable`.
- [x] Choice: `@ts-nocheck` is in the list. It silences a whole file, so it is the widest suppression.
- [x] Choice: the test builds each pattern from two parts, such as `"@ts-" + "ignore"`. The test file then holds no match. Never skip the test's own file: One rejects a file exclusion.
- [x] `grep -rn "@ts-\|eslint-disable" src` finds 0 lines today. The site has no ESLint, so an `eslint-disable` line would silence nothing.
- [x] The allow list is a `Map` in the test: the key is the path and the line text, and the value is the reason. It is empty. Its comment says it is the only place a suppression may live.
- [x] Choice: the key holds the line text, not the line number, so the entry does not go stale when a line above it moves.
- [x] An allow list entry with no match fails the test, so a stale entry cannot stay. It prints the report shape with the rule id `suppression/stale-allow`.
- [x] Each offense prints the report shape of ticket 03, with the fix: "fix the type or the code, or add the line to the allow list of this test with its reason."
- [x] A test runs the rule on one source string with a `@ts-ignore` line and finds one offense.
- [x] `docs/adr/0016-the-rules-are-checks.md` gains "No suppression comment": the rule, the allow list, and why this departs from One.
- [x] `pnpm check` passes.

## Comments

- 2026-11-02: merged into `main` from branch `rules-as-checks-02-no-suppression`, commits d5c8f67, 0191261, b7371cc, and 95cb2fb, with `--no-ff`. 552 tests pass, `pnpm check` green. The site has no suppression line, so the allow list is empty. A stale allow list entry prints in the report shape as `suppression/stale-allow`. The rule and the fix are one sentence each, as ADR 0016 asks; the ticket text had two. The PRD sentence about the allow list is corrected: the pipeline list starts with its five `noqa` lines, because ruff 0.17.3 enables BLE001 and RUF009 by default. Two reviewers passed it after one fix pass. Read 11 files: .scratch/rules-as-checks/site/issues/02-no-suppression-comments.md, .scratch/rules-as-checks/site/PRD.md, src/component-rule.test.ts, src/rule-report.ts, src/rule-report.test.ts, docs/adr/0016-the-rules-are-checks.md, tsconfig.json, vitest.config.ts, package.json, ~/repos/zero/docs/adr/0013-the-rules-are-checks.md, src/suppression-rule.test.ts.
