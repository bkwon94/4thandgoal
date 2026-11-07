# Easter eggs: evidence

Spec: `.scratch/easter-eggs/PRD.md`. Acceptance tests: `.scratch/easter-eggs/ACCEPTANCE.md`.
Built from: `f255557d`, on 2026-11-07. AT-3, AT-34, AT-41, and AT-50 ran again at `4f87122b`, after the fixes E1, E2, and E3. The agent gives no Test verdict. The Judge gives one for each test in `VERDICTS.md`.
Round time: the runner did not run, because a server that is not ours holds its fixed port 4173. The Playwright phases of `evidence/tools/site.spec.ts` took 15 min for 27 site tests.

The API ran on this machine like `make -C apps/api api-evidence`: passphrase `localtest`, commissioner key `localkey`, and a temp `CORNERSTONE_EGGS_DIR` outside the repo for each store. The scripts are in `evidence/tools/`. The real path of each eggs route is `/clients/cpc/eggs/<route>`. The tests write `/cpc/eggs/`.
AT-1 to AT-19 ran at `27424c16`. The fixes D1 and D2 changed only `eggfile.py` and `apps/site/e2e/eggs.spec.ts`, so that evidence stands at `f255557d`.

## AT-1: The egg check matches the test egg

App: pipeline
Then: The answer holds the letter C and a claim token.
Files: `evidence/AT-1/output.txt`, `evidence/AT-1/setup.txt`
Observation: The check of T1 (luck-3, tap3, light) answered HTTP 200 with match true, claimed false, letter C, and a token. setup.txt shows the drops: T1 is egg 2 of week 9 with the letter C. The real path of each route has the prefix /clients/cpc/eggs/; the test writes /cpc/eggs/.

## AT-2: A wrong condition is no match

App: pipeline
Then: The answer is no match, with no letter and no token.
Files: `evidence/AT-2/output.txt`
Observation: The same check with the theme dark answered HTTP 200 with {"match":false} only, with no letter and no token. The real path of each route has the prefix /clients/cpc/eggs/; the test writes /cpc/eggs/.

## AT-3: A clock window holds

App: pipeline
Then: The answer is no match. The same check inside the window matches.
Files: `evidence/AT-3/clock-check.py`, `evidence/AT-3/output.txt`
Observation: The real check of T2 at 00:40 ET answered {"match":false}. The real clock is outside the window 23:00-00:00 ET, so clock-check.py builds the real API app (create_app, the real clients, a temp egg store), drops T2 through the drop route, and sets the clock of the hunt in the app. Over HTTP, the check of T2 answered {"match":false} at 22:59 ET, {"match":true,"claimed":false,"letter":"A","token":...} at 23:30 ET, and {"match":false} at 00:00 ET. T2 is the only egg of that store, so its letter is A there. The real path of each route has the prefix /clients/cpc/eggs/; the test writes /cpc/eggs/.

## AT-4: A sim condition holds

App: pipeline
Then: The first check is no match. The second check matches.
Files: `evidence/AT-4/output.txt`
Observation: The check of T3 with sim_champion 3 (Lil Fridge) answered no match. The check with sim_champion 12 (Teehee) answered match true, letter E. The real path of each route has the prefix /clients/cpc/eggs/; the test writes /cpc/eggs/.

## AT-5: A claim counts

App: pipeline
Then: `/cpc/eggs/board` shows Lil Fridge with one C in CORNERSTONE.
Files: `evidence/AT-5/output.txt`
Observation: The claim with the token of AT-1, roster 3, CORNERSTONE, and the passphrase answered HTTP 200 with the letters CORNERSTONE [C]. The board then showed found 1, CORNERSTONE [('Lil Fridge', ['C'])], and the claim in latest. The real path of each route has the prefix /clients/cpc/eggs/; the test writes /cpc/eggs/.

## AT-6: The first claim wins a tie

App: pipeline
Then: One claim wins. The other answers that another manager claimed first.
Files: `evidence/AT-6/output.txt`
Observation: Two tokens from two checks of T1. The two claims ran at once: Lil Fridge answered HTTP 200, and Teehee answered HTTP 409 with "Another manager claimed first." The claims table holds one live row for egg 2 (roster 3), beside the undone row of AT-17. The real path of each route has the prefix /clients/cpc/eggs/; the test writes /cpc/eggs/.

## AT-7: The commissioner cannot hunt

App: pipeline
Then: The API refuses it, and T1 stays live.
Files: `evidence/AT-7/output.txt`
Observation: The claim for roster 6 (Bo Girds, the commissioner of values.eggs.commissioner) answered HTTP 422 with "The commissioner places the eggs and cannot hunt them." The board after showed found 0, latest empty, and a new check of T1 still matched with a token. The real path of each route has the prefix /clients/cpc/eggs/; the test writes /cpc/eggs/.

## AT-8: The claim needs the passphrase

