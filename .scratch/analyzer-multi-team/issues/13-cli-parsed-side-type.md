# 13: A parsed-side type for the analyze CLI

**Repo:** `cornerstone-fantasy-sleeper-weekly-report`

**What to fix:** `cli._trade_side` returns `tuple[int, list[tuple[str, int | None]]]` and `_proposed_sides` takes that tuple. `cli._routed` picks between two text builders with a flag argument and repeats the "to Team" and "from Team" text of `analysis.trade_side_lines`. Give the parsed side a small type and let the CLI reuse the one text builder.

**Blocked by:** None (can start immediately)

**Status:** wontfix

- [ ] A named type holds the roster id and the given players with their destinations
- [ ] One builder makes the "to Team" and "from Team" lines for the CLI and the prompt

## Comments

Closes as wontfix in the audit of `todoist-queue` on 2026-11-12.
Proof: Manager brain c133eb89 (#25) deleted `_trade_side`, `_proposed_sides`, `_routed`, and the `analyze` command from `cli.py`.
Read 1 file: .scratch/todoist-queue/audit.md.
