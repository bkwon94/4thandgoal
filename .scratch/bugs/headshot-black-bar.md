# Analyzer headshots show a black bar on the right

Kind: bug
Status: in-progress
Branch: `bug-headshot-black-bar`.
Source: the session of 2026-11-16.
Boundary: holds. 1 item of one kind; no new term or ADR; no moved seam; each done condition is one sentence.

## Items

### 1. Analyzer headshots show a black bar on the right

Done condition: Each player headshot in the trade analyzer fills its frame centered, with no black bar on the right side.
Method: diagnosing-bugs
Cause: `PlayerChip` in `packages/analyzer/site/form/analyze-result.tsx` gives the headshot `-mx-sp-2 self-stretch`, but the Tailwind base styles cap each `img` at `max-width: 100%`, so the frame stays the width of the chip content box, shifts left by its margin, and leaves a 16px strip of the dark chip at the right.
Red: at `8ab7621d`, `cd apps/site && pnpm check:grade-bar`

```text
Dalton Kincaid: 0.0px left gap, 16.0px right gap
Garrett Wilson: 0.0px left gap, 16.0px right gap
Nico Collins: 0.0px left gap, 16.0px right gap
  ✘  2 [grade-bar] › e2e/analyze-headshot.spec.ts:42:5 › each headshot frame fills its player chip, centered, with no strip at the right (headshot-black-bar item 1) (281ms)
    Error: Dalton Kincaid: the gap at the right of the frame
    Expected: 0
    Received: 16
  1 failed
  2 passed (1.4s)
```

Green: at `d011c5e8`, `cd apps/site && pnpm check:grade-bar`

```text
Dalton Kincaid: 0.0px left gap, 0.0px right gap
Garrett Wilson: 0.0px left gap, 0.0px right gap
Nico Collins: 0.0px left gap, 0.0px right gap
  ✓  2 [grade-bar] › e2e/analyze-headshot.spec.ts:42:5 › each headshot frame fills its player chip, centered, with no strip at the right (headshot-black-bar item 1) (340ms)
  3 passed (1.2s)
```

Test verdict: pending

## Comments
