# 09: Why does the target step of the Finder want QBs for roster 6?

Map: `.scratch/deadline-week/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** done

## Question

On the phone walk of decision 06, trade ideas for roster 6 gave only RB or WR for QB trades, such as "Kenneth Walker for Mahomes" and "Zay Flowers for Goff". The Fly log of the run at 02:51 UTC on 2026-11-19 shows the target step marked Mahomes and Goff as wanted, with a need of 0.9 for roster 6, and every Shortlist offer with `fair` from 0.29 to 0.39.

Replay the press of roster 6 on the week 11 snapshot, for about $0.10, and log each step. Find out:

1. The weak starting slots that code gives roster 6, and if QB is one of them, and why.
2. The Jev answers of the target question for each QB, and the state it read.
3. If the cause is the target question (the "or" in "would start or fill a weak spot"), the weak-slot rule in code, or the state.
4. Which change fixes it, in the frame of decision 05: a split question, a better state, or code logic. No threshold change, and no cut by a score.

The findings go beside this ticket, at `09-research-qb-targets.notes.md`. The league data stays out of the repo except the player names of the two Backtest marks.

## Decision

Brian chose options 1 and 2 on 2026-11-18. The findings are in `09-research-qb-targets.notes.md`. Spend: $0.0016, all Jev.

The cause: no step asks what the asker gives up. The QB slot of roster 6 is weak by the code rule (Rodgers projects QB19, past rank 12), so the targets aim at QBs. The NEED question reads only what a team gets, and the Shortlist ranks by a product with no floor, so "Zay Flowers for Goff" stands although it drops the lineup of roster 6 from 110.0 to 103.8 points a week. Also, `depth` counts a player who is Out as cover (`finder_search.py:150`).

The spec does two fixes:

1. **The Spares tree on the give side.** Decision 05 runs the tree for both teams of a pair. The depth count of the tree counts only a player who can play now, so a player who is Out is never cover.
2. **A gain question on the Shortlist.** Code puts the lineup points of each side before and after the trade into the state, as facts. Jev answers one Noul per side: "Does {team} start a better lineup after this trade?" A clear no, below `NO_AT` 0.3, drops the offer, as in the Spares tree. An unsure answer stays. A failed call is an error, never a no. In the replay it gave 0.09 and 0.08 on the two Backtest marks of decision 06.

Not now: the split of the target question stays out of scope (decision 05). The weak-slot rule stays as it is, because a change to it is a threshold change.
