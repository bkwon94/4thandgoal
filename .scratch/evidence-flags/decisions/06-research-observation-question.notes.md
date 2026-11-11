# Notes: can a fourth question catch an Observation that claims more than the files show?

Research for decision ticket 06. The replay ran on 2026-11-10 against the live API, model `jev-1.14.0` through the alias `jev-latest`. It used the cases, the commits, the state, and the PASS sample of ticket 02. No product code changed, and nothing was committed.

## Answer

Question (d) catches the two Observations that misstate a number, AT-54 and AT-55 of easter-eggs, but it misses the other two gaps, and it flags many PASS tests. The best draft asks one Noul per sentence of the Observation, "do the files show it", and one more Noul per sentence, "does it report a result that the Then line asks for". Code multiplies the two and takes the worst sentence. At a cut of 0.7 it catches 2 of 4 targets with 4 of 44 false flags (9%). That second draft was written after a look at these cases, so the rate is optimistic. The single Noul that the ticket asks for catches the same 2 of 4 at 0.7, but with 10 of 44 false flags (23%). No draft catches AT-50 for the right reason: Jev reads "no axe incomplete item" as shown, at 0.82, because the files show no incomplete item at all. No draft catches AT-47 of manager-brain: Jev takes `steps.json` and the read shots as proof of the tap, at 0.97. Question (a) with no Observation is worse than question (a) of ticket 02. It also misses AT-47, at 0.05, so the Observation text was not the cause of that miss. It drops AT-3 from 0.86 to 0.64, and it adds new flags where a cut file held the proof that the Observation gave. Most false flags of (d) are true about the state: the claim is in a shot that the state did not send, in the part of a file past the cut, or in the evidence of another test. So (d) needs all the files in the state before its rate can be trusted. All calls cost about $0.053.

## 1. The method

1. The cases are those of ticket 02: 12 failed rounds, 10 fixed rounds, and the same 44 PASS tests with seed `20261110`. `replay_obs.py` imports `build_case`, `FAILED`, `FIXED`, and `pass_sample` from `replay.py`, so the state, the cuts of text and shots, and the commits are the same.
2. Each test gets two requests. The first sends the state of ticket 02, with `agent_observation`, and holds every draft of (d). The second sends the same state with no `agent_observation` key, and holds the new (a).
3. A third run, `replay_rel.py`, sends the first state again with the relevance Nouls of the second draft of (d).
4. The targets of (d) are AT-50 at `35ca282e`, AT-54 and AT-55 at `9582a573`, and AT-47 at `878ccd3a`. The targets of (a) are the two of ticket 02: AT-3 at `8d646bd0` and AT-47 at `878ccd3a`.
5. A false flag is a flag on a test of the PASS sample. The rate is over all 44 tests.
6. Every request is in `results_obs.json` and `results_rel.json` in the scratchpad folder `replay/`, with each image swapped for its file name and size.

## 2. The questions as sent

All wording is in `obs_questions.py`, in section 7. Each question is a Noul. Code makes each flag.

- **d one Noul**, as the ticket asks: "Does `agent_observation` state something that the files in `evidence` do not show, or state a value that differs from the same value in a file?" Yes: "A result, a number, a time, a count, or a quoted text in `agent_observation` is in no file of `evidence`, or a file gives a different value for it, such as the Observation says 40 ms and a log says 35 ms." No: "Each result, number, and quoted text in `agent_observation` matches a text file or a screenshot. Background such as a reason, a commit, or a design note needs no file." The flag is the Noul.
- **d split**: the same judgment as two Nouls, because the one Noul joins two conditions with "or". "Does `agent_observation` state a result that no file in `evidence` shows?" and "Does `agent_observation` give a number or a quoted text that differs from the same value in a file of `evidence`?" The flag is the higher answer.
- **d per sentence**: one Noul per sentence of the Observation. "Do the files in `evidence` show this statement of `agent_observation`: "<sentence>"?" Yes includes "the statement is only background". The flag is 1 minus the lowest answer.
- **d v2, sentence × relevance**: the per-sentence Nouls, and one more Noul per sentence in a third request: "Does this statement of `agent_observation` report a result that the Then line of `test` asks for: "<sentence>"?" No: "The statement is about how the agent ran the test, a first try, a path or a port, a commit, or the evidence of another test." The flag is the highest p(relevant) × (1 − p(shown)) over the sentences.
- **a, no Observation**: the per-sentence Nouls of (a) from ticket 02, over the state with no `agent_observation`. The No criterion drops the clause "Only `agent_observation` says it". The flag is 1 minus the lowest answer.

The example "40 ms and 35 ms" is made up. It names no test value, so it does not tune the question to AT-55.

## 3. Results per question and cut

