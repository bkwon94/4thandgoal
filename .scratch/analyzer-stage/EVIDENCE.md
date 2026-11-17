# Analyzer stage: evidence

Spec: `.scratch/analyzer-stage/PRD.md`. Acceptance tests: `.scratch/analyzer-stage/ACCEPTANCE.md`.
Built from: `7b1d09c7`, on 2026-11-17. The agent gives no Test verdict. The Judge gives one for each test in `VERDICTS.md`.
Round time: 1 min for 2 site tests with a `steps.json` (AT-18 and AT-25). Each other site test has a Playwright script, named in its `steps.txt`; the scripts are in `evidence/harness/`.

Trades of this run, from the real cpc teams route of the local API on 2026-11-17. Trade T: Bo Girds (roster 6) gives Kenneth Walker III (`8151`) to Teehee (roster 12) for Tee Higgins (`6801`) and Bhayshul Tuten (`12490`). Trade B: no roster moved. The Blue Tent gets Caleb Williams (`11560`), Travis Kelce (`1466`), Stefon Diggs (`2449`), Derrick Henry (`3198`), and Christian McCaffrey (`4034`) from Lil Fridge; All You Need Is Love gets Rashee Rice (`10229`) and Brock Bowers (`11604`) from The Blue Tent; Lil Fridge gets Ashton Jeanty (`12527`) and Jeremiyah Love (`13287`) from All You Need Is Love, and Bucky Irving (`11584`) from The Blue Tent. Trade L: All You Need Is Love (roster 2) gives Chris Olave (`8144`, WR) to Unsolicited Dak Picks (roster 11) for Tank Dell (`9502`, WR). The fairness reason of AT-32 comes from trade B, the first real trade of 3 sides graded. The norcal trade of AT-20: The Mean Machine (roster 4) gives Tyler Allgeier (`8132`) to Mitseeker5000 (roster 6) for Chris Olave (`8144`) and Devin Singletary (`6130`). Each script ran against the export of a detached worktree of `a90b3c92` and the local API `make -C apps/api api-evidence` on port 8080; `steps.txt` of each test gives the reason and the method. AT-2, AT-3, AT-5, AT-9, AT-12, AT-13, AT-15, AT-17, AT-20, and AT-29 were recorded again on `7b1d09c7`, against the export of a detached worktree of `7b1d09c7` and the local API from the same worktree; their `steps.txt` gives the method of that round.

## AT-1: The idle mesh is calm

App: site
Then: The hero shows a flat mesh at the 24 px pitch of the hero grid, with no pulses, and two screenshots 2 s apart show the same mesh.
Files: `evidence/AT-1/steps.txt`, `evidence/AT-1/output.txt`, `evidence/AT-1/1280-dark.png`, `evidence/AT-1/1280-light.png`, `evidence/AT-1/375-dark.png`, `evidence/AT-1/375-light.png`, `evidence/AT-1/768-dark.png`, `evidence/AT-1/768-light.png`, `evidence/AT-1/a-1280-dark.png`, `evidence/AT-1/a-1280-light.png`, `evidence/AT-1/b-1280-dark.png`, `evidence/AT-1/b-1280-light.png`
Observation: At each width and theme the idle hero shows a flat grid with no light dots. At 1280 px the shots a and b, 2 s apart, are byte-equal in both themes, and the canvas drew 0 frames between them. The mesh reads `--spacing-hero-grid` 24px.

## AT-2: An added player shows on the stage

App: site
Then: The row of Teehee on the stage shows "1 player" and no headshot.
Files: `evidence/AT-2/steps.txt`, `evidence/AT-2/output.txt`, `evidence/AT-2/after-1280-dark.png`, `evidence/AT-2/after-1280-light.png`, `evidence/AT-2/after-375-dark.png`, `evidence/AT-2/after-375-light.png`, `evidence/AT-2/after-768-dark.png`, `evidence/AT-2/after-768-light.png`, `evidence/AT-2/before-1280-dark.png`, `evidence/AT-2/before-1280-light.png`, `evidence/AT-2/before-375-dark.png`, `evidence/AT-2/before-375-light.png`, `evidence/AT-2/before-768-dark.png`, `evidence/AT-2/before-768-light.png`
Observation: Before the add, the log reads `none (0 rows)` and 0 headshot tokens at each width and theme, and the before shots show only "Trade Analyzer" and "Who gets what?" with no stage row. After Kenneth Walker III goes to the side of Teehee, the log reads `Bo Girdsgets | Teeheegets1 player` and 0 headshot tokens at each width and theme, and the after shots show "1 PLAYER" in the row of Teehee with no face.

## AT-3: The wait starts on the tap

App: site
Then: Within 100 ms of the tap, the mesh moves and the stage line "Weighing the sides" shows.
Files: `evidence/AT-3/steps.txt`, `evidence/AT-3/output.txt`, `evidence/AT-3/1280-dark.png`, `evidence/AT-3/1280-light.png`, `evidence/AT-3/375-dark.png`, `evidence/AT-3/375-light.png`, `evidence/AT-3/768-dark.png`, `evidence/AT-3/768-light.png`
Observation: "Weighing the sides" was in the DOM 7.2 to 19.2 ms after the tap, and two frames of the wait canvas differed 39.1 to 52.4 ms after the tap, at each width and theme. Each shot started 9 to 50 ms after the tap, not at 100 ms, and shows the line "Weighing the sides" over the mesh.

