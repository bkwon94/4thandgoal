# 01: Tiers and the page column

**What to build:** A league member opens any page on a phone, a tablet, or a laptop and gets a page column sized for the tier: full width with the gutter under 640px, 640px from 640px, 720px from 1024px. The masthead spans the viewport at every tier, with its content aligned to the column. From the tablet tier up the body background and the column background differ, so the column reads as the report's page. The tiers and the column widths are named tokens in the theme, so the later features build on them. The 480px tier that folds the wide tables stays. No page changes its content.

**Blocked by:** None (can start immediately)

**Status:** done

- [ ] The theme names three tier tokens: phone, tablet from 640px, desktop from 1024px, on Tailwind's defaults.
- [ ] The theme names the page column width per tier. The desktop width is 720px, the tablet width 640px.
- [ ] At 390 by 844 every page looks as it does today: the column fills the width with the gutter, and there is no sideways scroll.
- [ ] At 768 by 1024 the column is 640px wide and centered, and the masthead spans the viewport with its content aligned to the column.
- [ ] At 1280 by 800 the column is 720px wide and centered, and the masthead spans the viewport with its content aligned to the column.
- [ ] From the tablet tier up the body background and the column background differ.
- [ ] The 480px tier still folds the rankings table and the wide week tables on a phone.
- [ ] The existing tests pass. The build and the export check pass.
- [ ] Checked with agent-browser at 390 by 844, 768 by 1024, and 1280 by 800 with reduced motion on. Screenshots in the feature folder.

## Comments

Closes as done in the audit of `todoist-queue` on 2026-11-12. The work merged in be975af5.
Proof: The commit "Size the page column per tier and span the masthead" merged in a5559600 on `main`.
Read 1 file: .scratch/todoist-queue/audit.md.
