# Flaky browser specs that block deploys

Kind: bug
Status: in-progress
Branch: `bug-flaky-browser-specs`.
Source: the handoff file `.handoff/flaky-specs.md`, Run 1.
Boundary: holds. 5 items of one kind; no new term or ADR; no moved seam; each done condition is one sentence.

## Items

### 1. The tour glide tests fail on a slow runner

Done condition: The AT-15 glide tests of `apps/site/e2e/front-door-tour-motion.spec.ts` pass when the first frame of the glide comes late, and they still fail when the hole stays at the old Stop.
Method: diagnosing-bugs
Cause: `glideTogether` in `apps/site/e2e/front-door-tour-motion.spec.ts` reads the real clock of the page, so a runner frame of 330 ms or more lands past 99% of the 450 ms spring and a real glide looks like a jump. This is a test bug: the spring of framer-motion runs on time and already starts late from its first frame (`resolveStartTime`, 40 ms). The fix gives the page a clock of frames, `frameClock`, that moves 1000/60 ms or 150 ms per frame. The stacked loops of `startSamples` only double each sample and do not cause this failure, so `door-motion.ts` stays as it is (item 6 under Later).
Red: at `1c9baeaa`, `(CLIENT=cpc pnpm build || CLIENT=cpc pnpm build) > /dev/null 2>&1 && pnpm exec playwright test --project=floor e2e/front-door-tour-motion.spec.ts -g "AT-15"` in `apps/site`

```text
AT-15 time of the hole between the Stops: 0.0 ms
  ✘  2 [floor] › e2e/front-door-tour-motion.spec.ts:198:7 › iPhone 390x660 with motion on › when the first frames of the glide come 400 ms late, the hole and the card still glide together (AT-15) (4.3s)
    Error: the hole shows between the Stops for 80 ms or more; the hole tops at each ms: 321@0, 321@0, 321@18, 321@18, 321@34, 321@34, 321@35, 321@35, 321@36, 321@36, 321@452, 321@452, 321@862, 321@862, 377@1277, 377@1277, ...
  1 failed
  2 passed (15.1s)
```

Green: at `c3c54350`, `(CLIENT=cpc pnpm build || CLIENT=cpc pnpm build) > /dev/null 2>&1 && pnpm exec playwright test --project=floor e2e/front-door-tour-motion.spec.ts -g "AT-15"` in `apps/site`

```text
AT-15 time of the hole between the Stops: 316.7 ms
  ✓  2 [floor] › e2e/front-door-tour-motion.spec.ts:195:7 › iPhone 390x660 with motion on › the hole and the card glide together from Stop 1 to Stop 2, until the card changes side (AT-15) (3.8s)
AT-15 time of the hole between the Stops: 316.7 ms
  ✓  1 [floor] › e2e/front-door-tour-motion.spec.ts:203:7 › iPhone 390x660 with motion on › when the first frames of the glide come 400 ms late, the hole and the card still glide together (AT-15) (5.0s)
AT-15 time of the hole between the Stops: 300.0 ms
  ✓  3 [floor] › e2e/front-door-tour-motion.spec.ts:199:7 › iPhone 390x660 with motion on › on a slow runner with 150 ms frames, the hole and the card still glide together (AT-15) (2.3s)
  3 passed (7.5s)
```

The proof that the loop still fails when the hole stays at the old Stop: at `c3c54350`, with the hole transition of `tour.tsx` set to `orStill(true, GLIDE)` for one run and then put back, the same command gives:

```text
  ✘  2 [floor] › ... the hole and the card glide together from Stop 1 to Stop 2, until the card changes side (AT-15) (3.2s)
  ✘  1 [floor] › ... when the first frames of the glide come 400 ms late, the hole and the card still glide together (AT-15) (4.4s)
  ✘  3 [floor] › ... on a slow runner with 150 ms frames, the hole and the card still glide together (AT-15) (2.5s)
    Error: the hole shows between the Stops for 80 ms or more; the hole tops at each ms: 321@0, 321@0, 321@150, 321@150, 321@300, 321@300, 321@450, 321@450, 377@600, 377@600, ...
  3 failed
```
Test verdict: FAIL Question 3: `smoke.log` shows "FAIL Front door 390x660 webkit: overlap" for the Front door flow, which is the flow that this tour glide fix changes, so not each flow passed.