## AT-4: The grade button goes pending

App: site
Then: The button has `aria-busy="true"` and `data-pending`, it keeps the focus, its label stays "Grade the Trade", and it is the wrapper of the ui-sdk `Button`.
Files: `evidence/AT-4/steps.txt`, `evidence/AT-4/output.txt`, `evidence/AT-4/1280-dark.png`, `evidence/AT-4/1280-light.png`, `evidence/AT-4/375-dark.png`, `evidence/AT-4/375-light.png`, `evidence/AT-4/768-dark.png`, `evidence/AT-4/768-light.png`, `evidence/AT-4/wrapper.txt`
Observation: At 2 s into the wait, at each width and theme, the button has `aria-busy="true"`, `data-pending=""`, `aria-disabled="true"`, the label "Grade the Trade", and `data-slot="button"`, and `document.activeElement` is the button. `wrapper.txt` shows the import of `Button` from `@ui-sdk/react/button` in `pending-button.tsx`.

## AT-5: The mesh weighs each side in turn

App: site
Then: The mesh dips under the side of Bo Girds, then under the side of Teehee, about 1.25 s each, with light pulses on the mesh lines.
Files: `evidence/AT-5/steps.txt`, `evidence/AT-5/output.txt`, `evidence/AT-5/dip-side-0-1280-dark.png`, `evidence/AT-5/dip-side-0-1280-light.png`, `evidence/AT-5/dip-side-0-375-dark.png`, `evidence/AT-5/dip-side-0-375-light.png`, `evidence/AT-5/dip-side-0-768-dark.png`, `evidence/AT-5/dip-side-0-768-light.png`, `evidence/AT-5/dip-side-1-1280-dark.png`, `evidence/AT-5/dip-side-1-1280-light.png`, `evidence/AT-5/dip-side-1-375-dark.png`, `evidence/AT-5/dip-side-1-375-light.png`, `evidence/AT-5/dip-side-1-768-dark.png`, `evidence/AT-5/dip-side-1-768-light.png`, `evidence/AT-5/pulls-1280-dark.json`, `evidence/AT-5/video-wait-1280-dark.webm`
Observation: At 1280 px dark the side that pulls hardest runs Bo Girds 154-1133 ms, Teehee 1404-2385 ms, Bo Girds 2652-3634 ms, and Teehee 3900-4887 ms, each with a peak pull of 0.50. The dip-side-1 shots (1799 to 1872 ms) and dip-side-0 shots (3039 to 3079 ms) show the grid bent down under the row of that side with light dots on the lines; `video-wait-1280-dark.webm` holds 30 s of the wait, and its first 5 s are the dips.

## AT-6: The stage lines change every 2.5 s

App: site
Then: 4 different stage lines show in the 10 s, each for about 2.5 s, and the first is "Weighing the sides".
Files: `evidence/AT-6/steps.txt`, `evidence/AT-6/output.txt`, `evidence/AT-6/line-2-1280-dark.png`, `evidence/AT-6/line-2-1280-light.png`, `evidence/AT-6/line-2-375-dark.png`, `evidence/AT-6/line-2-375-light.png`, `evidence/AT-6/line-2-768-dark.png`, `evidence/AT-6/line-2-768-light.png`, `evidence/AT-6/line-3-1280-dark.png`, `evidence/AT-6/line-3-1280-light.png`, `evidence/AT-6/line-3-375-dark.png`, `evidence/AT-6/line-3-375-light.png`, `evidence/AT-6/line-3-768-dark.png`, `evidence/AT-6/line-3-768-light.png`
Observation: At 1280 px dark the lines in 10 s are "Weighing the sides" at 23 ms, "Checking roster fit" at 2533 ms, "Reading Tee Higgins's season" at 5035 ms, and "Reading the standings" at 7537 ms. The other widths show the same 2.5 s steps. At 375 px light, the first session of the run, line 3 is "Weighing what Your Team gives up" in place of "Reading Tee Higgins's season".

## AT-7: A stage line names the trade

App: site
Then: At least one stage line names Kenneth Walker III, Tee Higgins, Bhayshul Tuten, Bo Girds, or Teehee.
Files: `evidence/AT-7/steps.txt`, `evidence/AT-7/output.txt`, `evidence/AT-7/1280-dark.png`, `evidence/AT-7/1280-light.png`, `evidence/AT-7/375-dark.png`, `evidence/AT-7/375-light.png`, `evidence/AT-7/768-dark.png`, `evidence/AT-7/768-light.png`
Observation: At 1280 px dark the 13 lines in 30.6 s include "Reading Tee Higgins's season", "Checking Teehee's depth at RB", "Weighing what bkwon gives up", and "Reading Kenneth Walker III's season". The shots at about 6.2 s show "Reading Tee Higgins's season", except 375 px light, which shows "Weighing what Your Team gives up".

## AT-8: The stage lines never claim a step is done

