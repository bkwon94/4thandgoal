# 07: The design package

Spec: `.scratch/clients/PRD.md`. Acceptance tests AT-16.

**App:** site

**What to build:** The primitives, the parts, the shell, and the usage count move into the `design` package. The menu takes its items, its labels, and one layout from `[menu]` of `client.toml`.

**Blocked by:** 03, 04

**Status:** ready-for-agent

- [x] The `design` package holds the modules of decision 01 and the usage count.
- [x] The shell has the three menu layouts `hamburger`, `bar`, and `tabs`. With no `items`, the menu takes the package list in its order.
- [x] The CPC menu keeps its hamburger, its items, and its labels.
- [x] A test client with the layout `bar` shows a bar (AT-16).
- [x] The site loads the count script only when `usage_code` is set.
