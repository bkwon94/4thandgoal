# 10: Prompt caching on every Claude call

**What to build:** Every Claude call in the tool marks its system prompt as a cache prefix, so the second and later calls with the same prompt files pay the cache read price instead of the full input price. The analyzer call keeps its prefix warm for an hour, because trade requests come minutes apart. The writer and the verifier keep the default five minutes, because the Tuesday build runs their calls back to back. A log line per call shows the cache write and the cache read token counts, so a cold prefix is visible.

Docs: https://platform.claude.com/docs/en/build-with-claude/prompt-caching

**Blocked by:** None (can start immediately). Touches the parse path in the writer module that every call shares.

**Status:** done

- [x] The shared parse path sends the system prompt as a content block list with `cache_control` of type `ephemeral`, not as a plain string. A call with no system prompt sends none, as today.
- [x] The analyzer call sets `ttl` to `1h` on its system block. The writer and the verifier use the default five minute lifetime.
- [x] The prefix is the same bytes on every call of one kind: the prompt files joined in a fixed order, with no date, no week, and no per-request fact in the system block. Per-request content stays in the user message.
- [x] Each system prompt clears the 512 token floor of the model, or the ticket says which one does not and leaves it uncached on purpose. All three clear it, by the count_tokens API: analyzer 4023, writer 3592, verifier 1821. A live pair of calls showed a cache read on each.
- [x] After each call, a log line at info level names the call kind, `cache_creation_input_tokens`, `cache_read_input_tokens`, and `input_tokens` from the response usage.
- [x] A test with the call patched asserts the request shape: the system block list, the `cache_control` type, and the `ttl` on the analyzer call only.
- [x] A live check against the API: two analyze requests a minute apart, the second shows `cache_read_input_tokens` above zero in the log.
- [x] The runbook notes the cache, the two lifetimes, and the write multipliers: 1.25x for five minutes, 2x for one hour, 0.05x on a read for Opus 5.5.
- [x] `uv run pytest -q` passes with no failed test.

## Comments

Closes as done in the audit of `todoist-queue` on 2026-11-12. The work merged in 6b0e1faf.
Proof: Every box is ticked; "Cache the system prompt on every Claude call" is on `main`, and `apps/pipeline/tests/test_writer.py` asserts the `cache_control` shape and the `1h` TTL.
Read 1 file: .scratch/todoist-queue/audit.md.
