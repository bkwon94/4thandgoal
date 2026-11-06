# packages/midseason/site/report: the midseason report page

## Knows

- `MidseasonScreen`, the whole page: the top band, the chapter rail, the opener, then the three acts on one scroll.
- The opener, the title race: the title odds of the leaders and the record leader's odds and place. Its "See the sim"
  link jumps to the finale, and it shows only when the app passes a finale.
- Each act: its dark title page on the hero surface, then its chapters in the order of the file.
- The chapter rail: one link per act, sticky under the top band at every width.
- The part of each chapter by its key, in `chapter-part.tsx`. A chapter with no part shows its title and its prose.
- The frame of a chapter, its prose, and the number formats of the report.
- A long list: its first 5 rows, then a "Show all" button, in `show-all.tsx`.

## Ports

- The route of the app, in `apps/site/src/app/_routes/midseason/`, reads the file and passes the report in.
- The children of `MidseasonScreen`: the finale at the end of the last act, where the app mounts the sim replay. The
  screen wraps it in a frame with the id `sim`, the target of "See the sim".

## Does not do

- It computes no fact. The pipeline writes each fact into the midseason file.
- It reads no file, no env, and no config, and it calls no loader (ADR 0012).
- It imports no sim. The app passes the replay in as a child.
