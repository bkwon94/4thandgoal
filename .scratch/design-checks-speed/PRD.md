# Design checks and speed: the checks catch misuse of the design parts, and the checks run in half the time

Status: ready-for-agent
Date: 2026-11-20
Apps: site. The site gets the design rules, the part docs, the role tokens, and the move to Bun. The pipeline changes only in CI, where its job splits into two jobs. The API does not change.
Spec branch: `design-checks-speed`.
Source: the map `.scratch/design-checks-speed/MAP.md` and decision tickets 01 to 07. The handoff `.handoff/design-system-and-speed.md`. ADR 0024, ADR 0035, and ADR 0038.
Tickets: 01 to 18, in `issues/`.

## Problem Statement

Brian wants the design system to defend itself, and he wants the checks to stop costing him minutes.

1. No check catches the misuse of a design part. An agent can add a raw `<button>`, a raw color, or an arbitrary Tailwind value, and the hook and CI stay green. Eight files use a raw `<button>` today. Thirty-two arbitrary values sit in the color and spacing groups. One of them, `top-[calc(var(--spacing-touch)+2*var(--spacing-sp-2)+1px)]`, repeats the token `--spacing-band-height` by hand.
2. The site has no linter and no formatter. `check:fast` runs only the client build, `tsc`, and Vitest.
3. A part has no doc that says when to use it and when not to. An agent picks a part by its name.
4. The chips of the front door mix the accent color by hand at five strengths, with `dark:` classes for each one. No token names the role of these washes.
5. A full `make check-fast` takes 195 s on the laptop, and Vitest takes 138 s of that. A whole CI run takes a median of 754 s. Playwright alone takes 666 s in one job.

## Solution

1. **The design rules.** One Oxlint config and one local plugin run five rules on the site code: the `@ui-sdk` import rule, no raw color, no raw `<button>` or `<dialog>`, no arbitrary color or spacing value, and the part doc lines. The hook lints the staged files, and CI lints all files. The code that fails a rule today gets a fix in this spec, with no allowlist.
2. **The part docs.** Each exported part of `ui/` and `parts/` has a "Use it when" line and a "Do not use it when" line in its top docstring. A rule fails a part without them.
3. **The role tokens.** The look tokens have two tiers: a **Scale step** and a **Role token**. Three role tokens replace the chip washes, with their dark values in the stylesheet, so the `dark:` classes go away.
4. **Bun runs the checks** (ADR 0038). `bun test` replaces Vitest, `bun check` replaces `tsc`, and `bun fmt` formats the code. pnpm stays the installer.
5. **The checks run in parallel.** `make check-fast` runs the apps and the site steps in parallel, with a cap for the hook. CI runs the unit suite and Playwright in shards, runs only the tests the diff can reach on a PR, and splits the pipeline job into two jobs.
6. **The targets.** A full `make check-fast` takes 97 s or less, half of 195 s. The whole CI run takes 360 s or less.

## User Stories

