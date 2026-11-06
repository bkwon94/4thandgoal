# 02: How does the site load web fonts with no loss of speed?

Map: `.scratch/site-redesign/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** done

## Question

The look uses web fonts in place of the system Helvetica. The site has speed work behind it, in `.scratch/site-speed/`. Find how a static Next.js export loads a font with no layout shift and no slow first paint: self-host or Google Fonts, `next/font`, subsets, and `font-display`. Check the license of each candidate font. The spec needs the load method and its cost in bytes.

## Decision

The site self-hosts the two fonts with `next/font/local`: one Latin variable woff2 file each, with `display: "swap"` and `preload: true`. The two files cost 53,660 bytes: Space Grotesk 22,320 and JetBrains Mono 31,340. The variable files are smaller than the static files. Both fonts use the SIL Open Font License 1.1, so self-host is allowed, and each `OFL.txt` sits next to its font file.

JetBrains Mono sets `adjustFontFallback: false` and gets a Menlo or Courier New fallback face, because the default Arial fallback breaks the number columns. `brand-tokens.test.ts` bans the text `next/font` now. The ban narrows to `next/font/google` and the outside font hosts. New checks hold a byte budget of 56,000 in total, exactly two font files, two font preloads on each page, and an `OFL.txt` for each font.

The build ticket still proves four points: a real build of both clients, the fallback on iOS and Android, the cache headers of the Worker, and a measure of the layout shift.

Notes: `decisions/02-research-web-fonts-without-speed-loss.notes.md`. Claude decided from the research, 2026-11-05. The fonts follow ticket 03; if the look changes its type pair, this decision runs again for the new pair.
