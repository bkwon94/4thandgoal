# The rules are checks

A rule ran only when an agent chose to run it, and CI ran only on `main`. An agent follows the checks
that run, so a rule with no check is no rule. We decided that one command holds every rule. `pnpm check`
runs typecheck, test, build, and `check:export`. CI runs it on every push to any branch. A prek hook
runs `pnpm check:fast`, a subset of typecheck and test, before each commit. The hook and CI call the
same scripts in `package.json`. The hook runs a subset, and CI runs all of the rules. The hook subset
must stay under 30 seconds, because `--no-verify` is banned. The hook checks the whole tree, not the
staged files, because the subset takes about 17 seconds and a staged-only check would miss a type
error in a file the commit does not touch. The hook does not run `pnpm install`. In a worktree with
no `node_modules` it fails, and the fix is `pnpm install`. The deploy workflow keeps its own
`pnpm check`, because a separate workflow cannot gate the deploy without `workflow_run`.

## The report of an offense

An agent must fix an offense without the ADR, so every rule test prints each offense in one
shape. The helper `report` in `src/rule-report.ts` prints it:

```text
src/components/week/standings.tsx:4  components/no-loader
  standings.tsx imports @/lib/data/week-data.
  Rule: a component takes data and returns markup (docs/adr/0004-a-component-takes-data-and-returns-markup.md).
  Fix: call the loader in src/app/ and pass the value to the component as a prop.
```

- **The location and the rule id.** The path is from the repo root. Two spaces come before the id.
- **What is wrong at this place**, with the names of this place.
- **The rule** in one sentence, with the path of its ADR.
- **The fix** in one sentence.

The rule id is `<topic>/<name>`. The topics are `components`, `published`, `suppression`, and
`readme`. The report starts with the count, such as "2 offenses.". A blank line comes between
two offenses. A JSON parse gives no line, so the location of a `published/shape` offense is the file
and the field path, such as `public/2026/week-07/page.json:games.0.byes`. The helper imports no app
code, so the build never bundles it.

## No suppression comment

No comment silences a rule. The test `src/suppression-rule.test.ts` reads every `.ts`, `.tsx`,
`.js`, and `.mjs` file under `src/` and `scripts/`, and `next.config.ts`, `vitest.config.ts`, and
`postcss.config.mjs`. It fails on `@ts-expect-error`, `@ts-ignore`, `@ts-nocheck`, and
`eslint-disable`. `@ts-nocheck` silences a whole file, so it is the widest suppression. The site has
no ESLint, so an `eslint-disable` line silences nothing, but the test still fails on it. The test
builds each pattern from two parts, so its own file holds no match. It never skips a file, because
One rejects a file exclusion. The rule id is `suppression/comment`.

A line that must stay goes in the allow list of the test, with its reason. The allow list is a `Map`
in the test, and it is the only place a suppression may live. The key is the path and the text of the
line. The key holds the text, not the line number, so an entry does not go stale when a line above
it moves. An entry that matches no line fails the test with the rule id `suppression/stale-allow`,
so a stale entry cannot stay. The list starts empty.

The allow list is the one departure from One. One allows no suppression, and it puts each exception
in the definition of the rule. Here `tsc` owns its rules, and we do not fork it. So an exception
lives in the allow list, with its reason, and in no other place.

## A README in each package folder

An agent reads a folder README and decides whether to open the folder. A package folder is each
folder directly under `src/components/` and under `src/lib/`, plus `src/lib/` and `src/hooks/`. Each
one holds a `README.md` with a one-line title and three headings, in this order:

- **Knows**: what the folder knows, in the terms of `GLOSSARY.md`. The README defines no term again.
- **Ports**: the outside systems that the folder reaches. A folder with no port writes "None.".
- **Does not do**: what the folder never does, and which folder does it instead.

The third heading is the heading that lets an agent stop the search. A README is under 25 lines.
`src/app/` gets no README, because it is the app layer. One ADR 0007 says an app needs none.

The test `src/readme-rule.test.ts` finds the folders and holds no list, so a new folder needs a
README on its first day. Its rule ids are `readme/missing`, `readme/headings`, and `readme/length`.
The test checks that each README exists and has the shape. It cannot check that the text is true,
so a review checks that.

No tracked `CLAUDE.md` sits below the repo root. Claude Code loads a nested `CLAUDE.md` by itself.
So it puts the text of a folder into the context, whether the agent needs it or not. The agent must
choose to read the next level. A `CLAUDE.md` also ties the layout to one tool. The test reads
`git ls-files`, so a `CLAUDE.md` in `node_modules` does not count. The rule id is `readme/no-claude-md`.
