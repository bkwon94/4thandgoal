# Egg polish: evidence

Spec: `.scratch/egg-polish/PRD.md`. Acceptance tests: `.scratch/egg-polish/ACCEPTANCE.md`.
Built from: `01cec88a`, on 2026-11-08. The agent gives no Test verdict. The Judge gives one for each test in `VERDICTS.md`.
Round time: 57 min for 38 tests with files. No test has a `steps.json`: each test needs its own board state from the local API, so Playwright scripts took every shot, in the shape of the evidence runner. Each test folder has a `steps.txt` that says how.

How the evidence ran:

- The API ran from this worktree on port 8081 with the env of `make -C apps/api api-evidence` (the test passphrase `localtest`, the test commissioner key `localkey`, 600 requests a minute, the origin `http://127.0.0.1:4173`) and an eggs store in a scratch folder. Each board state starts from a restart of the API with an empty store, because the limit of the egg check (60 an hour for one address) lives in its memory.
- The site was built from `01cec88a` with `NEXT_PUBLIC_API_URL=http://localhost:8081` and served on `http://127.0.0.1:4173`. AT-34 and AT-35 also use a build of `main` (`274ba9ec`) against the same API.
- T1 holds only in the light theme. A dark shot of the find card or the claim sheet finds T1 in light, then a page script sets the theme to dark, as the theme button does.
- In an empty store the letter rule gives the first egg the letter A. So T1 drops after a probe drop of filler eggs in week 10, at the place that gets C. A filler egg has a target that no element holds, so no reader can find it. Each board state gives each letter by a check and a claim of a filler egg through the real routes, so the hero counts include the unclaimed fillers.
- The scripts are in the session scratchpad under `evidence-scripts/` (`lib.mjs`, `find.mjs`, `claim.mjs`, `board.mjs`, `floor-boards.mjs`), not in the repo.

## AT-1: The tap squashes the egg

App: site
Then: The egg squashes within 0.2 s of the tap, before any crack line shows.
Files: `evidence/AT-1/steps.txt`, `evidence/AT-1/measures.txt`, `evidence/AT-1/frame-0.0s.png`, `evidence/AT-1/frame-0.1s.png`, `evidence/AT-1/frame-0.2s.png`, `evidence/AT-1/crop-house-0.0s-3x.png`, `evidence/AT-1/crop-house-reduced-3x.png`, `evidence/AT-1/recording.webm`
Observation: Recorded again from `e56bb80a`. The egg svg has the transform matrix(1.06, 0, 0, 0.91, 0, 0) at 0.05 s and scale(1.07, 0.89) at 0.1 s, while all six crack lines have 0 units drawn and all seven shards have opacity 0 through 0.15 s. The 3x crops of the house at 0 s and with reduced motion show no seam, and each is the same as a crop of the whole art alone, with a largest pixel difference of 0.

## AT-2: The crack starts at the tap point

App: site
Then: Every crack line starts at the spot of the tap.
Files: `evidence/AT-2/steps.txt`, `evidence/AT-2/lines.txt`, `evidence/AT-2/frame-0.4s.png`, `evidence/AT-2/frame-before-tap.png`, `evidence/AT-2/recording-strip.png`, `evidence/AT-2/recording.webm`
Observation: In the units of the egg art, the tap point is 45.0,72.6, and all six lines start at 44.5,71.8. On the screen, the card moves up at the tap: its top goes from 261.4 px to 179.6 px and the egg svg top from 324.0 px to 246.6 px. So in `frame-0.4s.png` the lines start near the upper left of the egg, about 80 px above the cyan ring of the tap, which sits on the lower left of the egg. `frame-before-tap.png` shows the ring on the upper left of the egg before the tap, and `recording-strip.png` shows the jump of the card in the real recording.

## AT-3: Each find cracks anew

App: site
Then: The crack lines of the two finds differ.
Files: `evidence/AT-3/steps.txt`, `evidence/AT-3/lines.txt`, `evidence/AT-3/find-1-0.4s.png`, `evidence/AT-3/find-2-0.4s.png`, `evidence/AT-3/side-by-side.png`
Observation: Both finds tap the egg point 63.0,88.0, and both sets of lines start at 62.5,87.8. Every later point of each of the six lines differs between the two finds, and the side-by-side frames show two different crack patterns.

## AT-4: The crack builds, then bursts