App: site
Then: Each list has 12 lines, line 1 is "Weighing the sides", line 12 is "Weighing it all together", and no line says Jev, Advisor, Finder, front door, rival, done, or finished.
Files: `evidence/AT-8/output.txt`, `evidence/AT-8/at8-evidence.test.ts`
Observation: The vitest run of `stage-lines.test.ts` gives 10 of 10 tests passed. The scratch test prints the 12 lines of trade T and of trade B: each list starts with "Weighing the sides" and ends with "Weighing it all together", and its checks of the count and the banned words passed.

## AT-9: A screen reader hears one message

App: site
Then: Two snapshots of the accessibility tree, at 2 s and at 7 s, show the same one status, "Grading the trade", and no stage line.
Files: `evidence/AT-9/steps.txt`, `evidence/AT-9/output.txt`, `evidence/AT-9/2s-1280-dark.png`, `evidence/AT-9/2s-1280-light.png`, `evidence/AT-9/2s-375-dark.png`, `evidence/AT-9/2s-375-light.png`, `evidence/AT-9/2s-768-dark.png`, `evidence/AT-9/2s-768-light.png`, `evidence/AT-9/7s-1280-dark.png`, `evidence/AT-9/7s-1280-light.png`, `evidence/AT-9/7s-375-dark.png`, `evidence/AT-9/7s-375-light.png`, `evidence/AT-9/7s-768-dark.png`, `evidence/AT-9/7s-768-light.png`, `evidence/AT-9/aria-2s-1280-dark.yaml`, `evidence/AT-9/aria-2s-1280-light.yaml`, `evidence/AT-9/aria-2s-375-dark.yaml`, `evidence/AT-9/aria-2s-375-light.yaml`, `evidence/AT-9/aria-2s-768-dark.yaml`, `evidence/AT-9/aria-2s-768-light.yaml`, `evidence/AT-9/aria-7s-1280-dark.yaml`, `evidence/AT-9/aria-7s-1280-light.yaml`, `evidence/AT-9/aria-7s-375-dark.yaml`, `evidence/AT-9/aria-7s-375-light.yaml`, `evidence/AT-9/aria-7s-768-dark.yaml`, `evidence/AT-9/aria-7s-768-light.yaml`
Observation: At 2 s and at 7 s, at each width and theme, the tree holds the region and heading "Grading the Trade" and one status node, `status: Grading the trade`; each of the 12 aria files has one line with "status". The stage lines shown by 7 s, "Weighing the sides", "Checking roster fit", and "Reading Tee Higgins's season", are in neither tree.

## AT-10: The grade shows with no fake delay

App: site
Then: The Lean word shows within 1.3 s of the analyze response.
Files: `evidence/AT-10/steps.txt`, `evidence/AT-10/output.txt`, `evidence/AT-10/1280-dark.png`, `evidence/AT-10/1280-light.png`, `evidence/AT-10/375-dark.png`, `evidence/AT-10/375-light.png`, `evidence/AT-10/768-dark.png`, `evidence/AT-10/768-light.png`
Observation: The grade is a cached repeat after the first real grade of trade T (36 s). Its response came 2.2 to 3.2 s after the POST, and the Lean word "Lean yes" was at rest 251 to 261 ms after the response, at each width and theme. The full-page shots show the result.

## AT-11: The reveal shows the Lean first

App: site
Then: The Lean word shows first, then the Lean scale, then the Case and the side tabs, all within about 1 s.
Files: `evidence/AT-11/steps.txt`, `evidence/AT-11/output.txt`, `evidence/AT-11/1280-dark.png`, `evidence/AT-11/1280-light.png`, `evidence/AT-11/375-dark.png`, `evidence/AT-11/375-light.png`, `evidence/AT-11/768-dark.png`, `evidence/AT-11/768-light.png`, `evidence/AT-11/video-reveal-1280-dark.webm`
Observation: From the response, at each width and theme: the Lean word at rest at 251 to 261 ms, the scale at 476 to 489 ms, the side tabs at 926 to 953 ms, and the Case at 974 to 1003 ms. The shots show the read hero at the end of the reveal. The video is `video-reveal-1280-dark.webm`.

## AT-12: The mesh dips toward the favored side

App: site
Then: The mesh lines of the favored side flash once, then the mesh dips toward that side and goes flat.
Files: `evidence/AT-12/steps.txt`, `evidence/AT-12/output.txt`, `evidence/AT-12/answer-T.json`, `evidence/AT-12/dip-1280-dark.png`, `evidence/AT-12/dip-1280-light.png`, `evidence/AT-12/dip-375-dark.png`, `evidence/AT-12/dip-375-light.png`, `evidence/AT-12/dip-768-dark.png`, `evidence/AT-12/dip-768-light.png`, `evidence/AT-12/flash-1280-dark.png`, `evidence/AT-12/flash-1280-light.png`, `evidence/AT-12/flash-375-dark.png`, `evidence/AT-12/flash-375-light.png`, `evidence/AT-12/flash-768-dark.png`, `evidence/AT-12/flash-768-light.png`, `evidence/AT-12/mesh-1280-dark.json`, `evidence/AT-12/video-reveal-1280-dark.webm`
Observation: `answer-T.json` gives the Lean "Lean yes" for Bo Girds, the asker, with fairness fair; at each width and theme the flash peaks at 0.95 to 0.992 at 88 to 93 ms after the response, only side 0, Bo Girds, pulls (0.550, side 1 0.000), and the last pulls are 0,0. The light in the box of each row at the flash peak is 255636 to 662459 for Bo Girds and 76085 to 197480 for Teehee, against 69945 to 158533 and 74929 to 165854 at rest; the flash and dip shots show the lit lines in the row of Bo Girds, and the video is `video-reveal-1280-dark.webm`.

