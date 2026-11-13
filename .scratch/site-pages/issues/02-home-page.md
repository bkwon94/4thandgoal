# 02: The home page per tier

**What to build:** A league member on a tablet or a laptop opens the home page and sees the Tools card and the Power Rankings card side by side in one row, with the Weekly Reports card under them at the full width. The row has the card gap between the two cards and above and below it. On a phone the three chapters stack with the chapter rules, as today. With no rankings file the Tools card is alone in the row and takes the full width. Each chapter label is a level-two heading in title case: "Tools", "Power Rankings", "Weekly Reports". The rankings lead reads "Top Three". The week list stays one week per row, newest first, and the rows reveal as today.

**Blocked by:** 01 (The page shell and the card look on every page)

**Status:** done

- [x] From the tablet tier the Tools chapter and the Power Rankings chapter sit in a two-column row with the card gap. On a phone they stack with the chapter rule.
- [x] The row is one child of the main, so the main's card gap applies above and below it.
- [x] With no rankings file the Tools chapter takes the full width of the row.
- [x] The Weekly Reports chapter sits under the row at the full width, one week per row, newest first.
- [x] The three labels are level-two headings with the text "Tools", "Power Rankings", and "Weekly Reports".
- [x] The rankings lead reads "Top Three".
- [x] The reveal steps of the rows are unchanged.
- [x] The home page test checks the three level-two headings in order, the "Top Three" lead, the analyzer link before the weeks, and the Tools chapter with no rankings file. Tests that read "Weekly reports" or "Top three" change with the casing.
- [x] A browser check at 768 and 1280 shows the row of two cards and the list under it. At 390 the page is unchanged.
- [x] `pnpm test`, `pnpm typecheck`, and `pnpm build` pass.

## Comments

Closes as done in the audit of `todoist-queue` on 2026-11-12. The work merged in e753f56e.
Proof: The commit "Put the two short home chapters in one row from the tablet tier" merged in 77173fb4 and 6486cff5; the front door (dc564361) replaced the home page later.
Read 1 file: .scratch/todoist-queue/audit.md.
