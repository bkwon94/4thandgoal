# 01 notes: why the Finder gives no offer or one offer

Ticket: `01-research-few-offers.md`. Map: `../MAP.md`.
Worktree: `.claude/worktrees/deadline-week`, branch `deadline-week`. Each source is a file of this repo, read on 2026-11-18.
Each line number is the line in that file now. Each team is its roster id. The notes name no manager and no team name.

## Summary

- Two steps cut the most, and they cut in different modes.
- **With one partner**, the Partner filter cuts. It stops 27 of 33 pairs. A stopped pair falls to the wider pass, which builds one plain-rule 1-for-1 offer. The Advisor then reads one offer and rejects it in 13 of those 27 runs. That run gives the line "No offer on the list helps your lineup enough to send." This is the line Brian saw.
- **With every partner**, the Advisor keeps 13 of 112 Shortlist offers over 12 runs. 9 runs give one pick. The Shortlist has little variety: one player of the asker sits in 6 to 9 of the 10 offers. The Advisor reads ten forms of one or two trades, not ten trades.
- The Partner filter never stops a partner on a "no". No answer of the 132 pairs is under 0.3. Each stop is an "unsure" answer between 0.38 and 0.70 to a "spares" question. The median of `asker_spares` is 0.70, which is the pass line itself.
- The guess "the 4-of-4 filter cuts too much" holds. The cause is the gate at `> 0.7`, not four "no" answers. The guess "the Advisor rejects most of the Shortlist" also holds, but the Shortlist it gets is narrow.
- Total spend: $1.48 of the $3.50 budget.

## 1. The chain in code

1. The Partner filter asks four Jev questions per partner (`packages/analyzer/python/src/analyzer/finder_search.py:29-63`). A partner passes only when each answer is above `YES_AT` (`finder_search.py:427`). `YES_AT` is 0.7 (`packages/analyzer/python/src/analyzer/trade_jev.py:37`). An answer from 0.3 to 0.7 is "unsure", and it stops the partner the same as a "no".
2. The targets: Jev rates each pool player of each side. A target needs `TARGET_AT` 0.6, at most `TARGET_MAX` 4 per side (`finder_search.py:71-72`). A partner with zero targets on one side builds no offer.
3. The offers: code builds each 1-for-1, 2-for-1, and 1-for-2 from the targets (`build_offers`).
4. The Shortlist: Jev asks the fair and the need questions of each offer. Code keeps the 10 with the highest product, with no floor (`finder_search.py:73`, `finder_search.py:495`). So the Shortlist cuts only by count.
5. The wider pass: when the targets build no offer at all, `wider_offers` builds at most one plain-rule 1-for-1 per partner that did not fail its request, with no Jev question (`finder_search.py:307`, `finder_search.py:461`). It includes partners that the filter stopped.
6. The Advisor reads the Shortlist and picks up to 3. The prompt says "Fewer good picks beat three weak ones" and asks for a trade that "the other manager would take" (`packages/analyzer/python/src/analyzer/prompts/finder_pick.md:32`). The none line of the prompt is the example "No offer on the list helps your lineup enough to send." (`finder_pick.md:50-52`).
7. The code lines `NO_PARTNER` and `NO_OFFER` (`packages/analyzer/python/src/analyzer/finder_pick.py:53-54`) show only for an empty Shortlist. The wider pass almost always fills the Shortlist, so the line that Brian saw comes from the Advisor, not from code.

## 2. Method

- Data: the saved CPC week 10 raw folder, `clients/cpc/data/2026/week-10/raw/`. Sleeper rosters of that folder were fetched on 2026-11-17, so they are the rosters of week 11, the deadline week. No week 11 folder exists yet. No fetch ran.
- Code: a throwaway script in the session scratchpad. It called `search` and `pick_trades` as `_find_one` of `apps/pipeline/src/cornerstone/advisor_eval.py:322` does, with no news. It wrapped Jev to keep every answer. It used the `Meter` of `advisor_eval.py` for the cost. The script is deleted. `git status` was clean after each run.
- Runs: 12 runs with every partner, one per CPC team. 33 runs with one partner: teams 8, 4, and 11 against each other team.
- Gap: the script did not save the raw output of the Advisor. A pick that fails its guards and its repair drops with no record. Run 1 shows this: the Advisor gave two picks, both failed a number guard, and one repair failed. So the "picks" column counts picks that stand, after the guards.

## 3. Every partner: the keep count of each step

Partners in is 11 in each run. "Targets" is the sum over the passed partners, as asker side / partner side. "Shortlist gives" is the count of different players of the asker in the Shortlist, and how many offers hold the most common one.

| Asker | Passed filter | Targets (asker / partner) | Offers | Wider pass | Shortlist | Shortlist gives (distinct, top) | Picks | Near |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 3 | 5 / 8 | 30 | no | 10 | 4, x6 | 1 | 3 |
| 2 | 3 | 7 / 9 | 44 | no | 10 | 2, x9 | 1 | 3 |
| 3 | 4 | 12 / 8 | 66 | no | 10 | 3, x4 | 1 | 2 |
| 4 | 1 | 0 / 4 | 11 | yes | 10 | 3, x6 | 1 | 2 |
| 5 | 5 | 15 / 10 | 80 | no | 10 | 3, x7 | 2 | 3 |
| 6 | 5 | 13 / 7 | 26 | no | 10 | 3, x7 | 1 | 3 |
| 7 | 0 | none | 11 | yes | 10 | 4, x4 | 1 | 3 |
| 8 | 1 | 1 / 3 | 6 | no | 6 | 1, x6 | 0 | 2 |
| 9 | 4 | 10 / 13 | 105 | no | 10 | 3, x8 | 1 | 3 |
| 10 | 1 | 0 / 4 | 11 | yes | 10 | 2, x6 | 2 | 1 |
| 11 | 1 | 1 / 3 | 6 | no | 6 | 1, x6 | 1 | 3 |
| 12 | 3 | 10 / 11 | 130 | no | 10 | 3, x7 | 1 | 2 |
| **All** | **31 of 132** | **74 / 80** | **526** | **3 of 12** | **112** | | **13** | **30** |

