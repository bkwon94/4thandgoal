# 06: Where does the Jev log live, and in what format?

Map: `.scratch/jev/MAP.md`.

**Kind:** spec

**Blocked by:** 03

**Status:** done

## Question

Each Jev check writes its answers, the Claude verdict when Claude ran, and the route that the cascade took.
The spec chooses the file, likely beside `verify.json` in `clients/<slug>/build/<season>/`, and its fields.
The weekly `publish` may stage `clients/<slug>/build/<season>/`, so a file there can ship with the week.

Research 01 adds two items for the spec. The build must save the text of each failed attempt, so real labels build up for the cascade. A code check for the word "drop" catches 2 of the 6 escapes at 0.8.

## Decision

The spec records it under The saved data. `VerifyResult` gets the optional fields `sentences` and `jev`, saved in `verify.json` for each attempt. No new file. Brian approved the spec on 2026-11-09.