App: site
Then: The egg shakes and glows from the tap point while the lines draw, then the shell bursts into shards that fly out from the tap point at about 0.56 s.
Files: `evidence/AT-4/steps.txt`, `evidence/AT-4/measures.txt`, `evidence/AT-4/frame-0.3s.png`, `evidence/AT-4/frame-0.6s.png`, `evidence/AT-4/recording.webm`
Observation: At 0.3 s the egg has the class egg-shake, the glow sits at the tap point 107.5,120.8 with opacity 0.12, and four lines are part drawn. At 0.6 s every line is fully drawn and fades, the glow has opacity 0.96, and each shard has a move and a turn away from the tap point. The CSS starts the halves, the shards, and the flash at 0.56 s. The 0.6 s frame shows the shards near the tap point and the halves at the start of their split.

## AT-5: The tile grows from the tap point

App: site
Then: The letter tile grows out of the spot of the tap, and the tile C with the copy "The letter C is yours to claim." shows at 1.3 s, plus or minus 0.2 s, after the tap.
Files: `evidence/AT-5/steps.txt`, `evidence/AT-5/timing.txt`, `evidence/AT-5/375-dark.png`, `evidence/AT-5/768-dark.png`, `evidence/AT-5/1280-dark.png`, `evidence/AT-5/375-light.png`, `evidence/AT-5/768-light.png`, `evidence/AT-5/1280-light.png`, `evidence/AT-5/recording.webm`
Observation: The copy "The letter C is yours to claim." showed 1302 ms after the pointerdown, and each shot shows the red tile C, that copy, "Claim C", and "Close". The transform-origin of the tile is the tap point in the units of the egg art. On the screen the card moves up about 82 px at the tap, so the growth origin sits at 227.0,418.2 px while the tap was at 227.1,500.8 px.

## AT-6: Enter cracks the egg from its middle

App: site
Then: The crack lines start at the middle of the egg, and the letter C shows.
Files: `evidence/AT-6/steps.txt`, `evidence/AT-6/lines.txt`, `evidence/AT-6/frame-0.4s.png`, `evidence/AT-6/recording.webm`
Observation: With the focus on the button "Crack the egg", Enter cracks the egg, and all six lines start at 90.0,130.0, the middle of the egg art. The recording run ends on the tile C and the title "The letter C is yours to claim.".

## AT-7: Reduced motion shows the letter at once

App: site
Then: The letter C shows at once, with no crack line, no shard, and no motion.
Files: `evidence/AT-7/steps.txt`, `evidence/AT-7/hunt-test-motion-off.txt`, `evidence/AT-7/page-script.txt`, `evidence/AT-7/after-tap-375-light.png`, `evidence/AT-7/recording.webm`
Observation: One animation frame after the tap, the tile reads C, the title reads "The letter C is yours to claim.", and the page has 0 crack lines, 0 shards, and 0 running animations. The vitest file of the hunt with motion off passes its 2 tests.

## AT-8: The crack needs no WebGL

App: site
Then: The crack plays to the letter C, and the page asks for no WebGL context.
Files: `evidence/AT-8/steps.txt`, `evidence/AT-8/page-script.txt`, `evidence/AT-8/recording.webm`
Observation: In Chromium with WebGL off (a blank page gets null for webgl and webgl2), the page makes 0 calls of getContext with a WebGL type from the load to the letter. The crack plays and ends on the tile C and its copy.

## AT-9: The claim ticket shows what the manager claims

App: site
Then: The claim ticket shows the tile C, CORNERSTONE, and Lil Fridge, and the stub reads "Tear to claim".
Files: `evidence/AT-9/steps.txt`, `evidence/AT-9/ticket.txt`, `evidence/AT-9/375-dark.png`, `evidence/AT-9/768-dark.png`, `evidence/AT-9/1280-dark.png`, `evidence/AT-9/375-light.png`, `evidence/AT-9/768-light.png`, `evidence/AT-9/1280-light.png`
Observation: In each shot the ticket shows the red tile C, CORNERSTONE, and Lil Fridge, and the red stub reads "TEAR TO CLAIM". The page script reads the stub name "Tear to claim C for CORNERSTONE" at each width and theme.

## AT-10: A locked stub names the next step