- The filter keeps 23% of the pairs.
- The target step rates 76 of 359 players of the askers and 81 of 351 players of the partners at 0.6 or more: about 22%. The cap of 4 per side then keeps 74 and 80. Another 63 players sit between 0.5 and 0.6.
- In 3 runs, the one passed partner wanted no player of the asker (asker side 0), so the targets built no offer and the wider pass ran.
- The median of the Jev fair answer in the Shortlist is 0.36 to 0.55 per run. So Jev reads most Shortlist offers as "unsure" on fair.
- The Advisor keeps 12% of the Shortlist as picks. 9 of 12 runs end with one pick. One run ends with none: "No offer on the list helps your lineup enough while also giving the other manager a reason to say yes."
- The cost of a run is $0.04 to $0.18. The time is 12 to 51 s.

## 4. One partner: the keep count of each step

| Asker | Pairs | Passed filter | Wider pass, one offer | Runs with a pick | Runs with no pick |
| --- | --- | --- | --- | --- | --- |
| 8 | 11 | 4 | 7 | 5 | 6 |
| 4 | 11 | 1 | 10 | 4 | 7 |
| 11 | 11 | 1 | 10 | 8 | 3 |
| **All** | **33** | **6** | **27** | **17** | **16** |

- 27 of 33 pairs fail the filter. Each of them goes to the wider pass with one offer. The Advisor picks that one offer in 14 runs and rejects it in 13.
- Of the 6 passed pairs, 2 built no offer from the targets and also went to the wider pass. 3 of the 6 end with no pick.
- 16 of 33 runs end with no pick. 9 of them use the exact line "No offer on the list helps your lineup enough to send." The other 7 say the same thing in other words, such as "No offer on the list is one the other manager would likely accept."

## 5. The question of the Partner filter that says no most often

No question said "no". Each stop came from an "unsure" answer at or below 0.7.

| Question | Min | Median | Max | At or below 0.7 | The only answer at or below 0.7 |
| --- | --- | --- | --- | --- | --- |
| `asker_spares` | 0.38 | 0.70 | 0.80 | 71 | 39 |
| `partner_spares` | 0.42 | 0.71 | 0.83 | 56 | 26 |
| `partner_has` | 0.53 | 0.87 | 0.93 | 6 | 1 |
| `asker_has` | 0.47 | 0.89 | 0.95 | 6 | 1 |

- `asker_spares` stops the most: "Can {asker} give up a player who would start at a weak slot of {partner}, with no hole in its own lineup?" (`finder_search.py:51-56`).
- The two "spares" questions sit on the pass line. A run of the same pair a second time moved each answer by 0.017 on average, at most 0.06. That flipped the result of 3 of 33 pairs. So the gate is close to a coin flip for many pairs.
- The two "has" questions almost always say yes, so they cut almost nothing.

## 6. The main cause, with the evidence

1. **One partner: the filter gate sends most pairs to a one-offer wider pass.** The gate counts "unsure" as a stop (`finder_search.py:427`). 77% of pairs stop. 127 of the 139 answers that stop them are "spares" answers, and 111 of those 127 are between 0.6 and 0.7. The wider pass then gives the Advisor one offer built by a plain rule, with no Jev target. About half the time the Advisor says no. That is the empty line of section 4.
2. **Every partner: the Shortlist is narrow, so the Advisor finds one good trade.** The top 10 by product holds one or two players of the asker again and again (section 3, column "Shortlist gives"). The near reasons show the same trade fall short for the same cause, such as "You give up Kyren Williams, and the RBs who can play now go from 2 to 1". The Advisor rejects a set of variants, not a set of ideas.
3. **The target step thins both of the above.** Only about 22% of the pool players reach 0.6. With at most 4 per side, and often 0 or 1 on the asker side, few distinct trades exist to rank.

## 7. Options that keep judgment

Each option keeps Jev and the Advisor as the judges. None throws out a trade by a score cut.

1. **Let "unsure" pass the Partner filter.** Stop a partner only on a clear "no" (below `NO_AT` 0.3), or on a "no" from both "spares" questions. In these runs, no answer was below 0.3, so every partner would go on to the target step. The target questions and the Advisor then judge each partner on real players. The cost rises with the partner count: about 11 target requests in place of about 3. Decision 02 must check the time.
2. **With one picked partner, skip the gate.** The manager named the partner, as he names an anchor, and the anchor search already skips the filter (`finder_search.py:414-418`). The Jev targets then build up to 10 real offers for the Advisor in place of one plain-rule offer.
3. **Give the Advisor distinct ideas.** Build the Shortlist with variety: for example, the best-rated offer for each player that the asker gives, or for each partner, before more forms of the same trade. This is a rule on which offers the Advisor reads, not a cut by score. A Jev question "Is this the same trade idea as offer X?" is a judgment form of the same rule.

## 8. Spend

- Total: $1.48, measured by the `Meter` of `advisor_eval.py`. Almost all of it is Claude, on `FINDER_PICK_MODEL`. Jev costs a fraction of a cent per run.
- Every partner: $0.97 for 12 runs.
- One partner: $0.51 for 33 runs. A run that falls to the wider pass costs about $0.01.
