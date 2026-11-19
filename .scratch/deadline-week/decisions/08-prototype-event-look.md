# 08: What do the banner, the deadline look, the board, and the feed look like?

Map: `.scratch/deadline-week/MAP.md`.

**Kind:** prototype

**Blocked by:** 03, 04

**Status:** done

## Question

Build several variations of the event: the Deadline banner with its countdown to the lock, the deadline look on the trade pages, the deadline board of needs and spares for each team, the live feed of trades, and the closed state after the lock. Use `ui-sdk`, scrolltide, transitions.dev, and the design skills of design-bar. Brian chooses on the phone at 390x660.

## Decision

Brian chose look `D · Final` on 2026-11-19, after three rounds on the phone. The prototype is on the branch `deadline-week-08-proto`: round 1 `d77ca1ab` (looks A Strip, B Clock, C Sheet), round 2 `ecb11e39` (look D), round 3 `48f18de1` (the polish). The code is in `apps/site/src/app/_routes/analyzer/deadline-proto/`. It stays off `main` as the primary source.

1. **No Deadline Board.** Brian: the needs and spares do not help enough, and the Finder answers "who can trade me an RB?" for one manager. The needs and spares of the prototype were a stub. The Spares tree stays for the give side of the Finder (decision 09).
2. **The Trade Wire is the event.** The Deadline banner holds a pill "Trade Wire" with a badge "N new". The whole Deadline banner is the ui-sdk sheet trigger (`@cpc/design/ui/sheet`). It opens the Trade Wire in a sheet from any page. Its accessible name is "Open the Trade Wire, 2 new trades". It has the pressed state of `transitions-dev` (scale 0.98, 150 ms, ease-out). The badge hides at 0 new trades.
3. **The sheet.** At its top sit two links, "Grade a trade" and "Find a trade". Each opens the analyzer in that mode of the switch of decision 07 (`?mode=grade`, `?mode=find`). Under them sit the eyebrow "TRADE DEADLINE ~2d 14h 05m", the title "Trade Wire", and a live dot with "Updated 4s ago" that ticks.
4. **Deadline week only.** The Trade Wire lists only the trades of week 11, newest first. No season history and no "New" mark. A new trade slides in at the top (400 ms, the smooth-out ease, 8 px, 2 px blur), and the badge changes in place. The empty line is "No trades yet this week." After the Lock with no trades: "No trades this week."
5. **The Deadline banner.** Two lines on one grid: the small eyebrow "TRADE DEADLINE", and the countdown "~2d 14h 05m". The tilde marks the estimate. The red dot sits in a gutter to the left of the one text edge. The top padding and the bottom padding are equal. No line "Monday night ... An estimate." anywhere.
6. **The last hours.** Under 3 h to the Lock, the Deadline banner takes the accent fill, shows the seconds, and shimmers. Reduced motion stops the shimmer.
7. **After the Lock.** The Deadline banner reads "The trade deadline has passed. Good luck in the playoffs." The badge reads "Final". The sheet hides the two trade links and lists the trades of the week.
8. **The analyzer.** Only the hero eyebrow changes: "Trade deadline ~2d 14h 05m", or "The trade deadline has passed" after the Lock. It sits above the switch of decision 07. No match line, because it needed the Deadline Board.
9. **Copy.** "Lock" stays an internal term in code and config. Copy says "trade deadline". Copy never says "Rosters are locked", because waivers and free agents still run after the trade deadline. Names take Title Case in copy: "Trade Wire".
10. **Both themes.** The Deadline banner and the sheet use the theme tokens only: open is `bg-card`, the last hours are `bg-accent`, closed is `bg-raised`.
11. **Even spacing.** Inside a trade, 8 px (`sp-2`) between the time line and each side row. Between trades, a 16 px pad, a 1 px rule, and a 16 px pad.
12. **Speed.** Brian wants the Trade Wire faster than decision 03. The Fly route keeps its answer for 5 s, not 30 s. The site polls every 10 s, not 60 s, and polls at once when the tab shows again. A trade shows about 5 to 15 s after Sleeper accepts it. Load on Sleeper: 12 calls per minute, under the limit of 1000.

Found on the phone, outside the prototype: a drag of the top of a sheet upward lifts the bottom edge of the sheet off the screen. The bug is in the shared `packages/design/site/ui/sheet.tsx`, so it hits every sheet.

Out: looks A, B, and C, the Deadline Board, the Trade Wire on the front door (B), and the board grid of needs against spares (C).
