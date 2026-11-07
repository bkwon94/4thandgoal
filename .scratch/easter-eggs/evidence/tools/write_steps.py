"""
Write evidence/AT-<n>/steps.txt for each site test of easter-eggs: how the shots and the logs of the test were made.
Run it from the repo root with python3. The text of each test names its phase of tools/site.spec.ts.
"""
from pathlib import Path

EV = Path(__file__).resolve().parent.parent
HEAD = """The runner of apps/site (pnpm --dir apps/site evidence easter-eggs) could not run: it serves on its fixed port 4173,
and a server that is not ours holds 4173 (python3 -m http.server 4173 of the worktree midseason-preview). So the
shots come from Playwright directly, with tools/site.spec.ts and tools/playwright.config.ts of this evidence folder.

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

Run: cd apps/site && EGGS_SCRATCH=<scratch> pnpm exec playwright test -c ../../.scratch/easter-eggs/evidence/tools/playwright.config.ts -g "<phase>"

This test:
"""

STEPS = {
    24: "Phase A0. Store A, empty. For each width and theme: open http://127.0.0.1:4175/ (NorCal), full-page shot home-<w>-<theme>.png, count the links to /eggs/, triple-tap two spots and count the egg checks sent, then open /eggs/ and take eggs-<w>-<theme>.png. The pipeline part is in output.txt.",
    25: "Phase A1. Store A, the six eggs of week 9. For each width and theme: open /2026/week-08/, one Playwright click on button[aria-controls=\"recap-3\"], wait 1.2 s, viewport shot. The page logs each request to /eggs/check.",
    26: "Phase L. 1280 px, light. Open /midseason/2026/, three mouse taps on the middle of [data-stable-id=\"luck-3\"], 150 ms apart. The page logs the pointerup times and each request body to /eggs/check. An earlier run of phase A1 used Playwright clicks with gaps of 191 and 1231 ms, and it sent tap2; its log stays in site-A1.txt.",
    27: "Phase A1. 1280 px, light. Open /midseason/2026/, mouse down on the middle of [data-stable-id=\"luck-3\"], wait 3.5 s, mouse up. The page logs each request body to /eggs/check.",
    28: "Phase A1. 1280 px, light. Open /2026/week-08/, tap [data-stable-id=\"number-top-score\"] (A), wait 600 ms, tap [data-stable-id=\"number-median\"] (B), wait 600 ms, then two taps 120 ms apart on [data-stable-id=\"number-closest\"] (C). The page logs each request body to /eggs/check.",
    29: "Phase A1. 1280 px, light. Open /midseason/2026/, select the first whole word of [data-stable-id=\"blurb-1jo5mqe\"] with a DOM range (document.getSelection().addRange), wait 1.5 s. The page logs each request body to /eggs/check.",
    30: "Phase L. 1280 px, light. Open /midseason/2026/, tap \"Sim the season\". A watch in the page logs the time of each change of the text of [data-stable-id=\"sim-row-3\"] (a new frame) and each pointerup. The spec learns the time of one frame, then taps the row three times, 200 ms apart, from 150 ms before the next frame. The page logs each request body to /eggs/check. An earlier run in phase A1 saw no frame change during its taps; its log stays in site-A1.txt.",
    31: "tools/callout.spec.ts, in the WebKit of Playwright, because Chromium does not compute -webkit-touch-callout. Open /midseason/2026/ at 375 px and read getComputedStyle(...).getPropertyValue(\"-webkit-touch-callout\") of the Luck cell, a link, and an image.",
    32: "Phase A1. For each width and theme: open /midseason/2026/ in the light theme, three fast taps (click clickCount 3) on [data-stable-id=\"luck-3\"], wait for \"You found an egg\", switch to the dark theme for a dark shot, wait 1.2 s, shot egg-<w>-<theme>.png. Tap \"Crack the egg\", wait 1.6 s, shot tile-<w>-<theme>.png.",
    33: "Phase A1. The find of AT-32, then tap \"Claim C\", wait for the group \"Your team\", shot <w>-<theme>.png. The log lists the pills of the group.",
    34: "Phase B. Store B: week 9 [number-top-score A, heading-leaders C, ...] and week 10 [heading-arcs A, T1 C, ...]; Teehee claims the C of heading-leaders into CORNERSTONE. For each width and theme, with the passphrase in the browser: find T1, crack, tap \"Claim C\", pick Teehee, shot teehee-<w>-<theme>.png, then pick Lil Fridge, shot lil-fridge-<w>-<theme>.png. The log reads each word button: disabled, and the count of .egg-ghost tiles.",
    35: "Phase B. The sheet of AT-34 with Teehee picked. Scroll to the notice \"Claim it as a block.\", shot <w>-<theme>.png.",
    36: "Phase A1. The sheet of AT-33. Pick Lil Fridge and CORNERSTONE. Shot no-passphrase-<w>-<theme>.png with no cpc.passphrase in local storage, and with-passphrase-<w>-<theme>.png in a second context with cpc.passphrase=localtest.",
    37: "Phase A2, store A: with the passphrase, find T1, crack, Claim C, Lil Fridge, CORNERSTONE, tap \"Claim C for CORNERSTONE\", wait for the dialog \"C goes to CORNERSTONE.\", wait 1.8 s, shot claim-<w>-<theme>.png, then undo egg 2 with the undo route. Phase E, store E (Lil Fridge holds E, A, G, L, S in EAGLES): two fast taps on [data-stable-id=\"luck-5\"] of /midseason/2026/ find egg 28 (E), crack, Claim E, Lil Fridge, EAGLES, \"Claim E for EAGLES\", shot won-<w>-<theme>.png, then undo egg 28.",
    38: "Phase A2, store A. Teehee claims T1 into CORNERSTONE through check and claim. For each width and theme: find T1, wait for the dialog \"Another manager claimed first.\", shot.",
    39: "Phase A2, store A, after a restart of the API. 60 checks of T2 from 127.0.0.1 through the check route, then one more to read its status. For each width and theme: three fast taps on the Luck cell of Lil Fridge, wait for \"The eggs need a rest\", shot.",
    40: "Phase A1, store A, six eggs, none claimed. For each page (/, /2026/week-08/, /midseason/2026/) and each width and theme: open the page, wait for the egg button in the header to read \"6 eggs left\", shot of the top 200 px. In the light theme, tap the egg button and log the new path.",
    41: "Phase A1 (Tuesday) and phase A2 (Wednesday), store A. The drop time of week 9 moves to the real Tuesday of the week 9 drop with sqlite3: UPDATE eggs SET dropped_at = '2026-11-10T09:00:00-05:00' WHERE week = 9. The browser clock is fixed with page.clock.setFixedTime: 2026-11-10 12:00 ET for tuesday-*.png, 2026-11-11 12:00 ET for wednesday-*.png, after Teehee claims the A of week 9 into LANSDALE. Then tap \"Hide the banner\", reload, shot hidden-*.png.",
    42: "Phase A2, store A. Lil Fridge claims the G of week 9 into EAGLES, so two of the six are claimed. For each width and theme: open /eggs/, wait 1.5 s, viewport shot of the hero.",
    43: "Phase B, store B, after AT-45. Five more claims give letters to seven managers. For each width and theme: open /eggs/, full-page shot before-<w>-<theme>.png, tap \"Show all 11\" on the CORNERSTONE card, shot of the card after-<w>-<theme>.png.",
    44: "Phase E, store E, after the curl claims of AT-12. For each width and theme: open /eggs/, shot of the region named EAGLES.",
    45: "Phase B, store B. Lil Fridge claims the A of week 9 into LANSDALE. Teehee claims T1 (C) as a block. With the C of Teehee in CORNERSTONE from the setup of AT-34, the store holds two claims and one block. For each width and theme: open /eggs/, shot of the region \"Latest claims\".",
    46: "Phase A0, store A, empty. For each width and theme: open /eggs/, shot of the region named \"How the hunt works\".",
    47: "Phase A0, store A, empty. For each width and theme: open /eggs/, scroll to the end and back, full-page shot. board.json is the board answer.",
    49: "Phase A1, store A. Each context has reducedMotion \"reduce\". Find T1 in the light theme, switch for a dark shot, tap \"Crack the egg\", wait 100 ms, shot. The log counts the running animations of the page.",
    50: "Phase A1, store A, six eggs. For 390 and 1280 px in each theme: the egg board /eggs/ after the board loads, the claim sheet after a find of T1, and the home page with the banner (browser clock 2026-11-10 12:00 ET). Each page runs scanText, scanContrast (scoped to the sheet or the banner), scanTargets, and scanScroll of apps/site/e2e/floor.ts, the scans of check:floor, with reduced motion. floor-eggs.txt is the output of CLIENT=cpc pnpm check:floor -g /eggs/.",
    51: "Phase A2, store A. With the passphrase in the browser, at 375 and 1280 px in each theme: find T1 (1-egg), crack (2-tile), Claim C, Lil Fridge, CORNERSTONE (3-sheet), claim (4-claimed), tap \"See the egg board\" and check the CORNERSTONE row of Lil Fridge and the feed (5-board, full page). Then undo egg 2. eggs-spec.txt is the output of apps/site/e2e/eggs.spec.ts on a fresh store.",
}

for number, text in STEPS.items():
    folder = EV / f"AT-{number}"
    folder.mkdir(exist_ok=True)
    (folder / "steps.txt").write_text(HEAD + text + "\n", encoding="utf-8")
print(f"wrote {len(STEPS)} steps files")
