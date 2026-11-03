# 04: The roster grade and the slot ranks

**What to build:** the hero shows the roster grade as a letter, the index cards show it too, and the Roster chapter lists one slot rank per position with one depth word. The pipeline computes a 0 to 100 score from the analyzer's snapshot and maps it to the letter. The site sees the letter only. Both repos.

**Blocked by:** 03 The routes, the index, the hero, and the menu

**Status:** done

- [x] The score reads each starting slot against the line, holes, depth above the line per position, and the best lineup's lineup value against the league.
- [x] The bands are A+ at 90, A at 80, B at 65, C at 50, D under 50. The score parts and the bands are tunables in one place.
- [x] Each entry carries the letter and the slot ranks for QB, RB, WR, and TE: the rank 1 to 12 and the depth word, deep, fine, or thin.
- [x] The managers module tests cover each band at its edge and each depth word.
- [x] The hero shows the letter with the depth words in short form under it. The index cards show the letter.
- [x] The Roster chapter lists the slot ranks as "RB · 2nd of 12 · deep". One quiet label, one emphasis per line.
- [x] The page tests read the letter and the slot ranks. All checks pass in both repos.