## AT-13: With motion off, the hero stays still

App: site
Then: The mesh does not move during the wait, and the result appears in a plain fade.
Files: `evidence/AT-13/steps.txt`, `evidence/AT-13/output.txt`, `evidence/AT-13/result-1280-dark.png`, `evidence/AT-13/result-1280-light.png`, `evidence/AT-13/result-375-dark.png`, `evidence/AT-13/result-375-light.png`, `evidence/AT-13/result-768-dark.png`, `evidence/AT-13/result-768-light.png`, `evidence/AT-13/video-reveal-1280-dark.webm`, `evidence/AT-13/wait-a-1280-dark.png`, `evidence/AT-13/wait-a-1280-light.png`, `evidence/AT-13/wait-a-375-dark.png`, `evidence/AT-13/wait-a-375-light.png`, `evidence/AT-13/wait-a-768-dark.png`, `evidence/AT-13/wait-a-768-light.png`, `evidence/AT-13/wait-b-1280-dark.png`, `evidence/AT-13/wait-b-1280-light.png`, `evidence/AT-13/wait-b-375-dark.png`, `evidence/AT-13/wait-b-375-light.png`, `evidence/AT-13/wait-b-768-dark.png`, `evidence/AT-13/wait-b-768-light.png`
Observation: Wait: at each width and theme the wait canvas drew 2 frames by 1 s and 3 frames by 3 s, 0 of its pixels differ between 1 s and 3 s, and its pulls stay 0.000,0.000. Reveal: at each width and theme the opacity of the result rises from 0.00 to 1, the Lean word moves 0.00 px, and the mesh flash max and pull max are 0; the video is `video-reveal-1280-dark.webm`.

## AT-14: With motion off, the stage lines still change

App: site
Then: The stage line changes about every 2.5 s, with no shimmer.
Files: `evidence/AT-14/steps.txt`, `evidence/AT-14/output.txt`, `evidence/AT-14/line-1-1280-dark.png`, `evidence/AT-14/line-1-1280-light.png`, `evidence/AT-14/line-1-375-dark.png`, `evidence/AT-14/line-1-375-light.png`, `evidence/AT-14/line-1-768-dark.png`, `evidence/AT-14/line-1-768-light.png`, `evidence/AT-14/line-2-1280-dark.png`, `evidence/AT-14/line-2-1280-light.png`, `evidence/AT-14/line-2-375-dark.png`, `evidence/AT-14/line-2-375-light.png`, `evidence/AT-14/line-2-768-dark.png`, `evidence/AT-14/line-2-768-light.png`
Observation: With reduced motion, at each width and theme, the lines show at about 10 ms, 2520 ms, and 5020 ms. The line has the class `is-still`, its `::before` has `display none`, and no animation runs in the hero. At 375 px light, line 3 is "Weighing what Your Team gives up".

## AT-15: The wait stays smooth on a phone

App: site
Then: In at least 3 of the 4 runs, no frame of the wait after the first second takes longer than 50 ms.
Files: `evidence/AT-15/steps.txt`, `evidence/AT-15/output.txt`, `evidence/AT-15/1280-dark.png`, `evidence/AT-15/1280-light.png`, `evidence/AT-15/375-dark.png`, `evidence/AT-15/375-light.png`, `evidence/AT-15/768-dark.png`, `evidence/AT-15/768-light.png`, `evidence/AT-15/frames-375-4x-run1.txt`, `evidence/AT-15/frames-375-4x-run2.txt`, `evidence/AT-15/frames-375-4x-run3.txt`, `evidence/AT-15/frames-375-4x-run4.txt`, `evidence/AT-15/trace-375-4x-run1.json.gz`, `evidence/AT-15/trace-375-4x-run2.json.gz`, `evidence/AT-15/trace-375-4x-run3.json.gz`, `evidence/AT-15/trace-375-4x-run4.json.gz`
Observation: In 4 separate runs at 375 px with a 4x CPU slowdown, the longest frame from 1 s to 5 s after the tap is 16.8, 16.8, 66.6, and 33.3 ms, with 0, 0, 1, and 0 frames over 50 ms. The shots show the wait at 5 s at each width and theme, with no slowdown.

## AT-16: The canvas pauses out of view

