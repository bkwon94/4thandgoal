# 09: What the differential rebuild diffs

Map: `.scratch/trusted-green/MAP.md`.

**Kind:** grill

**Blocked by:** 03

**Status:** done

## Question

Ticket 03 shows that a full rebuild is not deterministic and needs two secrets, while `page-json` matches the published week byte for byte in 2 s. Brian decides what the job diffs: the render of the saved facts only, or also the facts, which needs a pinned snapshot of the nflverse data in git.

## Decision

Brian chose C on 2026-11-18.

Spec 1 diffs the render: `page-json` for the latest published week of each client, compared with `clients/<slug>/published/`. It takes about 10 s and needs no secret. It guards the code of `page.json`, `topics.json`, and `waiver.json`.

The facts diff waits on research ticket 10. That run pins three inputs (the nflverse file, the clock from `verify.json`, and the saved research lists), builds the facts of week 10 two times today, and compares them. A match puts the facts diff in spec 1. A mismatch names the next input that changes.