App: pipeline
Then: The API answers 401.
Files: `evidence/AT-8/output.txt`
Observation: The claim with no X-League-Passphrase header answered HTTP 401 with an empty body. The real path of each route has the prefix /clients/cpc/eggs/; the test writes /cpc/eggs/.

## AT-9: A full slot refuses

App: pipeline
Then: The API refuses it.
Files: `evidence/AT-9/output.txt`
Observation: Lil Fridge held the C of CORNERSTONE from T1. The check of T4 matched with the letter C. The claim of T4 for Lil Fridge into CORNERSTONE answered HTTP 422 with "CORNERSTONE has no open slot for the letter C." The real path of each route has the prefix /clients/cpc/eggs/; the test writes /cpc/eggs/.

## AT-10: A block counts as found

App: pipeline
Then: The found count of the board rises by 1. The egg word cards and the feed show no block.
Files: `evidence/AT-10/output.txt`
Observation: Before: counts left 11, found 1, and one row in latest. The block claim of T4 (word null) answered HTTP 200 with word null. After: counts left 10, found 2. The letters of Lil Fridge stayed CORNERSTONE [C] only, and latest still held one row, the C of CORNERSTONE. The claims table holds the block row with an empty word. The real path of each route has the prefix /clients/cpc/eggs/; the test writes /cpc/eggs/.

## AT-11: A block refuses if the letter fits

App: pipeline
Then: The API refuses it, because C fits CORNERSTONE.
Files: `evidence/AT-11/output.txt`
Observation: Teehee held no letter in any egg word. The block claim of a T1 token (letter C) for Teehee answered HTTP 422 with "The letter C fits an egg word of the manager, so a block is not open." The real path of each route has the prefix /clients/cpc/eggs/; the test writes /cpc/eggs/.

## AT-12: A won egg word closes

App: pipeline
Then: The board names Lil Fridge the winner of EAGLES. The API refuses the claim of Teehee.
Files: `evidence/AT-12/output.txt`, `evidence/AT-12/setup.txt`
Observation: setup.txt: Lil Fridge holds E, A, G, L, S in EAGLES, and egg 28 holds E. The claim of egg 28 for Lil Fridge into EAGLES answered HTTP 200 with winner roster 3, word EAGLES. A new E egg of week 12 (look-ahead-1-7) then matched, and the claim of Teehee into EAGLES answered HTTP 422 with "EAGLES has a winner." The board shows the EAGLES winner Lil Fridge, and Teehee holds no letter in EAGLES. The real path of each route has the prefix /clients/cpc/eggs/; the test writes /cpc/eggs/.

## AT-13: The egg check has its own limit

App: pipeline
Then: The 61st check answers 429 with a retry-after. The analyze route still answers for the address.
Files: `evidence/AT-13/output.txt`
Observation: 61 checks from Fly-Client-IP 10.13.0.1: checks 1 to 60 answered HTTP 200, and check 61 answered HTTP 429 with retry-after 3600. For the same address after check 61, the teams route answered 200, an empty analyze body answered 422, and one real analyze call with a real Claude call answered HTTP 200 with the decision yes and fallback false. A check from 10.13.0.2 answered 200. This run is on a fresh API start of the same store; the first run before the restart gave the same statuses. The real path of each route has the prefix /clients/cpc/eggs/; the test writes /cpc/eggs/.

## AT-14: The drop needs the commissioner key

App: pipeline
Then: The API answers 401 and drops no egg.
Files: `evidence/AT-14/output.txt`
Observation: The drop with the passphrase and no X-Commissioner-Key answered HTTP 401 with content-length 0. The board counts and last_drop were the same before and after, and the store holds 0 eggs of week 11. The real path of each route has the prefix /clients/cpc/eggs/; the test writes /cpc/eggs/.

## AT-15: The letter rule of the first drop

App: pipeline
Then: The six letters are A, C, D, E, G, and L.
Files: `evidence/AT-15/output.txt`
Observation: A fresh API with an empty store. The drop of six test eggs for week 9 gave the letters ['A', 'C', 'D', 'E', 'G', 'L']. The real path of each route has the prefix /clients/cpc/eggs/; the test writes /cpc/eggs/.

## AT-16: The guard keeps the last letter of a leader

App: pipeline
Then: No egg of the drop holds E.
Files: `evidence/AT-16/output.txt`
Observation: The board before: Lil Fridge holds E, A, G, L, S in EAGLES. E ties at the top of the need with 11 managers, beside A, C, D, L, N, O, R, S, T; G has 10. The drop of six eggs for week 10 gave ['A', 'C', 'D', 'L', 'N', 'O'], with no E. E ties at the top and is not strictly the only top letter, because every manager still needs each letter of CORNERSTONE and LANSDALE. The real path of each route has the prefix /clients/cpc/eggs/; the test writes /cpc/eggs/.

