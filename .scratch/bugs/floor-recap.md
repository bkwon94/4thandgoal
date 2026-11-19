# The week 10 floor test fails on main after the tap on recap 3

Kind: bug
Status: in-progress
Branch: `bug-floor-recap`.
Source: the session of 2026-11-19. Main Check run 44611529354 at `ac287f48` and PRs #80 and #81 fail it.
Boundary: holds. 1 item of one kind; no new term or ADR; no moved seam; each done condition is one sentence.

## Items

### 1. The floor of cpc /2026/week-10/ fails after the tap on recap 3 at 1280px

Done condition: The full floor test of cpc `/2026/week-10/` after the tap on `recap-3` passes at 1280px in dark and light, and the floor still fails on a real contrast fault.
Method: diagnosing-bugs
Cause: `axeContrast` in `apps/site/e2e/floor.ts` fails each axe incomplete result. Since the label "Season Sim", the pill bar leaves the band title 0.41px short at 1280px in Linux Chromium, so an ellipsis cuts it. Chromium gives the cut title two text boxes, and after the tap on recap 3 the page under the opaque sticky band differs at their centers. axe returns `elmPartiallyObscuring`, so the floor fails a readable title. The fix judges such a text of an opaque sticky or fixed band again at the top of the page.
Red: at `f1f0c14b`, `(CLIENT=cpc pnpm build || CLIENT=cpc pnpm build) > /dev/null 2>&1 && pnpm exec playwright test --project=rules --project=floor e2e/floor-rules.spec.ts e2e/floor.spec.ts -g "band title|recap-3"` in `apps/site`

```text
  ✘  1 [rules] › e2e/floor-rules.spec.ts:200:5 › a band title cut by an ellipsis over a scrolled page passes, because its opaque band hides the page under it ...
  ✘  2 [rules] › e2e/floor-rules.spec.ts:205:5 › a faint band title cut by an ellipsis over a scrolled page still fails ...
    +   "incomplete: span Fix any of the following: Element's background color could not be determined because it partially overlaps other elements",
  2 failed
```

Green: at `2950b4d5`, `(CLIENT=cpc pnpm build || CLIENT=cpc pnpm build) > /dev/null 2>&1 && pnpm exec playwright test --project=rules --project=floor e2e/floor-rules.spec.ts e2e/floor.spec.ts -g "band title|recap-3"` in `apps/site`

```text
  ✓  2 [rules] › e2e/floor-rules.spec.ts:205:5 › a faint band title cut by an ellipsis over a scrolled page still fails (638ms)
  ✓  1 [rules] › e2e/floor-rules.spec.ts:200:5 › a band title cut by an ellipsis over a scrolled page passes, because its opaque band hides the page under it (638ms)
  ✓  5 [floor] › e2e/floor.spec.ts:169:11 › full floor: cpc /2026/week-10/ tap button[aria-controls="recap-3"]:not([aria-label]) dark 1280px (1.1s)
  ✓  6 [floor] › e2e/floor.spec.ts:169:11 › full floor: cpc /2026/week-10/ tap button[aria-controls="recap-3"]:not([aria-label]) light 1280px (1.2s)
  6 passed (4.0s)
```
Test verdict: pending

## Smoke

Smoke: pending

## Comments

- CI error: "incomplete: .max-rail\:sr-only Fix any of the following: Element's background color could not be determined because it partially overlaps other elements". It first shows on main at `ac287f48` (#78); main at `fd05189c` and `8780eefb` failed on other tests.
- The cpc tests of recap 3 at 1280px fail only in Linux Chromium. Mac Chromium sets the title at 360.67px, so it fits and has one text box. A probe in the image `mcr.microsoft.com/playwright:v1.64.1-noble` showed the 378.41px title, the two boxes, and the incomplete result in dark and light. At the top of the page axe passes the title in both themes. On CI the Red command also fails these two floor tests at `f1f0c14b`.
- The title cut is by design: the band gives the pill bar its full labels first. So the fix is in the floor check, not in `apps/site/src`.
