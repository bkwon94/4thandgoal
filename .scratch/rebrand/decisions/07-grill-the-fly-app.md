# 07: Does the API move to a new Fly app?

Map: `.scratch/rebrand/MAP.md`.

**Kind:** grill

**Blocked by:** 03

**Status:** wontfix

## Question

The Fly app is `cpcfantasy-api`, and Fly has no app rename. A new app needs a new volume, a copy of the eggs SQLite, and a move of the certificates, so the API can go down during the move. The other choice keeps `cpcfantasy-api` as an internal name that no manager sees. The research in `decisions/03-research-the-cutover.notes.md` advises to keep it.

## Decision

The Fly app keeps the name `cpcfantasy-api`. The domain stays, and no manager sees the app name. Brian decided it on 2026-11-11 with decision 02.
