# 05: Is the plugin the full Product name or a short form?

Map: `.scratch/rebrand/MAP.md`.

**Kind:** spec

**Blocked by:** 02

**Status:** done

## Question

The plugin `cpc` has the same name as the client `cpc`. Brian types the plugin name in each skill call, such as `cpc:plan`. The spec sets the plugin name: the Product name, or a short form of it.

## Decision

The plugin is `4ag`, and its marketplace is `4ag-local`. Brian decided it on 2026-11-11.

- The skills become `4ag:plan`, `4ag:implement`, and so on. The name no longer clashes with the client `cpc`.
- `claude plugin validate` passed a test plugin named `4ag` on 2026-11-11.
- The verdict marker `<!-- cpc:agent -->` in `scripts/verdict.py` stays, because old PR comments hold it.
