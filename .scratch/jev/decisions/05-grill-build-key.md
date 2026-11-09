# 05: Which key does the weekly build use?

Map: `.scratch/jev/MAP.md`.

**Kind:** grill

**Blocked by:** none

**Status:** open

## Question

Brian has two TypeSafe keys: one for the app and one for local use. `~/.secrets` holds the local key as `TYPESAFE_API_KEY`.
The weekly build runs on Brian's Mac through launchd, and `apps/pipeline/bin/cornerstone-build` sources `~/.secrets`. So the build uses the local key now.
With one key, the cost of the build mixes with the cost of local tests in the TypeSafe console.

Choose which key the build uses, and how the build gets it.

## Decision

None yet.
