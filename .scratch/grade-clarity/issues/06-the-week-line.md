# 06: The Week line

Spec: `.scratch/grade-clarity/PRD.md`. Acceptance tests AT-5, AT-11, AT-12, AT-13, AT-14, AT-17, AT-18, and AT-34.

**App:** both

**What to build:** Each side of a grade gets a Week line for the trade week and the next week, in a box "This week and next" on its card. For each position the trade touches, the line counts the players of the side who play, are not out, and rank above the line, before and after. It names the opponent of each player the side gets with its rank, each bye, and each player who is out. It never moves the letter. The verdict can name it.

**Blocked by:** 01, 02, 05.

**Status:** ready-for-agent

- [ ] Each side of the document holds `week_lines`, a list of `{week, text}` for the trade week and the next week only.
- [ ] Out counts in the trade week only. IR, PUP, NA, and Sus, out for the season, and a return week after the next week count in both weeks. Questionable and Doubtful never count.
- [ ] A grade on a Tuesday or a Wednesday says "listed Out last week".
- [ ] The fact sheet holds one Week line fact for each side. No factor is a Week line row.
- [ ] A three-side trade gives three sides with Week lines.
- [ ] The side card shows the box "This week and next" between the bullets and the fold.
- [ ] `make check-fast` passes at the root.