1. As Brian, I want the hook to fail a raw `<button>` outside `ui/`, so that each button keeps the look and the focus ring of the wrapper.
2. As Brian, I want the hook to fail a raw `<dialog>` outside `ui/`, so that each dialog keeps the focus trap and the motion of the wrapper.
3. As Brian, I want the hook to fail a raw color literal in a `.tsx` file, so that each color comes from a token of the look.
4. As Brian, I want the hook to fail an arbitrary color value, so that a new color shade gets a role token.
5. As Brian, I want the hook to fail an arbitrary spacing value, so that an agent uses a role token or a scale step.
6. As Brian, I want a `calc` that equals a token to fail, so that `--spacing-band-height` is not typed out by hand.
7. As Brian, I want variant selectors such as `data-[state=open]:` to stay allowed, so that the rule does not fail normal Tailwind state styles.
8. As Brian, I want layout values such as `grid-cols-[...]` to stay allowed, so that a page can set its own grid.
9. As Brian, I want motion values such as `transition-[...]` to stay allowed, so that the rule does not block motion work.
10. As Brian, I want a true one-off to pass with a one-line ignore and a reason, so that the reason stays next to the code.
11. As Brian, I want no allowlist file, so that no list grows stale.
12. As Brian, I want the `@ui-sdk` import rule in the same linter as the other rules, so that all design rules live in one place.
13. As Brian, I want the editor to show a design rule error at the line, so that an agent sees the error before the hook runs.
14. As an agent, I want each rule error to name the rule, the file, the line, and the fix, so that I can fix the error with no search.
15. As an agent, I want each part to say when to use it, so that I pick the right part.
16. As an agent, I want each part to say when not to use it and what to use instead, so that I do not pick a close but wrong part.
17. As Brian, I want a rule to fail a part with no "Use it when" line, so that a new part cannot ship with no doc.
18. As Brian, I want the part READMEs to keep their "Knows" lists, so that a reader still sees each folder at a glance.
19. As Brian, I want the chip washes to come from role tokens, so that a change of the accent changes each chip.
20. As Brian, I want the dark values of the washes in the stylesheet, so that a chip needs no `dark:` class.
21. As Brian, I want the spacing scale to stay a scale, so that 1,200 uses do not change for no gain.
22. As an agent, I want the glossary to define a role token and a scale step, so that I know which one to use.
23. As Brian, I want the site tests to run on `bun test`, so that the hook takes less time.
24. As Brian, I want each test that passes on Vitest today to pass on `bun test`, so that the move drops no coverage.
25. As Brian, I want the test count after the move to match the count before it, so that no test goes missing quietly.
26. As an agent, I want the tests to use the native `bun:test` calls, so that I read the real runner and not a shim.
27. As an agent, I want one helper for `stubGlobal` and `stubEnv` that restores each value, so that one test does not leak into the next.
28. As Brian, I want `main` to get the whole move in one squash merge, so that `main` never runs two test runners.
29. As Brian, I want `bun check` to type-check the site, so that the type check runs in less time.
30. As Brian, I want `next typegen` to run before `bun check`, so that the route types exist when the check runs.
31. As Brian, I want `bun fmt` to check the format in the hook and in CI, so that a diff holds no format noise.
32. As Brian, I want `bun fmt` to sort the Tailwind classes, so that the order of a class list is the same in each file.
33. As Brian, I want pnpm to stay the installer, so that the move to Bun does not change a dependency version.
34. As Brian, I want `make check-fast` to run its steps in parallel, so that the slowest step sets the time and not the sum.
35. As Brian, I want a cap on the parallel jobs of the hook, so that the site tests do not hit the 5 s timeout under load.
36. As Brian, I want a full `make check-fast` to take 97 s or less, so that a commit does not wait three minutes.
37. As Brian, I want CI to run the unit suite in shards, so that the unit job takes less time.
38. As Brian, I want the measured time to set the shard count, so that a shard does not cost more setup than it saves.
39. As Brian, I want CI on a PR to run only the tests the diff can reach, so that a small PR gets a fast answer.
40. As Brian, I want a change to a config file or the lock file to run the full suite, so that a wide change gets a full check.
41. As Brian, I want CI on `main` to run the full suite, so that the record branch always gets the full check.
42. As Brian, I want Playwright to run in shards, so that the site-browser job stops setting the time of the whole run.
43. As Brian, I want the serial projects of Playwright to stay serial, so that the timing specs keep their single worker.
44. As Brian, I want the pipeline job to split into a parallel job and a serial job, so that neither job sits above 360 s.
45. As Brian, I want the whole CI run to take 360 s or less, so that a PR is ready to merge in about six minutes.
46. As Brian, I want each speed change to cost no money, so that the project stays free.
47. As Brian, I want the before and after times recorded, so that I can see what each change gained.
48. As Brian, I want an ADR for the move to Bun, so that a later reader knows why the site tests do not run on Vitest.

## Implementation Decisions

**The design rules** (ticket 03)

- One Oxlint config at the site. One local plugin in the design package holds the custom rules. The plugin uses the ESLint rule shape, so canary `bun lint` can run the same file later.
- "All site code" means the site app source and the `site` side of each package. Test files are exempt from the element rule and the value rule.
- The `@ui-sdk` import rule is the built-in `no-restricted-imports`, with the `ui` folder of the design package as the one allowed path. The rule test of ADR 0035 goes away. ADR 0035 gets a line that names ADR 0038.
- The raw color rule fails a hex, `rgb()`, `hsl()`, or `oklch()` literal in a `.tsx` file. The `.css` files hold the token values, so the rule does not read them.
- The element rule fails a JSX `<button>` or `<dialog>` outside the `ui` folder. Each of the 8 files today moves to a wrapper of `ui`.
- The value rule fails an arbitrary value only for the prefixes `bg-`, `text-`, `border-`, `ring-`, `fill-`, `stroke-`, `shadow-`, and the padding, margin, gap, and inset prefixes. It reads class strings in `className`, in `cn(...)`, and in template literals. The `ui` folder is in scope.
- Each of the 32 uses today gets a fix or a one-line ignore with a reason. A `calc` that equals a token becomes the token.
- The doc rule reads the top docstring of each file of `ui` and `parts` that exports a component. It fails a file that has no line starting `Use it when:` or no line starting `Do not use it when:`.
- Each rule message names the rule, the problem, and the fix.

**The part docs** (map decision)

- The two lines sit in the top docstring, under the 2-line header that each file has now. "Do not use it when" names the part to use instead where one exists.
- The READMEs of `ui` and `parts` keep their "Knows" lists.

**The role tokens** (ticket 04)