### 2. The card covers its control after a burst of scroll

Done condition: After each burst of scroll in WebKit at 390x660, the tour card comes to rest beside its hole and never over its control, on a loaded runner too.
Method: diagnosing-bugs
Cause: `Stops` in `apps/site/src/app/front-door/tour.tsx` reads `away` from the side of this render only, so a scroll that flips the side and back fades the card in at once at its rest place while the hole still glides back, and the card covers its control for about 80 ms. This is a product bug: a person sees it on any phone, and a slow runner reads it at full opacity. A second cause made it worse: `holeLanded` cleared only on a new Stop, so a glide from a scroll counted as landed. The fix keeps the card away until `land`, through the state `gone`, and clears `holeLanded` on each new place of the hole. The loop samples each frame of the return with one frame loop of its own, in place of one read after a poll.
Red: at `bdbdb00d`, `(CLIENT=cpc pnpm build || CLIENT=cpc pnpm build) > /dev/null 2>&1 && pnpm exec playwright test --project=floor e2e/front-door-tour-motion.spec.ts -g "WebKit 390x660"` in `apps/site`

```text
    Error: the card covers its control as it comes back after a pause of 120 ms
    - Array []
    + Array [
    +   "frame 1: opacity 0.24, gap -4.2 px, hole top 305.3",
    +   "frame 2: opacity 0.47, gap -2.7 px, hole top 306.8",
    +   "frame 3: opacity 0.67, gap -0.5 px, hole top 309.0",
    + ]
  1 failed
    [floor] › e2e/front-door-tour-motion.spec.ts:289:7 › a burst of scroll at phone width with motion on › WebKit 390x660: the card shows again beside its hole
```

The loop went red on 6 of 6 runs with `--repeat-each 3`, in WebKit 390x660 and in Chromium 375x900, each at the first pause of 120 ms.

Green: at `faf63b79`, `(CLIENT=cpc pnpm build || CLIENT=cpc pnpm build) > /dev/null 2>&1 && pnpm exec playwright test --project=floor e2e/front-door-tour-motion.spec.ts -g "WebKit 390x660"` in `apps/site`

```text
  ✓  1 [floor] › e2e/front-door-tour-motion.spec.ts:289:7 › a burst of scroll at phone width with motion on › WebKit 390x660: the card shows again beside its hole (23.2s)
  1 passed (23.9s)
```

At `faf63b79`, the full spec `front-door-tour-motion.spec.ts` gives `8 passed`, the two scroll burst tests with `--repeat-each 3` give `6 passed`, and `front-door-tour.spec.ts`, `front-door-tour-replay.spec.ts`, and `front-door-tour-look.spec.ts` give `37 passed`.
Test verdict: FAIL Question 3: `smoke.log` shows the changed Front door flow failed, and `fail-390-light.png` shows the tour card "Suggestions" over the "Checked" control, so not each flow passed.

### 3. The norcal scene is not at rest after 100 ms

Done condition: The norcal scene test of `apps/site/e2e/scene.spec.ts` passes when the scene starts late, and it still fails when the scene plays its motion before it settles.
Method: diagnosing-bugs
Cause: `runScene` in `packages/design/site/parts/scene-canvas.ts` starts in `idle` and paints the scattered lights until the IntersectionObserver reports the entry, even under reduced motion. A slow phone reports the entry late, so the canvas shows a scattered chart, then jumps to the settled chart. This is a product bug: a reader with reduced motion on a slow phone sees it. The fix starts the scene in `rest`, or `drift` for a drift, under reduced motion, so the first frame is the settled chart. The loop holds each report of the view for 30 frames in the page, and records each state that the canvas marks from its first frame.
Red: at `3374a9aa`, `(CLIENT=norcal pnpm build || CLIENT=norcal pnpm build) > /dev/null 2>&1 && CLIENT=norcal pnpm exec playwright test --project=floor e2e/scene.spec.ts -g "AT-31"` in `apps/site`

