"""
Write .scratch/easter-eggs/EVIDENCE.md from ACCEPTANCE.md, the files of each evidence folder, and the observations below.
Run it from the repo root with python3 after the evidence of each test is in its folder.
"""
import re
from pathlib import Path

FEATURE = Path(__file__).resolve().parents[2]
EV = FEATURE / "evidence"
text = (FEATURE / "ACCEPTANCE.md").read_text(encoding="utf-8")
tests = {}
for block in re.split(r"\n(?=AT-\d+: )", text.split("## Tests", 1)[1].split("## Trace", 1)[0]):
    head = re.match(r"AT-(\d+): (.+)", block.strip())
    if not head:
        continue
    fields = dict(re.findall(r"^(App|Then): (.+)$", block, re.M))
    tests[int(head.group(1))] = (head.group(2), fields["App"], fields["Then"])

PATH = "The real path of each route has the prefix /clients/cpc/eggs/; the test writes /cpc/eggs/."
OBS = {
    1: f"The check of T1 (luck-3, tap3, light) answered HTTP 200 with match true, claimed false, letter C, and a token. setup.txt shows the drops: T1 is egg 2 of week 9 with the letter C. {PATH}",
    2: f"The same check with the theme dark answered HTTP 200 with {{\"match\":false}} only, with no letter and no token. {PATH}",
    3: f"At 00:40 ET the check of T2 (window 23:00-00:00) answered {{\"match\":false}}. Only a test can set the API clock, so the check inside the window is the API test of the window, which passed: 22:59 ET no match, 23:30 ET a match, 23:30 Los Angeles no match, 00:00 ET no match. An extra real check of a twin egg with the window 00:00-02:00 matched at 00:41 ET. {PATH}",
    4: f"The check of T3 with sim_champion 3 (Lil Fridge) answered no match. The check with sim_champion 12 (Teehee) answered match true, letter E. {PATH}",
    5: f"The claim with the token of AT-1, roster 3, CORNERSTONE, and the passphrase answered HTTP 200 with the letters CORNERSTONE [C]. The board then showed found 1, CORNERSTONE [('Lil Fridge', ['C'])], and the claim in latest. {PATH}",
    6: f"Two tokens from two checks of T1. The two claims ran at once: Lil Fridge answered HTTP 200, and Teehee answered HTTP 409 with \"Another manager claimed first.\" The claims table holds one live row for egg 2 (roster 3), beside the undone row of AT-17. {PATH}",
    7: f"The claim for roster 6 (Bo Girds, the commissioner of values.eggs.commissioner) answered HTTP 422 with \"The commissioner places the eggs and cannot hunt them.\" The board after showed found 0, latest empty, and a new check of T1 still matched with a token. {PATH}",
    8: f"The claim with no X-League-Passphrase header answered HTTP 401 with an empty body. {PATH}",
    9: f"Lil Fridge held the C of CORNERSTONE from T1. The check of T4 matched with the letter C. The claim of T4 for Lil Fridge into CORNERSTONE answered HTTP 422 with \"CORNERSTONE has no open slot for the letter C.\" {PATH}",
    10: f"Before: counts left 11, found 1, and one row in latest. The block claim of T4 (word null) answered HTTP 200 with word null. After: counts left 10, found 2. The letters of Lil Fridge stayed CORNERSTONE [C] only, and latest still held one row, the C of CORNERSTONE. The claims table holds the block row with an empty word. {PATH}",
    11: f"Teehee held no letter in any egg word. The block claim of a T1 token (letter C) for Teehee answered HTTP 422 with \"The letter C fits an egg word of the manager, so a block is not open.\" {PATH}",
    12: f"setup.txt: Lil Fridge holds E, A, G, L, S in EAGLES, and egg 28 holds E. The claim of egg 28 for Lil Fridge into EAGLES answered HTTP 200 with winner roster 3, word EAGLES. A new E egg of week 12 (look-ahead-1-7) then matched, and the claim of Teehee into EAGLES answered HTTP 422 with \"EAGLES has a winner.\" The board shows the EAGLES winner Lil Fridge, and Teehee holds no letter in EAGLES. {PATH}",
    13: f"61 checks from Fly-Client-IP 10.13.0.1: checks 1 to 60 answered HTTP 200, and check 61 answered HTTP 429 with retry-after 3600. For the same address after check 61, the teams route answered 200, an empty analyze body answered 422, and one real analyze call with a real Claude call answered HTTP 200 with the decision yes and fallback false. A check from 10.13.0.2 answered 200. This run is on a fresh API start of the same store; the first run before the restart gave the same statuses. {PATH}",
    14: f"The drop with the passphrase and no X-Commissioner-Key answered HTTP 401 with content-length 0. The board counts and last_drop were the same before and after, and the store holds 0 eggs of week 11. {PATH}",
    15: f"A fresh API with an empty store. The drop of six test eggs for week 9 gave the letters ['A', 'C', 'D', 'E', 'G', 'L']. {PATH}",
    16: f"The board before: Lil Fridge holds E, A, G, L, S in EAGLES. E ties at the top of the need with 11 managers, beside A, C, D, L, N, O, R, S, T; G has 10. The drop of six eggs for week 10 gave ['A', 'C', 'D', 'L', 'N', 'O'], with no E. E ties at the top and is not strictly the only top letter, because every manager still needs each letter of CORNERSTONE and LANSDALE. {PATH}",
    17: f"make egg-undo CLIENT=cpc EGG=2 against the local API printed {{\"egg_id\":2,\"undone\":true}} and exit 0. The board then showed found 0 and Lil Fridge with no letter in CORNERSTONE. The claims row stays with claimed_at and an undone_at time. A new check of T1 matched with a token, so T1 is live.",
    18: f"The full board JSON holds counts, weeks with slot states, words with managers and letters, latest, managers, and last_drop (week, count, dropped_at). A search of the answer for the page names, the targets, the actions, and the keys page, target, action, and conditions found 0 matches. {PATH}",
    19: "Each of the four reasons of the test egg file: 0 tracked repo files (the evidence folder of AT-19 left out) and 0 built site files. Each target is a stable id that the site gives every element of its kind: luck-3 is on 1 element, number-median and number-closest each on 3 elements (week pages), sim-trophy on 0 static elements (the sim renders it), among 980 distinct stable ids. In the repo source, the targets show only in the code that makes the stable id of every element of a kind and in tests. The search of the built site for the conditions and the action of the eggs found 0 files.",
    20: "make egg-draft CLIENT=cpc WEEK=8 with a temp egg file (T1 to T4 confirmed, weeks 9 and 10) took 95 s with a real Claude call and exit 0. It wrote 6 spots of week 8, each with a reason (133 to 178 characters) and confirmed = false. No spot has the page and the target of T1 to T4. Four spots hold an open list, which the file writes as a TOML array after D1. The page, the target, and the reason of each spot are cut. A first run before D1 failed with the error of a list value and wrote nothing.",
    21: "The drop step of the publish (drop_after_publish, run alone by tools/drop_step.py, so no commit and no push ran) with six spots of week 8, four confirmed, printed \"Dropped 4 eggs of week 8.\" and four egg lines, exit 0. The board went from left 0, to_drop 54 to left 4, to_drop 50.",
    22: "With the API stopped (health curl exit 7), the drop step printed \"WARNING: the egg drop of week 8 failed: [Errno 61] Connection refused. Run make egg-drop CLIENT=cpc WEEK=8 to retry.\" and exit 0. After a start of the API with a fresh store, make egg-drop CLIENT=cpc WEEK=8 printed \"Dropped 4 eggs of week 8.\", exit 0, and the board went to left 4.",
    23: "With six spots of week 8 and none confirmed, the drop step printed \"No eggs dropped: week 8 has no confirmed egg in <file>.\" and exit 0.",
    24: "The drop step for NorCal printed \"The client norcal has no eggs package, so no eggs dropped.\" and exit 0, and the NorCal eggs board route answers 404. On the NorCal home page, each width and theme shows 0 links to /eggs/ and sent 0 egg checks after two triple taps. The HTML holds no text \"egg\" and no name of the eggs parts. /eggs/ answers 404 with the 404 page and its not-found mark. The NorCal export has no eggs folder. Shots of home and /eggs/ at 375, 768, and 1280 px in each theme.",
    25: "One tap on the card of game 3 of week 8 set aria-expanded true and opened the recap (\"Won by 1.43\" and its text) in each shot. The page sent 0 egg checks at each width and theme.",
    26: "Three mouse taps on luck-3 at 0, 172, and 329 ms sent one check: page /midseason/2026/, target luck-3, action tap3, theme light, plus the open state chip-rb of the page. The store held a claim of T1 by then, so the card was the claimed-first card. A first run with Playwright clicks had a gap of 1231 ms and sent one tap2; its log stays in site-A1.txt.",
    27: "A press of 3524 ms on luck-3 sent one check with the action hold3, target luck-3, theme light.",
    28: "Tap A number-top-score, tap B number-median, then two taps on C number-closest, 1471 ms from the first tap to the last, sent one check: target number-closest, action tap2, trail [number-top-score, number-median].",
    29: "A DOM range selected the first whole word \"First\" of blurb-1jo5mqe. It sent one check: target blurb-1jo5mqe, action select, word \"first\". The selection came from a script, not from a drag of a finger.",
    30: "The replay ran with frames about 1520 ms apart. Taps on sim-row-3 at 0, 215, and 429 ms; the frame changed at 125 ms, between tap 1 and tap 2, and the row moved from place 02 to place 04. The listener sent one check with target sim-row-3 and action tap3. A first run in phase A1 saw no frame change during its taps; its log stays in site-A1.txt.",
    31: "Desktop WebKit 27.2 and Chromium do not compute -webkit-touch-callout (the value is empty), so the evidence reads the built CSS. The root has data-eggs. The rule \"[data-eggs] [data-stable-id]\" sets none, and it matches the Luck cell (callout none). The first link of the page (#sim) matches no callout rule, so the default holds (callout on). The first image matches \"[data-eggs] [data-stable-id] img\", which sets default (callout on). No iOS device measured the value.",
    32: "In each shot of the egg, the page is blurred behind the find card, with the egg and the line \"You found an egg\". After the tap on the egg, each tile shot shows the red C tile with \"The letter C is yours to claim.\" The log reads the tile C at each width and theme. A dark shot finds T1 in the light theme, then switches the theme. A still shot cannot show the crack or the spring as motion.",
    33: "The sheet shows 11 team pills at each width and theme: The Blue Tent, All You Need Is Love, Lil Fridge, NFC Least, London Cooking, To Infinity and Bijan, Return of T Mac, Maye d'force B with U, behold the lamb, Unsolicited Dak Picks, Teehee. Bo Girds is not a pill.",
    34: "With Teehee holding the C of CORNERSTONE, the pick of Teehee shows CORNERSTONE faded with its C and \"No open C in this word.\", and each word button is disabled with 0 ghost tiles. LANSDALE and EAGLES have no C, so they are disabled too. The pick of Lil Fridge, in the same sheet, shows CORNERSTONE enabled with 1 ghost tile, and LANSDALE and EAGLES disabled with 0.",
    35: "With Teehee picked, a dashed notice shows: \"C fits none of your egg words. Claim it as a block. Then no other manager can put it in a word.\" The button reads \"Claim C as a block\". This shows at each width and theme.",
    36: "With no passphrase in the browser, the sheet shows the field \"League passphrase\" and the button \"Enter the passphrase\". With cpc.passphrase set, the field is gone and the button reads \"Claim C for CORNERSTONE\". This holds at each width and theme.",
    37: "The claim of C for Lil Fridge into CORNERSTONE shows the hero card \"CLAIMED · LIL FRIDGE · 1/11\", the C tile in its slot, \"C goes to CORNERSTONE.\", and \"10 letters to go for the $50.\" The claim of E that fills EAGLES (store E) shows \"6/6\", the tiles E A G L E S, \"EAGLES is complete.\", and \"The $20 gift card is yours.\" The API undid each claim after its shot.",
    38: "With T1 claimed by Teehee, the find shows the card \"TOO LATE · C · Another manager claimed first. · The first claim wins the egg.\" at each width and theme.",
    39: "60 checks from 127.0.0.1, then one more answered 429 with Retry-After 3600. The three taps show the card \"LIMIT · 60 · MINUTES LEFT · The eggs need a rest. · Try again in 60 minutes.\" at each width and theme.",
    40: "Six eggs of week 9, none claimed. On the home page, week 8, and /midseason/2026/, the egg button of the top band shows the badge 6, with the label \"Egg board, 6 eggs left to find\", at each width and theme. A tap in the light theme opens /eggs/ from each page. The badge waits for the first board read after a start of the API, which reads the live rosters.",
    41: "The drop time of week 9 was set to the real Tuesday 2026-11-10 09:00 ET with sqlite3 in the temp store, and the browser clock was fixed. On Tuesday noon the banner reads \"6 eggs dropped today · 6 left\". On Wednesday noon after one claim it reads \"6 eggs dropped Tue · 5 left\". It links to /eggs/, and after the hide and a reload, 0 banners show. At 375 px the line is cut with an ellipsis after \"6 l...\", so the count left is not visible in the 375 shots; the DOM holds the full line.",
    42: "Six eggs, two claimed. The hero reads 4 left to find, 2 found, and 48 to drop. The grid shows 2 white (found), 4 red (out now), and 48 dashed slots. The data-slot count of the page is found 3, out 5, and future 49, because the legend holds one more of each.",
    43: "Seven managers hold letters. Each card shows its gift card, $50, $30, and $20. The CORNERSTONE card lists 5 rows before \"Show all 11\" and 11 rows after the tap, at each width and theme. Store B holds 12 eggs and 8 claims, so its counts differ from AT-42.",
    44: "After AT-12, the EAGLES card is a hero card with the tiles E A G L E S, \"Lil Fridge won it.\", a WON stamp, and \"The $20 gift card is theirs. The race is over.\"",
    45: "Store B holds two claims (Teehee C into CORNERSTONE, Lil Fridge A into LANSDALE) and one block (Teehee, T1). The feed shows two rows: \"Lil Fridge claimed an A for LANSDALE.\" and \"Teehee claimed a C for CORNERSTONE.\", with no page, no spot, and no block.",
    46: "The last card \"How the hunt works\" lists 8 points: 6 eggs drop each Tuesday from week 9 through week 17; tap or press a spot; the first claim gets the letter; each letter goes in an egg word or blocks; the letter rule and its guard; the gift cards CORNERSTONE $50, LANSDALE $30, EAGLES $20; and \"The commissioner places every egg, so the commissioner cannot hunt.\"",
    47: "In an empty store, /eggs/ shows 0 left to find, 0 found, and 54 to drop, and the three egg words with \"No letters yet. The race is open.\" and empty tiles, at each width and theme. board.json is the board answer.",
    48: "The grep of the eggs site copy (packages/eggs/site and apps/site/src/app/_routes/eggs, tests left out) found 0 \"rival\", 0 \"Brian\", and 0 page names or target ids in the copy. The built /eggs/ page holds 0 \"rival\" and 0 \"Brian\".",
    49: "With reduced motion, 100 ms after the tap on the egg, each shot shows the C tile at rest. The page has 0 running animations, and the tile and its parent have no animation and a transition of 0 s.",
    50: "CLIENT=cpc pnpm check:floor -g /eggs/ passed. It covered only the fast sweep of /eggs/ at 390 px dark, because its server uses a free port that the API does not allow, so the board did not load. The floor scans of apps/site/e2e/floor.ts, run on our server on 4174 at 390 and 1280 px in each theme, gave 0 text, target, and scroll failures on the loaded board, the claim sheet, and the banner. The contrast scan gave 0 for the banner, 3 axe \"incomplete\" items for the board (count values too short to judge), and 1 \"incomplete\" item for the sheet (a background axe could not find, or a tile too short to judge). The check counts an incomplete item as a failure.",
    51: "The flow at 375 and 1280 px in each theme: the egg, the C tile, the sheet with Lil Fridge and CORNERSTONE, the hero card \"C goes to CORNERSTONE.\", then /eggs/. The board shows the CORNERSTONE row \"Lil Fridge LEADS 1/11 C\" and the feed \"Lil Fridge claimed a C for CORNERSTONE.\" eggs-spec.txt: apps/site/e2e/eggs.spec.ts (with D2) passed 2 of 2 on a fresh store, at 375 and 1280 px.",
}