## AT-17: The commissioner undoes a claim

App: pipeline
Then: T1 is live again, the board loses the C of Lil Fridge, and the claims table keeps the claim with its undo time.
Files: `evidence/AT-17/output.txt`
Observation: make egg-undo CLIENT=cpc EGG=2 against the local API printed {"egg_id":2,"undone":true} and exit 0. The board then showed found 0 and Lil Fridge with no letter in CORNERSTONE. The claims row stays with claimed_at and an undone_at time. A new check of T1 matched with a token, so T1 is live.

## AT-18: The egg board names no spot

App: pipeline
Then: The answer holds no page, no target, no action, and no condition.
Files: `evidence/AT-18/output.txt`
Observation: The full board JSON holds counts, weeks with slot states, words with managers and letters, latest, managers, and last_drop (week, count, dropped_at). A search of the answer for the page names, the targets, the actions, and the keys page, target, action, and conditions found 0 matches. The real path of each route has the prefix /clients/cpc/eggs/; the test writes /cpc/eggs/.

## AT-19: The source names no spot

App: pipeline
Then: The grep finds no reason, and no target that only an egg holds.
Files: `evidence/AT-19/output.txt`
Observation: Each of the four reasons of the test egg file: 0 tracked repo files (the evidence folder of AT-19 left out) and 0 built site files. Each target is a stable id that the site gives every element of its kind: luck-3 is on 1 element, number-median and number-closest each on 3 elements (week pages), sim-trophy on 0 static elements (the sim renders it), among 980 distinct stable ids. In the repo source, the targets show only in the code that makes the stable id of every element of a kind and in tests. The search of the built site for the conditions and the action of the eggs found 0 files.

## AT-20: The draft proposes six spots

App: pipeline
Then: The file holds six spots, each with a reason and marked not confirmed. No spot repeats T1 to T4.
Files: `evidence/AT-20/output.txt`
Observation: make egg-draft CLIENT=cpc WEEK=8 with a temp egg file (T1 to T4 confirmed, weeks 9 and 10) took 95 s with a real Claude call and exit 0. It wrote 6 spots of week 8, each with a reason (133 to 178 characters) and confirmed = false. No spot has the page and the target of T1 to T4. Four spots hold an open list, which the file writes as a TOML array after D1. The page, the target, and the reason of each spot are cut. A first run before D1 failed with the error of a list value and wrote nothing.

## AT-21: The publish drops the confirmed eggs only

App: pipeline
Then: The output says 4 eggs dropped, and the board count to find rises by 4.
Files: `evidence/AT-21/output.txt`
Observation: The drop step of the publish (drop_after_publish, run alone by tools/drop_step.py, so no commit and no push ran) with six spots of week 8, four confirmed, printed "Dropped 4 eggs of week 8." and four egg lines, exit 0. The board went from left 0, to_drop 54 to left 4, to_drop 50.

## AT-22: The publish warns when the API is down

App: pipeline
Then: The drop step warns and exits 0. `make egg-drop` drops the 4 eggs.
Files: `evidence/AT-22/output.txt`
Observation: With the API stopped (health curl exit 7), the drop step printed "WARNING: the egg drop of week 8 failed: [Errno 61] Connection refused. Run make egg-drop CLIENT=cpc WEEK=8 to retry." and exit 0. After a start of the API with a fresh store, make egg-drop CLIENT=cpc WEEK=8 printed "Dropped 4 eggs of week 8.", exit 0, and the board went to left 4.

## AT-23: A week with no confirmed eggs

App: pipeline
Then: The output says that no eggs dropped.
Files: `evidence/AT-23/output.txt`
Observation: With six spots of week 8 and none confirmed, the drop step printed "No eggs dropped: week 8 has no confirmed egg in <file>." and exit 0.

## AT-24: NorCal has no eggs

App: both
Then: The drop step skips. The site has no egg button and no listener, and `/eggs/` is the 404 page.
Files: `evidence/AT-24/eggs-1280-dark.png`, `evidence/AT-24/eggs-1280-light.png`, `evidence/AT-24/eggs-375-dark.png`, `evidence/AT-24/eggs-375-light.png`, `evidence/AT-24/eggs-768-dark.png`, `evidence/AT-24/eggs-768-light.png`, `evidence/AT-24/home-1280-dark.png`, `evidence/AT-24/home-1280-light.png`, `evidence/AT-24/home-375-dark.png`, `evidence/AT-24/home-375-light.png`, `evidence/AT-24/home-768-dark.png`, `evidence/AT-24/home-768-light.png`, `evidence/AT-24/output.txt`, `evidence/AT-24/site-A0.txt`, `evidence/AT-24/steps.txt`
Observation: The drop step for NorCal printed "The client norcal has no eggs package, so no eggs dropped." and exit 0, and the NorCal eggs board route answers 404. On the NorCal home page, each width and theme shows 0 links to /eggs/ and sent 0 egg checks after two triple taps. The HTML holds no text "egg" and no name of the eggs parts. /eggs/ answers 404 with the 404 page and its not-found mark. The NorCal export has no eggs folder. Shots of home and /eggs/ at 375, 768, and 1280 px in each theme.

