# 16 — The expected points round half up

Spec: `.scratch/nflverse/PRD.md`, "Expected points". Found in the ticket 03 review on 2026-10-24.

**What to build:** `src/cornerstone/nflverse_expected.py` rounds the expected points and the mean gap with
`round(float, 2)`. Python rounds a float half to even on its binary value, so 16.805 can show 16.80. The module
rounds through `Decimal` with `ROUND_HALF_UP`, as the rest of the facts do, so a half rounds up every time.

**Why:** A reader who checks the award math against the file sees a cent off.

**Blocked by:** None.

**Status:** done 2026-10-24

- [x] An expected value of 16.805 rounds to 16.81.
- [x] A mean gap of 5.125 rounds to 5.13.
- [x] Every existing expected points test passes unchanged.
