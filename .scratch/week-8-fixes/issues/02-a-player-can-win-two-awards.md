# 02: A player can win two awards

Spec: `.scratch/week-8-fixes/PRD.md`, part 2.

**What to build:** Joe Burrow earned Top Scorer and Game Changer in week 8, and a rule gave him one. Find the
rule that keeps a player to one award and remove it. Each award picks its own winner.

**Blocked by:** none.

**Status:** ready-for-agent

- [ ] Find the rule. Name the module and the line in the close comment, and say how you found it.
- [ ] Remove it. Keep a comment that says each award picks its own winner, and why: a reader expects the top scorer to be the top scorer.
- [ ] If a test asserted the one-award rule, change it to assert the new rule.
- [ ] A test shows one player wins two awards when the numbers say so.
- [ ] The week 8 awards from the saved data show Joe Burrow in both. Name the two blurbs' first sentences in the close comment.
- [ ] `make golden` ran, and the golden diff is named in the close comment.
- [ ] `make check` passes.
