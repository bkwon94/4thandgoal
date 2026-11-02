# Rules as checks: every rule runs on every commit, and every folder says what it knows

Status: ready-for-agent
Date: 2026-11-02
Repos: the pipeline `cornerstone-fantasy-sleeper-weekly-report` and the site `cpcfantasyfootball`. The same PRD sits in both.
Source: One's records in `~/repos/zero/docs/adr/`: 0001, 0003, 0004, 0007, 0013, 0014, 0016.
Tickets: pipeline 01 to 06. Site 01 to 04: the check, no suppression, one report shape, the READMEs.

## Problem Statement

Brian: "I think the vision of One can be applied here. Just want to make it optimized for AI agents to work."

Both repos follow most of One already. Six gaps remain.

1. A rule runs only when an agent chooses. No repo has a hook. The pipeline has no test CI. The site CI runs only on `main`.
2. Three rule tests report in three shapes. None says the fix.
3. A comment can silence a rule. The pipeline has five `# noqa` lines.
4. The sheet entry-point rule is a comment, not a test.
5. A folder has no README that tells a cold agent what it knows, its ports, and what it does not do.
6. Twenty pipeline tests `monkeypatch` the Claude call or Sleeper.

## Solution

1. **One check command, the same in the hook and in CI** (One 0013). Pipeline: `make check` runs lint, typecheck, and tests. A prek hook runs `make check-fast`. A GitHub Action runs `make check` on every push. Site: `pnpm check` runs typecheck, test, build, and `check:export`. The hook runs `pnpm check:fast`. A CI job runs `pnpm check` on every push.
2. **The sheet has one entry point** (One 0003). Pipeline only. Outside `sheet/`, a module imports only `cornerstone.sheet` or `cornerstone.sheet.base`. `test_layers.py` holds the rule.
3. **No suppression comment** (One 0013). One test per repo fails on `noqa`, `type: ignore`, `pyright: ignore`, `@ts-expect-error`, `@ts-ignore`, and `eslint-disable`.
4. **One report shape for every rule test** (One 0013). `test_layers.py` is the model.
5. **A README in each package folder** (One 0001, 0007), with three headings: Knows, Ports, Does not do. Under 25 lines. No `CLAUDE.md` in a subfolder, ever. A test fails on a missing README.
6. **A writer port with one fake** (One 0004). Pipeline only. A `Writer` protocol for the Claude call and one in-memory fake. The twenty tests move to the fakes. A rule test fails on a `monkeypatch.setattr` of a provider or writer target.

## The report shape

```text
src/cornerstone/waiver.py:12  layers/upward-import
  cornerstone.waiver imports cornerstone.writer.
  Rule: a module imports only from its own layer or a lower one (docs/adr/0007-six-layers-import-downward-only.md).
  Fix: move the shared name to a module in a lower layer, or move cornerstone.waiver up in LAYER_OF.
```

The lines are the location and rule id, what is wrong here, the rule with its ADR, and the fix.

## Decisions

- **The hook tool is prek.** One uses it, Brian has it, and each worktree reads its own branch's config.
- **The hook runs a fast subset, and CI runs everything.** `--no-verify` is banned, so the hook must stay under 30 seconds. Today the subsets take about 3 and 17 seconds.
- **The publish commit runs the hook.** The site hook parses the new JSON before the push, so a bad shape stops the publish.
- **The allow list is the one departure from One.** One allows no suppression. Here a line that must stay goes in the allow list of the suppression test, with the file, the line text, and the reason. No other place may hold one. The reason: ruff and `tsc` own their rules, and we do not fork them. The list starts empty, because all five `noqa` lines name a rule that ruff does not select.
- **A fake is not a mock mode.** A fake at a port is a test double that only tests import. A mock mode is a runtime switch that serves fake data. The mock mode stays banned.
- **A gate starts at zero offenses** (One 0013). A rule ticket fixes every offense it finds.
- **Each ticket names its proof** (One 0014): the command and the test.
- **The ADRs.** Pipeline ADR 0009 and site ADR 0006, "the rules are checks", hold parts 1, 3, 4, and 5. Pipeline ADR 0007 gains the sheet entry. Pipeline ADR 0010 holds the fake rule.
- **STE stays in prose and in review**, not in a check. One has not built that check either (One 0016). A half-built word check costs more than it saves.
- **The paid model judge is out. Manifests and import bans between packages are out**, because each repo is one package.

## Testing Decisions

- Each rule test reads the real tree. It also runs its rule on one offending file in a temporary folder and finds one offense.
- The four pipeline golden tests pass with no golden change.

## Out of Scope

- Everything in One built for many teams, clients, deployments, or platforms.
- A site linter, or a change to the ruff rule set.
- The 20 `vi.mock` and `vi.spyOn` lines in the site tests.
- The patches of the nflverse fetch and of the build steps in the pipeline tests.

## Further Notes

- The week 8 build runs from the pipeline `main` at 08:00 ET on 2026-11-03, and the publish commits both repos. A hook from this feature would run inside that publish. Merge nothing from this feature in either repo before the week 8 page is live.
- The site publish stages every file. Commit or remove each site change before a publish.