App: site
Then: The stub reads "Pick an egg word", it does not tear, and the API gets no claim.
Files: `evidence/AT-10/steps.txt`, `evidence/AT-10/requests.txt`, `evidence/AT-10/ticket.txt`, `evidence/AT-10/375-dark.png`, `evidence/AT-10/768-dark.png`, `evidence/AT-10/1280-dark.png`, `evidence/AT-10/375-light.png`, `evidence/AT-10/768-light.png`, `evidence/AT-10/1280-light.png`
Observation: After the tap, each shot shows the grey stub "PICK AN EGG WORD" in place on the ticket, with "Egg word" in the body. The request log of each of the six runs has 0 POST /claim, and the board after the runs counts 0 found.

## AT-11: A drag tears the stub and sends the claim

App: site
Then: The holes of the perforation pop from the top down during the drag, the stub flutters away, the ticket shows the sweep, and the API gets one claim of T1 for Lil Fridge into CORNERSTONE.
Files: `evidence/AT-11/steps.txt`, `evidence/AT-11/holes.txt`, `evidence/AT-11/requests.txt`, `evidence/AT-11/recording-strip.png`, `evidence/AT-11/recording.webm`
Observation: The holes pop one by one from the top as the drag grows from 10 to 100 px, and the stub tilts further at each step. The strip shows the stub fly off and the CLAIMED stamp. The log has one POST /claim with roster_id 3 and CORNERSTONE, which answers 200. The page script finds no sweep element 100 ms and 300 ms after the release, because the local API answered first.

## AT-12: An early release sends nothing

App: site
Then: The stub springs back onto the ticket, and the API gets no claim.
Files: `evidence/AT-12/steps.txt`, `evidence/AT-12/requests.txt`, `evidence/AT-12/ticket.txt`, `evidence/AT-12/recording.webm`
Observation: At 55 px of drag the stub has a tilt transform. 1.5 s after the release its transform is none and it still reads "Tear to claim". The log has 0 POST /claim, and the board counts 0 found.

## AT-13: A tap tears the stub

App: site
Then: The stub tears by itself, and the API gets one claim of T1.
Files: `evidence/AT-13/steps.txt`, `evidence/AT-13/requests.txt`, `evidence/AT-13/recording.webm`
Observation: After one tap with no move, the log has one POST /claim that answers 200, and the end card reads "C goes to CORNERSTONE.".

## AT-14: A key tears the stub

App: site
Then: The stub tears, and the API gets one claim of T1. The accessible name of the stub is "Tear to claim C for CORNERSTONE".
Files: `evidence/AT-14/steps.txt`, `evidence/AT-14/requests.txt`, `evidence/AT-14/recording-space.webm`, `evidence/AT-14/recording.webm`
Observation: The ARIA snapshot shows `button "Tear to claim C for CORNERSTONE"` in the group "Claim ticket", and the focus is on it before the key. Enter and, on a fresh drop, Space each give one POST /claim that answers 200 and the end card "C goes to CORNERSTONE.".

## AT-15: A claim stamps CLAIMED

App: site
Then: The ticket stamps CLAIMED, and then the end card of a claim shows, with the red tile C in its slot of CORNERSTONE.
Files: `evidence/AT-15/steps.txt`, `evidence/AT-15/notes.txt`, `evidence/AT-15/end-375-dark.png`, `evidence/AT-15/end-768-dark.png`, `evidence/AT-15/end-1280-dark.png`, `evidence/AT-15/end-375-light.png`, `evidence/AT-15/end-768-light.png`, `evidence/AT-15/end-1280-light.png`, `evidence/AT-15/stamp-375-dark.png`, `evidence/AT-15/stamp-768-dark.png`, `evidence/AT-15/stamp-1280-dark.png`, `evidence/AT-15/stamp-375-light.png`, `evidence/AT-15/stamp-768-light.png`, `evidence/AT-15/stamp-1280-light.png`
Observation: Each stamp shot shows the ticket with the stub gone and a red CLAIMED stamp over its body. Each end shot shows the end card "C goes to CORNERSTONE." with the tiles of CORNERSTONE.

## AT-16: A claim too late stamps TAKEN

