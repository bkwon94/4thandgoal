# 03: Does a rebuild match the published files

Map: `.scratch/trusted-green/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** open

## Question

The differential rebuild runs `build --no-fetch` for the latest published week of each client, then diffs the output against `clients/<slug>/published/`. Find out four facts. Does the output match byte for byte? Which parts differ, such as a time stamp or text that Claude writes? How long does one rebuild take on a CI runner? Which secrets does it need? If one rebuild takes more than 5 minutes, the job runs one client only.

## Decision

None yet.