App: site
Then: The canvas draws no frame while the hero is out of view, and no frame while the tab is hidden.
Files: `evidence/AT-16/steps.txt`, `evidence/AT-16/output.txt`, `evidence/AT-16/1280-dark.png`, `evidence/AT-16/1280-light.png`, `evidence/AT-16/375-dark.png`, `evidence/AT-16/375-light.png`, `evidence/AT-16/768-dark.png`, `evidence/AT-16/768-light.png`
Observation: The page of the wait is no taller than the view, so the script added an empty 2000 px block to scroll the hero out. Out of view the canvas drew 0 frames over 2 s, and back in view it drew 62 to 76 frames in 1 s. With the page reported hidden through `visibilitychange`, the canvas drew 0 frames over 2 s, at each width and theme.

## AT-17: Hero text has no dark box

App: site
Then: No hero text sits on the plate box, and the record pills, the stat tiles, and the buttons keep their own fill.
Files: `evidence/AT-17/steps.txt`, `evidence/AT-17/output.txt`, `evidence/AT-17/404-1280-dark.png`, `evidence/AT-17/404-1280-light.png`, `evidence/AT-17/404-375-dark.png`, `evidence/AT-17/404-375-light.png`, `evidence/AT-17/404-768-dark.png`, `evidence/AT-17/404-768-light.png`, `evidence/AT-17/analyzer-result-1280-dark.png`, `evidence/AT-17/analyzer-result-1280-light.png`, `evidence/AT-17/analyzer-result-375-dark.png`, `evidence/AT-17/analyzer-result-375-light.png`, `evidence/AT-17/analyzer-result-768-dark.png`, `evidence/AT-17/analyzer-result-768-light.png`, `evidence/AT-17/manager-bo-girds-1280-dark.png`, `evidence/AT-17/manager-bo-girds-1280-light.png`, `evidence/AT-17/manager-bo-girds-375-dark.png`, `evidence/AT-17/manager-bo-girds-375-light.png`, `evidence/AT-17/manager-bo-girds-768-dark.png`, `evidence/AT-17/manager-bo-girds-768-light.png`, `evidence/AT-17/midseason-1280-dark.png`, `evidence/AT-17/midseason-1280-light.png`, `evidence/AT-17/midseason-375-dark.png`, `evidence/AT-17/midseason-375-light.png`, `evidence/AT-17/midseason-768-dark.png`, `evidence/AT-17/midseason-768-light.png`, `evidence/AT-17/week-09-1280-dark.png`, `evidence/AT-17/week-09-1280-light.png`, `evidence/AT-17/week-09-375-dark.png`, `evidence/AT-17/week-09-375-light.png`, `evidence/AT-17/week-09-768-dark.png`, `evidence/AT-17/week-09-768-light.png`
Observation: The plate scan finds 0 texts on a plate box on every page at each width and theme (band color rgb(20, 20, 20)); the W and L texts sit on record pills (10 on the manager page), the tile texts on stat tiles (8 on the manager page, 12 on the midseason opener), "Go to Week 10" and "Go Home" on buttons on the 404 page, and the 10 week 9 texts on no fill. On the analyzer result, the 8 texts of the fairness block sit on an other fill, the card `rounded-card border bg-card`, rgb(31, 31, 31) in dark and rgb(255, 255, 255) in light, as the result shots show.

## AT-18: The floor reads every hero text

App: site
Then: Each hero text on each page of the floor reaches 4.5:1 or more, at 390 and 1280 px, and the floor passes.
Files: `evidence/AT-18/steps.json`, `evidence/AT-18/cpc-1280-dark.png`, `evidence/AT-18/cpc-1280-light.png`, `evidence/AT-18/cpc-375-dark.png`, `evidence/AT-18/cpc-375-light.png`, `evidence/AT-18/cpc-768-dark.png`, `evidence/AT-18/cpc-768-light.png`, `evidence/AT-18/floor-cpc.txt`, `evidence/AT-18/floor-norcal.txt`, `evidence/AT-18/norcal-1280-dark.png`, `evidence/AT-18/norcal-1280-light.png`, `evidence/AT-18/norcal-375-dark.png`, `evidence/AT-18/norcal-375-light.png`, `evidence/AT-18/norcal-768-dark.png`, `evidence/AT-18/norcal-768-light.png`, `evidence/AT-18/runner.txt`, `evidence/AT-18/worst-cpc.txt`, `evidence/AT-18/worst-norcal.txt`
Observation: `CLIENT=cpc pnpm check:floor` gives 199 passed and 8 skipped, and norcal gives 193 passed and 11 skipped, on builds made as the check makes them. The worst hero ratio is 4.57:1 in cpc and 4.56:1 in norcal (`worst-cpc.txt`, `worst-norcal.txt`). The runner shots show the week 9 hero of each client.

## AT-19: The losing score of the week hero stays readable

App: site
Then: The score 106.71 reaches 4.5:1 or more at 390 and 1280 px.
Files: `evidence/AT-19/steps.txt`, `evidence/AT-19/output.txt`, `evidence/AT-19/1280-dark.png`, `evidence/AT-19/1280-light.png`, `evidence/AT-19/375-dark.png`, `evidence/AT-19/375-light.png`, `evidence/AT-19/768-dark.png`, `evidence/AT-19/768-light.png`
Observation: The pixel scan reads the text "106.71" of the week 9 hero at 5.66:1 at 390 px and 5.45:1 at 1280 px, in both themes. The shots show the hero with the score of Maye d'force B with U.

