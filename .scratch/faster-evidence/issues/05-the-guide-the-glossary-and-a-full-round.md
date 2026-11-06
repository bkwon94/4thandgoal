# 05: The guide, the glossary, and the first full round

Spec: `.scratch/faster-evidence/PRD.md`. Acceptance tests AT-1, AT-8, AT-12, AT-13, and AT-14.

**App:** both

**What to build:** The evidence guide of `cpc:implement` teaches the runner: the `steps.json` of a site test, the one command, `make api-evidence` before an analyzer test, and the line `Round time: <N> min for <M> site tests.` under `Built from` in `EVIDENCE.md`. The guide keeps `agent-browser` as the fallback for a test whose step no verb covers, with `setItem('cpc.theme','light')` for light and a scroll before a full-page shot. `GLOSSARY.md` gets the term **Evidence** in the Workflow section. The ticket writes a `steps.json` for each site-redesign test that asks for screenshots and that the six verbs cover, commits them, and runs one full round to see the 15 minutes hold. It restores each PNG of site-redesign with `git restore`.

**Blocked by:** 01, 03, 04

**Status:** ready-for-agent

- [x] `evidence.md` teaches each item above, and no step of it uses `removeItem('cpc.theme')`.
- [x] `GLOSSARY.md` holds **Evidence**, and the tracker and glossary rules pass.
- [x] A `steps.json` for each covered screenshot test of site-redesign is committed, each narrowed to its Evidence line. The close comment names each skipped test and the reason.
- [x] One run of `pnpm --dir apps/site evidence site-redesign`, with `make api-evidence` running, prints a total of 15 min or less. The close comment records the total.
- [ ] The analyzer tests AT-24 and AT-25 of site-redesign get no 429 and each take less than 61 s.
- [x] `git diff main -- .claude/plugin/skills/review` is empty.
