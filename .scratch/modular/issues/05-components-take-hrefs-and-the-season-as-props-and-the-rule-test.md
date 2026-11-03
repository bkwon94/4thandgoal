# 05: Components take hrefs and the season as props, and the rule test

**What to build:** The six components that build their own hrefs take them as props from the app layer. The two components that send the season in an API body take it as a prop. A test reads every file under the components folder and fails when a file imports the node fs, the config module, or a data loader, or reads the process env. ADR 0012 records the rule. This closes manager-pages site ticket 12: the week parts build the manager link by hand today, and after this ticket a link change touches only the routes module.

**Blocked by:** 04

**Status:** done

- [ ] No file under the components folder reads the base path or the season from the config.
- [ ] The rule test is green and names the file and the line on a breach.
- [ ] The managers index, the week footer, the menu, and the moves chapter take their hrefs as props.
- [x] `pnpm typecheck`, `pnpm test`, and `pnpm check:export` pass. The HTML markup has no diff against `main`. The flight data of the analyze page differs, because the analyzer now takes the season and the finder flag as props.

## Comments

- 2026-10-31: merged into `main` from branch `modular-05-props-and-rule`, commits cef7c15 and cb42fc5. 523 tests. The managers href stays a string, because a function prop cannot cross from a server page to a client component, and a string changes the fewest files. Components join a roster id onto the href they are given through `managerHrefFrom`; ADR 0012 now says so. Two reviewers passed it after one fix pass.
