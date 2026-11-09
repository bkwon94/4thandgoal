# 01: notes on Jev answers against past Claude verdicts

Ticket: `decisions/01-research-jev-on-past-labels.md`. Probes ran on 2026-11-09 on `jev-1.14.0`.
These notes give data, not the bar. Brian sets the bar in ticket 02.

## Sources

The scratchpad is `/private/tmp/claude-503/-Users-brian-kwon-repos-cpcfantasyfootball/dca6fb71-05df-45b3-a975-9d25fe459bf6/scratchpad/jev-01/`.
Below, `[S]/x` means the file `x` in that folder.

- [S]/extract.py and [S]/runs.json: every saved run of `blurbs.json`, `verify.json`, and `facts.json` in git history.
- [S]/build_set.py and [S]/set.json: the labeled set.
- [S]/fails_all.txt: every Claude fail in history, with its reason. [S]/fails_context.txt: the final blurb around each fail.
- [S]/questions.py: all question text, in one module. [S]/run.py: one request per blurb, with a cache.
- [S]/cache/: the exact payload and the raw answer of every request.
- [S]/results/confusion.md: the confusion tables of all seven designs, by week and threshold.
- [S]/results/r_table.md: each rebuilt fail across all designs. [S]/results/cost.md: tokens, cost, latency.
- [S]/results/hand_review_p.txt: the low Jev answers on Claude passes, and the natural cases.
- [S]/docs/: the live TypeSafe docs as fetched on 2026-11-09.

## Answers in short

1. **Agreement.** With the best design, Jev passes 4 of 22 rebuilt fails at a threshold of 0.9 and 6 of 22 at 0.8. It passes 722 of 1299 Claude passes at 0.9 and 1027 at 0.8. See the tables below.
2. **Question text.** One Noul per sentence beats atomic Nouls. Atomic Nouls flag too many true sentences, so almost no blurb skips Claude.
3. **State.** All chapter facts plus the vocabulary beats cited facts only. The vocabulary is the largest gain.
4. **Cost and latency.** The best design costs about $0.0002 per blurb and $0.0024 to $0.0028 per week. The median latency is 0.088 s per blurb.
5. **Week 8 implied meaning.** Jev catches "hoarded the rest of the hardware" at 0.7 and above, and the implied cause at all thresholds. Claude itself passed a near copy of the hoard sentence in another run.

## A gap in the data

The ticket assumes that `verify.json` holds each sentence and its Claude verdict. It does not.

- `verify.json` holds per attempt only `chapter`, `code_failures`, `verdicts`, and `passed`. A verdict has `index`, `supported`, and `reason`, with no text. Source: `clients/cpc/data/2026/week-08/verify.json`.
- `blurbs.json` holds only the final attempt. Source: `clients/cpc/data/2026/week-08/blurbs.json`.
- A failed attempt gets a retry, and two fails give the template blurb. So the text of a failed sentence is never saved. Source: `packages/facts/python/src/facts/verifier.py:556` to `:595`.
- The fact sheet of the week is in `facts.json` next to it, under `sheet.facts` and `sheet.chapters`.

The result: every saved sentence with text has a Claude pass. No saved sentence with text has a Claude fail.
Git history holds 43 Claude fails in 24 distinct runs, each with only a reason ([S]/fails_all.txt).
A search of the Claude Code session logs for six fail phrases found no full failed sentence.

So the set has two parts.

- **Set P (real labels).** The final attempt of each chapter in each distinct run, where every verdict is a pass.
- **Set R (rebuilt fails).** I rebuilt 22 of the 43 fails by hand from the Claude reason. Each one replaces the matching sentence of the final blurb of that run, with the facts of that run. I chose one fail per distinct pattern. The text of each is in [S]/build_set.py.

Set R is not a Claude label. It is my reading of what Claude rejected. Some rebuilt sentences differ from the original, so treat the escape counts as an estimate.
With 22 cases, 4 escapes is 18%, and the 95% interval is wide, about 5% to 40%.

## The data set

| week | set P blurbs | set P sentences | set R fails |
|---|---|---|---|
| CPC week 6 | 146 | 664 | 11 |
| CPC week 7 | 53 | 339 | 5 |
| CPC week 8 | 38 | 231 | 3 |
| NorCal week 8 | 10 | 65 | 3 |
| total | 247 | 1299 | 22 |

Source: [S]/build_set.py output. CPC week 6 has 18 distinct runs from the period of the pipeline build, so it has the most blurbs.
Each blurb carries its chapter title, every chapter fact and callback fact, and the cited IDs of each sentence. This matches what Claude sees (`verifier.py:491` to `:514`).

Two confounds affect set P.

