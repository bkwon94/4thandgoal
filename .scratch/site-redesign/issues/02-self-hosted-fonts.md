# 02: Self-hosted fonts

Spec: `.scratch/site-redesign/PRD.md`. Acceptance tests AT-36.

**App:** site

**What to build:** The site loads Space Grotesk and JetBrains Mono from its own origin, as two Latin variable woff2 files of 53,660 bytes in total. The number columns stay aligned before the mono font loads.

**Blocked by:** none

**Status:** ready-for-agent

- [ ] Both fonts load with `next/font/local`, `display: "swap"`, and `preload: true`. JetBrains Mono has a Menlo or Courier New fallback face.
- [ ] Each font has its `OFL.txt` beside it.
- [ ] A check holds the byte budget of 56,000 in total, exactly two font files, and two font preloads on each page.
- [ ] The ban on `next/font` narrows to `next/font/google` and the outside font hosts.
- [ ] A real build of both clients, the fallback on iOS and Android, the cache headers of the Worker, and the layout shift are measured.
- [ ] The evidence of AT-36 is recorded in `EVIDENCE.md`.
