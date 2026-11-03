# 08: The nflverse and nflverse_usage modules import each other

**What to build:** The two modules import each other as modules, with a comment in each that says why. One direction goes: `nflverse_week` in `nflverse.py` calls the usage readers, and the usage readers import the row helpers and the id map from `nflverse.py`. Move the shared row helpers and the id map into a small module both import, or pass them in, so the import goes one way. No behavior change. The suite stays green.

**Blocked by:** None (can start immediately). Found in the ticket 02 review on 2026-10-23.

**Status:** done

- [x] `nflverse_usage.py` does not import `nflverse.py`, or the reverse, and neither comment about the cycle remains.
- [x] The suite passes with no test change beyond import paths.