```text
  ✘  1 [floor] › e2e/scene.spec.ts:141:7 › the scene of the week page of norcal, at rest › draws the settled chart at once, the same at 0.1 s and 2.5 s, in both themes (AT-31, AT-33) (507ms)
    Error: expect(received).toBe(expected) // Object.is equality

    Expected: "rest"
    Received: "idle"

    > 170 |     expect(await stateOf(page)).toBe("rest");
  1 failed
```

The loop went red on 5 of 5 runs with `--repeat-each 5`, each with `Received: "idle"`.

Green: at `25c08da3`, `(CLIENT=norcal pnpm build || CLIENT=norcal pnpm build) > /dev/null 2>&1 && CLIENT=norcal pnpm exec playwright test --project=floor e2e/scene.spec.ts -g "AT-31"` in `apps/site`

```text
  ✓  1 [floor] › e2e/scene.spec.ts:141:7 › the scene of the week page of norcal, at rest › draws the settled chart at once, the same at 0.1 s and 2.5 s, in both themes (AT-31, AT-33) (2.9s)
  1 passed (3.4s)
```

The proof that the loop still fails when the scene plays its motion before it settles: at `25c08da3`, with the reduced-motion return of `enter` in `scene-canvas.ts` set to `if (false && motionOff)` for one run and then put back, the same command gives the output below. The frame at 2.5 s matches the frame at 0.1 s there, because the play ends before 2.5 s, so the list of states carries this check.

```text
  ✘  1 [floor] › e2e/scene.spec.ts:141:7 › the scene of the week page of norcal, at rest › draws the settled chart at once, the same at 0.1 s and 2.5 s, in both themes (AT-31, AT-33) (3.2s)
    Error: expect(received).toEqual(expected) // deep equality
      Array [
        "rest",
    +   "settle",
    +   "rest",
      ]
    > 175 |     expect(await statesOf()).toEqual(["rest"]);
  1 failed
```

At `25c08da3`, the full spec `scene.spec.ts` in the projects `floor` and `floor-timing` gives `15 passed` for norcal and `15 passed` for cpc.
Test verdict: FAIL Question 3: the Week report flow passed, but `smoke.log` shows the Front door flow failed, so not each flow passed.

### 4. The passphrase box tests time out

Done condition: Both AT-51 tests of `apps/site/e2e/front-door-passphrase.spec.ts` pass when an Announcement or the Tour opens on the load beat, and they still fail when the box sits under the keyboard.
Method: diagnosing-bugs
Cause: `front-door-passphrase.spec.ts` in `apps/site/e2e/` marks only the Announcement `season-sim-2026` seen by its id, so on a slow runner any other Announcement opens on the load beat, covers the front door, and the next tap waits out the 30 s timeout. This is a test bug: `useAnnouncement` opens an Announcement before the first tap by design and never over another sheet, so a person dismisses it, and the Tour never opens over an open modal layer. The two CI failures had causes that are already fixed: run 44526392859 ran before the spec marked the season sim Announcement seen, and run 43978248839 hit the keyboard lift of `win-one-sheet` ("element is outside of the viewport"), which `5e9ed010` fixed. The fix adds `skipAnnouncements` in `apps/site/e2e/announcement.ts`, which reads every key under `ANNOUNCEMENT_KEY_PREFIX` of `use-announcement.ts` as seen, and the spec calls it with `skipTour`. The loop starts the page clock on the release day of the season sim and moves it past the load beat, so the Announcement opens before the first tap on each run, and it drops the seen mark by id, so the season sim Announcement stands in for one that the spec does not name.
Red: at `9790fdb0`, `(CLIENT=cpc pnpm build || CLIENT=cpc pnpm build) > /dev/null 2>&1 && pnpm exec playwright test --project=floor e2e/front-door-passphrase.spec.ts -g "AT-51"` in `apps/site`

