# 01: Why does the Finder give no offer or one offer?

Map: `.scratch/deadline-week/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** done

## Question

Brian ran the Finder on Norcal. With one partner, it often says "No offer on the list helps your lineup enough to send." With every partner, it gave one trade idea. The spec must know which step cuts the most before it changes the Finder.

Run the Finder on the CPC week 11 data for every team, with no partner and with each partner. Count what each step keeps: the Partner filter, the targets, the offers, the Shortlist, and the picks of the Advisor. One guess to check: the Partner filter passes a partner only on four yes answers out of four. Write the findings at `decisions/01-research-few-offers.notes.md`.

## Decision

Brian chose all three fixes on 2026-11-18. The findings are in `decisions/01-research-few-offers.notes.md`.

The cause: the Partner filter stops 77% of pairs, and 127 of its 139 stops come from an "unsure" answer to one of the two "spares" questions, near the 0.7 line. With one partner, a stopped pair gets one plain-rule offer, and the Advisor rejects it about half the time. With every partner, the Shortlist holds 10 forms of one or two trades, so the Advisor keeps one.

The spec does these three fixes:

1. With one picked partner, the Finder skips the Partner filter, as the anchor search does. The Jev targets build the offers.
2. The Shortlist has variety: the best offer for each player that the asker gives, and for each partner, before more forms of the same trade. This chooses what the Advisor reads. It cuts no trade by a score.
3. The "spares" gate changes. An "unsure" answer passes, and only a clear "no" stops a partner. Ticket 05 splits each "spares" question into tiny questions in a Jev tree.

The cost: about 11 target requests in place of about 3 per search, about 1 to 2 s more.
