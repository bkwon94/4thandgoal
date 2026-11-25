# The week 11 data breaks four checks

Kind: bug
Status: in-progress
Branch: `bug-week-11-checks`.
Source: the session of 2026-11-24. The Check of `f44dc5b1` (run 45506075668) failed after the cpc week 11 publish.
Boundary: holds. 4 items of one kind; no new term or ADR; no moved seam; each done condition is one sentence.

## Items

### 1. The topics test pins the team names of the live rankings

Done condition: `apps/pipeline/tests/test_topics.py` passes on the cpc week 11 data, where some teams have new names.
Method: diagnosing-bugs.
Cause: `test_the_power_rankings_block_lists_each_team_with_its_rank_and_its_move` in `apps/pipeline/tests/test_topics.py` pins the team names, but `rank_movers_block` reads the names of `published/2026/rankings.json`, which each publish rewrites with the current names, so a rename breaks the test.
Red: at `4ee479ef`, `cd apps/pipeline && uv run --exact --package cornerstone pytest tests/test_topics.py -q`

```text
E       AssertionError: assert [(1, '💿 🐑', 3...on', -4), ...] == [(1, 'Return ...ee', -4), ...]
E         At index 0 diff: (1, '💿 🐑', 3) != (1, 'Return of T Mac', 3)
tests/test_topics.py:228: AssertionError
FAILED tests/test_topics.py::test_the_power_rankings_block_lists_each_team_with_its_rank_and_its_move
1 failed, 12 passed in 7.75s
```

The loop is the test itself, so the fix changes the loop file. The parent `4ee479ef` holds the loop, the week 11 data, and no fix.

Green: at `dfdd443d`, `cd apps/pipeline && uv run --exact --package cornerstone pytest tests/test_topics.py -q`

```text
.............                                                            [100%]
13 passed in 7.68s
```
Test verdict: pending

### 2. The analyzer stage spec pins the team names of the live rosters

Done condition: `apps/site/e2e/analyzer-stage.spec.ts` passes on the cpc week 11 build, where roster 2 has a new name.
Method: diagnosing-bugs.
Cause: `rawTeams` in `apps/site/src/fixtures/raw-teams.ts` reads the rosters of the latest week, and `openTradeB` in `apps/site/e2e/analyzer-stage.spec.ts` pins the name "All You Need Is Love" of roster 2, so the week 11 rename of roster 2 and the week 11 trades that move Tee Higgins, Bhayshul Tuten, Rashee Rice, and Ashton Jeanty off the rosters of trade T and trade B break 38 tests.
Red: at `312deb0e`, `cd apps/site && CLIENT=cpc pnpm check:floor analyzer-stage.spec.ts` after `CLIENT=cpc pnpm build`

```text
    Error: expect(locator).toBeVisible() failed
    Locator: locator('section[aria-label="Trade Analyzer"] [data-mesh-anchor]').filter({ has: locator('[data-stage-team]').getByText('Bo Girds', { exact: true }) }).getByText('2 players')
    Error: element(s) not found
      > 210 |       ).toBeVisible();

    Error: locator.click: Test timeout of 30000ms exceeded.
      - waiting for getByRole('dialog').getByRole('button', { name: /All You Need Is Love/ })
      > 313 |     .click();

  38 failed
  1 skipped
  4 passed (10.7m)
```

The loop is the spec itself, so the fix changes the loop file. The parent `312deb0e` holds the loop, the week 11 data, and no fix. The fix reads the week 10 rosters, which hold trade T, trade B, and the recorded answers, and it reads each team name of trade B from the teams by roster id.

Green: at `92b790f2`, `cd apps/site && CLIENT=cpc pnpm check:floor analyzer-stage.spec.ts` after `CLIENT=cpc pnpm build`

```text
  1 skipped
  42 passed (1.3m)
Running 12 tests using 1 worker
  12 passed (51.8s)
```
Test verdict: pending

### 3. A team link with a short name is under the tap floor

