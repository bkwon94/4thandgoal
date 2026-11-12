# 08: The site renders the known-games line

Spec: `.scratch/known-games/PRD.md`, "Two bounds in the as-of stamp". Repo: the site, `~/repos/cpcfantasyfootball`,
the analyze page and its types.

**What to build:** The analyze page reads the known-games block from the result document and renders one line
under the decision, where the as-of line sits today: "Stats through week 6, plus 13 week 7 games, 2 in progress"
Snaps pending for 9 games." With zero games read the line is "Stats through week 6", as today. With nothing in
progress and nothing pending, the line stops after the games count. The finder page renders the same line. The
types gain the block, and a document without the block still renders.

**Blocked by:** 02 (The known-games week).

**Status:** done

- [ ] A document with 13 games read, 2 in progress, and snaps pending for 9 renders the full line.
- [ ] A document with zero games read renders "Stats through week 6".
- [ ] A document with games read and nothing in progress or pending renders the games count and stops.
- [ ] A document with no known-games block renders as today.
- [ ] The finder page shows the same line.
- [ ] The line passes the site's lint and the page test that pins no blurb text.

## Comments

Closes as done in the audit of `todoist-queue` on 2026-11-12. The work merged in 631f2395.
Proof: The merge "known-games-08: the as-of line shows the known games" is on `main`, and `analyze-result.test.tsx` pins the exact line "Stats through week 6, plus 13 week 7 games, 2 in progress · Snaps pending for 9 games".
Read 1 file: .scratch/todoist-queue/audit.md.