## AT-20: The analyzer text stays readable while the mesh moves

App: site
Then: Each hero text, including the row label of each side, reaches 4.5:1 or more in each state, at 390 and 1280 px.
Files: `evidence/AT-20/steps.txt`, `evidence/AT-20/output.txt`, `evidence/AT-20/cpc-idle-1280-dark.png`, `evidence/AT-20/cpc-idle-1280-light.png`, `evidence/AT-20/cpc-idle-375-dark.png`, `evidence/AT-20/cpc-idle-375-light.png`, `evidence/AT-20/cpc-idle-768-dark.png`, `evidence/AT-20/cpc-idle-768-light.png`, `evidence/AT-20/cpc-reveal-1280-dark.png`, `evidence/AT-20/cpc-reveal-1280-light.png`, `evidence/AT-20/cpc-reveal-375-dark.png`, `evidence/AT-20/cpc-reveal-375-light.png`, `evidence/AT-20/cpc-reveal-768-dark.png`, `evidence/AT-20/cpc-reveal-768-light.png`, `evidence/AT-20/cpc-wait-1280-dark.png`, `evidence/AT-20/cpc-wait-1280-light.png`, `evidence/AT-20/cpc-wait-375-dark.png`, `evidence/AT-20/cpc-wait-375-light.png`, `evidence/AT-20/cpc-wait-768-dark.png`, `evidence/AT-20/cpc-wait-768-light.png`, `evidence/AT-20/norcal-idle-1280-dark.png`, `evidence/AT-20/norcal-idle-1280-light.png`, `evidence/AT-20/norcal-idle-375-dark.png`, `evidence/AT-20/norcal-idle-375-light.png`, `evidence/AT-20/norcal-idle-768-dark.png`, `evidence/AT-20/norcal-idle-768-light.png`, `evidence/AT-20/norcal-reveal-1280-dark.png`, `evidence/AT-20/norcal-reveal-1280-light.png`, `evidence/AT-20/norcal-reveal-375-dark.png`, `evidence/AT-20/norcal-reveal-375-light.png`, `evidence/AT-20/norcal-reveal-768-dark.png`, `evidence/AT-20/norcal-reveal-768-light.png`, `evidence/AT-20/norcal-wait-1280-dark.png`, `evidence/AT-20/norcal-wait-1280-light.png`, `evidence/AT-20/norcal-wait-375-dark.png`, `evidence/AT-20/norcal-wait-375-light.png`, `evidence/AT-20/norcal-wait-768-dark.png`, `evidence/AT-20/norcal-wait-768-light.png`
Observation: The worst ratio in idle is 9.18:1 in cpc and 8.81:1 in norcal; over 10 to 12 wait samples in 3122 to 3266 ms it is 6.98:1 in cpc and 8.10:1 in norcal ("This can take up to a minute."); at the end of the reveal it is 5.74:1 in cpc and 5.91:1 in norcal ("This week's player values are not out ye", as the log cuts it). The row labels read at worst Bo Girds 15.13:1 idle, 14.09:1 wait, and 5.74:1 reveal end, Teehee 15.13:1, 14.28:1, and 5.74:1, The Mean Machine 13.85:1, 10.60:1, and 5.91:1, and Mitseeker5000 13.85:1, 11.53:1, and 5.91:1, at 390 and 1280 px in both themes.

## AT-21: The egg banner text stays readable

App: site
Then: Each text of the egg banner reaches 4.5:1 or more at 390 and 1280 px.
Files: `evidence/AT-21/steps.txt`, `evidence/AT-21/output.txt`, `evidence/AT-21/1280-dark.png`, `evidence/AT-21/1280-light.png`, `evidence/AT-21/375-dark.png`, `evidence/AT-21/375-light.png`, `evidence/AT-21/768-dark.png`, `evidence/AT-21/768-light.png`
Observation: Test egg T1 dropped with HTTP 200. On the home page, the banner "1 egg dropped today · 1 left" and its "Egg board" link read 9.72:1 or more at 390 and 1280 px in both themes.

## AT-22: The floor still catches a gap

App: site
Then: The floor fails in both cases, and each failure names the case.
Files: `evidence/AT-22/output.txt`, `evidence/AT-22/tests.txt`
Observation: The command runs the two tests of `floor-rules.spec.ts`: an incomplete axe result outside a hero, and a hero with no text. Both gave the expected failure lines, named in `tests.txt`, and the run shows 2 passed.

## AT-23: The Finder keeps Sweep

App: site
Then: The Finder wait shows the `Sweep` bar, and no mesh and no stage line.
Files: `evidence/AT-23/steps.txt`, `evidence/AT-23/output.txt`, `evidence/AT-23/1280-dark.png`, `evidence/AT-23/1280-light.png`, `evidence/AT-23/375-dark.png`, `evidence/AT-23/375-light.png`, `evidence/AT-23/768-dark.png`, `evidence/AT-23/768-light.png`
Observation: In the norcal Finder wait, at each width and theme, the button reads "Finding…", one Sweep bar part shows, and the log counts 0 canvases in the Finder, 0 grading heroes, and 0 stage line parts.

