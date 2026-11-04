# 02: The pipeline reads the CPC client folder

Spec: `.scratch/clients/PRD.md`. Acceptance tests AT-1, AT-2, AT-19, AT-20, AT-21, and AT-22.

**App:** pipeline

**What to build:** The pipeline builds a CPC week from the CPC client folder, not from the League config. The sizes come from the Sleeper League settings. A build with no client slug or with a bad `client.toml` fails with a plain message.

**Blocked by:** 01

**Status:** ready-for-agent

- [x] The CPC client folder holds `client.toml`, `copy.toml`, `prompts/`, and `data/` with the history and the raw weeks. The values are those of the spec.
- [x] The shared NFL data and the Returns file sit in the root NFL data folder, outside each client.
- [x] The Sleeper adapter maps each season into the League settings: the sizes, the reception points, and the median game. Each derived CPC value equals the old League config value (AT-2).
- [x] The League config, `owner_username`, `is_owner`, `display_name`, and `prompts_dir` go away. `seller_gap` and `shootout_top` move into the tunables that read them.
- [x] `page.json` has no `is_brian` key. The golden files change by that key only (AT-1).
- [x] The week build with no client slug exits non-zero and names the client slug (AT-19).
- [x] The pydantic model of the client values exports a JSON Schema file. The check fails on an unknown key (AT-20), on a menu item for an omitted package (AT-21), and on a stale schema file (AT-22).
- [x] ADR 0022 adds `data/` to its tree.
