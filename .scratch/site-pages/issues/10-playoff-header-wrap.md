# 10: The playoff header takes three lines on a tablet

**What to build:** A league member on a tablet sees the "Playoff %" header of the rankings table on two lines at most, as on a phone and a desktop. At 768 the 40px column and the 11px label put it on three lines: "PLAY-", "OFF", "%". The soft hyphen in the header is on purpose. A 44px playoff column fixes it but leaves the team track 1.5px over the width the longest name needs. Find a header text or a column width that holds at every tier. The type scale of the report feature made the label bigger on a tablet, so this is from before the site-pages feature.

**Blocked by:** None

**Status:** wontfix

- [ ] The header takes two lines at most at 390, 768, and 1280.
- [ ] Every team name stays on one line at 768 and 1280.

## Comments

Closes as wontfix in the audit of `todoist-queue` on 2026-11-12.
Proof: The redesign 0a8b8868 replaced the rankings table with the Ladder, and no "Playoff %" column header exists in `apps/site/src` or `packages`.
Read 1 file: .scratch/todoist-queue/audit.md.
