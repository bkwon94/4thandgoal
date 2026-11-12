# 14: The Jev Swaps and the toggle

Spec: `.scratch/front-door-lineup/PRD.md`. Acceptance tests AT-4, AT-5, AT-6, AT-11, AT-20.

**App:** both

**What to build:** Jev judges each pair of a bench player and a starter he can replace, in one request per lineup, with one Choice per pair over the two Fact sheets. Code marks a Swap at a probability of 0.7 or more, resolves the candidates by the highest probability, and fills each slot once. A Swap row reads "Swap over <name>" with the name struck through, and the first Swap or Q row opens on arrival with its reason. The header toggle shows "By projection" and "With N Swaps", and the digits of the total roll. A failed Jev call gives the honest miss.

**Blocked by:** 13

**Status:** in-review

- [x] A pytest with the Jev fake marks a Swap at 0.70 and keeps the starter at 0.69 (AT-5).
- [x] A pytest with the Jev fake resolves the conflicts as AT-6 says (AT-6).
- [x] A pytest shows the honest miss on a failed Jev call (AT-20).
- [ ] A live lineup with a Swap shows the Swap row and its reason open on arrival (AT-4).
- [x] The toggle shows two totals, and the Swap total equals the sum of the projections with the Swaps (AT-11).