| Question | Cut | Hits | Hit tests | Gaps flagged (of 7) | Defects flagged (of 5) | False flags on PASS | False-flag rate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| d one Noul | 0.5 | 3 of 4 | AT-50, AT-54, AT-55 | 6 | 5 | 16 of 44 | 36% |
| d one Noul | 0.7 | 2 of 4 | AT-54, AT-55 | 3 | 1 | 10 of 44 | 23% |
| d one Noul | 0.9 | 1 of 4 | AT-54 | 2 | 0 | 3 of 44 | 7% |
| d split | 0.5 | 3 of 4 | AT-50, AT-54, AT-55 | 6 | 2 | 14 of 44 | 32% |
| d split | 0.7 | 2 of 4 | AT-54, AT-55 | 3 | 1 | 6 of 44 | 14% |
| d split | 0.9 | 1 of 4 | AT-54 | 2 | 0 | 1 of 44 | 2% |
| d per sentence | 0.5 | 3 of 4 | AT-50, AT-54, AT-55 | 5 | 2 | 13 of 44 | 30% |
| d per sentence | 0.7 | 3 of 4 | AT-50, AT-54, AT-55 | 4 | 1 | 9 of 44 | 20% |
| d per sentence | 0.9 | 1 of 4 | AT-54 | 1 | 0 | 2 of 44 | 5% |
| d v2 sentence × relevance | 0.5 | 3 of 4 | AT-50, AT-54, AT-55 | 5 | 1 | 9 of 44 | 20% |
| d v2 sentence × relevance | 0.7 | 2 of 4 | AT-54, AT-55 | 2 | 1 | 4 of 44 | 9% |
| d v2 sentence × relevance | 0.9 | 0 of 4 | none | 0 | 0 | 0 of 44 | 0% |
| a, no Observation | 0.5 | 1 of 2 | AT-3 | 1 | 2 | 4 of 44 | 9% |
| a, no Observation | 0.7 | 0 of 2 | none | 0 | 1 | 3 of 44 | 7% |
| a, no Observation | 0.9 | 0 of 2 | none | 0 | 0 | 2 of 44 | 5% |
| a of ticket 02, stored | 0.5 | 1 of 2 | AT-3 | 1 | 3 | 3 of 44 | 7% |
| a of ticket 02, stored | 0.7 | 1 of 2 | AT-3 | 1 | 3 | 2 of 44 | 5% |
| a of ticket 02, stored | 0.9 | 0 of 2 | none | 0 | 0 | 0 of 44 | 0% |

Each hit on AT-50 has the wrong reason. The lowest sentence of AT-50 is the ADR 0025 background, at 0.21 shown, not the claim of no axe incomplete item. So the hits for the right reason are AT-54 and AT-55 only, in each draft of (d).

The best cut of each draft:

- d one Noul: 0.7. It catches AT-54 at 0.98 and AT-55 at 0.77, with 10 of 44 false flags. At 0.9 it keeps only AT-54, with 3 of 44.
- d split: 0.9 for the fewest false flags, 1 of 44, but it keeps only AT-54. At 0.7 it catches 2 of 4 with 6 of 44.
- d per sentence: 0.7, with 3 of 4, but 1 hit is for the wrong reason, and 9 of 44 false flags.
- d v2: 0.7. It catches AT-54 at 0.82 and AT-55 at 0.78, with 4 of 44 false flags. The draft is tuned on these cases.
- a, no Observation: 0.5, with 1 of 2 and 4 of 44. It is worse than (a) of ticket 02 at each cut.

### The flag of each failed test

| Test | Round | Label | d one Noul | d split | d per sentence | d v2 | a, no Observation | a of ticket 02 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| easter-eggs AT-3 | 8d646bd0 | gap | 0.95 | 0.93 | 0.80 | 0.66 | 0.64 | 0.86 |
| easter-eggs AT-34 | 8d646bd0 | defect | 0.57 | 0.43 | 0.12 | 0.12 | 0.21 | 0.35 |
| easter-eggs AT-41 | 8d646bd0 | defect | 0.53 | 0.46 | 0.39 | 0.36 | 0.05 | 0.04 |
| easter-eggs AT-50 | 8d646bd0 | defect | 0.70 | 0.53 | 0.64 | 0.47 | 0.39 | 0.89 |
| easter-eggs AT-50 | 35ca282e | gap, Observation | 0.50 | 0.56 | 0.79 | 0.51 | 0.07 | 0.04 |
| easter-eggs AT-32 | 566d11e7 | gap | 0.54 | 0.62 | 0.37 | 0.31 | 0.34 | 0.43 |
| easter-eggs AT-34 | 566d11e7 | gap | 0.64 | 0.69 | 0.60 | 0.56 | 0.06 | 0.36 |
| easter-eggs AT-54 | 9582a573 | gap, Observation | 0.98 | 0.96 | 0.97 | 0.82 | 0.02 | 0.02 |
| easter-eggs AT-55 | 9582a573 | gap, Observation | 0.77 | 0.76 | 0.80 | 0.78 | 0.01 | 0.01 |
| manager-brain AT-19 | 878ccd3a | defect | 0.62 | 0.74 | 0.74 | 0.72 | 0.67 | 0.85 |
| manager-brain AT-36 | 878ccd3a | defect | 0.54 | 0.35 | 0.31 | 0.30 | 0.88 | 0.87 |
| manager-brain AT-47 | 878ccd3a | gap, Observation and fact | 0.34 | 0.43 | 0.20 | 0.17 | 0.05 | 0.04 |

