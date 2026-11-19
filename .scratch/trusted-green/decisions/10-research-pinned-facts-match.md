# 10: Do pinned inputs give the same facts

Map: `.scratch/trusted-green/MAP.md`.

**Kind:** research

**Blocked by:** 09

**Status:** done

## Question

A facts diff needs the facts of a week to be the same on each build. Pin three inputs: the nflverse extract of the week, the build clock from `verify.json`, and the research lists of the saved `facts.json`. Build the facts of week 10 two times for each client and compare them. Find out if they match, which values differ if not, and what the build must change to pin each input, such as a CLI option for `started` or a saved degraded extract.

## Decision

Research on 2026-11-18. Notes: `decisions/10-research-pinned-facts-match.notes.md`.

With the inputs pinned, two builds of week 10 give the same `facts.json` byte for byte for cpc and norcal, across processes, hash seeds, and time zones, in about 4 s per client. The ticket missed two inputs: the slow-source nflverse cache that `load_slow_sources` reads, and the live Sleeper news of one player per client.

Per decision 09, the match puts the facts diff in spec 1. The build needs five changes, and ticket 11 sets them:

1. The clock from `verify.json`, or a `--started` option.
2. A saved `raw/nflverse.json` on each build, also a degraded one, committed. About 680 KB per client per week.
3. The slow-source values saved into the week folder. A commit of the whole cache is about 24 MB a week.
4. A research call that reuses the saved claims, with no Claude call.
5. The Sleeper news saved into `raw/`.

The committed week 10 cannot pass, because its build had a degraded extract and saved none. The first week that can pass is the first one built after changes 2, 3, and 5.