App: site
Then: The second ticket stamps TAKEN, the stub comes back onto it, and then the end card for another manager first shows.
Files: `evidence/AT-16/steps.txt`, `evidence/AT-16/notes.txt`, `evidence/AT-16/end-375-dark.png`, `evidence/AT-16/end-768-dark.png`, `evidence/AT-16/end-1280-dark.png`, `evidence/AT-16/end-375-light.png`, `evidence/AT-16/end-768-light.png`, `evidence/AT-16/end-1280-light.png`, `evidence/AT-16/stamp-375-dark.png`, `evidence/AT-16/stamp-768-dark.png`, `evidence/AT-16/stamp-1280-dark.png`, `evidence/AT-16/stamp-375-light.png`, `evidence/AT-16/stamp-768-light.png`, `evidence/AT-16/stamp-1280-light.png`, `evidence/AT-16/teehee-end-375-light.png`, `evidence/AT-16/teehee-stamp-375-light.png`
Observation: With both browsers on Lil Fridge, as the Given says, the second claim answers 422, and the second sheet shows "CORNERSTONE has no open slot for the letter C." with the stub back on the ticket, no TAKEN stamp, and no end card. The real API refuses a second C of CORNERSTONE for the same manager before it checks the egg. In the extra race where the second browser picks Teehee, the claim answers 409, the ticket stamps TAKEN with the stub on it, and the end card reads "Another manager claimed first.".

## AT-17: A wrong passphrase brings the stub back

App: site
Then: The text "The passphrase is wrong. Ask a league member for it." shows, and the stub comes back onto the ticket. After the reader types the test passphrase and tears again, the ticket stamps CLAIMED.
Files: `evidence/AT-17/steps.txt`, `evidence/AT-17/notes.txt`, `evidence/AT-17/requests.txt`, `evidence/AT-17/375-dark.png`, `evidence/AT-17/768-dark.png`, `evidence/AT-17/1280-dark.png`, `evidence/AT-17/375-light.png`, `evidence/AT-17/768-light.png`, `evidence/AT-17/1280-light.png`, `evidence/AT-17/recording.webm`
Observation: Each shot shows the red text "The passphrase is wrong. Ask a league member for it." and the stub back on the ticket. The passphrase field is empty, so the stub is locked and reads "ENTER THE PASSPHRASE". In the recording, after "localtest" goes into the field, the second tear stamps CLAIMED.

## AT-18: A block ticket shows the block

App: site
Then: The ticket shows the tile C and the block in place of an egg word, and the stub reads "Tear to claim".
Files: `evidence/AT-18/steps.txt`, `evidence/AT-18/ticket.txt`, `evidence/AT-18/375-dark.png`, `evidence/AT-18/768-dark.png`, `evidence/AT-18/1280-dark.png`, `evidence/AT-18/375-light.png`, `evidence/AT-18/768-light.png`, `evidence/AT-18/1280-light.png`
Observation: The board holds the C of Lil Fridge in CORNERSTONE. With T4 (letter C) found and Lil Fridge picked, each ticket shows the tile C, BLOCK, and Lil Fridge, and the red stub reads "TEAR TO CLAIM", with the name "Tear to claim C as a block". The sheet shows the notice "C fits none of your egg words.".

## AT-19: Reduced motion keeps the claim still

App: site
Then: The stub leaves and the stamp CLAIMED shows, with no flutter, no sweep, and no motion.
Files: `evidence/AT-19/steps.txt`, `evidence/AT-19/page-script.txt`, `evidence/AT-19/stamp-375-light.png`, `evidence/AT-19/recording.webm`
Observation: At the stamp the stub has visibility hidden and the ticket reads CLAIMED. The page has 0 running animations one frame after the tap and at the stamp, and 0 elements with the flutter or the sweep class.

## AT-20: The egg board hero sits on the hero slots

App: site
Then: The hero shows the eyebrow "Egg hunt", the title "The Egg Board", the meta line of the gift cards, the grid of the eggs of each week with its legend, and three tiles for left to find, found, and to drop. The hero has no scene canvas.
Files: `evidence/AT-20/steps.txt`, `evidence/AT-20/hero.txt`, `evidence/AT-20/375-dark.png`, `evidence/AT-20/768-dark.png`, `evidence/AT-20/1280-dark.png`, `evidence/AT-20/375-light.png`, `evidence/AT-20/768-light.png`, `evidence/AT-20/1280-light.png`
Observation: Each shot shows the hero with the eyebrow "EGG HUNT", the title "The Egg Board", the line "$100 in gift cards. Three egg words. First to fill a word wins it.", the grid of weeks 09 to 17 with its legend, and three tiles LEFT TO FIND 1, FOUND 0, TO DROP 53. The page script counts 0 canvas elements in the hero and 0 on the page.

