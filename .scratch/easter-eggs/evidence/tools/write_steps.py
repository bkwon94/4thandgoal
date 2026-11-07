"""
Write evidence/AT-<n>/steps.txt for each site test of easter-eggs: how the shots and the logs of the test were made.
Run it from the repo root with python3. The text of each test names its phase of tools/site.spec.ts.
"""
import os
import sys
from pathlib import Path

# EGGS_EV moves the output to a folder outside the repo. The arguments name the tests to write, or none for all.
EV = Path(os.environ.get("EGGS_EV") or Path(__file__).resolve().parent.parent)
HEAD = """The runner of apps/site (pnpm --dir apps/site evidence easter-eggs) serves on its fixed port 4173, and this run may
not use 4173, because another local stack of the commissioner shares the machine. So the shots come from Playwright
directly, with tools/site.spec.ts and tools/playwright.config.ts of this evidence folder.

1. Build each client against the local API: CLIENT=cpc NEXT_PUBLIC_API_URL=http://localhost:8080 pnpm build, and the
   same for CLIENT=norcal. Copy each apps/site/out to <scratch>/out-cpc and <scratch>/out-norcal, outside the repo.
2. The spec serves out-cpc on http://127.0.0.1:4174 and out-norcal on http://127.0.0.1:4175. A missing path gets
   404.html with the status 404, as the Worker gives it.
3. The spec starts the local API with tools/start-api.sh: the values of make -C apps/api api-evidence (passphrase
   localtest, commissioner key localkey, 600 requests a minute), CORNERSTONE_EGGS_DIR=<scratch>/eggs-<store>, a temp
   folder outside the repo, and CORNERSTONE_ALLOWED_ORIGINS=http://127.0.0.1:4173,http://127.0.0.1:4174.
   A restart of the API keeps the store and clears the limits of each address, which live in memory.
4. The spec sets each state with the real routes of the API: drop, check, claim, and undo.
5. Each browser context sets cpc.theme in local storage before the first paint, so the page opens in the theme of the
   shot. A dark shot of a find of T1 finds T1 in the light theme, because T1 holds only in the light theme, then
   switches the page to the dark theme as the theme button does: the class "dark" on the root and cpc.theme.
6. The real path of each route is /clients/cpc/eggs/<route>. The tests write /cpc/eggs/.

Run: cd apps/site && EGGS_SCRATCH=<scratch> EGGS_EV=<scratch>/ev pnpm exec playwright test -c ../../.scratch/easter-eggs/evidence/tools/playwright.config.ts -g "<phase>"

This test:
"""

