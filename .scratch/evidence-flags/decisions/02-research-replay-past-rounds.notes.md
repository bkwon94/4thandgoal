# Notes: which past labels are real evidence gaps, and how well does Jev flag them?

Research for decision ticket 02. The labels come from git history of the six Judge specs. The replay ran on 2026-11-10 against the live API, model `jev-1.14.0` through the alias `jev-latest`. No product code changed, and nothing was committed.

## Answer

The 12 FAIL and BLOCKED results of five rounds split into 7 evidence gaps and 5 defects. The defects are 4 product defects and 1 test with bad wording. The gaps have three kinds: a fact of the Then line that no file shows (2), motion with only still shots (2), and an Observation that claims more than the files show or misstates a file (3). The three draft questions catch the first two kinds and miss the third kind, because no draft question compares the Observation with the files. Question (b) needed one revision: the first draft caught 0 of 2. The second draft lets code find a video or timed frames, and asks Jev only whether a text log holds animation values. It catches 2 of 2 at a cut of 0.7 with 0 of 44 false flags, but it was tuned on the same cases, so the result is optimistic. Question (a) catches 1 of 2 gaps at 0.7 with 2 of 44 false flags, and it also flags 3 of 5 defects. Question (c) catches the cut banner text of AT-41 at 0.98, but it flags 4 of 22 PASS tests with shots at 0.7. A look at those shots shows that most are real: a design ellipsis, a fixed bar over text in a full-page shot, or a stamp over a word. So (c) sees cut text well, but it must ask about the text that the Then line names, not about any text on the page. One image costs about one input token per 380 pixels. All calls together cost about $0.05.

## 1. The labels

The rounds come from `git log --all -- '.scratch/*/VERDICTS.md'`. The fast-cycle files under `evidence/` are skipped. Each label comes from the Judge reason at that round and from the commits between that round and the next one.

| Test | Round | Judge reason (quoted) | Label | Why |
| --- | --- | --- | --- | --- |
| easter-eggs AT-3 | `8d646bd0` | FAIL "The Then line needs a match inside the window, but output.txt shows only a pytest line "1 passed" with no check and no time inside 23:00-00:00 ET; the match it shows is of a different egg with the window 00:00-02:00." | gap: fact not shown | The next round added a real clock check, with no code change, and got PASS. |
| easter-eggs AT-34 | `8d646bd0` | FAIL "The Then line says CORNERSTONE is faded, but the teehee shots show the CORNERSTONE card with the same look as the enabled CORNERSTONE card in the lil-fridge shots, and site-B.txt records only disabled and the ghost count." | defect: card not faded | Commit `7f1e39a2` "E1: Fade a disabled egg word card with the muted tokens". The evidence also had only stills for "pulses", which the Judge raised two rounds later. |
| easter-eggs AT-41 | `8d646bd0` | FAIL "The Then line says the Tuesday banner reads "6 eggs dropped today · 6 left", but tuesday-375-light.png and tuesday-375-dark.png show the line cut to "6 eggs dropped today · 6 l..."." | defect: banner text cut | Commit `76503c6f` "E2: Wrap the line of the egg banner and let the strip grow". |
| easter-eggs AT-50 | `8d646bd0` | FAIL "The Then line says each one passes, but site-A1.txt shows 3 contrast failures for the board and 1 for the claim sheet at each width and theme, and check:floor covered only a fast sweep of /eggs/ at 390 px dark." | defect: contrast failures | Commit `4f87122b` "E3: Let axe read the contrast of the board hero and the claim sheet". |
| easter-eggs AT-50 | `35ca282e` | BLOCKED "The Observation says the scans had "no axe incomplete item", but floor-eggs.txt and site-A1.txt show only counts of failures and no count of axe incomplete items." | gap: Observation claim not in files | The next round re-recorded the evidence only, and got PASS. |
| easter-eggs AT-32 | `566d11e7` | FAIL "The Then line says the ring shows, the egg cracks, and the C tile springs up, but the files show only a still egg card and a still tile, with no ring, no crack, and no spring." | gap: motion with still shots | The next round added `.webm` videos, timed frames, and `site-M32.txt` with animation values. |
| easter-eggs AT-34 | `566d11e7` | FAIL "The Then line says a ghost tile pulses, but the shots show a still ghost tile and site-B.txt logs no animation of it." | gap: motion with still shots | Same fix as AT-32. |
| easter-eggs AT-54 | `9582a573` | FAIL "The Observation says the real grade took 17 s, but site-N.txt shows "The grade took 8 s", so the Observation states something that the files do not show." | gap: Observation misstates a file | The next round re-recorded the evidence only, and got PASS. |
| easter-eggs AT-55 | `9582a573` | FAIL "The Observation gives the pointerups of the three taps on luck-3 as 12, 170, and 331 ms, but site-N.txt shows 10, 168, and 327 ms, so the Observation states something that the files do not show." | gap: Observation misstates a file | Same as AT-54. |
| manager-brain AT-19 | `878ccd3a` | FAIL "The Then line needs each player name in a Bullet or a Case to be in a cited fact, but check_reads output shows 29 player names that are not in their cited facts." | defect: test wording | Commit `cec76b5d` "Revise AT-19 of manager-brain: a player of the trade may be named". |
| manager-brain AT-36 | `878ccd3a` | FAIL "The Then line says no code holds a verdict, but search-site.txt shows the code of analyze-result.tsx still names the Lean element with the id `verdict-word`." | defect: code still names verdict | Commit `8f01d1c7` "J-LEAN: the Lean element has the stable id lean-word". |
| manager-brain AT-47 | `878ccd3a` | FAIL "The Then line needs the card to show a headline and the same tap as the analyzer, but in each card shot the fixed bar covers most of the headline, and no shot shows a tap on a card Bullet that opens its fact." | gap: tap not shown, headline under the fixed bar | The next round re-shot each card at the top of the page and added `card-tap-*` shots, with no change to the card code. |

Counts: 7 evidence gaps and 5 defects. The rounds `e539ae4b`, `d3c0589b`, and `46abaa50` of easter-eggs and `a64a0b91` of manager-brain hold only PASS. The other four specs, jev, egg-polish, card-polish, and hero-slots, hold only PASS.

