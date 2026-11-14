# A new question scrolls into view from a scrolled-up Thread

Kind: bug
Status: done
Branch: `bug-ask-scroll`.
Source: the session of 2026-11-13.
Boundary: holds. 1 item of one kind; no new term or ADR; no moved seam; each done condition is one sentence.

## Items

### 1. A sent question does not scroll into view when the Thread is scrolled up

Done condition: When the manager scrolls up in a Thread and sends a question by a Suggestion chip or the ask box, the page scrolls so the new question and its Answer sit in view, with no manual scroll.
Method: diagnosing-bugs
Cause: the scroll effect in `apps/site/src/app/front-door/front-door.tsx` calls `scrollIntoView` with `smooth` in the commit of the new turn, and the keyframe measure of Motion (`measureAllKeyframes` in `motion-dom`) then calls `window.scrollTo(0, <the old scroll>)` for a height animation of the same render, such as the strip of a tapped chip as it closes, so that instant scroll stops the smooth scroll and the page stays where the manager left it.
Red: at `60d6e2c8`, `cd apps/site && CLIENT=cpc pnpm build && pnpm exec playwright test --project=floor e2e/front-door-scroll-up.spec.ts`

```text
  ✘  1 [floor] › e2e/front-door-scroll-up.spec.ts:56:5 › a Suggestion chip tapped in a scrolled-up Thread scrolls its question to the top under the Thread header
  ✓  2 [floor] › e2e/front-door-scroll-up.spec.ts:70:5 › a question typed in a scrolled-up Thread scrolls to the top under the Thread header
    Error: the bubble top of Your next matchup sits under the header
    Expected: <= 16
    Received:    921.125
  1 failed
  1 passed
```

Green: at `2b85fb51`, `cd apps/site && CLIENT=cpc pnpm build && pnpm exec playwright test --project=floor e2e/front-door-scroll-up.spec.ts`

```text
  ✓  1 [floor] › e2e/front-door-scroll-up.spec.ts:56:5 › a Suggestion chip tapped in a scrolled-up Thread scrolls its question to the top under the Thread header (7.4s)
  ✓  2 [floor] › e2e/front-door-scroll-up.spec.ts:70:5 › a question typed in a scrolled-up Thread scrolls to the top under the Thread header (8.1s)

  2 passed (9.1s)
```
Test verdict: PASS

## Comments

Closes with the squash merge of the PR of `bug-ask-scroll`. Commits: `60d6e2c8`, `2b85fb51`. Date: 2026-11-13.
The loop `apps/site/e2e/front-door-scroll-up.spec.ts` went red on the chip case at `60d6e2c8` and green on both cases at `2b85fb51`, and the site has 1506 passing vitest tests.
The typed-question case passed at the red commit in WebKit, so the loop shows the chip half of the bug only.
With reduced motion on, the chip case ends 20 px under the Thread header, not 16, which a later run can check.
Read 7 files: docs/agents/issue-tracker.md, docs/adr/0033-a-quick-run-skips-the-spec-flow.md, GLOSSARY.md, .claude/plugin/skills/quick/format.md, .claude/plugin/skills/quick/judge.md, .claude/plugin/skills/implement/build.md, apps/site/src/app/front-door/front-door.tsx.
The CI floor of norcal failed the chip case 51 px under the header, because `--door-dock` lagged the shrunk dock by one frame and the fill of the newest turn left out its `pt-sp-6` step, so WebKit stopped the scroll at a short foot, and `29008c1b` fixes both.
