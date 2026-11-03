# 01: Which rows of the manager page show the bye week

Map: `.scratch/zz-dry-run/MAP.md`.

**Kind:** grill

**Blocked by:** none.

**Status:** done

## Question

The manager page lists players in the top performers and the best adds, and it has no roster list. The spec must name the rows that get the bye week, because the rows set the fields that the pipeline adds to `managers.json`.

## Decision

Both lists show the bye week: each top performer row and each best add row. The page gets no new roster list, because a roster list is a feature of its own. A player who changed NFL teams shows the bye of his team now. Brian decided it in the grill of 2026-11-03. (dry run)

The grill (dry run):

1. Q: Which rows show the bye week? Recommended: the top performers and the best adds, since the page has no roster list. A: Both lists. (dry run)
2. Q: A player who changed NFL teams this season: whose bye? Recommended: his team now. A: His team now. (dry run)
3. Q: Does the bye need a glossary term? Recommended: no, "bye week" is plain. A: No term. (dry run)
