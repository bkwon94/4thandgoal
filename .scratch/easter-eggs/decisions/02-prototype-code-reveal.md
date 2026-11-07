# 02: How an egg shows its code and keeps it secret

Map: `.scratch/easter-eggs/MAP.md`.

**Kind:** prototype

**Blocked by:** 01

**Status:** done

## Question

The repo is public, and each browser downloads the page JSON whole. Decide how the site shows an egg code only after the steps of the egg kind, with only a hash in the build. Decide how the pipeline makes each code, keeps it out of the repo, and gives it to Brian. A prototype of one hard egg kind shows if the method holds against a read of the source.

## Decision

Brian decided in the grill of 2026-11-06, in ticket 01, with no prototype. The egg code is gone: a manager taps an egg and claims it at once. The API keeps a secret list of eggs, each a page, a target, an action, and a letter. The bundle holds one generic listener that sends each fast multi-tap and long press to the API, with the page and the element. The API answers with a letter and a one-time claim token only for a match. Brian keeps `eggs.toml` outside the repo and sends it to the API with the passphrase that the API already uses. So neither the public repo nor the bundle names a spot, and an AI that reads the source learns only that multi-taps go to the API.
