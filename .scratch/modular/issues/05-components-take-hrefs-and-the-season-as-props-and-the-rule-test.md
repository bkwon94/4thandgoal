# 05: Components take hrefs and the season as props, and the rule test

**What to build:** The six components that build their own hrefs take them as props from the app layer. The two components that send the season in an API body take it as a prop. A test reads every file under the components folder and fails when a file imports the node fs, the config module, or a data loader, or reads the process env. ADR 0004 records the rule.

**Blocked by:** 04

**Status:** ready-for-agent

- [ ] No file under the components folder reads the base path or the season from the config.
- [ ] The rule test is green and names the file and the line on a breach.
- [ ] The managers index, the week footer, the menu, and the moves chapter take their hrefs as props.
- [ ] `pnpm typecheck`, `pnpm test`, and `pnpm check:export` pass. `out/` has no diff against `main`.