The session log was right on AT-3, AT-50 BLOCKED, AT-32, AT-34 in round 3, and the three product defects. It left out AT-54 and AT-55, which are evidence gaps, and the three FAIL results of manager-brain.

The target of each question:

- (a), a fact of the Then line not shown: easter-eggs AT-3 and manager-brain AT-47.
- (b), motion with only still shots: easter-eggs AT-32 and AT-34 of round `566d11e7`.
- (c), cut or covered text in a shot: easter-eggs AT-41, a defect that a shot shows, and manager-brain AT-47.
- No question targets the three gaps of the kind "Observation claim not in files".

## 2. The method

1. The script reads `ACCEPTANCE.md`, `EVIDENCE.md`, and each file in the `Files:` line of each test with `git show <round>:<path>`. Each file is at the same commit as the round.
2. The state holds the test (`given`, `when`, `then`, `evidence_asked`), the `agent_observation`, and the evidence: the file names, the text files, the video names, and the screenshots.
3. Each text file is cut at 3000 characters, and all text files of a test at 15000 characters.
4. All questions of one test go in one request, so the state is read once.
5. The failed tests use the round of the FAIL or BLOCKED. The PASS sample uses the last round of each spec, with seed `20261110`, and leaves out each test that failed in any round. The sample has 44 tests: easter-eggs 9, manager-brain 8, jev 6, egg-polish 7, card-polish 7, and hero-slots 7. 29 are site tests and 15 are pipeline or both tests. 22 of them have screenshots.
6. A second set, "fixed rounds", replays each failed test at the next round where it got PASS.
7. Every request and its payload, with each image replaced by its file name and size, is in `results.json` in the scratchpad folder `replay/`.

## 3. The screenshot cut method

The script uses Pillow in the `cpc-league` environment:

1. Scale a shot wider than 1568 px down to a width of 1568 px. Scale a shot narrower than 280 px up to 280 px. No shot in the replay needed either step: the shots are 375, 768, or 1280 px wide.
2. Pad a shot shorter than 280 px with white to 280 px.
3. Cut the shot from the top into tiles of 1568 px in height. Keep the first two tiles only. A last tile under 280 px starts higher, so it overlaps the tile above it.
4. Encode each tile as PNG.
5. Pick at most four shots per test: first the `375-light` shots, then the `1280-light` shots, then the rest by name.
6. Stop the addition of tiles at an estimate of 16000 image tokens per request, so that each question stays under the 32k limit of one question.

Two faults of the method showed in the replay:

- A tile edge can cut a line of text. Question (c) may then flag the cut that the tile made. The top tile of easter-eggs AT-43 at 0.66 is probably such a case. Cut tiles with an overlap, or at a blank row of pixels.
- A full-page shot draws each fixed bar at one place in the middle of the page, over other text. Question (c) flags that, and the flag is correct about the image but not about the product.

The replay used the package name `cpc-league`. The ticket said `league`, but `uv` found no package of that name. The flag `--exact` removes packages that `cpc-league` does not need from the shared `.venv`. Run `uv sync --all-packages` at the root to put them back. This replay ran it once at the end.

## 4. Tokens per image

A calibration run sent the same small request with 0, 1, and 2 blank PNG images of each size. The table gives the extra input tokens.

| Image size | 1 image | 2 images |
| --- | --- | --- |
| 280 × 280 | 251 | 492 |
| 375 × 900 | 975 | 1942 |
| 1280 × 720 | 2439 | 4873 |
| 1568 × 1568 | 6323 | 12633 |

So one image costs about one input token per 350 to 390 pixels, and the cost grows in a straight line with the number of images. A tile of a phone shot at 375 × 1568 costs about 1550 tokens. A tile of a desktop shot at 1280 × 1568 costs about 5300 tokens. The docs give no rule yet. These numbers come from blank images, and the replay requests fit them.

## 5. The questions as sent

All wording, criteria, and cuts are in `flag_questions.py`, below in section 10. Each question is a Noul. Code makes each flag from the Noul answers.

- (a) One Noul per sentence of the Then line: "Do the files in `evidence` show this fact from the Then line of `test`: "<sentence>"?" The flag is 1 minus the lowest answer.
- (b), first draft: two Nouls. "Does the Then line of `test` describe something that moves or animates on the screen over time?" and "Do the files in `evidence` record how the screen changes over time?" The flag is p(motion) × (1 − p(record)).
- (b), second draft: code gives 0 if a video exists or if two or more file names hold a time in ms. Otherwise one Noul asks: "Does a file in `evidence.text_files` log animation values, such as opacity, scale, a transform, or a stroke offset, at more than one moment of one animation?" The flag is p(motion) × (1 − p(log)). The second draft ran with no screenshots in the state.
- (c) One Noul per screenshot tile: "In the screenshot `evidence.screenshots.<key>`, is some text cut off or too big for its space?" The flag is the highest answer.

The first draft of (b) failed for a clear reason. Jev read any log line with a time, such as a request time, as a record of change over time. The record Noul gave 0.63 on the pipeline test AT-3 and 0.67 on AT-32, which had only stills. The second draft moves the file-type part into code and asks Jev one narrow thing. The second draft also had one bug in code at first: the frame-name rule missed `frame-400ms-375-dark.png`. The fixed rule is in the module. The flags below use the fixed rule on the stored answers, with no new call.

## 6. Results per question and cut

A hit is a flag on a test in the target set of that question. A miss is a target with no flag. A false flag is a flag on a test of the PASS sample. The rate for (c) counts only the 22 PASS tests with screenshots.