- The labels come from older prompts. The vocabulary has changed since week 6. The probe used the vocabulary of today (`packages/facts/python/src/facts/prompts/vocabulary.md`).
- Claude is not consistent. The same pattern gets a pass in one run and a fail in another. See "Claude disagrees with itself" below.

## The designs

All designs send one request per blurb, with every sentence question in it (fan-out). The model is pinned to `jev-1.14.0` ([S]/questions.py).
Each sentence goes into its own question text, so no question has to look up an ID in a list (skill guidance, https://docs.typesafe.ai/model-jaggedness.md "Indirection").
The state always holds the chapter title and the full blurb, so a pronoun such as "he" has its subject.

| design | questions per sentence | state |
|---|---|---|
| `single_all` | one Noul: "Does every claim in the sentence follow from `facts`?" | all chapter facts |
| `single_cited` | the same Noul, with the cited facts inside the question | no facts in state |
| `atomic_all` | four Nouls: unstated cause, unstated rank or comparison, a claim no fact supports, a claim a fact contradicts | all chapter facts |
| `atomic_cited` | the same four, with the cited facts inside each question | no facts in state |
| `single_all_vocab` | the one Noul, with "read each stat term as `vocabulary` defines it" | all chapter facts, plus the vocabulary as named fields |
| `single_cited_vocab` | the one Noul, cited facts | the vocabulary |
| `atomic_all_vocab` | the four atomic Nouls | all chapter facts, plus the vocabulary |

The decision is in code ([S]/analyze.py). A sentence passes at threshold t when `follows` is at least t.
For an atomic design, a sentence passes when every problem Noul is at most 1 − t. A blurb skips Claude only when every sentence passes.
A failed call counts as an error, never as a pass. No call failed.

I added the vocabulary designs after the first run. The lowest Jev answers on Claude passes were the licensed phrases of the vocabulary.
Examples: "without X, that is a loss" for a swing player, and "the drops cost the game" for a drop swing (`prompts/vocabulary.md:18`, `:39`).
Claude reads the vocabulary first (`verifier.py:494`). The first state did not have it, so it failed the human test of the skill.

## Results

### All designs, totals

"Escapes" is the key number: a rebuilt fail that Jev passes. "Jev fails" is a Claude pass that Jev fails. "Skip" is the share of set P blurbs that would skip Claude.

| design | t | escapes (of 22) | Jev fails (of 1299) | skip (of 247) |
|---|---|---|---|---|
| `single_all` | 0.7 | 7 | 262 | 41% |
| `single_all` | 0.8 | 5 | 420 | 24% |
| `single_all` | 0.9 | 4 | 746 | 8% |
| `single_cited` | 0.8 | 4 | 465 | 18% |
| `single_cited` | 0.9 | 2 | 712 | 4% |
| `atomic_all` | 0.7 | 4 | 582 | 10% |
| `atomic_all` | 0.8 | 3 | 756 | 3% |
| `atomic_cited` | 0.8 | 2 | 750 | 3% |
| `single_all_vocab` | 0.5 | 16 | 59 | 80% |
| `single_all_vocab` | 0.7 | 8 | 151 | 58% |
| `single_all_vocab` | 0.8 | 6 | 272 | 43% |
| `single_all_vocab` | 0.9 | 4 | 577 | 17% |
| `single_all_vocab` | 0.95 | 2 | 872 | 3% |
| `single_cited_vocab` | 0.8 | 6 | 354 | 30% |
| `single_cited_vocab` | 0.9 | 3 | 605 | 8% |
| `atomic_all_vocab` | 0.7 | 4 | 475 | 18% |
| `atomic_all_vocab` | 0.9 | 2 | 945 | 2% |

Source: [S]/results/confusion.md, which also has 0.5 and 0.95 for each design.
At an equal number of escapes, `single_all_vocab` gives the most skips, or ties `atomic_all_vocab` at about half the cost.
The vocabulary roughly doubles the skips of `single_all` at 0.8 and 0.9, with the same number of escapes.

### The best design by week: `single_all_vocab`

| week | t | both pass | Claude pass + Jev fail | Claude fail + Jev pass | both fail | blurbs that skip Claude |
|---|---|---|---|---|---|---|
| CPC week 6 | 0.7 | 557 | 107 | 3 | 8 | 71/146 (49%) |
| CPC week 6 | 0.8 | 492 | 172 | 1 | 10 | 51/146 (35%) |
| CPC week 6 | 0.9 | 338 | 326 | 1 | 10 | 18/146 (12%) |
| CPC week 7 | 0.7 | 312 | 27 | 3 | 2 | 37/53 (70%) |
| CPC week 7 | 0.8 | 282 | 57 | 3 | 2 | 29/53 (55%) |
| CPC week 7 | 0.9 | 196 | 143 | 1 | 4 | 15/53 (28%) |
| CPC week 8 | 0.7 | 216 | 15 | 1 | 2 | 28/38 (74%) |
| CPC week 8 | 0.8 | 197 | 34 | 1 | 2 | 19/38 (50%) |
| CPC week 8 | 0.9 | 153 | 78 | 1 | 2 | 8/38 (21%) |
| NorCal week 8 | 0.7 | 63 | 2 | 1 | 2 | 8/10 (80%) |
| NorCal week 8 | 0.8 | 56 | 9 | 1 | 2 | 7/10 (70%) |
| NorCal week 8 | 0.9 | 35 | 30 | 1 | 2 | 2/10 (20%) |

Source: [S]/results/confusion.md, section `single_all_vocab`. The thresholds 0.5 and 0.95 are there too.
Weeks 7 and 8 do much better than week 6. Week 6 has the trade chapters and the oldest prompts.

### Whole blurbs from set R

A rebuilt fail does harm only when its whole blurb skips Claude. For `single_all_vocab`:

- At 0.8, 3 of 22 set R blurbs skip Claude: R04, R09, and R11.
- At 0.9, 2 of 22 skip: R09 and R11.
- At 0.95, none skip.

Source: [S]/results/r_table.md. The R number is the fail number in [S]/fails_all.txt.

## Hand review of each escape

These are the set R fails that `single_all_vocab` passes at 0.8. Team names are replaced.

1. **R13 and R20, "dropped" for a loss.** Example: "the new pickup Devaughn Vele chipped in 13.9 for the losing side, and they have now dropped 3 straight." Jev gives 0.97 and 0.95. The fact is true: the team lost 3 straight. The word breaks a vocabulary rule, because "drop" names a dropped pass (`vocabulary.md:37`). Claude is right by the rules. The harm is a wrong word, not a false fact. A code check can catch it: a form of "drop" in a sentence that cites no drop fact.
2. **R11, the namesake.** "Jeremiyah Love, the namesake of team A, scored 2.3 and is now listed Out." Jev gives 0.91. No fact says the team name refers to the player. Claude is right by the rules. Jev reads the pun as plain. The harm is low. The same pattern with CeeDee Lamb (R18) gets 0.70, so Jev catches that one at 0.8.
3. **R09, "every receiver".** "Tee Higgins topped every receiver with 37.5 for team A, and Ja'Marr Chase added 31.1 right behind him." Jev gives 0.94. The fact says 1st of 46 started WRs, not every receiver. The original also implied that Chase played for team A, but my rebuild makes that weaker. Claude is right on the scope, but the scope point is narrow.
4. **R04, a claim that other facts contradict.** "The new pickups on the losing side gave next to nothing: the Titans defense finished at -0.7 and Jaylin Noel, now listed Questionable, managed 0.7." Jev gives 0.82. Other recent adds on that side scored 20, 17.02, 16.4, and 14.6, in facts the sentence does not cite. Claude is right. Jev misses a contradiction that needs a scan of many facts. Note that Claude passed a near copy, "went nowhere", in another run (P, run `aa3bd188`).
5. **R15, "has not won a game in 3 weeks".** Jev gives 0.86. The power ranking fact says 0-3 head-to-head but 1-2 at the median. Claude is right. Jev misses that a median win counts as a win.

Sources: [S]/results/r_table.md, [S]/build_set.py, [S]/fails_all.txt.

In all five cases Claude looks right. Two of them, R13 and R20, are a code check, not a judgment.
At 0.9 only R09, R11, R13, and R20 escape. At 0.95 only R13 and R20 escape.

## The week 8 implied meaning

| case | text, names replaced | Claude | `single_all_vocab` | `atomic_all_vocab` flag |
|---|---|---|---|---|
| R05 | "...took the Lucky award: 28.9 points..., and team A hoarded the rest of the hardware." | fail | 0.59 | rank 0.77, unsupported 0.78 |
| natural, run `3dc97604` | "Team A hoarded the rest: Tee Higgins topped every starter with 32.5, and Tony Pollard scored 26.2 on the bench." | **pass** | 0.81 | contradicted 0.17, the highest of the four |
| R06 | "Team B has now lost 4 straight, and the Tampa Bay Buccaneers defense posted 13.25 and cut the losers' playoff odds to 76%." | fail | 0.35 | cause 0.55 |
| R10 | "Team C hogged the leaderboard, with Joe Burrow 1st among QBs at 52.48 and Brock Bowers 1st among TEs at 28.2." | fail | 0.56 | unsupported 0.62 |
| R08 | "D'Andre Swift scored 27.9 on a 14.69 projection, the biggest gap above projection on any winning side." | fail | 0.69 | unsupported 0.59 |

Sources: [S]/results/r_table.md, [S]/results/hand_review_p.txt.

Jev catches each week 8 implied-meaning fail at 0.7 and above. It never gives them a high answer.
The natural hoard sentence got a Claude pass with the reason "'Hoarded the rest' reads as hyperbole, and the colon names which awards it means". Jev gives it 0.81, so it would skip Claude at 0.8 but not at 0.9. Both readings are fair, and the label itself is not firm.

## Claude disagrees with itself

Set P is not a gold standard. The same pattern gets different Claude verdicts in different runs.

- "Hoarded the rest" passed in run `3dc97604` and failed in run `8159f80b`.
- "The new pickups on the losing side went nowhere" passed in run `aa3bd188`. "Gave next to nothing" with the same facts failed in run `8159f80b`.
- "So both sides have lineup homework this week" passed. "So both managers must fill receiver holes before next week" failed (fail #25).

Some Jev fails on Claude passes look right under the vocabulary of today.
Example: "Recent add Aaron Rodgers was lucky at 17.02" on a 16.37 projection. Today "lucky" for a recent add needs at least twice the projection (`vocabulary.md:33`). Jev gives 0.08.
Other Jev fails are plain errors. Example: "The jump came after an 11-point win over the 3rd-place team." A fact says exactly that, and Jev gives 0.20. Source: [S]/results/hand_review_p.txt.

## Cost and latency

| design | tokens per blurb | cost per blurb | latency p50 | latency p95 | cost of one week (CPC week 8, 13 blurbs) | sum of latency, one week |
|---|---|---|---|---|---|---|
| `single_all` | 3330 | $0.00014 | 0.071 s | 0.119 s | $0.0019 | 1.04 s |
| `single_cited` | 1751 | $0.00007 | 0.067 s | 0.108 s | $0.0011 | 0.86 s |
| `atomic_all` | 5163 | $0.00022 | 0.083 s | 0.161 s | $0.0030 | 1.16 s |
| `single_all_vocab` | 4881 | $0.00021 | 0.088 s | 0.136 s | $0.0028 | 1.29 s |
| `atomic_all_vocab` | 6920 | $0.00029 | 0.093 s | 0.169 s | $0.0040 | 1.30 s |

Source: [S]/results/cost.md, which has every design and every week. Cost uses $0.042 per million input tokens. Output is free (https://docs.typesafe.ai/models.md).
Latency is the wall time of one request from this machine, with 4 requests in parallel. The sum of latency is the time with no parallel requests.
The total spend for this ticket was $0.348: seven designs over 269 blurbs, plus a pilot of 3 blurbs. No call failed.

## What this means for ticket 02

**Recommended design:** `single_all_vocab`.

- One Noul per sentence, one request per blurb.
- The state holds the chapter title, the blurb, every chapter fact and callback fact, and the vocabulary as named fields. This is what Claude sees.
- A blurb skips Claude only when every sentence passes. A failed call sends the blurb to Claude.
- Add one code check before Jev: a form of "drop" in a sentence that cites no drop fact goes to Claude. This removes R13 and R20, the two escapes at 0.95.

**Threshold, and the trade-off.** The numbers below are for `single_all_vocab`, with and without the drop check. The weeks 7 and 8 skip is the better guide to future weeks.

| t | sentence escapes, of 22 | escapes with the drop check | R blurbs that skip | skip, all set P | skip, weeks 7 and 8 |
|---|---|---|---|---|---|
| 0.8 | 6 | 4 | 3 | 43% | 55 of 101 blurbs (54%) |
| 0.9 | 4 | 2 | 2 | 17% | 25 of 101 blurbs (25%) |
| 0.95 | 2 | 0 | 0 | 3% | 4 of 101 blurbs (4%) |

- At 0.9, the cascade skips Claude on about 3 of 13 blurbs a week. The escapes left after the drop check are a namesake pun and a narrow scope word.
- At 0.8, the cascade skips about 7 of 13 blurbs a week. It also passes a claim that uncited facts contradict (R04) and a wrong reading of the median (R15).
- At 0.95, there is no saving.
- The Jev check costs under $0.003 a week at any threshold. So the saving is only in Claude calls and in time.

**Limits on these numbers.**

- Set R has only 22 cases, and I rebuilt them by hand. The bar of ticket 02 needs real fails.
- So the build must save the text of each failed attempt with its verdicts. Ticket 06 (the Jev log) is the place to decide this. Then a log-only run gives real labels within a few weeks.
- Set P labels come from older prompts, and Claude is not consistent. Some "Claude pass + Jev fail" cases are Claude errors under today's rules.
