# 05: Top score and Median Trend tiles

Spec: `.scratch/card-polish/PRD.md`. Acceptance tests AT-14, AT-15, AT-16, AT-18, and AT-30.

**App:** site

**What to build:** `Tile` takes an optional trend of week points, the page week, and a chart kind. The week page reads the `weeks` of every manager in `managers.json` and builds two series from week 1 to the page week: the highest points of each week as bars, and the median of each week as a stepped area, after the Lime Metrics item. The median is the published median of the week, or else the median of the points of every team with the rounding rule of the week numbers. The bar of the page week is lit. Each Trend tile has a text of its trend. Closest and Game Changer stay plain.

**Blocked by:** none

**Status:** ready-for-agent

- [ ] The CPC week 8 Top score tile shows 134.1 and bars 156.92, 156.52, 140.6, 145.63, 158.96, 126.79, 148.13, and 134.1, with week 8 lit.
- [ ] The CPC Median trend ends at 99.6, and the NorCal Median trend ends at the number of the NorCal tile.
- [ ] The week 6 page shows six bars and no later week.
- [ ] A unit test of the series function covers both median sources.
- [ ] Closest and Game Changer show no chart.
- [ ] `make check-fast` passes.
