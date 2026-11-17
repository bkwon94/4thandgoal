# The analyzer counts an injury only for Out or Doubtful

Kind: quick-win
Status: done
Branch: `win-injury-out-doubtful`.
Source: the session of 2026-11-17.
Boundary: holds. 3 items of one kind; no new term or ADR; no moved seam; each done condition is one sentence.

## Items

### 1. The injury Measure reads only Out and Doubtful of the trade week

Done condition: The injury Measure reads against a side only for a player it gets who is out for the season, on IR, PUP, NA, or Sus with no near return, or listed Out with no near return or Doubtful by the NFL game status of the trade week, so a Sleeper Out or Doubtful with no NFL game status for the trade week, an Out with a near return, a Questionable status, or a count of injury report weeks never counts.
Method: tdd
Red: at `7c7085aa`, `uv run --exact --package cornerstone pytest -q -p no:xdist apps/pipeline/tests/test_measures.py -k test_injury_counts_only_an_out_or_doubtful`

```text
FAILED apps/pipeline/tests/test_measures.py::test_injury_counts_only_an_out_or_doubtful_of_the_trade_week_and_a_sleeper_out_of_no_near_return[sleeper out with no returns row and no trade week report never counts]
FAILED ...[trade week report Doubtful counts]
FAILED ...[trade week report Out with a near return never counts]
FAILED ...[a count of past report weeks alone never counts]
4 failed, 3 passed, 207 deselected
E  AssertionError: assert 'Golden is ou...week on file.' == 'Freiermuth i...week on file.'
E    + Golden is out with no return week on file.
E  AssertionError: assert 'No player it...njury report.' == 'Freiermuth i...ul in week 6.'
E    + No player it gets is out for long or often on the injury report.
E  AssertionError: assert 'Golden was o...5 of 5 weeks.' == 'Freiermuth i...week on file.'
E    + Golden was on the injury report in 5 of 5 weeks.
```

Green: at `2e978737`, `uv run --exact --package cornerstone pytest -q -p no:xdist apps/pipeline/tests/test_measures.py -k test_injury_counts_only_an_out_or_doubtful`

```text
.......                                                                  [100%]
7 passed, 207 deselected in 1.04s
```

Test verdict: PASS

### 2. The injury facts name only Out and Doubtful

Done condition: The injury fact of the trade fact sheet and of the sell high sheet names an injury only as the rule of item 1 reads it, gives the latest NFL practice status of the trade week in place of a Sleeper Out that has no NFL game status yet, and holds no count of injury report weeks.
Method: tdd
Red: at `d02c82e9`, `uv run --exact --package cornerstone pytest -q -p no:xdist apps/pipeline/tests/test_measures.py -k test_the_injury_facts_name_only`

```text
FAILED ...[a stale sleeper out with no trade week row says the status is from the last game]
FAILED ...[a stale sleeper out with a practice row gives the practice status]
FAILED ...[a trade week Questionable is a plain status]
FAILED ...[a trade week Doubtful counts]
FAILED ...[a sleeper IR with no near return counts]
FAILED ...[past report weeks alone give no count]
6 failed, 214 deselected
E  + Matthew Golden is listed Out now, with no return week on file.
E  + Matthew Golden has no injury status now. He was on the NFL injury report in 5 weeks this season before the trade.
```

Green: at `c3da67a6`, `uv run --exact --package cornerstone pytest -q -p no:xdist apps/pipeline/tests/test_measures.py -k test_the_injury_facts_name_only`

```text
6 passed, 214 deselected in 0.88s
```

Test verdict: PASS

### 3. The Week line reads the NFL game status of the trade week

Done condition: The Week line reads a player as out in the trade week for an NFL game status of Out or Doubtful, and never for a Sleeper Out or Doubtful with no NFL game status for the trade week.
Method: tdd
Red: at `ca308bcb`, `uv run --exact --package cornerstone pytest -q -p no:xdist apps/pipeline/tests/test_week_line.py -k test_the_week_line_reads_the_nfl_game_status`

```text
FAILED ...[sleeper out with no game status for the trade week]
FAILED ...[sleeper out with a trade week Questionable]
FAILED ...[trade week Out]
FAILED ...[trade week Doubtful]
4 failed, 2 passed, 33 deselected
E  AssertionError: assert ('stay at 2.' in 'Week 9: WRs in the top 36 who play stay at 1. ... Egbuka, Samuel and Nacua are listed Out.')
E  AssertionError: assert ('stay at 1.' in 'Week 9: WRs in the top 36 who play stay at 2. ... Egbuka and Samuel are listed Out.')
```

Green: at `b94c3ec4`, `uv run --exact --package cornerstone pytest -q -p no:xdist apps/pipeline/tests/test_week_line.py -k test_the_week_line_reads_the_nfl_game_status`

```text
6 passed, 35 deselected in 1.00s
```

Test verdict: PASS

## Comments

- Item 3 reverses rule 4 of `.scratch/grade-clarity/decisions/02-research-depth-chart-freshness.md`, "Questionable and Doubtful never count", for Doubtful only.
- Brian, 2026-11-17: the status must be the one of the current week. An Out from the last week needs the reports of this week. The snapshot holds the NFL injury report by week (`Snapshot.injuries`), and `week_line.py` already marks Tuesday and Wednesday as the days of a stale Out (`LAST_GAME_DAYS`).
- Brian, 2026-11-17: an Out with a near return stays news, with no mark. The NFL practice status fills the days before the game status. Source: the nflverse file `injuries_<season>.csv.gz` (`INJURIES_URL`), from the NFL injury API.
- The case of Brian: Kenneth Walker III, Sleeper id `8151`, KC. He missed week 10 and news has him back in week 11. On 2026-11-17 the Sleeper file has him `Out` (groin), and `data/nfl/2026/returns.json` has no row for him. Today the injury Measure reads him against the side that gets him: "out with no return week on file". His Out must not count in the trade. Build the red test of item 1 on this case.
- Closes with the squash merge of the PR of `win-injury-out-doubtful`. Commits: `7c7085aa`, `2e978737`, `d02c82e9`, `c3da67a6`, `ca308bcb`, `1c905439`, `b94c3ec4`. Date: 2026-11-17.
  The loop of each item went red, then green, and the quick Judge gave PASS to all 3 items; at the last item the pipeline suite had 1698 passed, the API suite 581, and the analyzer package 30.
  Later: `analyze-response.json` in the API tests and the site fixtures still holds the old fact text "listed Questionable now, with no return week on file", and the Measure text "out for long or often" still says "often".
  Later: the nflverse file has no practice day, so the practice fact names the week only; `.scratch/stakes/pipeline/research.md` still lists the removed `INJURY_WEEKS`.
  Read 12 files: AGENTS.md, docs/agents/issue-tracker.md, docs/adr/0033-a-quick-run-skips-the-spec-flow.md, GLOSSARY.md, .claude/plugin/skills/quick/format.md, .claude/plugin/skills/quick/judge.md, .claude/plugin/skills/implement/build.md, packages/analyzer/python/src/analyzer/measures.py, packages/analyzer/python/src/analyzer/trade_facts.py, packages/analyzer/python/src/analyzer/week_line.py, packages/league/python/src/league/nflverse.py, .scratch/grade-clarity/decisions/02-research-depth-chart-freshness.notes.md.
