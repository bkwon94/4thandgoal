# 06: Past-season splits

Spec: `.scratch/manager-brain/PRD.md`. Acceptance tests AT-5, AT-6, and AT-7.

**App:** pipeline

**What to build:** A history claim carries a number with its game count. The sheet gets, per player and per season of the last 3 complete seasons, the team, the half-PPR points per game in weeks 1 to 8 and in weeks 9 to 17, and in cold games, each with its game count. A cold game is outdoors at 40 F or below. The source is the nflverse weekly player file, with the gsis ids mapped to Sleeper ids. A past season file is cached with no max age. A player with no past season gets no split, and the Advisor speaks of him with no number.

**Blocked by:** 02

**Status:** in-review

- [x] The sheet of Derrick Henry has the splits of 2023, 2024, and 2025, each with its game count.
- [x] The sheet of the rookie Omar Cooper Jr. has no split, and no read gives him a past-season number.
- [x] A second press downloads no past-season file.
- [x] `make check-fast` passes.
