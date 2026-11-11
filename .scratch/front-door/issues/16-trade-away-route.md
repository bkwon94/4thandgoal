# 16: A trade away of one named player reaches the trade ideas Topic

Spec: `.scratch/front-door/PRD.md`. Source: H6 of `.scratch/front-door/HANDS-ON.md`. Acceptance test AT-17.

**App:** api

**What to build:** "i want to trade parker washington" streamed a text, then ended as the honest miss. Jev picked trade ideas each time, but `fits_topic` sat at the 0.7 cutoff, from 0.68 to 0.75, so the route flipped between the Topic and a free answer. The trade ideas Topic text says that it also gives ideas when the manager wants to trade away one named player. The route eval holds two questions of this kind, so the set grows from 40 scored questions to 42, and the bar keeps the share of 87.5% at 37 of 42. The 0.7 cutoff stays. A `/find` built around the named player is a later spec.

**Blocked by:** 09

**Status:** done

- [x] The trade ideas Topic names a trade away of one named player.
- [x] The route eval holds "i want to trade parker washington" and "looking to move Zay Flowers", each with `topic:trade_ideas`.
- [x] `HITS_NEEDED` is 37 and the eval scores 42 questions.
- [x] The live route eval passes, and both new questions route to trade ideas.
- [ ] AT-17 in `ACCEPTANCE.md` names the new bar of 37 of 42, after the commissioner approves it.

## Comments
- Closes with the squash merge of the spec PR.
