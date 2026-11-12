# 01: The page shell and the card look on every page

**What to build:** A league member on a tablet or a laptop sees every chapter on every page as a card on the grey body with an even gap, the look the weekly report has today. The home page, the rankings page, the analyzer page, and the week page render through one page shell that centers the page column, turns the main clear from the tablet tier, and spaces the chapters with the card gap. The week page passes its chapter rail to the shell and looks the same as today. The report scope attribute and the chapter variants that read it go away, so a chapter has one card rule for every page. On a phone every page stays the unbroken white page with the chapter rules. In the dark theme the cards take the dark partners of their tokens, as the report cards do.

**Blocked by:** None (can start immediately)

**Status:** done

- [x] One shared component, named for the glossary term page column, renders the three-track grid from the tablet tier and the main with the card gap. It takes an optional rail and the page content.
- [x] The week page renders through the shell with its rail. The week page tests pass unchanged: the nine chapters, the rail, the in-view mark, and the footer.
- [x] The home page, the rankings page, and the analyzer page render through the shell with no rail. Their tests pass unchanged.
- [x] The report scope attribute is gone from the week page, and no chapter variant reads it. The chapter's card look from the tablet tier holds on every page.
- [x] The waiver page is untouched.
- [x] The comment on the chapter part says a chapter is a card on every page from the tablet tier, not only in the report.
- [x] The glossary term page column still matches what the shell does. No new glossary term.
- [x] A browser check at 768 and 1280 shows the home page as three white cards with the card gap, the rankings page as one dark card on the grey body, and the week page unchanged. At 390 each page is unchanged.
- [x] `pnpm test`, `pnpm typecheck`, and `pnpm build` pass.

## Comments

Closes as done in the audit of `todoist-queue` on 2026-11-12. The work merged in dd18742a.
Proof: The commit "Add the page column shell and the card look on every page" merged in 94f52bea and then in 6486cff5 on `main`.
Read 1 file: .scratch/todoist-queue/audit.md.