### The same tests at the next round, where each got PASS

| Test | Round | d one Noul | d split | d per sentence | d v2 | a, no Observation | a of ticket 02 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| easter-eggs AT-3 | 35ca282e | 0.81 | 0.50 | 0.71 | 0.20 | 0.02 | 0.02 |
| easter-eggs AT-41 | 35ca282e | 0.39 | 0.32 | 0.03 | 0.03 | 0.04 | 0.02 |
| easter-eggs AT-50 | e539ae4b | 0.47 | 0.35 | 0.74 | 0.63 | 0.09 | 0.02 |
| easter-eggs AT-32 | d3c0589b | 0.76 | 0.63 | 0.38 | 0.37 | 0.05 | 0.05 |
| easter-eggs AT-34 | d3c0589b | 0.72 | 0.71 | 0.43 | 0.39 | 0.08 | 0.49 |
| easter-eggs AT-54 | 46abaa50 | 0.78 | 0.49 | 0.21 | 0.12 | 0.02 | 0.01 |
| easter-eggs AT-55 | 46abaa50 | 0.67 | 0.67 | 0.60 | 0.59 | 0.01 | 0.01 |
| manager-brain AT-19 | a64a0b91 | 0.63 | 0.69 | 0.74 | 0.72 | 0.88 | 0.09 |
| manager-brain AT-36 | a64a0b91 | 0.60 | 0.44 | 0.32 | 0.31 | 0.89 | 0.80 |
| manager-brain AT-47 | a64a0b91 | 0.43 | 0.44 | 0.69 | 0.66 | 0.34 | 0.05 |

The per-sentence drafts follow the fix of AT-54: 0.97 to 0.21, and 0.82 to 0.12 for v2. The one Noul does not: it stays at 0.78. AT-55 drops only from 0.78 to 0.59 under v2, so its fixed round sits in the band between 0.3 and 0.7. A flag of the one Noul does not follow the gap well.

## 4. Where Jev was wrong

### The misses on the targets

| Test | Question | Flag | The answer | What Jev did |
| --- | --- | --- | --- | --- |
| easter-eggs AT-50, `35ca282e` | d per sentence | 0.79, wrong reason | "The scans gave 0 failures of each kind on all three, with no axe incomplete item." shown at 0.82 | The files show only counts of failures. Jev read the absence of an incomplete item as proof of no incomplete item. The flag came from the ADR 0025 sentence, shown at 0.21. |
| easter-eggs AT-50, `35ca282e` | d one Noul | 0.50 | the one Noul at 0.50 | Unsettled. The Noul gives no sentence, so code cannot tell why. |
| easter-eggs AT-50, `35ca282e` | d v2 | 0.51 | the ADR sentence: relevant 0.65, shown 0.21 | The relevance Noul cut the background sentence to 0.51, and the axe claim stays shown. |
| manager-brain AT-47, `878ccd3a` | each d | 0.17 to 0.43 | "The tap opens the analyzer read of that trade: ..." shown at 0.97 | `steps.json` clicks "See the Full Result", and the read shots show the analyzer read. Jev took that as the tap of the Then line. The Judge wanted a tap on a card Bullet. |
| manager-brain AT-47, `878ccd3a` | a, no Observation | 0.05 | "The tap opens the analyzer read of that trade." shown at 0.95 | The same reading, with no Observation in the state. So the Observation text did not cause the miss of ticket 02. The miss comes from the wording of the Then line, which does not say "a Bullet". |
| easter-eggs AT-3, `8d646bd0` | a, no Observation | 0.64 | "The same check inside the window matches." shown at 0.36 | Lower than the 0.86 of ticket 02. The cause is not clear: the only file is the same in both requests. |

The hits for the right reason:

- AT-54: "A real grade ... took 17 s ..." shown at 0.03. `site-N.txt` says "The grade took 8 s".
- AT-55: "Three mouse taps on luck-3 (pointerups at 12, 170, and 331 ms) ..." shown at 0.20. `site-N.txt` says 10, 168, and 327 ms.

### The false flags on PASS tests at 0.7 or more