```text
  1) [floor] › e2e/front-door-passphrase.spec.ts:129:7 › the passphrase box of the passphrase modal with the iOS keyboard (AT-51) › the box sits above the keyboard with a kept team and no kept passphrase

    Error: no Announcement and no Tour covers the front door before the first tap

    expect(locator).toHaveText(expected) failed

    Locator: getByRole('dialog')
    - Array []
    + Array [
    +   "Your team ... What-if: ...Cornerstone Fantasy Football League: New: Season simSee your path to the playoffsPick this week's results and watch your playoff odds move.Open the simNot now",
    + ]
    >  97 |   await expect(page.getByRole("dialog"), "no Announcement and no Tour covers the front door before the first tap").toHaveText([]);
  1 failed
  1 passed (7.8s)
```

The loop went red on 5 of 5 runs with `--repeat-each 5`, each at the check before the first tap, in about 5.5 s and not at the 30 s timeout. The first test passes at the red commit, because its team sheet opens on load, so no Announcement opens on that load, and `skipTour` keeps the Tour away.

Green: at `59d623e0`, `(CLIENT=cpc pnpm build || CLIENT=cpc pnpm build) > /dev/null 2>&1 && pnpm exec playwright test --project=floor e2e/front-door-passphrase.spec.ts -g "AT-51"` in `apps/site`

```text
  ✓  1 [floor] › e2e/front-door-passphrase.spec.ts:134:7 › the passphrase box of the passphrase modal with the iOS keyboard (AT-51) › the box sits above the keyboard with a kept team and no kept passphrase (2.0s)
the box spans 394 to 448 px, and the keyboard starts at 516 px
  ✓  2 [floor] › e2e/front-door-passphrase.spec.ts:116:7 › the passphrase box of the passphrase modal with the iOS keyboard (AT-51) › the team sheet asks only for the team, and the box sits above the keyboard on the first Topic tap (4.1s)
  2 passed (5.9s)
```

The proof that the loop still fails when the box sits under the keyboard: at `59d623e0`, with `translate-y-[100px]` added to the `SheetContent` class of `passphrase-sheet.tsx` for one run and then put back, the same command gives:

```text
  ✘  1 [floor] › e2e/front-door-passphrase.spec.ts:134:7 › ... the box sits above the keyboard with a kept team and no kept passphrase (1.9s)
the box spans 494 to 548 px, and the keyboard starts at 516 px
  ✘  2 [floor] › e2e/front-door-passphrase.spec.ts:116:7 › ... the team sheet asks only for the team, and the box sits above the keyboard on the first Topic tap (4.0s)
    Error: the whole box is above the keyboard
    Expected: <= 516
    Received:    548
  2 failed
```

At `59d623e0`, the two AT-51 tests with `--repeat-each 5` give `10 passed`, the full spec `front-door-passphrase.spec.ts` gives `2 passed`, and `make check-fast BASE=main` passes. Other front-door specs with a kept team, such as `front-door-kept.spec.ts`, still call only `skipTour`; a later run can give them `skipAnnouncements` too.
Test verdict: FAIL Question 3: the Passphrase flow passed, but `smoke.log` shows the Front door flow failed, so not each flow passed.

### 5. The Tour card covers the status of the first answer at phone width

Done condition: In WebKit at 390x660, the overlap check of the smoke run ignores the inert page under an open Tour Stop but still finds a real overlap, and the `Front door` smoke flow passes.
Method: diagnosing-bugs
Cause: `findOverlap` in `apps/site/e2e/smoke.ts` reads each visible text of the page, so it reads the text of the inert page under the modal Stop card as an overlap. This is a smoke-check bug, not a product bug: the Stop card is a modal layer by design (AT-39, and "The Stop card" in the PRD of `front-door-tour`). It dims the page, makes it inert, and sits beside its hole. At 390x660 the hole of Stop 1 is the Suggestions row at the foot of the screen, so the card must sit over the page above it, and after a first answer that page is the answer. The Tour starts after the passphrase modal exits, by story 42 of the same PRD, so the smoke flow meets the Tour over its answer. The card covers its own control on no Stop (AT-16), and a person reads the answer after Done or Skip. The fix counts only the texts inside an open `[aria-modal="true"]` layer while one shows, the layer rule that `modalOpen` in `tour.tsx` uses. The loop drives the real front door with the fake of the API port of `front-door-scroll.spec.ts` and the recorded stream `fix.sse`, replays the Tour from the menu, and runs `findOverlap` on each Stop.
Red: at `e2598f3d`, `(CLIENT=cpc pnpm build || CLIENT=cpc pnpm build) > /dev/null 2>&1 && pnpm exec playwright test --project=floor e2e/front-door-tour-look.spec.ts -g "overlap check of the smoke run"` in `apps/site`