## AT-21: The tab row shows each race

App: site
Then: The tab row reads CORNERSTONE 2/11, LANSDALE 1/8, and EAGLES 0/6, in that order.
Files: `evidence/AT-21/steps.txt`, `evidence/AT-21/slider.txt`, `evidence/AT-21/375-dark.png`, `evidence/AT-21/768-dark.png`, `evidence/AT-21/1280-dark.png`, `evidence/AT-21/375-light.png`, `evidence/AT-21/768-light.png`, `evidence/AT-21/1280-light.png`, `evidence/AT-21/slider-375-dark.png`, `evidence/AT-21/slider-768-dark.png`, `evidence/AT-21/slider-1280-dark.png`, `evidence/AT-21/slider-375-light.png`, `evidence/AT-21/slider-768-light.png`, `evidence/AT-21/slider-1280-light.png`
Observation: In each shot and in slider.txt, the tab row reads CORNERSTONE 2/11, LANSDALE 1/8, and EAGLES 0/6, in that order, and the slider opens on CORNERSTONE.

## AT-22: The closest race opens first

App: site
Then: The slider opens on EAGLES, and the tabs keep the order CORNERSTONE, LANSDALE, EAGLES.
Files: `evidence/AT-22/steps.txt`, `evidence/AT-22/slider.txt`, `evidence/AT-22/375-dark.png`, `evidence/AT-22/768-dark.png`, `evidence/AT-22/1280-dark.png`, `evidence/AT-22/375-light.png`, `evidence/AT-22/768-light.png`, `evidence/AT-22/1280-light.png`, `evidence/AT-22/slider-375-dark.png`, `evidence/AT-22/slider-768-dark.png`, `evidence/AT-22/slider-1280-dark.png`, `evidence/AT-22/slider-375-light.png`, `evidence/AT-22/slider-768-light.png`, `evidence/AT-22/slider-1280-light.png`
Observation: On open, the shown slide is EAGLES, and the slide order is EAGLES, CORNERSTONE, LANSDALE. The tabs keep the order CORNERSTONE 2/11, LANSDALE 0/8, EAGLES 5/6, with EAGLES selected.

## AT-23: The giant word lights the letters of the leader

App: site
Then: The giant word lights E, A, G, L, and S in white, and shows the second E as a dim outline.
Files: `evidence/AT-23/steps.txt`, `evidence/AT-23/giant-word.txt`, `evidence/AT-23/375-dark.png`, `evidence/AT-23/768-dark.png`, `evidence/AT-23/1280-dark.png`, `evidence/AT-23/375-light.png`, `evidence/AT-23/768-light.png`, `evidence/AT-23/1280-light.png`, `evidence/AT-23/slide-375-dark.png`, `evidence/AT-23/slide-768-dark.png`, `evidence/AT-23/slide-1280-dark.png`, `evidence/AT-23/slide-375-light.png`, `evidence/AT-23/slide-768-light.png`, `evidence/AT-23/slide-1280-light.png`
Observation: The giant word of EAGLES shows E, A, G, L, and S as white tiles with dark letters, and the second E as an outline with a grey letter and border and no fill. giant-word.txt reads the same states and colors at each width and theme.

## AT-24: A swipe or a tab moves the slide

App: site
Then: The side swipe moves to the next slide, the tap moves to LANSDALE with the giant word swapping letter by letter, and the swipe up scrolls the page.
Files: `evidence/AT-24/steps.txt`, `evidence/AT-24/page-script.txt`, `evidence/AT-24/recording.webm`
Observation: The touch swipe to the left moves the slide from EAGLES to CORNERSTONE, the next slide in the slide order. The tap on LANSDALE selects it and shows its slide, and each giant word takes a roll state (LANSDALE in, CORNERSTONE out-up), and the recording holds the move. The touch swipe up moves scrollY from 703 to 999, and the slide stays LANSDALE.

## AT-25: A slide keeps the detail of each manager

