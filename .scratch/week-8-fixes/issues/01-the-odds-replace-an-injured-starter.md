# 01: The odds replace an injured starter

Spec: `.scratch/week-8-fixes/PRD.md`, part 1.

**What to build:** In the playoff odds, a starter whose projection is zero because of an injury is replaced
by the better of the best bench player and the best waiver player at that position. The projection shift
then measures the real roster, not a hole. Any position, not only QB. Week 8 case: Lamar Jackson, listed Out.

**Blocked by:** none.

**Status:** ready-for-agent

- [x] Find where the odds engine builds each roster's projection and the projection shift. Name the module in the close comment, and say how you found it.
- [x] An injured starter is a starter with a zero projection and an injury status that is not healthy. A healthy starter with a zero projection is not replaced; say why in a comment.
- [x] The replacement is the better projection of the best bench player and the best waiver player at that slot's position. A flex slot takes any of its positions.
- [x] The waiver pool is the free agents the data already holds. No new fetch.
- [x] A test with one injured QB starter and a bench QB at 15 points shows the roster's projection rises by 15.
- [x] A test with no bench QB and one waiver QB at 12 points shows the rise of 12.
- [x] A test with a healthy zero-projection starter shows no change.
- [x] The week 8 odds from the saved data change for the rosters with an injured starter. Name each one and its before and after in the close comment.
- [x] `make golden` ran, and the golden diff is named in the close comment.
- [x] `make check` passes.