```text
  ✘  1 [floor] › e2e/front-door-tour-look.spec.ts:256:7 › iPhone 390x660 › the overlap check of the smoke run finds no overlap when each Stop shows over the first answer (10.7s)
    Error: Suggestions: the overlap check of the smoke run
    expect(received).toBeNull()
    Received: "<span> \"Checked\" and <span> \"Picks for your team right now. Tap one t\""
    > 265 |       await expect.poll(() => findOverlap(page), { message: `${header}: the overlap check of the smoke run` }).toBeNull();
  1 failed
```

The loop went red on 5 of 5 runs with `--repeat-each 5`, each with the same pair of texts.

Green: at `5432d4f8`, `(CLIENT=cpc pnpm build || CLIENT=cpc pnpm build) > /dev/null 2>&1 && pnpm exec playwright test --project=floor e2e/front-door-tour-look.spec.ts -g "overlap check of the smoke run"` in `apps/site`

```text
  ✓  1 [floor] › e2e/front-door-tour-look.spec.ts:256:7 › iPhone 390x660 › the overlap check of the smoke run finds no overlap when each Stop shows over the first answer (6.3s)
  1 passed (7.1s)
```

The proof that the check still finds an overlap: the rules test "a modal layer over a text of the page is no overlap, but two texts inside the layer still overlap" in `smoke-rules.spec.ts` passes at `5432d4f8`. With the skip of `findOverlap` turned off for one run and then put back, it fails with "FAIL Week report 390x660 webkit: overlap: <h1> "Week 10" and <p> "Suggestions"". The seeded overlap test with no modal layer still passes.

At `5432d4f8`, the loop with `--repeat-each 5` gives `5 passed`, the four specs `front-door-tour*.spec.ts` give `46 passed`, and `make check-fast BASE=main` passes with `834 passed` in Vitest. The done condition says the card never covers the status line. The card still sits over the dimmed, inert answer by design, so the fix reads that cover as no fault. If Brian wants the Tour to wait until the first answer is read, that is a change of story 42, not of this item.
Test verdict: pending

## Smoke

Smoke: flows `Front door`, `Passphrase`, `Week report`, `Manager page`, `Analyzer`, `Power rankings`, `Midseason report`. "Smoke run: 7 flows, 6 passed, 1 failed". Shots in `.scratch/bugs/flaky-browser-specs/smoke/`. The one failure is "FAIL Front door 390x660 webkit: overlap: <span> "Suggestions" and <span> "Checked"". The same flow on `main` at `8780eefb`, in a clean worktree, gives the same failure and "Smoke run: 1 flow, 0 passed, 1 failed", so this run did not cause it.

## Comments

- The smoke run found an old bug on `main`: at 390x660, the Suggestions Stop of the Tour opens over the "Checked" status of the first answer. It needs its own quick run.
- Other front-door specs with a kept team, such as `front-door-kept.spec.ts`, call only `skipTour` and not `skipAnnouncements`. They can flake as item 4 did, and need a later run.
- Brian added item 5 after the quick Judge gave FAIL on items 1 to 4, each on question 3, because of the old overlap of item 5. This is the one fix round.
- Brian changed the done condition of item 5 on 2026-11-19: the Tour card is a modal layer by design, so the fix is in the overlap check of the smoke run, and the card does not move.
