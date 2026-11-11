# 17: A free answer states facts only, and the rewrite drops a failed sentence

Spec: `.scratch/front-door/PRD.md`. Source: H6 of `.scratch/front-door/HANDS-ON.md`. Acceptance tests AT-21, AT-22.

**App:** api

**What to build:** In 5 live replays of "i want to trade parker washington", the Jev check failed no wrong number. Each failed sentence was advice or an opinion word, such as "decent", "a good time to sell", or "you can afford to move him". The rewrite let Claude reword a failed sentence, so in one run the second text kept it near the cutoff and ended as the honest miss. The instructions of a free answer allow only facts from the tool results, with no advice, no rating, and no opinion word. The word "verdict" is an old word of ADR 0030, so the rule says "rating". A trade question ends with the facts, and the Suggestion offers the trade Topic. The rewrite removes each failed sentence, or restates it with only the exact numbers of the tool results, and adds no new claim. The 0.7 check cutoff stays, because it caught real opinions.

**Blocked by:** 05

**Status:** in-review

- [x] `INSTRUCTIONS` of `free_wording.py` forbids advice, a rating, and an opinion word.
- [x] `REWRITE` removes or restates each failed sentence and adds no new claim.
- [x] A unit test reads the text of both prompts.
- [x] A live free answer on the trade question and on 2 opinion questions passes the check, with at most one rewrite.
