# 05: Which key does the weekly build use?

Map: `.scratch/jev/MAP.md`.

**Kind:** grill

**Blocked by:** none

**Status:** done

## Question

Brian has two TypeSafe keys: one for the app and one for local use. `~/.secrets` holds the local key as `TYPESAFE_API_KEY`.
The weekly build runs on Brian's Mac through launchd, and `apps/pipeline/bin/cornerstone-build` sources `~/.secrets`. So the build uses the local key now.
With one key, the cost of the build mixes with the cost of local tests in the TypeSafe console.

Choose which key the build uses, and how the build gets it.

## Decision

Brian decided on 2026-11-09. The weekly build uses the local key, `TYPESAFE_API_KEY` in `~/.secrets`, which `cornerstone-build` already sources. The check is log only, and the cost is under $0.003 a week, so a separate key adds nothing now. The app key goes to Fly when the API first calls Jev.