App: site
Then: The slide shows "Lil Fridge leads with 4 of 11.", the top 5 managers with their tiles, and after the tap, all 12 managers in place.
Files: `evidence/AT-25/steps.txt`, `evidence/AT-25/slider.txt`, `evidence/AT-25/after-375-dark.png`, `evidence/AT-25/after-768-dark.png`, `evidence/AT-25/after-1280-dark.png`, `evidence/AT-25/after-375-light.png`, `evidence/AT-25/after-768-light.png`, `evidence/AT-25/after-1280-light.png`, `evidence/AT-25/before-375-dark.png`, `evidence/AT-25/before-768-dark.png`, `evidence/AT-25/before-1280-dark.png`, `evidence/AT-25/before-375-light.png`, `evidence/AT-25/before-768-light.png`, `evidence/AT-25/before-1280-light.png`, `evidence/AT-25/slider-after-375-dark.png`, `evidence/AT-25/slider-after-768-dark.png`, `evidence/AT-25/slider-after-1280-dark.png`, `evidence/AT-25/slider-after-375-light.png`, `evidence/AT-25/slider-after-768-light.png`, `evidence/AT-25/slider-after-1280-light.png`, `evidence/AT-25/slider-before-375-dark.png`, `evidence/AT-25/slider-before-768-dark.png`, `evidence/AT-25/slider-before-1280-dark.png`, `evidence/AT-25/slider-before-375-light.png`, `evidence/AT-25/slider-before-768-light.png`, `evidence/AT-25/slider-before-1280-light.png`
Observation: Before the tap, the slide reads "Lil Fridge leads with 4 of 11." and lists 5 managers with their tiles. The button reads "Show all 11", not "Show all 12", because the board lists the 11 managers who hunt (the commissioner, roster 6, is not listed). After the tap, the slide lists all 11 managers in place, and the button reads "Show the top 5".

## AT-26: A tie says that the managers tie

App: site
Then: The leader line reads "Lil Fridge and Teehee tie with 2 of 11.", with the two teams in the order of the rosters.
Files: `evidence/AT-26/steps.txt`, `evidence/AT-26/slider.txt`, `evidence/AT-26/375-dark.png`, `evidence/AT-26/768-dark.png`, `evidence/AT-26/1280-dark.png`, `evidence/AT-26/375-light.png`, `evidence/AT-26/768-light.png`, `evidence/AT-26/1280-light.png`, `evidence/AT-26/slider-375-dark.png`, `evidence/AT-26/slider-768-dark.png`, `evidence/AT-26/slider-1280-dark.png`, `evidence/AT-26/slider-375-light.png`, `evidence/AT-26/slider-768-light.png`, `evidence/AT-26/slider-1280-light.png`
Observation: The leader line reads "Lil Fridge and Teehee tie with 2 of 11.", with Lil Fridge (roster 3) first and Teehee (roster 12) second, both marked LEADS.

## AT-27: A won word washes red and goes last

App: site
Then: The last slide is EAGLES. It washes the frame red, lights every letter in red, and shows Lil Fridge and the gift card. The tab reads "EAGLES · Won".
Files: `evidence/AT-27/steps.txt`, `evidence/AT-27/slider.txt`, `evidence/AT-27/375-dark.png`, `evidence/AT-27/768-dark.png`, `evidence/AT-27/1280-dark.png`, `evidence/AT-27/375-light.png`, `evidence/AT-27/768-light.png`, `evidence/AT-27/1280-light.png`, `evidence/AT-27/slider-375-dark.png`, `evidence/AT-27/slider-768-dark.png`, `evidence/AT-27/slider-1280-dark.png`, `evidence/AT-27/slider-375-light.png`, `evidence/AT-27/slider-768-light.png`, `evidence/AT-27/slider-1280-light.png`
Observation: The slide order puts EAGLES last. On its slide the frame is red (rgb(184, 52, 42)), every letter of EAGLES has the state won (a red tile with a white letter and a white border), and the slide reads "Lil Fridge won it." and "The $20 gift card is theirs. The race is over.". The tab reads "EAGLES · Won".

## AT-28: Before any claim the board opens on CORNERSTONE

App: site
Then: The slider opens on CORNERSTONE with every letter as a dim outline, and the line "No letters yet. The race is open." shows.
Files: `evidence/AT-28/steps.txt`, `evidence/AT-28/slider.txt`, `evidence/AT-28/375-dark.png`, `evidence/AT-28/768-dark.png`, `evidence/AT-28/1280-dark.png`, `evidence/AT-28/375-light.png`, `evidence/AT-28/768-light.png`, `evidence/AT-28/1280-light.png`, `evidence/AT-28/slider-375-dark.png`, `evidence/AT-28/slider-768-dark.png`, `evidence/AT-28/slider-1280-dark.png`, `evidence/AT-28/slider-375-light.png`, `evidence/AT-28/slider-768-light.png`, `evidence/AT-28/slider-1280-light.png`
Observation: The slider opens on CORNERSTONE. Every letter of its giant word has the state outline, and the slide reads "No letters yet. The race is open.".

