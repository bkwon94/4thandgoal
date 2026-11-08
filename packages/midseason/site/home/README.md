# packages/midseason/site/home: the home parts of the midseason report

## Knows

- `Takeover`, the opener of the report, the title race, with a link to the report. It keeps the static grid, so the
  home page has no scene while the takeover holds its top.
- `takeoverOn`, true while the latest published week is at or before the takeover end week of the file.
- `ReportTile`, the one big fact of the file's tile and a link to the report, in the shape of the R3 tile.

## Ports

- The home part of the app, in `apps/site/src/app/_routes/midseason/home.tsx`, reads the file and the latest week.
- The href of the report, which the app builds.

## Does not do

- It computes no fact. The pipeline writes the tile into the midseason file.
- It reads no file, no env, and no config (ADR 0012).
- It adds no menu item and no dock item.
