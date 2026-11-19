# 03: The live Trade Wire sheet

Spec: `.scratch/deadline-week/PRD.md`. Acceptance tests AT-5, AT-6, AT-18, AT-19, AT-20, AT-21, AT-22, AT-23, AT-24, AT-25, AT-27, AT-29, and AT-52.

**App:** site

**What to build:** The sheet that the Deadline banner opens shows the Trade Wire. From the top: "Grade a trade" and "Find a trade", the eyebrow "TRADE DEADLINE" with the countdown, the title "Trade Wire", a live dot with "Updated Ns ago" that ticks, and the trades of week 11 from the Trade Wire route. Each trade shows the time, each team with its avatar, the players it gets with positions, and any FAAB, with 8 px between rows and a 16 px pad, a 1 px rule, and a 16 px pad between trades. The site polls every 10 s while the tab shows, polls at once when the tab shows again, and stops at the Lock. A new trade slides in at the top, and the badge "N new" on the Deadline banner changes in place. The badge hides at 0. The empty line is "No trades yet this week.", or "No trades this week." after the Lock. A failed read keeps the last list and shows a short note. "Find a trade" shows only when the `finder` flag is on. Both links hide after the Lock. No Deadline Board page or link exists.

**Blocked by:** 01, 02

**Status:** ready-for-agent

- [ ] The Deadline banner has the name "Open the Trade Wire, N new trades", and the badge matches the count of the route.
- [ ] A new trade from the route shows at the top within 15 s, with the slide of transitions-dev, and no slide under reduced motion.
- [ ] No route call goes out while the tab hides, and one goes out within 1 s of the show.
- [ ] The empty lines, the failed read note, and the hidden links after the Lock show in a real browser.
- [ ] The gaps between rows and between trades are each even within 1 px, in both themes, at the four sizes.
