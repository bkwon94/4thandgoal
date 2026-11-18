# 10: Do pinned inputs give the same facts

Map: `.scratch/trusted-green/MAP.md`.

**Kind:** research

**Blocked by:** 09

**Status:** open

## Question

A facts diff needs the facts of a week to be the same on each build. Pin three inputs: the nflverse extract of the week, the build clock from `verify.json`, and the research lists of the saved `facts.json`. Build the facts of week 10 two times for each client and compare them. Find out if they match, which values differ if not, and what the build must change to pin each input, such as a CLI option for `started` or a saved degraded extract.

## Decision

None yet.