| Test | d one Noul | d split | d per sentence | d v2 | a, no Observation | a of ticket 02 |
| --- | --- | --- | --- | --- | --- | --- |
| easter-eggs AT-11 | 0.70 | 0.59 | 0.29 | 0.27 | 0.09 | 0.09 |
| easter-eggs AT-7 | 0.80 | 0.43 | 0.78 | 0.28 | 0.09 | 0.16 |
| easter-eggs AT-20 | 0.91 | 0.83 | 0.86 | 0.55 | 0.02 | 0.01 |
| easter-eggs AT-43 | 0.90 | 0.85 | 0.76 | 0.72 | 0.25 | 0.45 |
| easter-eggs AT-37 | 0.56 | 0.47 | 0.15 | 0.15 | 0.93 | 0.76 |
| manager-brain AT-46 | 0.62 | 0.62 | 0.79 | 0.76 | 0.13 | 0.07 |
| manager-brain AT-49 | 0.14 | 0.15 | 0.90 | 0.86 | 0.01 | 0.01 |
| jev AT-3 | 0.29 | 0.26 | 0.65 | 0.63 | 0.94 | 0.58 |
| egg-polish AT-32 | 0.94 | 0.93 | 0.61 | 0.59 | 0.02 | 0.03 |
| egg-polish AT-35 | 0.80 | 0.64 | 0.90 | 0.87 | 0.13 | 0.04 |
| egg-polish AT-11 | 0.86 | 0.79 | 0.81 | 0.44 | 0.04 | 0.06 |
| card-polish AT-10 | 0.21 | 0.11 | 0.02 | 0.02 | 0.88 | 0.77 |
| card-polish AT-29 | 0.50 | 0.77 | 0.46 | 0.31 | 0.05 | 0.03 |
| card-polish AT-11 | 0.79 | 0.69 | 0.86 | 0.34 | 0.08 | 0.03 |
| card-polish AT-17 | 0.87 | 0.89 | 0.78 | 0.63 | 0.54 | 0.32 |
| hero-slots AT-4 | 0.70 | 0.56 | 0.68 | 0.48 | 0.01 | 0.01 |

The worst sentence of each false flag, with its answers:

| Test | Sentence | Shown | Relevant | Why |
| --- | --- | --- | --- | --- |
| easter-eggs AT-7 | "The real path of each route has the prefix /clients/cpc/eggs/; the test writes /cpc/eggs/." | 0.22 | 0.36 | A note on the path. The relevance Noul drops it. |
| easter-eggs AT-20 | "A first run before D1 failed with the error of a list value and wrote nothing." | 0.14 | 0.36 | A first try. The relevance Noul drops it. The v2 worst is now "took 95 s ... exit 0", shown 0.40, which may sit past the cut of the log. |
| easter-eggs AT-43 | "Each letter row shows even tiles with a gap between two tiles, inside the card." | 0.24 | 0.95 | A claim about a shot. Probably a wrong answer, or the tile edge cut the row, as in ticket 02. Not checked by eye. |
| manager-brain AT-46 | "The shots of AT-38 and AT-47 show a Lean word, Bullets, and no letter badge." | 0.21 | 0.96 | True: no file of AT-46 holds those shots. The relevance Noul did not see "the evidence of another test". |
| manager-brain AT-49 | "No hero, no Lean word, and no scale show." | 0.10 | 0.96 | A claim of absence on a shot. Not checked by eye. If the shots show no hero, Jev reads an absence claim as not shown, the reverse of AT-50. |
| egg-polish AT-35 | "The shots of each section look the same on both builds; ..." | 0.10 | 0.97 | The test has 19 files, and the state sends 4 shots. The proof is in the shots not sent. |
| egg-polish AT-11 | "Recorded again from `34b5c424`." | 0.19 | 0.14 | A commit note. The relevance Noul drops it. |
| card-polish AT-11 | "`evidence/AT-9/computed.txt` reads 28 lit blades of 48." | 0.14 | 0.39 | A file of another test. The relevance Noul drops it. |
| card-polish AT-17 | "The screen reader names in AT-18 read ..." | 0.22 | 0.81 | The evidence of another test. |
| egg-polish AT-32 | the one Noul at 0.94 | — | — | The one Noul gives no sentence. The worst sentence, "The e2e run prints 0 matches ...", is shown at 0.39. |

The new flags of (a) with no Observation:

| Test | Fact | Shown | Why |
| --- | --- | --- | --- |
| easter-eggs AT-37 | "A claim that fills an egg word says the gift card is the manager's." | 0.07 | The same miss as ticket 02, at 0.24 there. The `won-*` shots were not sent. |
| jev AT-3 | "the build exits 0 and writes `clients/cpc/build/2026/week-08/page.json`." | 0.06 | The log is cut at 3000 characters. The Observation of ticket 02 filled the gap, at 0.42. |
| manager-brain AT-19, fixed round | "Each player name is in a cited fact or is a player of the trade itself." | 0.12 | `output.txt` is cut. With the Observation, ticket 02 gave 0.09 as the flag. |
| card-polish AT-10 | "If it is lower, the blur is gone ..." | 0.12 | The conditional sentence of ticket 02. Code must drop it. |