## AT-29: The arrow keys move between tabs

App: site
Then: The focus moves to LANSDALE, then to EAGLES, and the slide follows each tab. The tab row has the role `tablist`, each tab has the role `tab`, and each slide has the role `tabpanel`.
Files: `evidence/AT-29/steps.txt`, `evidence/AT-29/aria-tree.txt`, `evidence/AT-29/page-script.txt`, `evidence/AT-29/recording.webm`
Observation: After focus on CORNERSTONE, the first ArrowRight moves the focus and the selection to LANSDALE and shows its tabpanel, and the second moves them to EAGLES. The ARIA snapshot shows a tablist "Egg words" with three tabs and a tabpanel; the DOM has 1 tablist, 3 tabs, and 3 tabpanels, each labelled by its tab.

## AT-30: Reduced motion changes the word at once

App: site
Then: The slide changes at once, with no roll, no blur, and no letter swap.
Files: `evidence/AT-30/steps.txt`, `evidence/AT-30/page-script.txt`, `evidence/AT-30/after-tap-375-light.png`, `evidence/AT-30/recording.webm`
Observation: One frame after the tap on LANSDALE, the shown tabpanel is LANSDALE, 0 animations run, every transition and animation duration of the slides and letters is 0s, and --es-dur of the slider is 0s.

## AT-31: Every part keeps the readability floor

App: site
Then: Axe finds 0 violations and 0 incomplete items, each tap target is 44px or more, and no page scrolls to the side at 390px.
Files: `evidence/AT-31/steps.txt`, `evidence/AT-31/eggs-output.txt`, `evidence/AT-31/floor-boards.txt`
Observation: The eggs project prints axe violations 0 and axe incomplete 0, 0 tap targets under 44px, and 0 sideways scroll, for the find card, the claim sheet, and each slide of the egg board in both themes, and its 3 tests pass. That run holds only one claim on its board. The extra check on the boards of AT-22 and AT-27 finds 0 violations, 0 small targets, and a page width of 390, but 1 incomplete item (color-contrast) on each slide: the muted labels of the weeks with no egg in the hero grid. The control board with T1 alone gives 0 incomplete items.

## AT-32: The board gives no hint

App: site
Then: No text, attribute, or link on the board names `/midseason/2026/`, `luck-3`, or any other page or target of an egg.
Files: `evidence/AT-32/steps.txt`, `evidence/AT-32/page-script.txt`
Observation: On each of the three slides, page.content() of the board holds 0 matches of /midseason/2026/, /midseason/2026, midseason, luck-3, luck, tap2, and evidence-filler, and main holds no link. The board answer of the API holds 0 of them too. The e2e run prints 0 matches of /midseason/2026/, /midseason/2026, and luck-3 at 375 and 1280 px.

## AT-33: A manager finds, cracks, tears, and sees the claim

App: site
Then: The test finds T1, cracks the egg, tears the stub, and sees the letter C of Lil Fridge on the egg board.
Files: `evidence/AT-33/steps.txt`, `evidence/AT-33/eggs-output.txt`
Observation: The output shows 3 passed: the path of a manager at 375 px and at 1280 px, and the floor test. In this run T1 got the letter A from the letter rule of an empty store, not C, and the test read A from the drop answer and checked A on the board.

## AT-34: The egg button and the egg banner do not change