| Question | Cut | Hits | Misses | Gaps flagged (of 7) | Defects flagged (of 5) | False flags on PASS | False-flag rate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| a | 0.5 | 1 of 2 | 1 | 1 | 3 | 3 of 44 | 7% |
| a | 0.7 | 1 of 2 | 1 | 1 | 3 | 2 of 44 | 5% |
| a | 0.9 | 0 of 2 | 2 | 0 | 0 | 0 of 44 | 0% |
| b v1 | 0.5 | 0 of 2 | 2 | 0 | 0 | 0 of 44 | 0% |
| b v1 | 0.7 | 0 of 2 | 2 | 0 | 0 | 0 of 44 | 0% |
| b v1 | 0.9 | 0 of 2 | 2 | 0 | 0 | 0 of 44 | 0% |
| b v2 | 0.5 | 2 of 2 | 0 | 2 | 1 | 2 of 44 | 5% |
| b v2 | 0.7 | 2 of 2 | 0 | 2 | 1 | 0 of 44 | 0% |
| b v2 | 0.9 | 2 of 2 | 0 | 2 | 1 | 0 of 44 | 0% |
| c | 0.5 | 2 of 2 | 0 | 2 | 2 | 6 of 22 | 27% |
| c | 0.7 | 2 of 2 | 0 | 2 | 2 | 4 of 22 | 18% |
| c | 0.9 | 2 of 2 | 0 | 1 | 1 | 3 of 22 | 14% |

The best cut of each question:

- (a): 0.7. It catches AT-3 at 0.86 and misses AT-47. It has 2 false flags of 44. Its other flags land on 3 defects, and 2 of those 3 for the right reason.
- (b) v2: 0.7. It catches both motion gaps at 0.97 and 0.93, with 0 false flags. The defect it flags, AT-34 of round 1, at 0.94, had the same motion gap. The Judge did not raise that gap until round 3. The result is optimistic, because the second draft was written after a look at these cases.
- (c): 0.9 for the fewest false flags, with 3 of 22. It catches AT-41 at 0.98. Its AT-47 hit is weak, because AT-47 stays at 0.93 after the fix.

The flag probability of each failed test:

| Test | Round | Label | Kind | a | b v1 | b v2 | c |
| --- | --- | --- | --- | --- | --- | --- | --- |
| easter-eggs AT-3 | 8d646bd0 | gap | fact not shown | 0.86 | 0.00 | 0.01 | 0.00 |
| easter-eggs AT-34 | 8d646bd0 | defect | card not faded | 0.35 | 0.38 | 0.94 | 0.79 |
| easter-eggs AT-41 | 8d646bd0 | defect | banner text cut | 0.04 | 0.00 | 0.02 | 0.98 |
| easter-eggs AT-50 | 8d646bd0 | defect | contrast failures | 0.89 | 0.01 | 0.01 | 0.00 |
| easter-eggs AT-50 | 35ca282e | gap | Observation claim not in files | 0.04 | 0.01 | 0.02 | 0.00 |
| easter-eggs AT-32 | 566d11e7 | gap | motion with still shots | 0.43 | 0.33 | 0.97 | 0.30 |
| easter-eggs AT-34 | 566d11e7 | gap | motion with still shots | 0.36 | 0.25 | 0.93 | 0.74 |
| easter-eggs AT-54 | 9582a573 | gap | Observation misstates a file | 0.02 | 0.01 | 0.04 | 0.05 |
| easter-eggs AT-55 | 9582a573 | gap | Observation misstates a file | 0.01 | 0.01 | 0.02 | 0.00 |
| manager-brain AT-19 | 878ccd3a | defect | test wording, revised | 0.85 | 0.01 | 0.01 | 0.00 |
| manager-brain AT-36 | 878ccd3a | defect | code still names verdict | 0.87 | 0.01 | 0.02 | 0.00 |
| manager-brain AT-47 | 878ccd3a | gap | tap not shown; headline under fixed bar | 0.04 | 0.07 | 0.06 | 0.95 |

The same tests at the next round, where each got PASS:

| Test | Round | a | b v1 | b v2 | c |
| --- | --- | --- | --- | --- | --- |
| easter-eggs AT-3 | 35ca282e | 0.02 | 0.01 | 0.01 | 0.00 |
| easter-eggs AT-41 | 35ca282e | 0.02 | 0.00 | 0.02 | 0.30 |
| easter-eggs AT-50 | e539ae4b | 0.02 | 0.01 | 0.01 | 0.00 |
| easter-eggs AT-32 | d3c0589b | 0.05 | 0.00 | 0.00 | 0.05 |
| easter-eggs AT-34 | d3c0589b | 0.49 | 0.01 | 0.01 | 0.70 |
| easter-eggs AT-54 | 46abaa50 | 0.01 | 0.01 | 0.04 | 0.07 |
| easter-eggs AT-55 | 46abaa50 | 0.01 | 0.01 | 0.02 | 0.00 |
| manager-brain AT-19 | a64a0b91 | 0.09 | 0.01 | 0.01 | 0.00 |
| manager-brain AT-36 | a64a0b91 | 0.80 | 0.01 | 0.02 | 0.00 |
| manager-brain AT-47 | a64a0b91 | 0.05 | 0.04 | 0.19 | 0.93 |

Each hit of (a) and (b) v2 drops below 0.1 after the fix. AT-41 under (c) drops from 0.98 to 0.30. So each of these flags follows the gap or the defect, not the test.

## 7. Tokens and cost

| Run | Requests | Input tokens | Cost |
| --- | --- | --- | --- |
| Calibration | 9 | about 30,000 | under $0.002 |
| First main run, lost to a bug in the log code after each answer came back | 66 | about 430,000 (not recorded) | about $0.018 |
| Main run | 66 | 432,670 | $0.0182 |
| (b) v2 run, no images | 66 | 143,648 | $0.0060 |
| Total | 207 | about 1.04 M | about $0.045 |

The price is $0.042 per million input tokens, and output is free. 33 requests of the main run held images, with 131 tiles in all. The largest request had 19,024 input tokens, with 8 tiles. A request with no images had 1,000 to 7,800 tokens. Each request took a few seconds.

## 8. Where Jev was wrong

The misses:

| Test | Question | Flag | What Jev did |
| --- | --- | --- | --- |
| manager-brain AT-47, `878ccd3a` | a | 0.04 | The fact "The tap opens the analyzer read of that trade" got 0.98 shown. The Observation and `steps.json` say it, but no shot shows a tap on a card Bullet. Jev took the text as proof of a screen state. |
| easter-eggs AT-32, `566d11e7` | b v1 | 0.33 | The record Noul gave 0.67 to stills plus a log. Fixed in v2. |
| easter-eggs AT-34, `566d11e7` | b v1 | 0.25 | The record Noul gave 0.74. Fixed in v2. |
| easter-eggs AT-50, `35ca282e` | none | 0.04 | No draft question asks whether each claim of the Observation is in the files. |
| easter-eggs AT-54, AT-55, `9582a573` | none | 0.02, 0.01 | The same. The Then facts are all in the files. Only the numbers of the Observation are wrong. |