So most false flags of (d) come from three faults of the state, not from the question:

1. The state sends at most 4 shots, but `file_names` lists all of them. A claim about a shot not sent looks unsupported.
2. A text file is cut at 3000 characters. A claim past the cut looks unsupported.
3. An Observation cites the evidence of another test. The state does not hold it.

The rest are claims of absence. Jev answers them both ways: "no axe incomplete item" at 0.82 shown, and "No hero ... show" at 0.10 shown.

## 5. What the replay suggests

1. Keep (d) per sentence, with the relevance Noul, as the one draft worth a second test. Code can then name the sentence in the flag, which the one Noul cannot.
2. Send every shot and the full text of each file to (d), or tell code to skip a sentence that names a file the state does not hold. Without that, the false-flag rate measures the cut, not the question.
3. Have code drop a sentence that names another test, such as "AT-18" or "evidence/AT-9/".
4. Treat a claim of absence as its own case. Code can find "no" and "0" claims with a regular expression, and ask "Does a file in `evidence` report a count of <item>?" This targets AT-50.
5. Drop (a) with no Observation. It is worse at each cut, and it does not fix AT-47.
6. AT-47 needs the Then line to say what is tapped. That is a fix of the test wording, not of a question.
7. Re-check every cut on rounds after this replay. The (d) set has 4 targets, so one case moves the hit rate by 25 points.

## 6. Tokens and cost

| Run | Requests | Input tokens | Cost |
| --- | --- | --- | --- |
| One test call on AT-54 | 2 | 13,861 | $0.0006 |
| d drafts, with Observation | 66 | 443,519 | $0.0186 |
| a, no Observation | 66 | 393,646 | $0.0165 |
| d v2 relevance | 66 | 417,763 | $0.0175 |
| Total | 200 | 1,268,789 | $0.0533 |

The price is $0.042 per million input tokens, and output is free. There were 0 errors. The budget was $0.50.

## 7. The code

The scripts are in the scratchpad folder `replay/` of this session, next to the scripts of ticket 02. Run each from the worktree with `uv run --package cpc-league python <script>`, in this order: `replay_obs.py`, `replay_rel.py`, `analyze_obs.py`.

### `obs_questions.py`

