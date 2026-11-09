# 03: What the search across all partners costs

Map: `.scratch/manager-brain/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** done

## Question

Measure on the week 8 rosters of cpc and norcal: the candidates of 1-for-1 and 2-for-1 per partner, the partners that the four-question filter keeps, the tokens of Jev per candidate, and the cost and the time of one Finder call. The targets are under about 30 seconds and under about 10 cents. Read the TypeSafe limits and prices from the live docs. Code counts can run before `jev` merges.

## Decision

Brian decided on 2026-11-09. The notes are in `03-research-search-cost.notes.md`.

1. **A full search costs too much.** One asker against 11 partners has about 10,000 candidates on cpc week 8, from 5,109 to 12,990. Jev on all of them costs about 50 cents and takes about 100 s per press.
2. **No math filter.** The research proposed a code screen on lineup loss and a cap of 50 per partner. Brian rejected both: "I personally don't like the math or pure code filters." A screen on season points drops trades a manager wants, such as a backup who is about to start.
3. **Players first, then offers.** The finder narrows the way a manager does:
   1. The partner filter: Jev asks the four questions for each partner.
   2. The targets: for each partner that passes, Jev asks of each of his players "would the asker want him?", and of each player of the asker "would that manager want him?".
   3. The offers: code builds every one-for-one and two-for-one trade from the targets only. Code counts here and does not judge.
   4. The shortlist: Jev asks its questions on each offer, such as "would both managers accept?".
   5. The pick: the Advisor reads the shortlist, picks up to three trades, and writes why.
4. **Code keeps the hard rules only:** no kicker, no defense, no player out with no return week, and no handcuff. They decide which trades are legal, not which are good.
5. **The targets:** about 2 to 4 per side, and about 10 to 30 offers per partner. Claude estimates under 1 cent and about 10 to 20 s per press. Prototype 04 measures the real numbers and checks that the targets make sense to Brian.
6. **The rate limits.** Brian read them on 2026-11-09: 80 requests per second and 100,000 tokens per second. One press sends about 11 requests per step, which fits. The shortlist step can pass 100,000 tokens when every partner passes, so code sends its requests in waves under the token limit. Prototype 04 measures the real counts.

The risk: a target that Jev misses drops every trade with that player.
