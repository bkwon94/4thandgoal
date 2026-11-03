# 12: Drop awards from the managers entry

**What to build:** the managers file still carries `awards` per entry, and `saved_awards` still reads every `facts.json`. The site does not read `awards` on a manager. It builds the four season numbers from `weeks`. Drop `awards` from the entry and bump `MANAGERS_SCHEMA_VERSION`, with the site types in the same step. Both repos.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] The entry has no `awards`, and `saved_awards` and its reads of `facts.json` are gone.
- [ ] `MANAGERS_SCHEMA_VERSION` goes up, and the site types and the loader check change in the same step.
- [ ] The site pages build from the new file. All checks pass in both repos.