Done condition: the readability floor of `/2026/managers/7/` at 390px passes on the cpc week 11 build, where a team link shows only "💿 🐑".
Method: diagnosing-bugs.
Cause: `TradeTeam` in `packages/managers/site/page/moves.tsx` gives the team link `min-h-touch` but no `min-w-touch`, so a team named only two emoji gives a link 39px wide, under the tap floor of 44px.
Red: at `0f3ac7f3`, `cd apps/site && CLIENT=cpc pnpm check:floor -g /2026/managers/7/` after `CLIENT=cpc pnpm build`

```text
    Error: cpc /2026/managers/7/ light 390px breaks the readability floor
    + Array [
    +   "a.min-h-touch \"💿 🐑\" is 39x44px, under the tap floor of 44px",
    +   "a.min-h-touch \"💿 🐑\" is 39x44px, under the tap floor of 44px",
    + ]
  2 failed
    [floor] › e2e/floor.spec.ts:190:11 › full floor: cpc /2026/managers/7/ dark 390px
    [floor] › e2e/floor.spec.ts:190:11 › full floor: cpc /2026/managers/7/ light 390px
  2 passed (4.3s)
```

The loop is the floor spec `apps/site/e2e/floor.spec.ts` with no change, so the red commit adds no file. `0f3ac7f3` holds the loop, the week 11 data, and no fix.

Green: at `39cad4d9`, `cd apps/site && CLIENT=cpc pnpm check:floor -g /2026/managers/7/` after `CLIENT=cpc pnpm build`

```text
  ✓  1 [floor] › e2e/floor.spec.ts:190:11 › full floor: cpc /2026/managers/7/ dark 390px (1.2s)
  ✓  2 [floor] › e2e/floor.spec.ts:190:11 › full floor: cpc /2026/managers/7/ light 390px (1.2s)
  ✓  4 [floor] › e2e/floor.spec.ts:190:11 › full floor: cpc /2026/managers/7/ light 1280px (1.2s)
  ✓  3 [floor] › e2e/floor.spec.ts:190:11 › full floor: cpc /2026/managers/7/ dark 1280px (1.2s)
  4 passed (3.3s)
```
Test verdict: pending

### 4. A player name splits a word over two lines on the week page

Done condition: the no-split-word check of `/2026/week-11/` passes at 375px and 1280px on the cpc week 11 build, with "David Montgomery" on the page.
Method: diagnosing-bugs.
Cause: the player name span of `Side` in `packages/week/site/chapters/trades.tsx` has `min-w-0`, so in the 132px column of a pair card it shrinks to 80px beside the 44px photo, under the width of "Montgomery", and the `overflow-wrap: break-word` of `body` splits the word.
Red: at `38492802`, `cd apps/site && CLIENT=cpc pnpm check:floor -g /2026/week-11/` after `CLIENT=cpc pnpm build`

```text
  1) [floor] › e2e/floor.spec.ts:301:7 › no split word: cpc /2026/week-11/ 375px
    Error: cpc /2026/week-11/ 375px splits a word
    +   "span.text-body \"David Montgomery\": the word \"Montgomery\" breaks over 2 lines",
  2) [floor] › e2e/floor.spec.ts:301:7 › no split word: cpc /2026/week-11/ 1280px
    Error: cpc /2026/week-11/ 1280px splits a word
    +   "span.text-body \"David Montgomery\": the word \"Montgomery\" breaks over 2 lines",
  2 failed
  11 passed (8.1s)
```

The loop is the floor spec `apps/site/e2e/floor.spec.ts` with no change, so the red commit adds no file. `38492802` holds the loop, the week 11 data, and no fix. The fix gives the span `min-w-min grow basis-0` and the row `flex-wrap`, so a longest word that does not fit beside the photo moves the name under the photo.

Green: at `8da7ab95`, `cd apps/site && CLIENT=cpc pnpm check:floor -g /2026/week-11/` after `CLIENT=cpc pnpm build`

```text
  ✓   4 [floor] › e2e/floor.spec.ts:301:7 › no split word: cpc /2026/week-11/ 375px (224ms)
  ✓   5 [floor] › e2e/floor.spec.ts:301:7 › no split word: cpc /2026/week-11/ 768px (228ms)
  ✓   6 [floor] › e2e/floor.spec.ts:301:7 › no split word: cpc /2026/week-11/ 1280px (233ms)
  13 passed (7.9s)
```
Test verdict: pending

## Comments