App: site
Then: The egg button and the egg banner look and read as on `main`.
Files: `evidence/AT-34/steps.txt`, `evidence/AT-34/texts.txt`, `evidence/AT-34/main-banner-375-dark.png`, `evidence/AT-34/main-banner-768-dark.png`, `evidence/AT-34/main-banner-1280-dark.png`, `evidence/AT-34/main-banner-375-light.png`, `evidence/AT-34/main-banner-768-light.png`, `evidence/AT-34/main-banner-1280-light.png`, `evidence/AT-34/main-top-375-dark.png`, `evidence/AT-34/main-top-768-dark.png`, `evidence/AT-34/main-top-1280-dark.png`, `evidence/AT-34/main-top-375-light.png`, `evidence/AT-34/main-top-768-light.png`, `evidence/AT-34/main-top-1280-light.png`, `evidence/AT-34/spec-banner-375-dark.png`, `evidence/AT-34/spec-banner-768-dark.png`, `evidence/AT-34/spec-banner-1280-dark.png`, `evidence/AT-34/spec-banner-375-light.png`, `evidence/AT-34/spec-banner-768-light.png`, `evidence/AT-34/spec-banner-1280-light.png`, `evidence/AT-34/spec-top-375-dark.png`, `evidence/AT-34/spec-top-768-dark.png`, `evidence/AT-34/spec-top-1280-dark.png`, `evidence/AT-34/spec-top-375-light.png`, `evidence/AT-34/spec-top-768-light.png`, `evidence/AT-34/spec-top-1280-light.png`
Observation: The egg button reads "Egg board, 1 egg left to find" with the badge 1, and the banner reads "1 egg dropped today · 1 left Egg board", on both builds at each width and theme. The banner shots and the top shots are the same files byte for byte on both builds, except the top shot at 768 px dark, where the two shots look the same to the eye.

## AT-35: The latest claims and the rules do not change

App: site
Then: The latest claims and how the hunt works look and read as on `main`.
Files: `evidence/AT-35/steps.txt`, `evidence/AT-35/main-text.txt`, `evidence/AT-35/spec-text.txt`, `evidence/AT-35/main-latest-375-dark.png`, `evidence/AT-35/main-latest-1280-dark.png`, `evidence/AT-35/main-latest-375-light.png`, `evidence/AT-35/main-latest-1280-light.png`, `evidence/AT-35/main-rules-375-dark.png`, `evidence/AT-35/main-rules-1280-dark.png`, `evidence/AT-35/main-rules-375-light.png`, `evidence/AT-35/main-rules-1280-light.png`, `evidence/AT-35/spec-latest-375-dark.png`, `evidence/AT-35/spec-latest-1280-dark.png`, `evidence/AT-35/spec-latest-375-light.png`, `evidence/AT-35/spec-latest-1280-light.png`, `evidence/AT-35/spec-rules-375-dark.png`, `evidence/AT-35/spec-rules-1280-dark.png`, `evidence/AT-35/spec-rules-375-light.png`, `evidence/AT-35/spec-rules-1280-light.png`
Observation: The text of "Latest claims" and "How the hunt works" is the same on both builds. The shots of each section look the same on both builds; the latest claims of the spec shots read NOW and those of main read 1M, because main ran about a minute later.

## AT-36: No new dependency and no Scrolltide source

App: site
Then: No `package.json` adds a dependency, and the diff holds no Scrolltide source.
Files: `evidence/AT-36/output.txt`
Observation: `git diff main -- '**/package.json'` and the glob form print nothing, and the root package.json and pnpm-lock.yaml have no diff. The file list holds docs, e2e files, globals.css, hero.tsx, and files of packages/eggs/site. The word Scrolltide shows only in the markdown of .scratch/egg-polish and its tickets, as a name, with no source.

## AT-37: The API does not change

App: site
Then: The diff is empty.
Files: `evidence/AT-37/output.txt`
Observation: `git diff --stat main -- apps/api packages/eggs/python` prints nothing, and the line count of the full diff is 0. The diff of packages/eggs/site/lib, the API client of the site, is empty too.

## AT-38: No egg word gets its own tint

App: site
Then: CORNERSTONE and LANSDALE sit on the dark hero ground, and only EAGLES, the won word, is red.
Files: `evidence/AT-38/steps.txt`, `evidence/AT-38/colors.txt`, `evidence/AT-38/cornerstone-375-dark.png`, `evidence/AT-38/cornerstone-375-light.png`, `evidence/AT-38/eagles-375-dark.png`, `evidence/AT-38/eagles-375-light.png`, `evidence/AT-38/lansdale-375-dark.png`, `evidence/AT-38/lansdale-375-light.png`
Observation: At 375 px in both themes, the slides of CORNERSTONE and LANSDALE sit on the dark frame (rgb(20, 20, 20), class bg-band), and only the won slide of EAGLES has the red frame (rgb(184, 52, 42), class bg-accent).