## AT-25: A normal tap sends no check

App: site
Then: The card opens, and the listener sends no check.
Files: `evidence/AT-25/1280-dark.png`, `evidence/AT-25/1280-light.png`, `evidence/AT-25/375-dark.png`, `evidence/AT-25/375-light.png`, `evidence/AT-25/768-dark.png`, `evidence/AT-25/768-light.png`, `evidence/AT-25/site-A1.txt`, `evidence/AT-25/steps.txt`
Observation: One tap on the card of game 3 of week 8 set aria-expanded true and opened the recap ("Won by 1.43" and its text) in each shot. The page sent 0 egg checks at each width and theme.

## AT-26: A multi-tap sends one check

App: site
Then: The listener sends one check with the page, the id, the action 3 taps, and the light theme.
Files: `evidence/AT-26/site-A1.txt`, `evidence/AT-26/site-L.txt`, `evidence/AT-26/steps.txt`
Observation: Three mouse taps on luck-3 at 0, 172, and 329 ms sent one check: page /midseason/2026/, target luck-3, action tap3, theme light, plus the open state chip-rb of the page. The store held a claim of T1 by then, so the card was the claimed-first card. A first run with Playwright clicks had a gap of 1231 ms and sent one tap2; its log stays in site-A1.txt.

## AT-27: A long hold sends one check

App: site
Then: The listener sends one check with the hold 3.
Files: `evidence/AT-27/site-A1.txt`, `evidence/AT-27/steps.txt`
Observation: A press of 3524 ms on luck-3 sent one check with the action hold3, target luck-3, theme light.

## AT-28: A tap combo sends one check

App: site
Then: The listener sends one check with the action 2 taps on C and the trail A, B.
Files: `evidence/AT-28/site-A1.txt`, `evidence/AT-28/steps.txt`
Observation: Tap A number-top-score, tap B number-median, then two taps on C number-closest, 1471 ms from the first tap to the last, sent one check: target number-closest, action tap2, trail [number-top-score, number-median].

## AT-29: A selected word sends one check

App: site
Then: The listener sends one check with the word and the id of the blurb.
Files: `evidence/AT-29/site-A1.txt`, `evidence/AT-29/steps.txt`
Observation: A DOM range selected the first whole word "First" of blurb-1jo5mqe. It sent one check: target blurb-1jo5mqe, action select, word "first". The selection came from a script, not from a drag of a finger.

## AT-30: The count by id holds across sim frames

App: site
Then: The listener sends one check with the action 3 taps.
Files: `evidence/AT-30/site-A1.txt`, `evidence/AT-30/site-L.txt`, `evidence/AT-30/steps.txt`
Observation: The replay ran with frames about 1520 ms apart. Taps on sim-row-3 at 0, 215, and 429 ms; the frame changed at 125 ms, between tap 1 and tap 2, and the row moved from place 02 to place 04. The listener sent one check with target sim-row-3 and action tap3. A first run in phase A1 saw no frame change during its taps; its log stays in site-A1.txt.

## AT-31: The iOS callout is off on targets only

