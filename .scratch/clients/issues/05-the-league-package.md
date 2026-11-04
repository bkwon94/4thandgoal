# 05: The league package

Spec: `.scratch/clients/PRD.md`. Acceptance tests AT-1 and AT-14.

**App:** both

**What to build:** The shared kernel moves into the `league` package, in both languages. Every outside service enters through it. The points key and the position lists come from the League settings.

**Blocked by:** 02

**Status:** in-review

- [x] The `league` package holds the modules of decision 01, in Python, and `headshot` and `avatar` on the site side.
- [x] The Sleeper adapter takes its cache dir in its constructor. The fetch calls drop the cache argument.
- [x] The reception points choose the points key: 0, 0.5, or 1. Another value fails the build with a plain message (AT-14).
- [x] The roster slots set the position lists. `K` leaves the CPC pool with no change to the golden files.
- [x] `chart` is a package value of `league`, with no chart as the default. CPC sets its chart.
- [x] The README states that the Sleeper player ID is the canonical ID, and lists each Sleeper shape as a duty of a later adapter.
- [x] The CPC golden diff is empty (AT-1).