STEPS = {
    24: 'Phase A0. Store A, empty. For each width and theme: open http://127.0.0.1:4175/ (NorCal), full-page shot home-<w>-<theme>.png, count the links to /eggs/, triple-tap two spots and count the egg checks sent, then open /eggs/ and take eggs-<w>-<theme>.png. The pipeline part is in output.txt.',
    25: 'Phase A1. Store A, the six eggs of week 9. For each width and theme: open /2026/week-08/, one Playwright click on button[aria-controls="recap-3"], wait 1.2 s, viewport shot. The page logs each request to /eggs/check.',
    26: 'Phase L. 1280 px, light. Open /midseason/2026/ and wait for the egg button, because the listener mounts only after the board names a drop. Two mouse taps on the middle of [data-stable-id="luck-3"], 150 ms apart. The page logs the pointerup times and each request body to /eggs/check. Phase A1 runs the same double-tap; its log is site-A1.txt.',
    27: 'Phase A1. 1280 px, light. Open /midseason/2026/ and wait for the egg button. Mouse down on the middle of [data-stable-id="luck-3"], wait 3.5 s, mouse up, wait 1 s. Then mouse down, wait 1.5 s, mouse up, wait 1 s. The page logs the checks that each press sent to /eggs/check.',
    28: 'Phase A1. 1280 px, light. Open /2026/week-08/, tap [data-stable-id="number-top-score"] (A), wait 600 ms, tap [data-stable-id="number-median"] (B), wait 600 ms, then two taps 120 ms apart on [data-stable-id="number-closest"] (C). The page logs each request body to /eggs/check.',
    29: 'Phase A1. 1280 px, light. Open /midseason/2026/, select the first whole word of [data-stable-id="blurb-1jo5mqe"] with a DOM range (document.getSelection().addRange), wait 1.5 s. The page logs each request body to /eggs/check.',
    30: 'Phase L. 1280 px, light. Open /midseason/2026/, wait for the egg button, and tap "Sim the season". A watch in the page logs the time of each change of the text of [data-stable-id="sim-row-3"] (a new frame) and each pointerup. The spec learns the time of one frame, then taps the row two times, 200 ms apart, from 150 ms before the next frame. The page logs each request body to /eggs/check. Phase A1 runs two taps 250 ms apart with a read of the frame before and after each tap; its log is site-A1.txt.',
    31: 'tools/callout.spec.ts, in the WebKit of Playwright, because Chromium does not compute -webkit-touch-callout. Open /midseason/2026/ at 375 px and read getComputedStyle(...).getPropertyValue("-webkit-touch-callout") of the Luck cell, a link, and an image.',
    32: 'Phase A1. For each width and theme: open /midseason/2026/ in the light theme, wait for the egg button, double-tap (click clickCount 2) [data-stable-id="luck-3"], wait for "You found an egg", switch to the dark theme for a dark shot, wait 1.2 s, shot egg-<w>-<theme>.png. Tap "Crack the egg", wait 1.6 s, shot tile-<w>-<theme>.png. Phase M32, store M32: at 375 and 1280 px in each theme, a video and a sampler of the computed style and the running animations of each part of the find, with burst shots after the tap on the egg.',
    33: 'Phase A1. The find of AT-32, then tap "Claim C", wait for the group "Your team", shot <w>-<theme>.png. The log lists the pills of the group.',
    34: 'Phase B. Store B: week 9 [number-top-score A, heading-leaders C, ...] and week 10 [heading-arcs A, T1 C, ...]; Teehee claims the C of heading-leaders into CORNERSTONE. For each width and theme, with the passphrase in the browser: find T1 with a double-tap, crack, tap "Claim C", pick Teehee, shot teehee-<w>-<theme>.png, then pick Lil Fridge, shot lil-fridge-<w>-<theme>.png. The log reads each word button: disabled, and the count of .egg-ghost tiles. Phase M34, store M34, the same state: at 375 and 1280 px in each theme, the opacity of the ghost tile at +0, +400, +800, and +1200 ms, and three cropped shots ghost-<w>-<theme>-<n>.png.',
    35: 'Phase B. The sheet of AT-34 with Teehee picked. Scroll to the notice "Claim it as a block.", shot <w>-<theme>.png.',
    36: 'Phase A1. The sheet of AT-33. Pick Lil Fridge and CORNERSTONE. Shot no-passphrase-<w>-<theme>.png with no cpc.passphrase in local storage, and with-passphrase-<w>-<theme>.png in a second context with cpc.passphrase=localtest.',
    37: 'Phase A2, store A: with the passphrase, find T1 with a double-tap, crack, Claim C, Lil Fridge, CORNERSTONE, tap "Claim C for CORNERSTONE", wait for the dialog "C goes to CORNERSTONE.", wait 1.8 s, shot claim-<w>-<theme>.png, then undo egg 2 with the undo route. Phase E, store E (Lil Fridge holds E, A, G, L, S in EAGLES): two fast taps on [data-stable-id="luck-5"] of /midseason/2026/ find egg 28 (E), crack, Claim E, Lil Fridge, EAGLES, "Claim E for EAGLES", shot won-<w>-<theme>.png, then undo egg 28.',
    38: 'Phase A2, store A. Teehee claims T1 into CORNERSTONE through check and claim. For each width and theme: find T1 with a double-tap, wait for the dialog "Another manager claimed first.", shot.',
    39: 'Phase A2, store A, after a restart of the API. 60 checks of T2 from 127.0.0.1 through the check route, then one more to read its status. For each width and theme: a double-tap on the Luck cell of Lil Fridge, wait for "The eggs need a rest", shot.',
    40: 'Phase A1, store A, six eggs, none claimed. For each page (/, /2026/week-08/, /midseason/2026/) and each width and theme: open the page, wait for the egg button in the header to read "6 eggs left", shot of the top 200 px. In the light theme, tap the egg button and log the new path.',
    41: 'Phase A1 (Tuesday) and phase A2 (Wednesday), store A. The drop time of week 9 moves to the real Tuesday of the week 9 drop with sqlite3: UPDATE eggs SET dropped_at = \'2026-11-10T09:00:00-05:00\' WHERE week = 9. The browser clock is fixed with page.clock.setFixedTime: 2026-11-10 12:00 ET for tuesday-*.png, 2026-11-11 12:00 ET for wednesday-*.png, after Teehee claims the A of week 9 into LANSDALE. Then tap "Hide the banner", reload, shot hidden-*.png.',
    42: 'Phase A2, store A. Lil Fridge claims the G of week 9 into EAGLES, so two of the six are claimed. For each width and theme: open /eggs/, wait 1.5 s, viewport shot of the hero.',
    43: 'Phase B, store B, after AT-45. Five more claims give letters to seven managers. For each width and theme: open /eggs/, full-page shot before-<w>-<theme>.png, tap "Show all 11" on the CORNERSTONE card, shot of the card after-<w>-<theme>.png.',
    44: 'Phase E, store E, after the curl claims of AT-12 (tools/api-store-e2.sh). For each width and theme: open /eggs/, shot of the region named EAGLES.',
    45: 'Phase B, store B. Lil Fridge claims the A of week 9 into LANSDALE. Teehee claims T1 (C) as a block. With the C of Teehee in CORNERSTONE from the setup of AT-34, the store holds two claims and one block. For each width and theme: open /eggs/, shot of the region "Latest claims".',
    46: 'Phase A0, store A, empty. For each width and theme: open /eggs/, shot of the region named "How the hunt works".',
    47: 'Phase P47, store P47, empty. board.json is the board answer. For the home page, week 8, and /eggs/, at each width and theme: open the page, wait for the board answer, scroll to the end and back, full-page shot <page>-<w>-<theme>.png, and count the egg buttons and the egg banners. Then at 1280 px in each theme: two mouse taps 150 ms apart on [data-stable-id="luck-3"] of /midseason/2026/, and the count of requests to /eggs/check.',
    49: 'Phase A1, store A. Each context has reducedMotion "reduce". Find T1 in the light theme with a double-tap, switch for a dark shot, tap "Crack the egg", wait 100 ms, shot. The log counts the running animations of the page.',
    50: 'Phase A1, store A, six eggs. For 340, 390, and 1280 px in each theme: the egg board /eggs/ after the board loads, the claim sheet after a find of T1, and the home page with the banner (browser clock 2026-11-10 12:00 ET). Each page runs scanText, scanContrast (scoped to the sheet or the banner), scanTargets, and scanScroll of apps/site/e2e/floor.ts, the scans of check:floor, with reduced motion, and the raw axe result of the rule color-contrast on the same scope. floor-eggs.txt is the output of CLIENT=cpc pnpm check:floor -g /eggs/.',
    51: 'Phase A2, store A. With the passphrase in the browser, at 375 and 1280 px in each theme: find T1 with a double-tap (1-egg), crack (2-tile), Claim C, Lil Fridge, CORNERSTONE (3-sheet), claim (4-claimed), tap "See the egg board" and check the CORNERSTONE row of Lil Fridge and the feed (5-board, full page). Then undo egg 2. eggs-spec.txt is the output of apps/site/e2e/eggs.spec.ts on a fresh store.',
    52: 'Phase N, store N, the drop of week 9 with T1, an analyzer egg, and heading-luck. 375 px, light, a touch context (hasTouch, isMobile). On /midseason/2026/, after the egg button shows: a touch press of 2.2 s on [data-stable-id="luck-3"] with Input.dispatchTouchEvent of the DevTools protocol, and a cancelable contextmenu MouseEvent fired on the element under the press at about 700 ms. Then a mouse right-click on the Luck cell, the first link (main a[href]), and the first image (main img), and a touch press with a menu event on the link and on the image. A log on the window, in the bubble phase after the listener, reads defaultPrevented of each menu event. The page logs each request body to /eggs/check.',
    54: 'Phase N, store N, with the egg verdict-word, tap2, trade_teams [1, 3] on /analyze/. 1280 px, light. Fill the passphrase sheet, pick The Blue Tent as Your Team and Lil Fridge as Team Two, add the first player of each list, tap "Grade the Trade", and wait for [data-stable-id="verdict-word"]. The grade is a real call of the local API with real Sleeper data and a real Claude call. Then two mouse taps 150 ms apart on the verdict word. The page logs the marks data-trade-key and data-trade-answer and each request body to /eggs/check. find-1280-light.png is the page after the answer. output.txt is the API part.',
    55: 'Phase N, store N. 1280 px, light. On /midseason/2026/, after the egg button shows: three mouse taps 150 ms apart on [data-stable-id="luck-3"], wait 1.5 s, then five mouse taps 150 ms apart on [data-stable-id="luck-5"]. The page logs the pointerup times, each request body to /eggs/check, and the open dialogs. output.txt is the API part.',
    56: 'Phase N, store N. On /midseason/2026/, after the egg button shows, the spec sets the data-stable-id of the first blurb to blurb-luck, the id of the test, because the site makes each blurb id from its text. At 375 px with touch taps and at 1280 px with mouse taps: a double-tap (150 ms apart) near the start of the blurb, then near its end. The page logs each request body to /eggs/check. draft.txt is the real draft_week of packages/eggs with a fixed answer of the agent port (tools/at56_draft.py). drop.txt is the API part (tools/api-catalog.sh).',
}

wanted = {int(arg) for arg in sys.argv[1:]} or set(STEPS)
for number, text in STEPS.items():
    if number not in wanted:
        continue
    folder = EV / f"AT-{number}"
    folder.mkdir(exist_ok=True)
    (folder / "steps.txt").write_text(HEAD + text + "\n", encoding="utf-8")
print(f"wrote {len(wanted)} steps files")
