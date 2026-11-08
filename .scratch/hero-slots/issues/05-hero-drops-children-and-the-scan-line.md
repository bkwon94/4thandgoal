# 05: `Hero` drops `children` and the scan line

Spec: `.scratch/hero-slots/PRD.md`. Acceptance tests AT-2, AT-3, AT-4, AT-14, and AT-39.

**App:** site

**What to build:** All 11 heroes use the slots, so `Hero` stops accepting free content and the inconsistency cannot come back. The scan line goes. The six first heroes share one title style, one eyebrow style, and one meta style.

**Blocked by:** 02, 03, and 04

**Status:** ready-for-agent

- [ ] A test passes `children` to `Hero` under `@ts-expect-error`, and the typecheck passes (AT-14).
- [ ] The title of each of the six first heroes measures 40px and weight 300 (AT-2).
- [ ] Each eyebrow has the same computed font, size, case, tracking, and color (AT-3).
- [ ] Each meta line is 16px and takes two lines or fewer at 375 px (AT-4).
- [ ] No hero shows a scan line on entry, and the global stylesheet holds no scan-line rule (AT-39).
- [ ] `make check-fast` passes.
