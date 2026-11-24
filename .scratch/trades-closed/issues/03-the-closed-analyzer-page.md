# 03: The closed analyzer page

Spec: `.scratch/trades-closed/PRD.md`. Acceptance tests AT-1, AT-2, AT-3, AT-4, AT-5, AT-8, AT-11, AT-13, AT-15, AT-19, AT-25, and AT-26.

**App:** site.

**What to build:** A site build of a client with Trades closed leaves out the "Trade Analyzer" menu item, the analyzer row of the home tools, and the analyzer line of the Site answer. It writes the closed page at `/analyze/` in place of the analyzer page. The closed page has the top band, the line "The trade deadline has passed. Trades open again next season.", and one link to Home. It does not read the query, so each old link of the analyzer gives the same page. The page uses the design parts and ui-sdk per ADR 0037. An analyzer page from a build before the close shows the `line` of the 410 reply in place of a grade. The analyzer code stays: a build with a future `lock` has the analyzer again. The weekly trade cards and the transaction history of each manager page do not change.

**Blocked by:** 01, 02

**Status:** ready-for-agent

- [ ] A `cpc` build made today has no "Trade Analyzer" in the menu (AT-1) and no analyzer home tool in the generated registry (AT-2).
- [ ] `/analyze/`, the prefill link `/analyze/?team=3&with=6&give=5045&get=8151`, and `/analyze/?mode=find` each show the closed page in WebKit at 375, 768, and 1280 px, both themes, and pass the iPhone 15 check (AT-3, AT-4, AT-5).
- [ ] With the browser clock at 20:00 Eastern on 2026-11-23, `/analyze/` still shows the closed page (AT-26).
- [ ] The Site answer of a closed `cpc` build lists no analyzer line (AT-8).
- [ ] A press of Grade the Trade on a page from before the close shows the closed line from the 410 (AT-15).
- [ ] A `norcal` build made today keeps the menu item and the analyzer (AT-19). A `cpc` build with a future `lock` in a scratch copy has the analyzer again (AT-25).
- [ ] The week 10 page still shows each of its trade cards, and the manager page of roster 1 still shows 2 trades (AT-11, AT-13).