## AT-24: The front door chat wait does not change

App: site
Then: The chat wait shows no mesh and no stage line.
Files: `evidence/AT-24/steps.txt`, `evidence/AT-24/output.txt`, `evidence/AT-24/1280-dark.png`, `evidence/AT-24/1280-light.png`, `evidence/AT-24/375-dark.png`, `evidence/AT-24/375-light.png`, `evidence/AT-24/768-dark.png`, `evidence/AT-24/768-light.png`
Observation: 1.5 s after Send, at each width and theme, the chat shows the question and "Reading the league…" with a dot spinner. The log counts 0 mesh canvases, 0 stage line parts, and 0 grading heroes.

## AT-25: The hero scene does not change

App: site
Then: The hero scene keeps its own row, and no light of the scene sits under a hero text.
Files: `evidence/AT-25/steps.json`, `evidence/AT-25/1280-dark.png`, `evidence/AT-25/1280-light.png`, `evidence/AT-25/375-dark.png`, `evidence/AT-25/375-light.png`, `evidence/AT-25/768-dark.png`, `evidence/AT-25/768-light.png`
Observation: The runner shots show the week 9 hero with its scene of dots in its own row above the two team rows and scores, in both themes at each width.

## AT-26: The analyze call stays one request with no stream

App: site
Then: The network log shows one `POST` to the analyze route, with a JSON response, not `text/event-stream`.
Files: `evidence/AT-26/steps.txt`, `evidence/AT-26/output.txt`, `evidence/AT-26/1280-dark.png`, `evidence/AT-26/1280-light.png`, `evidence/AT-26/375-dark.png`, `evidence/AT-26/375-light.png`, `evidence/AT-26/768-dark.png`, `evidence/AT-26/768-light.png`, `evidence/AT-26/network-cached-grade-1280-dark.txt`, `evidence/AT-26/network-first-grade-1280-dark.txt`
Observation: At each width and theme the network log shows one `POST /clients/cpc/analyze` and one 200 response with `content-type: application/json` and no transfer-encoding. The first uncached grade shows the same, after 36 s (`network-first-grade-1280-dark.txt`).

## AT-27: A big trade stays compact

App: site
Then: The stage shows 3 rows, one per side, and the row of The Blue Tent shows 3 headshots and a "+2" token.
Files: `evidence/AT-27/steps.txt`, `evidence/AT-27/output.txt`, `evidence/AT-27/1280-dark.png`, `evidence/AT-27/1280-light.png`, `evidence/AT-27/375-dark.png`, `evidence/AT-27/375-light.png`, `evidence/AT-27/768-dark.png`, `evidence/AT-27/768-light.png`
Observation: At each width and theme the wait hero shows 3 rows of 44 px. The Blue Tent shows Caleb Williams, Travis Kelce, and Stefon Diggs as photos and a "+2" token; Lil Fridge shows 3 photos, and All You Need Is Love shows 2.

## AT-28: Idle shows no headshot on the stage

App: site
Then: The row of Bo Girds shows "2 players", the row of Teehee shows "1 player", and the hero shows no headshot.
Files: `evidence/AT-28/steps.txt`, `evidence/AT-28/output.txt`, `evidence/AT-28/1280-dark.png`, `evidence/AT-28/1280-light.png`, `evidence/AT-28/375-dark.png`, `evidence/AT-28/375-light.png`, `evidence/AT-28/768-dark.png`, `evidence/AT-28/768-light.png`
Observation: At each width and theme the rows read "Bo Girds gets 2 players" and "Teehee gets 1 player", with 0 headshot tokens. The only images in the hero are the two team avatars.

## AT-29: The headshots rise into the rows on the tap

App: site
Then: Within 1 s, the row of Bo Girds shows the headshots of Tee Higgins and Bhayshul Tuten, and the row of Teehee shows the headshot of Kenneth Walker III.
Files: `evidence/AT-29/steps.txt`, `evidence/AT-29/output.txt`, `evidence/AT-29/1280-dark.png`, `evidence/AT-29/1280-light.png`, `evidence/AT-29/375-dark.png`, `evidence/AT-29/375-light.png`, `evidence/AT-29/768-dark.png`, `evidence/AT-29/768-light.png`
Observation: The last of 3 headshot tokens came to rest 599 to 619 ms after the tap at each width and theme. Bo Girds shows Tee Higgins and Bhayshul Tuten, and Teehee shows Kenneth Walker III, each a loaded photo from sleepercdn.com, and each shot started 1005 to 1080 ms after the tap.

## AT-30: The result shows the players once

App: site
Then: The result has no "The Trade" chapter, and below the hero it has no player chip, no headshot, and no `FoldLine` card.
Files: `evidence/AT-30/steps.txt`, `evidence/AT-30/output.txt`, `evidence/AT-30/1280-dark.png`, `evidence/AT-30/1280-light.png`, `evidence/AT-30/375-dark.png`, `evidence/AT-30/375-light.png`, `evidence/AT-30/768-dark.png`, `evidence/AT-30/768-light.png`
Observation: At each width and theme, for each side tab, the log counts 0 headings "The Trade", 0 groups "The trade", 0 visible images, 0 player chips, and 0 fold-line parts below the read hero. The full-page shots show the headshots only in the hero.