```python
"""
Draft Evidence flag questions of ticket 06: question (d) on the Observation, and question (a) with no Observation.
Every word that Jev reads as a question lives here; replay_obs.py builds the state and calls Jev.
"""
from typesafe_sdk import Noul, NoulCriteria

from flag_questions import then_facts

# Question (d), as the ticket asks it: one Noul over the whole Observation.
OBS_UNSUPPORTED = (
    "Does `agent_observation` state something that the files in `evidence` do not show, "
    "or state a value that differs from the same value in a file?"
)
OBS_UNSUPPORTED_YES = (
    "A result, a number, a time, a count, or a quoted text in `agent_observation` is in no file of `evidence`, "
    "or a file gives a different value for it, such as the Observation says 40 ms and a log says 35 ms."
)
OBS_UNSUPPORTED_NO = (
    "Each result, number, and quoted text in `agent_observation` matches a text file or a screenshot. "
    "Background such as a reason, a commit, or a design note needs no file."
)

# Question (d), split: one Noul for a claim that no file holds, one Noul for a value that a file contradicts.
OBS_MISSING = "Does `agent_observation` state a result that no file in `evidence` shows?"
OBS_MISSING_YES = (
    "The Observation names a result, a count, or a screen state, and no text file or screenshot of `evidence` holds it."
)
OBS_MISSING_NO = (
    "Each result of the Observation is in a text file or a screenshot. "
    "Background such as a reason, a commit, or a design note needs no file."
)
OBS_DIFFERS = (
    "Does `agent_observation` give a number or a quoted text that differs from the same value in a file of `evidence`?"
)
OBS_DIFFERS_YES = "A file gives the same item a different value, such as the Observation says 40 ms and a log says 35 ms."
OBS_DIFFERS_NO = "Each number and quoted text of the Observation is the same as in the file that holds it, or no file gives that item."

# Question (d), per sentence: one Noul for each sentence of the Observation. Code takes the least-shown sentence.
OBS_SENTENCE = "Do the files in `evidence` show this statement of `agent_observation`: \"{sentence}\"?"
OBS_SENTENCE_YES = (
    "A text file or a screenshot holds the statement with the same values, "
    "or the statement is only background, such as a reason, a commit, or a design note."
)
OBS_SENTENCE_NO = "No file holds the statement, or a file gives a different value for a number or a quoted text in it."

# Question (a), with no Observation in the state. The NO criterion drops the clause about the Observation.
FACT_SHOWN = "Do the files in `evidence` show this fact from the Then line of `test`: \"{fact}\"?"
FACT_SHOWN_YES = (
    "A file in `evidence.text_files` or a shot in `evidence.screenshots` shows the fact itself: "
    "the command output, the log line, the code, or the screen holds it for the case the test names."
)
FACT_SHOWN_NO = (
    "No file shows the fact. The files show a different case or item, "
    "or a file shows only a test pass line such as \"1 passed\" with no detail of the fact."
)


def obs_questions(observation: str) -> dict[str, Noul]:
    """The Nouls of question (d) for one test, all over the state with the Observation."""
    qs = {
        "d_one": Noul(instructions=OBS_UNSUPPORTED, criteria=NoulCriteria(true=OBS_UNSUPPORTED_YES, false=OBS_UNSUPPORTED_NO)),
        "d_missing": Noul(instructions=OBS_MISSING, criteria=NoulCriteria(true=OBS_MISSING_YES, false=OBS_MISSING_NO)),
        "d_differs": Noul(instructions=OBS_DIFFERS, criteria=NoulCriteria(true=OBS_DIFFERS_YES, false=OBS_DIFFERS_NO)),
    }
    for i, s in enumerate(then_facts(observation)):
        qs[f"d_sent_{i}"] = Noul(instructions=OBS_SENTENCE.format(sentence=s),
                                 criteria=NoulCriteria(true=OBS_SENTENCE_YES, false=OBS_SENTENCE_NO))
    return qs


def fact_questions(then_line: str) -> dict[str, Noul]:
    """The Nouls of question (a) with no Observation: one per sentence of the Then line."""
    return {f"a_fact_{i}": Noul(instructions=FACT_SHOWN.format(fact=f),
                                criteria=NoulCriteria(true=FACT_SHOWN_YES, false=FACT_SHOWN_NO))
            for i, f in enumerate(then_facts(then_line))}


def flags(nouls: dict[str, float]) -> dict[str, float]:
    """The flag probability of each variant. The decision logic lives here, in code.

    d: the one Noul as it is.
    d_split: the higher of the two split Nouls.
    d_sent: 1 - the lowest answer over the sentences of the Observation.
    a_noobs: 1 - the lowest answer over the facts of the Then line.
    """
    sents = [p for k, p in nouls.items() if k.startswith("d_sent_")]
    facts = [p for k, p in nouls.items() if k.startswith("a_fact_")]
    return {
        "d": nouls["d_one"],
        "d_split": max(nouls["d_missing"], nouls["d_differs"]),
        "d_sent": 1 - min(sents) if sents else 0.0,
        "a_noobs": 1 - min(facts) if facts else 0.0,
    }


# Question (d), second draft: per sentence, a second Noul asks if the sentence reports a result the Then line asks for.
# The first draft flagged true but harmless gaps, such as a note on a first run or a claim about the shots of another test.
OBS_RELEVANT = (
    "Does this statement of `agent_observation` report a result that the Then line of `test` asks for: \"{sentence}\"?"
)
OBS_RELEVANT_YES = "The statement gives an outcome, a value, or a screen state that one fact of the Then line depends on."
OBS_RELEVANT_NO = (
    "The statement is about how the agent ran the test, a first try, a path or a port, a commit, "
    "or the evidence of another test."
)


def relevance_questions(observation: str) -> dict[str, Noul]:
    """One Noul per sentence of the Observation, in the same order as the d_sent_ Nouls."""
    return {f"d_rel_{i}": Noul(instructions=OBS_RELEVANT.format(sentence=s),
                               criteria=NoulCriteria(true=OBS_RELEVANT_YES, false=OBS_RELEVANT_NO))
            for i, s in enumerate(then_facts(observation))}


def relevance_flag(nouls: dict[str, float]) -> float:
    """Flag the worst sentence that matters: max over sentences of p(relevant) * (1 - p(shown))."""
    idx = [k.removeprefix("d_sent_") for k in nouls if k.startswith("d_sent_")]
    return max((nouls[f"d_rel_{i}"] * (1 - nouls[f"d_sent_{i}"]) for i in idx), default=0.0)
```

### `replay_obs.py`