The flags on PASS tests at 0.5 or more:

| Test | App | Question | Flag | Look at the evidence |
| --- | --- | --- | --- | --- |
| easter-eggs AT-37 | site | a | 0.76 | The fact "A claim that fills an egg word says the gift card is the manager's" got 0.24 shown. The Observation says it. The `won-*` shots were not in the four shots sent, so the state may lack the proof. |
| easter-eggs AT-37 | site | b v2 | 0.59 | "The hero card shows the count rise" reads as motion. The Judge took the before and after stills. |
| jev AT-3 | pipeline | a | 0.58 | "The build exits 0 and writes page.json" got 0.42 shown, and "one warning per checked attempt" got 0.58. The log is cut at 3000 characters, so the cut may hide the proof. |
| card-polish AT-10 | site | a | 0.77 | The second sentence, "If it is lower, the blur is gone", is a condition that did not apply. Jev read it as a fact to show. Code must split out a conditional sentence. |
| card-polish AT-10 | site | b v2 | 0.66 | The test asks for a frame rate. `output.txt` gives "median 60 fps over 47 frames". That is a measure of motion, not a log of animation values, so v2 flags it. |
| manager-brain AT-49 | site | c | 0.95 | Correct about the image: "from Maye d'force B wit..." ends in an ellipsis, and the "Grade the Trade" bar covers a line. The test asks about the error card, so the Judge did not care. |
| manager-brain AT-43 | site | c | 0.94 | Correct about the image: the full-page shot draws the fixed header in the middle of the page, over the "THE SIDES" text, and the nav covers a row. |
| card-polish AT-8 | site | c | 0.92 | Correct about the image: the trade card truncates "behold the ..." by design. |
| card-polish AT-3 | site | c | 0.80 | The same design ellipsis, "behold the ...". |
| easter-eggs AT-43 | site | c | 0.66 | Probably the tile edge cuts the last claim row. A fault of the cut method. |
| egg-polish AT-15 | site | c | 0.60 | Correct about the image: the CLAIMED stamp covers "CORNERSTONE" on the ticket, by design. |

The flags on the fixed rounds:

- manager-brain AT-36 at `a64a0b91`, question (a), 0.80. The fact "Each old adjuster writes facts as a Measure" got 0.20 shown in both rounds. So the round-1 flag on AT-36 had the wrong reason: the Judge failed AT-36 for `verdict-word`, and Jev flagged the other sentence.
- manager-brain AT-47 at `a64a0b91`, question (c), 0.93. The re-shot card still has the fixed bar over the "Pick a partner" line. The image is correct, but the Then line does not name that text.
- easter-eggs AT-34 at `d3c0589b`, question (c), 0.70, on a ghost tile shot. Not checked by eye.

## 9. What the replay suggests for tickets 03 to 05

1. Add a fourth question: one Noul per number or quoted value in the Observation, "Does a file in `evidence` show <claim>?". Code can pull the numbers and quotes with a regular expression. This targets 3 of the 7 gaps, which no draft question catches.
2. Scope (c) to the text that the Then line names. Pass the quoted strings of the Then line, and ask if each one shows in full. A flag on any text of the page is mostly true, but the Judge does not fail a test for it.
3. Keep the file-type part of (b) in code, as in v2.
4. Have code drop a sentence of the Then line that starts with "If" before (a).
5. Cut tall shots with an overlap, or at a blank row, so a tile edge never cuts a line.
6. Re-check every cut on rounds that come after this replay. The sets are small: (a) and (b) each have 2 targets, so one case moves a rate by 50 points.

## 10. The code

The three files are in the scratchpad folder `replay/`. Run each from the worktree with `uv run --exact --package cpc-league python <file> [calibrate|run|motion_v2]`. `TYPESAFE_API_KEY` comes from the environment.

### `flag_questions.py`

The question module: all wording, criteria, cuts, and flag logic.

```python
"""
Draft Evidence flag questions for Jev: the wording, the criteria, and the probability cuts, all in one place.
The replay script builds the state and calls Jev; this module holds every word that Jev reads as a question.
"""
import re

from typesafe_sdk import Noul, NoulCriteria

# The probability cuts the replay reports. A flag probability at or above a cut is a flag.
CUTS = (0.5, 0.7, 0.9)

# Question (a): one Noul for each sentence of the Then line. Code splits the line, because each sentence is one fact.
FACT_SHOWN = (
    "Do the files in `evidence` show this fact from the Then line of `test`: \"{fact}\"?"
)
FACT_SHOWN_YES = (
    "A file in `evidence.text_files` or a shot in `evidence.screenshots` shows the fact itself: "
    "the command output, the log line, the code, or the screen holds it for the case the test names."
)
FACT_SHOWN_NO = (
    "No file shows the fact. Only `agent_observation` says it, or the files show a different case or item, "
    "or a file shows only a test pass line such as \"1 passed\" with no detail of the fact."
)

# Question (b): two Nouls. Code flags when the Then line asks for motion and the files do not record it.
ASKS_MOTION = "Does the Then line of `test` describe something that moves or animates on the screen over time?"
ASKS_MOTION_YES = (
    "The Then line names a change a person sees as it happens, such as a pulse, a spring, a crack, a slide, or a fade in."
)
ASKS_MOTION_NO = (
    "The Then line names only what one still moment can show, such as text, a color, a faded look, a count, or a layout."
)
RECORDS_MOTION = "Do the files in `evidence` record how the screen changes over time?"
RECORDS_MOTION_YES = (
    "`evidence.video_files` holds a video, or the shots are frames taken at several times, "
    "or a text file logs animation values at several times."
)
RECORDS_MOTION_NO = (
    "Each shot is one still moment, and no text file logs values at more than one time."
)

# Question (c): one Noul for each screenshot. Code takes the highest probability over the shots of a test.
TEXT_NOT_FIT = "In the screenshot `evidence.screenshots.{key}`, is some text cut off or too big for its space?"
TEXT_NOT_FIT_YES = (
    "A word or a line stops at the edge of its box or the screen, ends in \"...\" so the full text does not show, "
    "runs out of its box, or sits under a bar or another element so a person cannot read it."
)
TEXT_NOT_FIT_NO = "Each line of text shows in full inside its box, and nothing covers it."


def then_facts(then_line: str) -> list[str]:
    """Split a Then line into its sentences. Each sentence is one fact for question (a)."""
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z`\"])", then_line.strip())
    return [p.strip() for p in parts if p.strip()]