## AT-31: Edit sits in the header of The Sides

App: site
Then: The Stack opens with trade T and scrolls into view, and the target of Edit is 44 px or more on each side.
Files: `evidence/AT-31/steps.txt`, `evidence/AT-31/output.txt`, `evidence/AT-31/header-1280-dark.png`, `evidence/AT-31/header-1280-light.png`, `evidence/AT-31/header-375-dark.png`, `evidence/AT-31/header-375-light.png`, `evidence/AT-31/header-768-dark.png`, `evidence/AT-31/header-768-light.png`, `evidence/AT-31/stack-1280-dark.png`, `evidence/AT-31/stack-1280-light.png`, `evidence/AT-31/stack-375-dark.png`, `evidence/AT-31/stack-375-light.png`, `evidence/AT-31/stack-768-dark.png`, `evidence/AT-31/stack-768-light.png`
Observation: The Edit target is 59.0 x 44.0 px at 375 px, 60.9 x 44.0 at 768 px, and 62.8 x 44.0 at 1280 px. It sits on the line of the heading The Sides, to its right. After the tap the region "Who gets what" is in view and names Tee Higgins, Bhayshul Tuten, and Kenneth Walker III, at each width and theme.

## AT-32: A long fairness reason folds

App: site
Then: Before the tap the reason shows 3 lines and "More", and after the tap it shows in full.
Files: `evidence/AT-32/steps.txt`, `evidence/AT-32/output.txt`, `evidence/AT-32/after-1280-dark.png`, `evidence/AT-32/after-1280-light.png`, `evidence/AT-32/after-375-dark.png`, `evidence/AT-32/after-375-light.png`, `evidence/AT-32/after-768-dark.png`, `evidence/AT-32/after-768-light.png`, `evidence/AT-32/before-1280-dark.png`, `evidence/AT-32/before-1280-light.png`, `evidence/AT-32/before-375-dark.png`, `evidence/AT-32/before-375-light.png`, `evidence/AT-32/before-768-dark.png`, `evidence/AT-32/before-768-light.png`
Observation: Trade B, graded for real at 375 px dark (32 s), gives the reason of The Blue Tent "The Blue Tent adds McCaffrey and Henry at RB, plus a QB, a TE, and a WR, for an injured TE and two others." At 375 px it shows 3 of 4 lines and More, a 44 x 44 px target; after the tap it shows 4 of 4 lines and no More. At 768 and 1280 px it fits in 2 lines with no More. The other reasons run 3 lines or fewer.

## AT-33: A long stage line shows in full

App: site
Then: Each stage line is set at the size of `text-body`, and a line wider than the hero scrolls from right to left until its end is in view.
Files: `evidence/AT-33/steps.txt`, `evidence/AT-33/output.txt`, `evidence/AT-33/end-1280-dark.png`, `evidence/AT-33/end-1280-light.png`, `evidence/AT-33/end-375-dark.png`, `evidence/AT-33/end-375-light.png`, `evidence/AT-33/end-768-dark.png`, `evidence/AT-33/end-768-light.png`, `evidence/AT-33/start-1280-dark.png`, `evidence/AT-33/start-1280-light.png`, `evidence/AT-33/start-375-dark.png`, `evidence/AT-33/start-375-light.png`, `evidence/AT-33/start-768-dark.png`, `evidence/AT-33/start-768-light.png`, `evidence/AT-33/video-375-dark.webm`
Observation: At 375 px, trade L line "Checking Unsolicited Dak Picks's depth at WR" is 307 px wide in a line box of 293 px, in a hero of 341 px, with `--think-scroll -14px`. Its left edge moves from 41.0 to 27.0 px, and its right edge rests at 334.1 px. Each line is 14px at 375 px, 15px at 768 px, and 16px at 1280 px, the three values of `--text-body`. The line fits at 768 and 1280 px and does not move there. The video is `video-375-dark.webm`.

## AT-34: With motion off, a long stage line wraps

App: site
Then: The line wraps to a second line in full and does not move.
Files: `evidence/AT-34/steps.txt`, `evidence/AT-34/output.txt`, `evidence/AT-34/a-1280-dark.png`, `evidence/AT-34/a-1280-light.png`, `evidence/AT-34/a-375-dark.png`, `evidence/AT-34/a-375-light.png`, `evidence/AT-34/a-768-dark.png`, `evidence/AT-34/a-768-light.png`, `evidence/AT-34/b-1280-dark.png`, `evidence/AT-34/b-1280-light.png`, `evidence/AT-34/b-375-dark.png`, `evidence/AT-34/b-375-light.png`, `evidence/AT-34/b-768-dark.png`, `evidence/AT-34/b-768-light.png`
Observation: With reduced motion at 375 px, the line "Checking Unsolicited Dak Picks's depth at WR" has class `is-still`, `white-space normal`, and 2 lines (39.2 px at a line height of 19.6px), with the same rect and transform `none` in the shots 1 s apart. At 768 and 1280 px it fits on 1 line.