```python
"""
Replay question (d) and question (a) with no Observation on the cases of ticket 02, and save each answer to results_obs.json.
Run from the worktree: uv run --package cpc-league python <this file>. Two requests per test: one state with the Observation, one without.
"""
import json
import time
from concurrent.futures import ThreadPoolExecutor

from typesafe_sdk import TypeSafeClient

import obs_questions as oq
from replay import FAILED, FIXED, HEADERS, HERE, MODEL, PRICE_PER_MTOK, build_case, pass_sample


def crit(q, side: str) -> str:
    """The SDK stores the criteria as a dict or as an object, so read either."""
    c = q.criteria
    return c[side] if isinstance(c, dict) else getattr(c, side)


def payload(state: dict, shot_meta: list, qs: dict) -> dict:
    """The request as sent, with each image swapped for its file name and size."""
    st = json.loads(json.dumps({**state, "evidence": {**state["evidence"], "screenshots": {}}}))
    st["evidence"]["screenshots"] = {m["key"]: f"<image {m['file']} sent {m['sent']}>" for m in shot_meta}
    return {"state": st, "questions": {k: {"instructions": q.instructions, "true": crit(q, "true"),
                                           "false": crit(q, "false")} for k, q in qs.items()}}


def ask(client: TypeSafeClient, kind: str, spec: str, sha: str, at: str) -> dict:
    case = build_case(spec, sha, at)
    with_obs = case["state"]
    no_obs = {k: v for k, v in with_obs.items() if k != "agent_observation"}
    q_obs = oq.obs_questions(with_obs["agent_observation"])
    q_fact = oq.fact_questions(case["then"])
    hdr = HEADERS if case["shot_meta"] else None
    t0 = time.time()
    r1 = client.system_one(with_obs, q_obs, model=MODEL, extra_headers=hdr)
    r2 = client.system_one(no_obs, q_fact, model=MODEL, extra_headers=hdr)
    nouls = {**{k: r1.nouls[k].noul for k in q_obs}, **{k: r2.nouls[k].noul for k in q_fact}}
    return {"kind": kind, "spec": spec, "sha": sha, "at": at, "app": case["app"], "model": r1.model,
            "tokens_obs": r1.usage.input_tokens, "tokens_fact": r2.usage.input_tokens,
            "images": len(case["shot_meta"]), "seconds": round(time.time() - t0, 1), "nouls": nouls,
            "flags": oq.flags(nouls),
            "payload_obs": payload(with_obs, case["shot_meta"], q_obs),
            "payload_fact": payload(no_obs, case["shot_meta"], q_fact)}


def main() -> None:
    client = TypeSafeClient(model=MODEL)
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
            print(r.get("kind"), r.get("spec"), r.get("at"), r.get("flags"), r.get("error", ""), flush=True)
    tokens = sum(r["tokens_obs"] + r["tokens_fact"] for r in results)
    (HERE / "results_obs.json").write_text(json.dumps({"results": results, "errors": errors, "input_tokens": tokens,
                                                       "cost_usd": tokens * PRICE_PER_MTOK / 1e6}, indent=1, default=str))
    print("requests", 2 * len(results), "errors", len(errors), "tokens", tokens, "cost", tokens * PRICE_PER_MTOK / 1e6)


if __name__ == "__main__":
    main()
```

### `replay_rel.py`

```python
"""
Replay the second draft of question (d): one relevance Noul per sentence of the Observation, on the cases of ticket 02.
Run from the worktree after replay_obs.py: uv run --package cpc-league python <this file>. It writes results_rel.json.
"""
import json
from concurrent.futures import ThreadPoolExecutor

from typesafe_sdk import TypeSafeClient

import obs_questions as oq
from replay import HEADERS, HERE, MODEL, PRICE_PER_MTOK, build_case


def main() -> None:
    client = TypeSafeClient(model=MODEL)
    prior = json.loads((HERE / "results_obs.json").read_text())["results"]

    def run(r):
        try:
            case = build_case(r["spec"], r["sha"], r["at"])
            qs = oq.relevance_questions(case["state"]["agent_observation"])
            if not qs:
                return {"kind": r["kind"], "sha": r["sha"], "at": r["at"], "tokens": 0, "nouls": {}}
            resp = client.system_one(case["state"], qs, model=MODEL,
                                     extra_headers=HEADERS if case["shot_meta"] else None)
            return {"kind": r["kind"], "sha": r["sha"], "at": r["at"], "tokens": resp.usage.input_tokens,
                    "nouls": {k: resp.nouls[k].noul for k in qs},
                    "questions": {k: q.instructions for k, q in qs.items()}}
        except Exception as err:  # A failed call is an error in the record, never a "no".
            return {"kind": r["kind"], "sha": r["sha"], "at": r["at"], "error": f"{type(err).__name__}: {err}"}

    with ThreadPoolExecutor(4) as pool:
        out = list(pool.map(run, prior))
    tokens = sum(o.get("tokens", 0) for o in out)
    errors = [o for o in out if "error" in o]
    (HERE / "results_rel.json").write_text(json.dumps({"results": out, "input_tokens": tokens}, indent=1))
    print("requests", len(out), "errors", len(errors), "tokens", tokens, "cost", tokens * PRICE_PER_MTOK / 1e6)


if __name__ == "__main__":
    main()
```

