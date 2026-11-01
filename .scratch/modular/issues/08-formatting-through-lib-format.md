# 08: Formatting through `lib/format/`

**What to build:** The format folder gains `record(wins, losses)`, `oneDecimal`, and one `count(n, one, many)`. The five inline record strings and the two test copies call `record`. The two `count` helpers and the local `oneDecimal` fold in. The standings points go through `num`. The three `metaLine` functions stay local with names that say what each builds.

**Blocked by:** 03

**Status:** done

- [ ] A grep for the inline record template finds only the helper.
- [ ] No component defines `count`, `oneDecimal`, or `metaLine` under that bare name.
- [ ] Each new helper has a unit test.
- [ ] `out/` has no diff against `main`, or the ticket names the standings line if `num` changes a trailing zero.

## Comments

- 2026-10-31: merged into `main` from branch `modular-08-format`, commits 51b8b19 and d5d88fe. 519 tests. The standings points keep `toFixed(2)`: `num` drops a trailing zero, and 2 of the 24 standings values in weeks 6 and 7 end in one, such as 698.30. The standings line is the one allowed diff, and it did not change because the old call stayed. Two reviewers passed it after one fix pass.
