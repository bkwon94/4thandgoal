# 08: Player news and the rumor guard

Spec: `.scratch/manager-brain/PRD.md`. Acceptance tests AT-12, AT-13, AT-14, AT-15, and AT-24.

**App:** pipeline

**What to build:** The Advisor knows the latest news of each trade player, and a rumor stays a rumor. On each call, code fetches the Sleeper news feed of each trade player and puts the newest 2 items of the last 7 days on the sheet as `NEWS.{player_id}.{n}` facts. Each fact reads "Reported on <YYYY-MM-DD> by <Source>: <description cut at 300 characters>", with no URL in the numbers. A cache in memory keeps the feed of a player for 1 hour, and a failed fetch gives no news and never stops the call. A code check makes a Bullet that cites news hold "reported", "report", "per", "according to", "rumor", or the source name, with one retry. The Jev faithfulness check and the Jev rumor check run log-only.

**Blocked by:** 02

**Status:** ready-for-agent

- [x] A press with Jonathan Taylor gives at most 2 `NEWS.6813.` facts, each from the last 7 days, newest first.
- [x] Every Bullet of the eval that cites news names the report.
- [x] With the feed host blocked, `/analyze` returns a read with no news fact.
- [x] A second press within 1 hour fetches no news for the same player.
- [x] The log holds the result of both Jev checks, and no read is blocked by them.
- [x] `make check-fast` passes.