def questions(then_line: str, screenshot_keys: list[str]) -> dict[str, Noul]:
    """All Nouls of one test, keyed so that `flags` can read them back."""
    qs: dict[str, Noul] = {}
    for i, fact in enumerate(then_facts(then_line)):
        qs[f"a_fact_{i}"] = Noul(instructions=FACT_SHOWN.format(fact=fact),
                                 criteria=NoulCriteria(true=FACT_SHOWN_YES, false=FACT_SHOWN_NO))
    qs["b_asks_motion"] = Noul(instructions=ASKS_MOTION, criteria=NoulCriteria(true=ASKS_MOTION_YES, false=ASKS_MOTION_NO))
    qs["b_records_motion"] = Noul(instructions=RECORDS_MOTION,
                                  criteria=NoulCriteria(true=RECORDS_MOTION_YES, false=RECORDS_MOTION_NO))
    for i, key in enumerate(screenshot_keys):
        qs[f"c_shot_{i}"] = Noul(instructions=TEXT_NOT_FIT.format(key=key),
                                 criteria=NoulCriteria(true=TEXT_NOT_FIT_YES, false=TEXT_NOT_FIT_NO))
    return qs


def flags(nouls: dict[str, float]) -> dict[str, float]:
    """The flag probability of each question, from the Noul answers. The decision logic lives here, in code.

    (a) flags when the least-shown fact is not shown: 1 - min(p).
    (b) flags when the Then line asks for motion and the files do not record it: p_motion * (1 - p_records).
    (c) flags when the worst shot has text that does not fit: max(p). No shot gives 0.
    """
    facts = [p for k, p in nouls.items() if k.startswith("a_fact_")]
    shots = [p for k, p in nouls.items() if k.startswith("c_shot_")]
    return {
        "a": 1 - min(facts) if facts else 0.0,
        "b": nouls["b_asks_motion"] * (1 - nouls["b_records_motion"]),
        "c": max(shots) if shots else 0.0,
    }


# Question (b), second draft. Code finds a video or a burst of timed frames from the file names.
# Jev then judges only the text logs, because the first draft read any timed log line as a record of motion.
LOGS_MOTION = (
    "Does a file in `evidence.text_files` log animation values, such as opacity, scale, a transform, "
    "or a stroke offset, at more than one moment of one animation?"
)
LOGS_MOTION_YES = "A log lists the value of one animated property at two or more times, such as \"scale 0.29 at 527 ms, 1 at 1351 ms\"."
LOGS_MOTION_NO = (
    "The logs hold only end states, counts, request times, or one computed style, with no value of an animated property over time."
)
# A timed frame names its time in ms anywhere in the file name, such as frame-400ms-375-dark.png.
FRAME_NAME = re.compile(r"\d+ms[-_.].*\.(png|jpe?g)$")


def motion_v2_questions() -> dict[str, Noul]:
    return {
        "b_asks_motion": Noul(instructions=ASKS_MOTION, criteria=NoulCriteria(true=ASKS_MOTION_YES, false=ASKS_MOTION_NO)),
        "b_logs_motion": Noul(instructions=LOGS_MOTION, criteria=NoulCriteria(true=LOGS_MOTION_YES, false=LOGS_MOTION_NO)),
    }


def motion_v2_flag(nouls: dict[str, float], file_names: list[str], video_files: list[str]) -> float:
    """Flag when the Then line asks for motion, no video or timed frames exist, and no log holds animation values."""
    frames = sum(1 for n in file_names if FRAME_NAME.search(n))
    if video_files or frames >= 2:
        return 0.0
    return nouls["b_asks_motion"] * (1 - nouls["b_logs_motion"])
```

### `replay.py`

The replay script. It calls `typesafe_sdk` directly.

```python
"""
Replay the draft Evidence flag questions on past Judge rounds, read from git, and save each answer to results.json.
Run from the worktree: uv run --exact --package cpc-league python <this file> [calibrate|run].
"""
import io
import json
import random
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PIL import Image as PILImage
from typesafe_sdk import Image, Noul, TypeSafeClient

import flag_questions as fq

HERE = Path(__file__).parent
MODEL = "jev-latest"
HEADERS = {"TypeSafe-Danger-Zone-Images": "true"}
PRICE_PER_MTOK = 0.042
TEXT_EXT = {"txt", "json", "log", "diff", "md", "py", "ts", "sh", "mjs"}
VIDEO_EXT = {"webm", "mp4", "gif"}
TEXT_CAP, TEXT_TOTAL_CAP = 3000, 15000
MAX_SHOTS, MAX_TILES = 4, 2
# The calibration run measured about one input token per 380 pixels. The cap keeps each question under 32k tokens.
PIXELS_PER_TOKEN, IMAGE_TOKEN_BUDGET = 380, 16000

