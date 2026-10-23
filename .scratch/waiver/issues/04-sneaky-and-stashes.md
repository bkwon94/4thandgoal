# 04: Sneaky and stashes

Spec: `.scratch/waiver/PRD.md`.

**What to build:** The file gains two buckets. Sneaky: free agents whose usage trend score is in the
top quarter and whose projection score is in the bottom half, or who sit one depth chart slot below
an injured player. Stashes: free agents out or on IR with a return week inside the season and a rest
of season projection in the top half of their position, plus the handcuff rule for a player one slot
below a starter. Each player in these buckets carries a story fact from the injury file and the depth
chart, "Pittman is out, and Bernard is next on the depth chart". Every bucket entry says which rule
put him there.

The return week comes from the hand-kept returns file first and the injury file second. A player in
best adds is not sneaky.

**Blocked by:** 02 Usage and environment.

**Status:** ready-for-agent

- [ ] A player with a rising snap share and a flat projection lands in sneaky and not in best adds.
- [ ] A player one slot below an injured starter lands in sneaky with the story fact naming the starter.
- [ ] A player out with a return week and a top-half rest of season projection lands in stashes.
- [ ] A handcuff one slot below a healthy starter lands in stashes when the rule holds.
- [ ] A player out with no return week does not land in stashes.
- [ ] Each entry carries its bucket reason, and the story fact has no digit that is not in its numbers.
- [ ] Glossary gains **Sneaky add**, **Stash**, and **Story fact**.
