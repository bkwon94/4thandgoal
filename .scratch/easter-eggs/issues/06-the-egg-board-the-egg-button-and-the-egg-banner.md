# 06: The egg board, the egg button, and the egg banner

Spec: `.scratch/easter-eggs/PRD.md`. Acceptance tests AT-40, AT-41, AT-42, AT-43, AT-44, AT-45, AT-46, AT-47, AT-48, and AT-50.

**App:** site

**What to build:** A manager follows the hunt from any page. The egg button in the top band shows the count left and opens `/eggs/`. The egg banner on the home page names the day of the last egg drop. The egg board has the hero with the grid of 54 eggs, one card per egg word, the "Latest claims" feed, and "How the hunt works", as on the canvas of ticket 08.

**Blocked by:** 01, 02

**Status:** in-review

- [x] The egg button sits beside the theme button on every page of a client with the package. Its badge is the count left to find, and a tap opens `/eggs/`.
- [x] The egg banner reads "6 eggs dropped today · 6 left" on the day of the drop, then "6 eggs dropped Tue · 5 left". A hide stays after a reload until the next drop.
- [x] The hero shows the counts left to find, found, and to drop, over 54 slots that are white, red, or dashed.
- [x] One card per egg word shows its gift card value, its leader, the top 5, and "Show all 11". A won egg word is a hero card with a WON stamp.
- [x] "Latest claims" shows the manager, the letter, and the egg word, with no page, no spot, and no block. "How the hunt works" ends the page.
- [x] Before the first drop, the board shows three empty egg words and 54 to drop.
- [ ] The copy has no "rival", no name of the commissioner, and no hint. The readability floor passes on the board and the banner.