# The failed tests, with the round commit of the VERDICTS.md that holds each FAIL or BLOCKED.
FAILED = [
    ("easter-eggs", "8d646bd0", "AT-3"), ("easter-eggs", "8d646bd0", "AT-34"),
    ("easter-eggs", "8d646bd0", "AT-41"), ("easter-eggs", "8d646bd0", "AT-50"),
    ("easter-eggs", "35ca282e", "AT-50"),
    ("easter-eggs", "566d11e7", "AT-32"), ("easter-eggs", "566d11e7", "AT-34"),
    ("easter-eggs", "9582a573", "AT-54"), ("easter-eggs", "9582a573", "AT-55"),
    ("manager-brain", "878ccd3a", "AT-19"), ("manager-brain", "878ccd3a", "AT-36"),
    ("manager-brain", "878ccd3a", "AT-47"),
]
# The next round of each failed test, where the same test got PASS.
FIXED = [
    ("easter-eggs", "35ca282e", "AT-3"), ("easter-eggs", "35ca282e", "AT-41"),
    ("easter-eggs", "e539ae4b", "AT-50"), ("easter-eggs", "d3c0589b", "AT-32"),
    ("easter-eggs", "d3c0589b", "AT-34"), ("easter-eggs", "46abaa50", "AT-54"),
    ("easter-eggs", "46abaa50", "AT-55"), ("manager-brain", "a64a0b91", "AT-19"),
    ("manager-brain", "a64a0b91", "AT-36"), ("manager-brain", "a64a0b91", "AT-47"),
]
# The final round of each Judge spec, and the PASS sample size per app.
FINAL = {
    "easter-eggs": ("46abaa50", {"pipeline": 5, "site": 4}),
    "manager-brain": ("a64a0b91", {"pipeline": 4, "site": 4}),
    "jev": ("47b1dc6d", {"pipeline": 6}),
    "egg-polish": ("d09f540a", {"site": 7}),
    "card-polish": ("2813de83", {"site": 7}),
    "hero-slots": ("f9304b5e", {"site": 7}),
}


def git(*args: str) -> bytes:
    return subprocess.run(["git", *args], check=True, capture_output=True).stdout


def show(sha: str, path: str) -> bytes | None:
    try:
        return git("show", f"{sha}:{path}")
    except subprocess.CalledProcessError:
        return None


def acceptance_block(sha: str, spec: str, at: str) -> dict:
    text = show(sha, f".scratch/{spec}/ACCEPTANCE.md").decode()
    lines = text.splitlines()
    start = next(i for i, l in enumerate(lines) if l.startswith(f"{at}:"))
    block = {"id": at, "title": lines[start].split(":", 1)[1].strip()}
    for l in lines[start + 1:]:
        if not l.strip() or re.match(r"^AT-\d+:", l):
            break
        if ":" in l:
            k, v = l.split(":", 1)
            block[k.strip().lower()] = v.strip()
    return block


def evidence_block(sha: str, spec: str, at: str) -> dict:
    text = show(sha, f".scratch/{spec}/EVIDENCE.md").decode()
    m = re.search(rf"^## {at}:.*?(?=^## |\Z)", text, re.S | re.M)
    out = {}
    for l in (m.group(0) if m else "").splitlines():
        for key in ("Then", "Files", "Observation"):
            if l.startswith(f"{key}:"):
                out[key.lower()] = l.split(":", 1)[1].strip()
    return out


def tiles(png: bytes) -> list[tuple[bytes, tuple[int, int], tuple[int, int]]]:
    """Scale a shot to a width of 280 to 1568 px, then cut it top down into tiles of 1568 px or less in height."""
    im = PILImage.open(io.BytesIO(png)).convert("RGB")
    orig = im.size
    w, h = im.size
    if w > 1568:
        im = im.resize((1568, round(h * 1568 / w)), PILImage.LANCZOS)
    elif w < 280:
        im = im.resize((280, round(h * 280 / w)), PILImage.LANCZOS)
    w, h = im.size
    if h < 280:
        canvas = PILImage.new("RGB", (w, 280), "white")
        canvas.paste(im, (0, 0))
        im, h = canvas, 280
    out = []
    top = 0
    while top < h and len(out) < MAX_TILES:
        # A last tile under 280 px starts higher, so it overlaps the tile above it.
        t = top if h - top >= 280 else h - 280
        crop = im.crop((0, t, w, min(t + 1568, h)))
        buf = io.BytesIO()
        crop.save(buf, format="PNG")
        out.append((buf.getvalue(), orig, crop.size))
        top += 1568
    return out


def pick_shots(names: list[str]) -> list[str]:
    """Up to MAX_SHOTS shots: phone light shots first, then wide light shots, then the rest by name."""
    def rank(n: str) -> tuple:
        return (0 if "375-light" in n else 1 if "1280-light" in n else 2, n)
    return sorted(names, key=rank)[:MAX_SHOTS]


def build_case(spec: str, sha: str, at: str) -> dict:
    acc = acceptance_block(sha, spec, at)
    ev = evidence_block(sha, spec, at)
    files = re.findall(r"`([^`]+)`", ev.get("files", ""))
    if not files:
        listing = git("ls-tree", "-r", "--name-only", sha, f".scratch/{spec}/evidence/{at}/").decode().split()
        files = [p.split(f".scratch/{spec}/", 1)[1] for p in listing]
    text_files, videos, pngs, total = {}, [], [], 0
    for f in files:
        ext = f.rsplit(".", 1)[-1].lower()
        name = f.split("/")[-1]
        if ext in VIDEO_EXT:
            videos.append(name)
        elif ext == "png":
            pngs.append(f)
        elif ext in TEXT_EXT and total < TEXT_TOTAL_CAP:
            raw = show(sha, f".scratch/{spec}/{f}")
            if raw is None:
                continue
            body = raw.decode("utf-8", "replace")
            cut = body[:TEXT_CAP] + (f"\n[cut: {len(body) - TEXT_CAP} more characters]" if len(body) > TEXT_CAP else "")
            text_files[name] = cut
            total += len(cut)
    shots, shot_meta = {}, []
    for f in pick_shots(pngs):
        raw = show(sha, f".scratch/{spec}/{f}")
        if raw is None:
            continue
        stem = re.sub(r"[^A-Za-z0-9]+", "_", f.split("/")[-1].rsplit(".", 1)[0])
        parts = tiles(raw)
        for i, (data, orig, size) in enumerate(parts):
            if sum(m["sent"][0] * m["sent"][1] for m in shot_meta) + size[0] * size[1] > IMAGE_TOKEN_BUDGET * PIXELS_PER_TOKEN:
                break
            key = stem if len(parts) == 1 else f"{stem}_part{i + 1}"
            shots[key] = Image(data)
            shot_meta.append({"key": key, "file": f, "orig": orig, "sent": size})
    state = {
        "test": {"id": at, "title": acc.get("title"), "app": acc.get("app"), "given": acc.get("given"),
                 "when": acc.get("when"), "then": acc.get("then"), "evidence_asked": acc.get("evidence")},
        "agent_observation": ev.get("observation", ""),
        "evidence": {"file_names": [f.split("/")[-1] for f in files], "text_files": text_files,
                     "video_files": videos, "screenshots": shots},
    }
    return {"spec": spec, "sha": sha, "at": at, "app": acc.get("app"), "then": acc.get("then", ""),
            "state": state, "shot_meta": shot_meta, "png_count": len(pngs)}