App: site
Then: The callout is off on the Luck cell and on for the link and the image.
Files: `evidence/AT-31/output.txt`, `evidence/AT-31/steps.txt`
Observation: Desktop WebKit 27.2 and Chromium do not compute -webkit-touch-callout (the value is empty), so the evidence reads the built CSS. The root has data-eggs. The rule "[data-eggs] [data-stable-id]" sets none, and it matches the Luck cell (callout none). The first link of the page (#sim) matches no callout rule, so the default holds (callout on). The first image matches "[data-eggs] [data-stable-id] img", which sets default (callout on). No iOS device measured the value.

## AT-32: The find shows the egg and its letter

App: site
Then: The page blurs, the ring and the egg show, the egg cracks, and the red C tile springs up.
Files: `evidence/AT-32/egg-1280-dark.png`, `evidence/AT-32/egg-1280-light.png`, `evidence/AT-32/egg-375-dark.png`, `evidence/AT-32/egg-375-light.png`, `evidence/AT-32/egg-768-dark.png`, `evidence/AT-32/egg-768-light.png`, `evidence/AT-32/site-A1.txt`, `evidence/AT-32/steps.txt`, `evidence/AT-32/tile-1280-dark.png`, `evidence/AT-32/tile-1280-light.png`, `evidence/AT-32/tile-375-dark.png`, `evidence/AT-32/tile-375-light.png`, `evidence/AT-32/tile-768-dark.png`, `evidence/AT-32/tile-768-light.png`
Observation: In each shot of the egg, the page is blurred behind the find card, with the egg and the line "You found an egg". After the tap on the egg, each tile shot shows the red C tile with "The letter C is yours to claim." The log reads the tile C at each width and theme. A dark shot finds T1 in the light theme, then switches the theme. A still shot cannot show the crack or the spring as motion.

## AT-33: The team pills omit the commissioner

App: site
Then: The sheet shows 11 team pills, and Bo Girds is not one of them.
Files: `evidence/AT-33/1280-dark.png`, `evidence/AT-33/1280-light.png`, `evidence/AT-33/375-dark.png`, `evidence/AT-33/375-light.png`, `evidence/AT-33/768-dark.png`, `evidence/AT-33/768-light.png`, `evidence/AT-33/site-A1.txt`, `evidence/AT-33/steps.txt`
Observation: The sheet shows 11 team pills at each width and theme: The Blue Tent, All You Need Is Love, Lil Fridge, NFC Least, London Cooking, To Infinity and Bijan, Return of T Mac, Maye d'force B with U, behold the lamb, Unsolicited Dak Picks, Teehee. Bo Girds is not a pill.

## AT-34: The egg word cards of the claim

App: site
Then: CORNERSTONE is faded and disabled. A ghost tile pulses in its C slot only on a word with an open slot.
Files: `evidence/AT-34/lil-fridge-1280-dark.png`, `evidence/AT-34/lil-fridge-1280-light.png`, `evidence/AT-34/lil-fridge-375-dark.png`, `evidence/AT-34/lil-fridge-375-light.png`, `evidence/AT-34/lil-fridge-768-dark.png`, `evidence/AT-34/lil-fridge-768-light.png`, `evidence/AT-34/site-B.txt`, `evidence/AT-34/steps.txt`, `evidence/AT-34/teehee-1280-dark.png`, `evidence/AT-34/teehee-1280-light.png`, `evidence/AT-34/teehee-375-dark.png`, `evidence/AT-34/teehee-375-light.png`, `evidence/AT-34/teehee-768-dark.png`, `evidence/AT-34/teehee-768-light.png`
Observation: At 4f87122b, with Teehee picked, CORNERSTONE, LANSDALE, and EAGLES are disabled with 0 ghost tiles, and each shows a dashed edge, a grey surface, and grey text. The computed values are background rgb(235, 235, 235), border dashed, and text rgb(102, 102, 102) in light, and background rgb(38, 38, 38), border dashed, and text rgb(153, 153, 153) in dark. With Lil Fridge picked, CORNERSTONE is enabled with 1 ghost tile, a white surface, a solid edge, and dark text rgb(20, 20, 20). LANSDALE and EAGLES stay disabled and faded. This holds at each width and theme.

## AT-35: The block notice

App: site
Then: A dashed notice offers a block.
Files: `evidence/AT-35/1280-dark.png`, `evidence/AT-35/1280-light.png`, `evidence/AT-35/375-dark.png`, `evidence/AT-35/375-light.png`, `evidence/AT-35/768-dark.png`, `evidence/AT-35/768-light.png`, `evidence/AT-35/site-B.txt`, `evidence/AT-35/steps.txt`
Observation: With Teehee picked, a dashed notice shows: "C fits none of your egg words. Claim it as a block. Then no other manager can put it in a word." The button reads "Claim C as a block". This shows at each width and theme.

## AT-36: The passphrase field shows only when needed

App: site
Then: With no passphrase, the field shows and the button names it. With one, the field is gone.
Files: `evidence/AT-36/no-passphrase-1280-dark.png`, `evidence/AT-36/no-passphrase-1280-light.png`, `evidence/AT-36/no-passphrase-375-dark.png`, `evidence/AT-36/no-passphrase-375-light.png`, `evidence/AT-36/no-passphrase-768-dark.png`, `evidence/AT-36/no-passphrase-768-light.png`, `evidence/AT-36/site-A1.txt`, `evidence/AT-36/steps.txt`, `evidence/AT-36/with-passphrase-1280-dark.png`, `evidence/AT-36/with-passphrase-1280-light.png`, `evidence/AT-36/with-passphrase-375-dark.png`, `evidence/AT-36/with-passphrase-375-light.png`, `evidence/AT-36/with-passphrase-768-dark.png`, `evidence/AT-36/with-passphrase-768-light.png`
Observation: With no passphrase in the browser, the sheet shows the field "League passphrase" and the button "Enter the passphrase". With cpc.passphrase set, the field is gone and the button reads "Claim C for CORNERSTONE". This holds at each width and theme.

## AT-37: The claim hero card

App: site
Then: The hero card shows the count rise and the C tile in its slot. A claim that fills an egg word says the gift card is the manager's.
Files: `evidence/AT-37/claim-1280-dark.png`, `evidence/AT-37/claim-1280-light.png`, `evidence/AT-37/claim-375-dark.png`, `evidence/AT-37/claim-375-light.png`, `evidence/AT-37/claim-768-dark.png`, `evidence/AT-37/claim-768-light.png`, `evidence/AT-37/site-A2.txt`, `evidence/AT-37/site-E.txt`, `evidence/AT-37/steps.txt`, `evidence/AT-37/won-1280-dark.png`, `evidence/AT-37/won-1280-light.png`, `evidence/AT-37/won-375-dark.png`, `evidence/AT-37/won-375-light.png`, `evidence/AT-37/won-768-dark.png`, `evidence/AT-37/won-768-light.png`
Observation: The claim of C for Lil Fridge into CORNERSTONE shows the hero card "CLAIMED · LIL FRIDGE · 1/11", the C tile in its slot, "C goes to CORNERSTONE.", and "10 letters to go for the $50." The claim of E that fills EAGLES (store E) shows "6/6", the tiles E A G L E S, "EAGLES is complete.", and "The $20 gift card is yours." The API undid each claim after its shot.

## AT-38: Another manager claimed first

App: site
Then: The hero card says that another manager claimed first.
Files: `evidence/AT-38/1280-dark.png`, `evidence/AT-38/1280-light.png`, `evidence/AT-38/375-dark.png`, `evidence/AT-38/375-light.png`, `evidence/AT-38/768-dark.png`, `evidence/AT-38/768-light.png`, `evidence/AT-38/site-A2.txt`, `evidence/AT-38/steps.txt`
Observation: With T1 claimed by Teehee, the find shows the card "TOO LATE · C · Another manager claimed first. · The first claim wins the egg." at each width and theme.

## AT-39: The limit hero card

App: site
Then: The card reads "The eggs need a rest. Try again in N minutes." with a real N.
Files: `evidence/AT-39/1280-dark.png`, `evidence/AT-39/1280-light.png`, `evidence/AT-39/375-dark.png`, `evidence/AT-39/375-light.png`, `evidence/AT-39/768-dark.png`, `evidence/AT-39/768-light.png`, `evidence/AT-39/site-A2.txt`, `evidence/AT-39/steps.txt`
Observation: 60 checks from 127.0.0.1, then one more answered 429 with Retry-After 3600. The three taps show the card "LIMIT · 60 · MINUTES LEFT · The eggs need a rest. · Try again in 60 minutes." at each width and theme.

## AT-40: The egg button is on every page

App: site
Then: Each top band shows the egg button with the badge 6. The tap opens `/eggs/`.
Files: `evidence/AT-40/drop.json`, `evidence/AT-40/home-1280-dark.png`, `evidence/AT-40/home-1280-light.png`, `evidence/AT-40/home-375-dark.png`, `evidence/AT-40/home-375-light.png`, `evidence/AT-40/home-768-dark.png`, `evidence/AT-40/home-768-light.png`, `evidence/AT-40/midseason-1280-dark.png`, `evidence/AT-40/midseason-1280-light.png`, `evidence/AT-40/midseason-375-dark.png`, `evidence/AT-40/midseason-375-light.png`, `evidence/AT-40/midseason-768-dark.png`, `evidence/AT-40/midseason-768-light.png`, `evidence/AT-40/site-A1.txt`, `evidence/AT-40/steps.txt`, `evidence/AT-40/week-08-1280-dark.png`, `evidence/AT-40/week-08-1280-light.png`, `evidence/AT-40/week-08-375-dark.png`, `evidence/AT-40/week-08-375-light.png`, `evidence/AT-40/week-08-768-dark.png`, `evidence/AT-40/week-08-768-light.png`
Observation: Six eggs of week 9, none claimed. On the home page, week 8, and /midseason/2026/, the egg button of the top band shows the badge 6, with the label "Egg board, 6 eggs left to find", at each width and theme. A tap in the light theme opens /eggs/ from each page. The badge waits for the first board read after a start of the API, which reads the live rosters.

## AT-41: The egg banner

App: site
Then: On Tuesday the banner reads "6 eggs dropped today · 6 left". On Wednesday it reads "6 eggs dropped Tue · 5 left". It links to `/eggs/`, and after the reload it stays hidden.
Files: `evidence/AT-41/hidden-1280-dark.png`, `evidence/AT-41/hidden-1280-light.png`, `evidence/AT-41/hidden-375-dark.png`, `evidence/AT-41/hidden-375-light.png`, `evidence/AT-41/hidden-768-dark.png`, `evidence/AT-41/hidden-768-light.png`, `evidence/AT-41/site-A1.txt`, `evidence/AT-41/site-A2.txt`, `evidence/AT-41/steps.txt`, `evidence/AT-41/tuesday-1280-dark.png`, `evidence/AT-41/tuesday-1280-light.png`, `evidence/AT-41/tuesday-375-dark.png`, `evidence/AT-41/tuesday-375-light.png`, `evidence/AT-41/tuesday-768-dark.png`, `evidence/AT-41/tuesday-768-light.png`, `evidence/AT-41/wednesday-1280-dark.png`, `evidence/AT-41/wednesday-1280-light.png`, `evidence/AT-41/wednesday-375-dark.png`, `evidence/AT-41/wednesday-375-light.png`, `evidence/AT-41/wednesday-768-dark.png`, `evidence/AT-41/wednesday-768-light.png`
Observation: At 4f87122b, the drop time of week 9 was set to the real Tuesday 2026-11-10 09:00 ET with sqlite3 in the temp store, and the browser clock was fixed. On Tuesday noon the banner line reads "6 eggs dropped today · 6 left". On Wednesday noon, after one claim, it reads "6 eggs dropped Tue · 5 left". At every width and theme, scrollWidth equals clientWidth, so the line is not cut. At 375 px the Tuesday line wraps to two lines (40 px high). The banner links to /eggs/, and after the hide and a reload, 0 banners show.

## AT-42: The hero of the egg board

App: site
Then: The counts are 4 left to find, 2 found, and 48 to drop. The grid shows 2 white, 4 red, and 48 dashed slots.
Files: `evidence/AT-42/1280-dark.png`, `evidence/AT-42/1280-light.png`, `evidence/AT-42/375-dark.png`, `evidence/AT-42/375-light.png`, `evidence/AT-42/768-dark.png`, `evidence/AT-42/768-light.png`, `evidence/AT-42/site-A2.txt`, `evidence/AT-42/steps.txt`
Observation: Six eggs, two claimed. The hero reads 4 left to find, 2 found, and 48 to drop. The grid shows 2 white (found), 4 red (out now), and 48 dashed slots. The data-slot count of the page is found 3, out 5, and future 49, because the legend holds one more of each.

## AT-43: The egg word cards of the board

App: site
Then: The cards show $50, $30, and $20 and the top 5 of each egg word. The tap shows all 11 managers.
Files: `evidence/AT-43/after-1280-dark.png`, `evidence/AT-43/after-1280-light.png`, `evidence/AT-43/after-375-dark.png`, `evidence/AT-43/after-375-light.png`, `evidence/AT-43/after-768-dark.png`, `evidence/AT-43/after-768-light.png`, `evidence/AT-43/before-1280-dark.png`, `evidence/AT-43/before-1280-light.png`, `evidence/AT-43/before-375-dark.png`, `evidence/AT-43/before-375-light.png`, `evidence/AT-43/before-768-dark.png`, `evidence/AT-43/before-768-light.png`, `evidence/AT-43/site-B.txt`, `evidence/AT-43/steps.txt`
Observation: Seven managers hold letters. Each card shows its gift card, $50, $30, and $20. The CORNERSTONE card lists 5 rows before "Show all 11" and 11 rows after the tap, at each width and theme. Store B holds 12 eggs and 8 claims, so its counts differ from AT-42.

## AT-44: A won egg word

App: site
Then: EAGLES is a hero card with a WON stamp and Lil Fridge.
Files: `evidence/AT-44/1280-dark.png`, `evidence/AT-44/1280-light.png`, `evidence/AT-44/375-dark.png`, `evidence/AT-44/375-light.png`, `evidence/AT-44/768-dark.png`, `evidence/AT-44/768-light.png`, `evidence/AT-44/site-E.txt`, `evidence/AT-44/steps.txt`
Observation: After AT-12, the EAGLES card is a hero card with the tiles E A G L E S, "Lil Fridge won it.", a WON stamp, and "The $20 gift card is theirs. The race is over."

## AT-45: Latest claims

App: site
Then: The feed shows two rows, each with the manager, the letter, and the egg word. It shows no page, no spot, and no block.
Files: `evidence/AT-45/1280-dark.png`, `evidence/AT-45/1280-light.png`, `evidence/AT-45/375-dark.png`, `evidence/AT-45/375-light.png`, `evidence/AT-45/768-dark.png`, `evidence/AT-45/768-light.png`, `evidence/AT-45/site-B.txt`, `evidence/AT-45/steps.txt`
Observation: Store B holds two claims (Teehee C into CORNERSTONE, Lil Fridge A into LANSDALE) and one block (Teehee, T1). The feed shows two rows: "Lil Fridge claimed an A for LANSDALE." and "Teehee claimed a C for CORNERSTONE.", with no page, no spot, and no block.

## AT-46: How the hunt works

App: site
Then: It states the egg drop each Tuesday, the claim, the letter rule, the gift cards, and that the commissioner cannot hunt.
Files: `evidence/AT-46/1280-dark.png`, `evidence/AT-46/1280-light.png`, `evidence/AT-46/375-dark.png`, `evidence/AT-46/375-light.png`, `evidence/AT-46/768-dark.png`, `evidence/AT-46/768-light.png`, `evidence/AT-46/site-A0.txt`, `evidence/AT-46/steps.txt`
Observation: The last card "How the hunt works" lists 8 points: 6 eggs drop each Tuesday from week 9 through week 17; tap or press a spot; the first claim gets the letter; each letter goes in an egg word or blocks; the letter rule and its guard; the gift cards CORNERSTONE $50, LANSDALE $30, EAGLES $20; and "The commissioner places every egg, so the commissioner cannot hunt."

## AT-47: The egg board before the first drop

App: site
Then: The three egg words show with no letters, and the count to drop is 54.
Files: `evidence/AT-47/1280-dark.png`, `evidence/AT-47/1280-light.png`, `evidence/AT-47/375-dark.png`, `evidence/AT-47/375-light.png`, `evidence/AT-47/768-dark.png`, `evidence/AT-47/768-light.png`, `evidence/AT-47/board.json`, `evidence/AT-47/site-A0.txt`, `evidence/AT-47/steps.txt`
Observation: In an empty store, /eggs/ shows 0 left to find, 0 found, and 54 to drop, and the three egg words with "No letters yet. The race is open." and empty tiles, at each width and theme. board.json is the board answer.

## AT-48: The copy rules hold

App: site
Then: The grep finds none.
Files: `evidence/AT-48/output.txt`
Observation: The grep of the eggs site copy (packages/eggs/site and apps/site/src/app/_routes/eggs, tests left out) found 0 "rival", 0 "Brian", and 0 page names or target ids in the copy. The built /eggs/ page holds 0 "rival" and 0 "Brian".

## AT-49: Reduced motion

App: site
Then: The C tile shows with no motion.
Files: `evidence/AT-49/1280-dark.png`, `evidence/AT-49/1280-light.png`, `evidence/AT-49/375-dark.png`, `evidence/AT-49/375-light.png`, `evidence/AT-49/768-dark.png`, `evidence/AT-49/768-light.png`, `evidence/AT-49/site-A1.txt`, `evidence/AT-49/steps.txt`
Observation: With reduced motion, 100 ms after the tap on the egg, each shot shows the C tile at rest. The page has 0 running animations, and the tile and its parent have no animation and a transition of 0 s.

## AT-50: The readability floor holds

App: site
Then: Each one passes.
Files: `evidence/AT-50/floor-eggs.txt`, `evidence/AT-50/site-A1.txt`, `evidence/AT-50/steps.txt`
Observation: At 4f87122b, CLIENT=cpc pnpm check:floor -g /eggs/ passed after a plain CPC build. By design it covers only the static shell of /eggs/: ADR 0025 keeps any state that needs the live API out of the check, because a fake API is a mock, and CI has no API. The loaded board, the claim sheet, and the banner got the same four scans of floor.ts (text, contrast, targets, scroll) in the phase A1 run on 4174, at 390 and 1280 px in each theme. The scans gave 0 failures of each kind on all three, with no axe incomplete item.

## AT-51: The whole flow, end to end

App: both
Then: The egg board shows the C of Lil Fridge in CORNERSTONE and the claim in the feed.
Files: `evidence/AT-51/1-egg-1280-dark.png`, `evidence/AT-51/1-egg-1280-light.png`, `evidence/AT-51/1-egg-375-dark.png`, `evidence/AT-51/1-egg-375-light.png`, `evidence/AT-51/2-tile-1280-dark.png`, `evidence/AT-51/2-tile-1280-light.png`, `evidence/AT-51/2-tile-375-dark.png`, `evidence/AT-51/2-tile-375-light.png`, `evidence/AT-51/3-sheet-1280-dark.png`, `evidence/AT-51/3-sheet-1280-light.png`, `evidence/AT-51/3-sheet-375-dark.png`, `evidence/AT-51/3-sheet-375-light.png`, `evidence/AT-51/4-claimed-1280-dark.png`, `evidence/AT-51/4-claimed-1280-light.png`, `evidence/AT-51/4-claimed-375-dark.png`, `evidence/AT-51/4-claimed-375-light.png`, `evidence/AT-51/5-board-1280-dark.png`, `evidence/AT-51/5-board-1280-light.png`, `evidence/AT-51/5-board-375-dark.png`, `evidence/AT-51/5-board-375-light.png`, `evidence/AT-51/eggs-spec.txt`, `evidence/AT-51/site-A2.txt`, `evidence/AT-51/steps.txt`
Observation: The flow at 375 and 1280 px in each theme: the egg, the C tile, the sheet with Lil Fridge and CORNERSTONE, the hero card "C goes to CORNERSTONE.", then /eggs/. The board shows the CORNERSTONE row "Lil Fridge LEADS 1/11 C" and the feed "Lil Fridge claimed a C for CORNERSTONE." eggs-spec.txt: apps/site/e2e/eggs.spec.ts (with D2) passed 2 of 2 on a fresh store, at 375 and 1280 px.