### `analyze_obs.py`

```python
"""
Score question (d) and question (a) with no Observation: hits, misses, and false flags at each cut.
Reads results_obs.json, results_rel.json, and results.json of ticket 02, and prints Markdown tables for the notes file.
"""
import contextlib
import io
import json
from pathlib import Path

import flag_questions as fq
import obs_questions as oq

# analyze.py of ticket 02 prints its tables on import, so the import runs with its output thrown away.
with contextlib.redirect_stdout(io.StringIO()):
    from analyze import LABELS

HERE = Path(__file__).parent
R = json.loads((HERE / "results_obs.json").read_text())["results"]
REL = {(o["kind"], o["sha"], o["at"]): o for o in json.loads((HERE / "results_rel.json").read_text())["results"]}
OLD = {(r["kind"], r["sha"], r["at"]): r["flags"]["a"] for r in json.loads((HERE / "results.json").read_text())["results"]}
# The targets of ticket 06: the three Observation gaps for (d), and AT-47 for both (d) and (a).
TARGETS = {"d": {("35ca282e", "AT-50"), ("9582a573", "AT-54"), ("9582a573", "AT-55"), ("878ccd3a", "AT-47")},
           "a": {("878ccd3a", "AT-47"), ("8d646bd0", "AT-3")}}
COLS = (("d", "d one Noul", "d"), ("d_split", "d split", "d"), ("d_sent", "d per sentence", "d"),
        ("d_rel", "d v2 sentence x relevance", "d"), ("a_noobs", "a, no Observation", "a"), ("a_old", "a of ticket 02", "a"))


def values(r: dict) -> dict:
    f = dict(r["flags"])
    key = (r["kind"], r["sha"], r["at"])
    f["d_rel"] = oq.relevance_flag({**r["nouls"], **REL[key]["nouls"]})
    f["a_old"] = OLD[key]
    return f


rows = [(r, values(r)) for r in R]
failed = [x for x in rows if x[0]["kind"] == "failed"]
passed = [x for x in rows if x[0]["kind"] == "pass"]
fixed = [x for x in rows if x[0]["kind"] == "fixed"]

print("| Question | Cut | Hits | Hit tests | Gaps flagged (of 7) | Defects flagged (of 5) | False flags on PASS | False-flag rate |")
print("| --- | --- | --- | --- | --- | --- | --- | --- |")
for col, name, tgt in COLS:
    for cut in fq.CUTS:
        t = [(r, f) for r, f in failed if (r["sha"], r["at"]) in TARGETS[tgt]]
        hits = [r["at"] for r, f in t if f[col] >= cut]
        gaps = sum(1 for r, f in failed if LABELS[(r["sha"], r["at"])][0] == "gap" and f[col] >= cut)
        defs = sum(1 for r, f in failed if LABELS[(r["sha"], r["at"])][0] == "defect" and f[col] >= cut)
        ff = sum(1 for r, f in passed if f[col] >= cut)
        print(f"| {name} | {cut} | {len(hits)} of {len(t)} | {', '.join(hits) or 'none'} | {gaps} | {defs} | {ff} of {len(passed)} | {ff / len(passed):.0%} |")

head = "| Test | Round | Label | " + " | ".join(n for _, n, _ in COLS) + " |"
sep = "| --- " * (3 + len(COLS)) + "|"
for title, group in (("Failed rounds", failed), ("Fixed rounds", fixed)):
    print(f"\n{title}\n\n{head}\n{sep}")
    for r, f in group:
        lab = LABELS.get((r["sha"], r["at"]), ("pass", "", set()))[0] if r["kind"] == "failed" else "pass"
        print(f"| {r['spec']} {r['at']} | {r['sha']} | {lab} | " + " | ".join(f"{f[c]:.2f}" for c, _, _ in COLS) + " |")
print(f"\nPASS tests with any flag at 0.7 or more\n\n| Test | " + " | ".join(n for _, n, _ in COLS) + " |")
print("| --- " * (1 + len(COLS)) + "|")
for r, f in passed:
    if max(f[c] for c, _, _ in COLS) >= 0.7:
        print(f"| {r['spec']} {r['at']} | " + " | ".join(f"{f[c]:.2f}" for c, _, _ in COLS) + " |")

t_obs = sum(r["tokens_obs"] for r in R)
t_fact = sum(r["tokens_fact"] for r in R)
t_rel = sum(o.get("tokens", 0) for o in REL.values())
for name, n, t in (("d drafts, with Observation", len(R), t_obs), ("a, no Observation", len(R), t_fact),
                   ("d v2 relevance", len(REL), t_rel)):
    print(f"\n{name}: {n} requests, {t} input tokens, ${t * 0.042 / 1e6:.4f}")
```

