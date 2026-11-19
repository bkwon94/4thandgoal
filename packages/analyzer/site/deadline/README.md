# packages/analyzer/site/deadline: the Deadline banner and the sheet of the Trade Wire

## Knows

- The Deadline banner of `deadline-banner.tsx`: the strip under the top band of each page during Deadline week. It shows "TRADE DEADLINE" over the countdown, the accent fill and the seconds in the last hours, and the passed line with the badge "Final" after the Lock. It goes away one day after the Lock.
- The whole banner is one button, the trigger of the shared sheet. The sheet holds the eyebrow with the countdown, the title "Trade Wire", and the list.
- The banner measures its height into `--deadline-banner-h`, so the band height token of `globals.css` grows by it.

## Ports

- The clock of the reader, `Date.now()`, read each second. The phase and the countdown come from `../lib/deadline.ts`.
- The shared sheet, through the sheet wrapper of the design package (ADR 0035, ADR 0037).

## Does not do

- It reads no file, no env, and no config, and it imports no app. The app passes the Lock of the client.
- It renders no countdown at build time, because the time of the build is not the time of the reader.
- Its copy never says "Lock" and never says "Rosters are locked". Copy says "trade deadline".