def passed_ids(sha: str, spec: str) -> list[str]:
    text = show(sha, f".scratch/{spec}/VERDICTS.md").decode()
    return re.findall(r"^(AT-\d+): PASS", text, re.M)


def pass_sample() -> list[tuple[str, str, str]]:
    rng = random.Random(20261110)
    failed_ids = {(s, a) for s, _, a in FAILED}
    out = []
    for spec, (sha, quota) in FINAL.items():
        ids = [a for a in passed_ids(sha, spec) if (spec, a) not in failed_ids]
        by_app: dict[str, list[str]] = {}
        for a in ids:
            app = acceptance_block(sha, spec, a).get("app", "")
            by_app.setdefault("site" if app == "site" else "pipeline", []).append(a)
        for app, n in quota.items():
            out += [(spec, sha, a) for a in rng.sample(by_app[app], min(n, len(by_app[app])))]
    return out


def payload_for_log(case: dict, qs: dict[str, Noul]) -> dict:
    """The request as sent, with each image swapped for its file name and size, so a case can rerun."""
    st = json.loads(json.dumps({**case["state"], "evidence": {**case["state"]["evidence"], "screenshots": {}}}))
    st["evidence"]["screenshots"] = {m["key"]: f"<image {m['file']} sent {m['sent']}>" for m in case["shot_meta"]}
    def crit(q: Noul, side: str) -> str:
        c = q.criteria
        return c[side] if isinstance(c, dict) else getattr(c, side)
    return {"state": st, "questions": {k: {"instructions": q.instructions, "true": crit(q, "true"),
                                           "false": crit(q, "false")} for k, q in qs.items()}}


def ask(client: TypeSafeClient, kind: str, spec: str, sha: str, at: str) -> dict:
    case = build_case(spec, sha, at)
    qs = fq.questions(case["then"], [m["key"] for m in case["shot_meta"]])
    t0 = time.time()
    resp = client.system_one(case["state"], qs, model=MODEL, extra_headers=HEADERS)
    nouls = {k: resp.nouls[k].noul for k in qs}
    return {"kind": kind, "spec": spec, "sha": sha, "at": at, "app": case["app"], "model": resp.model,
            "input_tokens": resp.usage.input_tokens, "images": len(case["shot_meta"]), "png_count": case["png_count"],
            "shot_meta": case["shot_meta"], "seconds": round(time.time() - t0, 1), "nouls": nouls,
            "flags": fq.flags(nouls), "payload": payload_for_log(case, qs)}


def calibrate(client: TypeSafeClient) -> None:
    """Find the tokens of one image: the same request with 0, 1, and 2 images of each size."""
    q = {"x": Noul(instructions="Does `note` say hello?")}
    sizes = {"375x900": (375, 900), "1280x720": (1280, 720), "1568x1568": (1568, 1568), "280x280": (280, 280)}
    base = client.system_one({"note": "hello"}, q, model=MODEL).usage.input_tokens
    rows = {"base": base}
    for name, (w, h) in sizes.items():
        buf = io.BytesIO()
        PILImage.new("RGB", (w, h), "white").save(buf, format="PNG")
        for n in (1, 2):
            st = {"note": "hello", "shots": {f"s{i}": Image(buf.getvalue()) for i in range(n)}}
            tok = client.system_one(st, q, model=MODEL, extra_headers=HEADERS).usage.input_tokens
            rows[f"{name} x{n}"] = tok - base
    print(json.dumps(rows, indent=1))
    (HERE / "calibrate.json").write_text(json.dumps(rows, indent=1))


def motion_v2(client: TypeSafeClient) -> None:
    """Rerun only the second draft of question (b), on the same cases, with no screenshots in the state."""
    jobs = [("failed", *c) for c in FAILED] + [("fixed", *c) for c in FIXED] + [("pass", *c) for c in pass_sample()]

    def run(job):
        kind, spec, sha, at = job
        case = build_case(spec, sha, at)
        ev = case["state"]["evidence"]
        state = {**case["state"], "evidence": {k: v for k, v in ev.items() if k != "screenshots"}}
        resp = client.system_one(state, fq.motion_v2_questions(), model=MODEL)
        nouls = {k: resp.nouls[k].noul for k in fq.motion_v2_questions()}
        return {"kind": kind, "spec": spec, "sha": sha, "at": at, "input_tokens": resp.usage.input_tokens,
                "nouls": nouls, "flag_b2": fq.motion_v2_flag(nouls, ev["file_names"], ev["video_files"])}

    with ThreadPoolExecutor(4) as pool:
        results = list(pool.map(run, jobs))
    for r in results:
        print(r["kind"], r["spec"], r["at"], r["input_tokens"], r["nouls"], round(r["flag_b2"], 3))
    tokens = sum(r["input_tokens"] for r in results)
    (HERE / "results_motion_v2.json").write_text(json.dumps({"results": results, "input_tokens": tokens}, indent=1))
    print("tokens", tokens, "cost", tokens * PRICE_PER_MTOK / 1e6)


def main() -> None:
    client = TypeSafeClient(model=MODEL)
    if sys.argv[1:] == ["calibrate"]:
        calibrate(client)
        return
    if sys.argv[1:] == ["motion_v2"]:
        motion_v2(client)
        return
    jobs = [("failed", *c) for c in FAILED] + [("fixed", *c) for c in FIXED] + [("pass", *c) for c in pass_sample()]
    results, errors = [], []

    def run(job):
        try:
            return ask(client, *job)
        except Exception as err:  # A failed call is an error in the record, never a "no".
            return {"error": f"{type(err).__name__}: {err}", "job": job}

    with ThreadPoolExecutor(4) as pool:
        for r in pool.map(run, jobs):
            (errors if "error" in r else results).append(r)
            print(r.get("kind"), r.get("spec"), r.get("at"), r.get("input_tokens"), r.get("flags"), r.get("error", ""))
    tokens = sum(r["input_tokens"] for r in results)
    (HERE / "results.json").write_text(json.dumps({"results": results, "errors": errors, "input_tokens": tokens,
                                                   "cost_usd": tokens * PRICE_PER_MTOK / 1e6}, indent=1, default=str))
    print("requests", len(results), "errors", len(errors), "tokens", tokens, "cost", tokens * PRICE_PER_MTOK / 1e6)