- The look tokens have two tiers, a Scale step and a Role token. The glossary holds both terms.
- `--color-accent-wash`, `--color-accent-wash-chosen`, and `--color-accent-wash-hover` replace the hand mixes of the chips. Light: the accent mixed into the card at 10, 20, and 28 percent. Dark: the raised color, then the accent mixed into the raised color at 24 and 34 percent. The dark values live in the dark block of the stylesheet.
- The spacing scale stays a scale. `--oc-dur` and `--es-dur` stay as they are, because the part writes each one at runtime.

**Bun** (tickets 01, 05, and 06, and ADR 0038)

- Bun v1.4.5 or later. The repo pins the Bun version in one place, and CI installs that version.
- pnpm stays the installer. Bun runs on the `node_modules` that pnpm installs.
- `bun test` runs from the site app with the happy-dom preload that the Bun docs give. The `@` alias resolves as it does now.
- Each missing `vi` call becomes a native `bun:test` call: `mock`, `spyOn`, and `mock.module`. One helper gives `stubGlobal` and `stubEnv`, each restored in `afterEach`. A test with `vi.resetModules` or `vi.hoisted` changes its setup.
- The files move in batches on the spec branch, one ticket for each group of packages. Until the last batch, `check:fast` runs Vitest on the old files and `bun test` on the moved files. The last ticket removes Vitest and its config.
- `bun check` replaces `tsc --noEmit`, after `next typegen`. The script name `check` of the site hides the subcommand, so the site renames its script or calls `bun check --no-script`.
- `bun fmt` runs in check mode in the hook and in CI. The first format of the whole code is one commit with no other change.

**The parallel checks** (map decision and ticket 07)

- `make check-fast` runs the scripts, the apps, and the packages in parallel. Inside the site, the lint, the format check, the type check, and the tests run in parallel after the client build.
- The hook caps the parallel jobs. The cap keeps the site tests under the 5 s timeout under load.
- CI runs `bun test --shard=<i>/<n>` in a matrix. The time of the full suite after the move sets `n`.
- On a PR, CI runs `bun test --changed=origin/main`. A change to a config file, the lock file, or the test preload runs the full suite. A push to `main` runs the full suite.
- CI runs Playwright with `--shard=<i>/<n>` in a matrix. The serial projects keep one worker. The measured split sets `n`.
- The pipeline job splits into a job for the parallel tests and a job for the serial tests.
- The `node_modules` cache and the shared API app are not in this spec. Each saves too little: 3 s and 2 s.

## Testing Decisions

A good test checks behavior that a reader can see from the outside: the exit code of a command, the message of a rule, and the time of a run. It does not check the inside of a rule. It uses real files and real runs, never a mock (ADR 0015).

The seams, from the highest down:

1. **The root `make check-fast` and the CI run.** This is an existing seam. The speed targets are its wall-clock time: a full local run on the same laptop as the baseline, the M2 Pro with 10 cores, and the median of the CI runs of the spec branch. The baseline is in `decisions/02-research-baseline-times.notes.md`.
2. **The lint command on fixture files.** This is a new seam with one entry point. A rule test runs Oxlint with the real config on a small folder of fixture files. Each rule has one file that breaks it and one file that passes. The test checks the exit code and the rule name in the output. Prior art: the rule tests of the root scripts, such as the test of `retry_rule.py`.
3. **The lint command on the real code.** CI lints all site code and expects exit 0. That proves that each of the 8 buttons and the 32 values got a fix or an ignore with a reason.
4. **The test count.** The count of the tests that pass after the move equals the count before it, 1,775 tests in 183 files, plus or minus each test that the spec adds or removes on purpose. The ticket of the last batch records both counts.
5. **The look of the chips.** The chips of the front door look the same in light and dark mode before and after the role tokens. Prior art: the screenshot evidence of the site specs.

## Out of Scope

- The move from pnpm to `bun install`. Brian keeps pnpm for now. The facts for a later move are in `decisions/01-research-bun-latest.notes.md`.
- The Python tools of the pipeline and the API, such as `pytest` and `ruff`. Bun does not run Python. The pipeline job only splits in CI.
- The landmines timing rules. They know Vitest names that this spec removes. The Quick Win in the queue runs after this spec merges.
- `bun lint`. It is on canary only. Oxlint runs the plugin until a release build ships it.
- A rename of the spacing scale. It stays a scale.
- The `node_modules` cache in CI and one shared app for the API tests. Each saves 3 s or less.

## Further Notes

- The landmines spike can reuse the Oxlint config of this spec. Its timing rules then check Bun names.
- Other sessions run checks on this laptop. A timed run waits until `pgrep -fl 'vitest|bun test|check-fast|pytest'` shows nothing, as ticket 02 did.
- Vitest reports that `isolate: false` saves about 32 s. That does not matter after the move, but it is a fallback if the move stalls.
- ADR 0038 records the move to Bun. ADR 0035 gets one line that its rule test moved to Oxlint.
