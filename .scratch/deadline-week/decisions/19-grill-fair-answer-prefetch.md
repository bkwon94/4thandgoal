# 19: Can the Finder ask its fair questions before a press?

Map: `.scratch/deadline-week/MAP.md`.

**Kind:** grill

**Blocked by:** 13, 16

**Status:** done

## Question

After ticket 13 and the speed fix, a real press for Bo Girds takes 64 to 93 s. The Finder of the site stops at 60 s. Step 1, the fair check of about 5,500 Value offers in both side orders, takes 41 s, near the floor of the account limit of 100,000 tokens per second. The pick call takes 15 to 45 s. Decide whether the API asks the fair questions before a press.

## Decision

Brian agreed on 2026-11-20, after the page "Finder Prefetch" (https://claude.ai/artifact/6qB2nk2oJXq35WLNLdetcg).

1. **A fair cache in the API process.** The fair question reads only the players of each side, their chart values, the chart sums, and the team names. It reads no lineup. So the answer of one offer serves a press of either team. The key is the chart week and the player ids of each side, in the side order. The value is the Noul answer of that order.
2. **A warm-up in the background.** At API start, a worker builds the Value offers of all 66 team pairs and asks each fair question that the cache does not hold. A new chart week gives new keys, so the worker asks again.
3. **Small updates after a trade.** A changed roster gives new keys only for the offers that hold a moved player. The worker asks only those.
4. **A press goes first.** The warm-up and a press share the one pacer. The warm-up waits while a press is live.
5. **A miss is not an error.** A press asks each missing key live through the pacer, as today, and stores the answer.
6. **Step 2 and the pick stay live.** Need and gain read the lineup of the asker, so no cache holds them.

This reverses one line of decision 02, "no prewarm", for the fair answers only.

Brian chose CPC only on 2026-11-20, because a warm-up of CPC costs about $1.46 per deploy and Norcal adds $1.72.

**Check before the build.** The fair state labels the two teams `asker` and `partner`. A real test must show that the mean of the two side orders does not move when the labels swap. If it moves, the fair state uses labels that name no asker, in the warm-up and in the live press.

**Estimates, not claims.** A full warm-up is about 6 times the step 1 of one press: about 22M tokens, about 4 minutes, and about $0.90 of Jev. The Fly app keeps one machine up (`min_machines_running = 1`), so only a deploy clears the cache. No copy states a time.

**Tests.** No acceptance test changes. The Finder gives the same answers, and AT-55 to AT-62 still cover them.