if __name__ == "__main__":
    main()
```

### `analyze.py`

The scoring script. It prints the tables of section 6.

```python
"""
Score the replay: hits, misses, and false flags of each question at each cut, from results.json and results_motion_v2.json.
Prints Markdown tables for the notes file.
"""
import json
from pathlib import Path

import flag_questions as fq

HERE = Path(__file__).parent
R = json.loads((HERE / "results.json").read_text())
B2 = {(r["kind"], r["sha"], r["at"]): r for r in json.loads((HERE / "results_motion_v2.json").read_text())["results"]}

# The label of each failed test: (sha, at) -> (gap or defect, the gap kind, the questions that target it).
LABELS = {
    ("8d646bd0", "AT-3"): ("gap", "fact not shown", {"a"}),
    ("8d646bd0", "AT-34"): ("defect", "card not faded", set()),
    ("8d646bd0", "AT-41"): ("defect", "banner text cut", {"c"}),
    ("8d646bd0", "AT-50"): ("defect", "contrast failures", set()),
    ("35ca282e", "AT-50"): ("gap", "Observation claim not in files", set()),
    ("566d11e7", "AT-32"): ("gap", "motion with still shots", {"b"}),
    ("566d11e7", "AT-34"): ("gap", "motion with still shots", {"b"}),
    ("9582a573", "AT-54"): ("gap", "Observation misstates a file", set()),
    ("9582a573", "AT-55"): ("gap", "Observation misstates a file", set()),
    ("878ccd3a", "AT-19"): ("defect", "test wording, revised", set()),
    ("878ccd3a", "AT-36"): ("defect", "code still names verdict", set()),
    ("878ccd3a", "AT-47"): ("gap", "tap not shown; headline under fixed bar", {"a", "c"}),
}


def flag_values(r: dict) -> dict:
    f = dict(r["flags"])
    b2 = B2[(r["kind"], r["sha"], r["at"])]
    ev = r["payload"]["state"]["evidence"]
    f["b2"] = fq.motion_v2_flag(b2["nouls"], ev["file_names"], ev["video_files"])
    return f


rows = [(r, flag_values(r)) for r in R["results"]]
failed = [(r, f) for r, f in rows if r["kind"] == "failed"]
passed = [(r, f) for r, f in rows if r["kind"] == "pass"]
fixed = [(r, f) for r, f in rows if r["kind"] == "fixed"]

print("## Failed tests: flag probabilities\n")
print("| Test | Round | Label | Kind | a | b (v1) | b (v2) | c |")
print("| --- | --- | --- | --- | --- | --- | --- | --- |")
for r, f in failed:
    lab = LABELS[(r["sha"], r["at"])]
    print(f"| {r['spec']} {r['at']} | {r['sha']} | {lab[0]} | {lab[1]} | {f['a']:.2f} | {f['b']:.2f} | {f['b2']:.2f} | {f['c']:.2f} |")

print("\n## Results per question and cut\n")
print("| Question | Cut | Hits | Misses | Gaps flagged (of 7) | Defects flagged (of 5) | False flags on PASS | False-flag rate |")
print("| --- | --- | --- | --- | --- | --- | --- | --- |")
n_shot_pass = sum(1 for r, _ in passed if r["images"])
for q, qname in (("a", "a"), ("b", "b v1"), ("b2", "b v2"), ("c", "c")):
    target = "b" if q == "b2" else q
    for cut in fq.CUTS:
        tgt = [(r, f) for r, f in failed if target in LABELS[(r["sha"], r["at"])][2]]
        hits = [r["at"] for r, f in tgt if f[q] >= cut]
        gaps = sum(1 for r, f in failed if LABELS[(r["sha"], r["at"])][0] == "gap" and f[q] >= cut)
        defs = sum(1 for r, f in failed if LABELS[(r["sha"], r["at"])][0] == "defect" and f[q] >= cut)
        ff = [f"{r['spec']} {r['at']}" for r, f in passed if f[q] >= cut]
        denom = n_shot_pass if q == "c" else len(passed)
        print(f"| {qname} | {cut} | {len(hits)} of {len(tgt)} | {len(tgt) - len(hits)} | {gaps} | {defs} | {len(ff)} of {denom} | {len(ff) / denom:.0%} |")

print("\n## PASS tests with a flag at 0.5 or more\n")
print("| Test | App | a | b v1 | b v2 | c |")
print("| --- | --- | --- | --- | --- | --- |")
for r, f in passed:
    if max(f.values()) >= 0.5:
        print(f"| {r['spec']} {r['at']} | {r['app']} | {f['a']:.2f} | {f['b']:.2f} | {f['b2']:.2f} | {f['c']:.2f} |")

print("\n## Fixed rounds (same test, next round, PASS)\n")
print("| Test | Round | a | b v1 | b v2 | c |")
print("| --- | --- | --- | --- | --- | --- |")
for r, f in fixed:
    print(f"| {r['spec']} {r['at']} | {r['sha']} | {f['a']:.2f} | {f['b']:.2f} | {f['b2']:.2f} | {f['c']:.2f} |")

tok = R["input_tokens"]
b2tok = sum(r["input_tokens"] for r in B2.values())
img_req = [r for r, _ in rows if r["images"]]
print(f"\nmain run: {len(rows)} requests, {tok} input tokens, ${tok * 0.042 / 1e6:.4f}")
print(f"b v2 run: {len(B2)} requests, {b2tok} input tokens, ${b2tok * 0.042 / 1e6:.4f}")
print(f"PASS sample: {len(passed)} tests, {sum(1 for r, _ in passed if r['app'] == 'site')} site, "
      f"{sum(1 for r, _ in passed if r['app'] != 'site')} pipeline or both, {n_shot_pass} with shots")
print(f"requests with images: {len(img_req)}, images sent: {sum(r['images'] for r in img_req)}, "
      f"max tokens one request: {max(r['input_tokens'] for r, _ in rows)}")
```
