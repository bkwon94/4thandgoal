# 02: No suppression comments

Spec: `.scratch/rules-as-checks/PRD.md`, part 3 and "The allow list is the one departure from One". One 0013.

**What to build:** `src/suppression-rule.test.ts` fails on any suppression comment in the site code. The
site has none today, so the test is a guard from the first day. The allow list starts empty.

**Blocked by:** 03 (the report shape and its helper).

**Status:** ready-for-agent

- [x] Rule id `suppression/comment`. Rule sentence: "No comment silences a rule. A line that must stay goes in the allow list of this test, with its reason."
- [x] The test reads every `.ts`, `.tsx`, `.js`, and `.mjs` file under `src/` and `scripts/`, and the config files at the root: `next.config.ts`, `vitest.config.ts`, `postcss.config.mjs`.
- [x] It matches `@ts-expect-error`, `@ts-ignore`, `@ts-nocheck`, and `eslint-disable`.
- [x] Choice: `@ts-nocheck` is in the list. It silences a whole file, so it is the widest suppression.
- [x] Choice: the test builds each pattern from two parts, such as `"@ts-" + "ignore"`. The test file then holds no match. Never skip the test's own file: One rejects a file exclusion.
- [x] `grep -rn "@ts-\|eslint-disable" src` finds 0 lines today. The site has no ESLint, so an `eslint-disable` line would silence nothing.
- [x] The allow list is a `Map` in the test: the key is the path and the line text, and the value is the reason. It is empty. Its comment says it is the only place a suppression may live.
- [x] Choice: the key holds the line text, not the line number, so the entry does not go stale when a line above it moves.
- [x] An allow list entry with no match fails the test, so a stale entry cannot stay.
- [x] Each offense prints the report shape of ticket 03, with the fix: "Fix the type or the code. If the line must stay, add it to the allow list with its reason."
- [x] A test runs the rule on one source string with a `@ts-ignore` line and finds one offense.
- [x] `docs/adr/0006-the-rules-are-checks.md` gains "No suppression comment": the rule, the allow list, and why this departs from One.
- [x] `pnpm check` passes.
