# 08: Formatting through `lib/format/`

**What to build:** The format folder gains `record(wins, losses)`, `oneDecimal`, and one `count(n, one, many)`. The five inline record strings and the two test copies call `record`. The two `count` helpers and the local `oneDecimal` fold in. The standings points go through `num`. The three `metaLine` functions stay local with names that say what each builds.

**Blocked by:** 03

**Status:** ready-for-agent

- [ ] A grep for the inline record template finds only the helper.
- [ ] No component defines `count`, `oneDecimal`, or `metaLine` under that bare name.
- [ ] Each new helper has a unit test.
- [ ] `out/` has no diff against `main`, or the ticket names the standings line if `num` changes a trailing zero.
