# packages/analyzer/site/deadline: the Deadline banner and the sheet of the Trade Wire

## Knows

- The Deadline banner of `deadline-banner.tsx`: the strip under the top band of each page during Deadline week. It shows "TRADE DEADLINE" over the countdown, the accent fill and the seconds in the last hours, and the passed line with the badge "Final" after the Lock. It goes away one day after the Lock.
- The whole banner is one button, the trigger of the shared sheet. Its name is "Open the Trade Wire, N new trades", and its badge "N new" counts the trades of the week. The badge hides at 0 and reads "Final" after the trade deadline.
- The sheet of `wire-sheet.tsx` holds, from the top: "Grade a trade" and "Find a trade", the eyebrow with the countdown, the title "Trade Wire", the live dot with "Updated Ns ago", and the trades. "Find a trade" shows only when the app passes its link. Both links hide after the trade deadline.
- Each trade shows its time in Eastern, each team with its avatar, the players it gets with positions, and any FAAB. A new trade slides in at the top, with no slide under reduced motion.
- The empty line is "No trades yet this week.", or "No trades this week." after the trade deadline. A failed read keeps the last list and shows "The last update failed."
- The banner measures its height into `--deadline-banner-h`, so the band height token of `globals.css` grows by it.

## Ports

- The clock of the reader, `Date.now()`, read each second. The phase and the countdown come from `../lib/deadline.ts`.
- The shared sheet, through the sheet wrapper of the design package (ADR 0035, ADR 0037).
- The Trade Wire route, `GET /clients/<slug>/deadline/trades`, through `../lib/use-trade-wire.ts`. It polls each 10 s while the tab shows, reads at once when the tab shows again, sends no call while the tab hides, and stops at the trade deadline after one last read.
- The league passphrase in local storage, sent with each read.

## Does not do

- It reads no file, no env, and no config, and it imports no app. The app passes the Lock of the client, the API target, and the two trade links.
- It has no Deadline Board and links to none.
- It renders no countdown at build time, because the time of the build is not the time of the reader.
- Its copy never says "Lock" and never says "Rosters are locked". Copy says "trade deadline".