def files(number):
    folder = EV / f"AT-{number}"
    names = sorted(p.name for p in folder.iterdir() if p.is_file()) if folder.is_dir() else []
    return ", ".join(f"`evidence/AT-{number}/{name}`" for name in names) or "none"

site = sum(1 for n, (_, app, _) in tests.items() if (EV / f"AT-{n}" / "steps.txt").exists())
out = ["# Easter eggs: evidence", "",
       "Spec: `.scratch/easter-eggs/PRD.md`. Acceptance tests: `.scratch/easter-eggs/ACCEPTANCE.md`.",
       "Built from: `f255557d`, on 2026-11-07. The agent gives no Test verdict. The Judge gives one for each test in `VERDICTS.md`.",
       f"Round time: the runner did not run, because a server that is not ours holds its fixed port 4173. The Playwright phases of `evidence/tools/site.spec.ts` took 15 min for {site} site tests.",
       "",
       "The API ran on this machine like `make -C apps/api api-evidence`: passphrase `localtest`, commissioner key `localkey`, and a temp `CORNERSTONE_EGGS_DIR` outside the repo for each store. The scripts are in `evidence/tools/`. The real path of each eggs route is `/clients/cpc/eggs/<route>`. The tests write `/cpc/eggs/`.",
       "AT-1 to AT-19 ran at `27424c16`. The fixes D1 and D2 changed only `eggfile.py` and `apps/site/e2e/eggs.spec.ts`, so that evidence stands at `f255557d`.",
       ""]
for number in sorted(tests):
    title, app, then = tests[number]
    out += [f"## AT-{number}: {title}", "", f"App: {app}", f"Then: {then}", f"Files: {files(number)}", f"Observation: {OBS[number]}", ""]
(FEATURE / "EVIDENCE.md").write_text("\n".join(out), encoding="utf-8")
print(f"{len(tests)} tests, {site} with steps.txt")
