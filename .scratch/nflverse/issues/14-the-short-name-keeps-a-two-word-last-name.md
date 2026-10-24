# 14 — The short name keeps a two-word last name

Spec: none. Found in the ticket 09 review on 2026-10-24.

**What to build:** `last_name` in `src/cornerstone/names.py` takes the last word of the full name, so
"Amon-Ra St. Brown" becomes "Brown" in the trend reason. The helper keeps a last name of two words when the word
before the last is a short particle such as "St.", "Van", "De", or "Von". "Amon-Ra St. Brown" then shortens to
"St. Brown". `_short_names` in `src/cornerstone/adjusters.py` needs no change.

**Why:** "Brown" names a different player to every reader of the league.

**Blocked by:** None.

**Status:** done 2026-10-24

- [x] "Amon-Ra St. Brown" shortens to "St. Brown".
- [x] "Equanimeous St. Brown" and "Amon-Ra St. Brown" in one trade both show in full, as the shared-name rule says.
- [x] "Josh Jacobs" still shortens to "Jacobs". "Marvin Harrison Jr." still shortens to "Harrison".
- [x] Every existing names test passes unchanged.
