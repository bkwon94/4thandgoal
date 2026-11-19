# 01: The Lock and the Deadline banner

Spec: `.scratch/deadline-week/PRD.md`. Acceptance tests AT-1, AT-2, AT-3, AT-4, AT-7, AT-8, AT-9, AT-10, AT-11, and AT-50.

**App:** site

**What to build:** During Deadline week, every page of the CPC site shows the Deadline banner under the top band. It reads "TRADE DEADLINE" over a countdown with a tilde, such as "~2d 14h 05m". Under 3 h to the Lock it takes the accent fill, shows seconds, and shimmers, unless the reader prefers reduced motion. After the Lock it reads "The trade deadline has passed. Good luck in the playoffs." with the badge "Final". One day after the Lock it goes away by itself. The Lock is one value in the client config of CPC, 00:00 Eastern on Tue 2026-11-24. Norcal has no Lock and no Deadline banner. The whole Deadline banner is one button, the trigger of the shared sheet through its wrapper, with the press state of transitions-dev. In this ticket the sheet holds the eyebrow, the title "Trade Wire", and the empty line only. Ticket 03 fills it. Copy says "trade deadline", never "Lock". The fills use the theme tokens only, and the top band grows to fit the Deadline banner on each page, the front door too.

**Blocked by:** none

**Status:** ready-for-agent

- [x] One pure function of the time and the Lock gives the state (open, last hours, closed, ended) and the countdown text, with tests at the edges: 3 h before, the Lock, and one day after.
- [x] The Deadline banner shows on each CPC page in both themes, with equal top and bottom padding and one left edge for both lines.
- [x] The Deadline banner is one button with the name "Open the Trade Wire" and opens the shared sheet.
- [x] Norcal shows no Deadline banner.
- [x] The WebKit check passes at 390 by 660, 810 by 980, 1080 by 740, and 1280 by 800, with no horizontal scroll and no overlap.
- [x] The front door Tour still shows in full, with no overlap by the Deadline banner, on the first visit.
