# 05: The guide, the glossary, and the first full round

Spec: `.scratch/faster-evidence/PRD.md`. Acceptance tests AT-1, AT-8, AT-12, AT-13, and AT-14.

**App:** both

**What to build:** The evidence guide of `cpc:implement` teaches the runner: the `steps.json` of a site test, the one command, `make api-evidence` before an analyzer test, and the line `Round time: <N> min for <M> site tests.` under `Built from` in `EVIDENCE.md`. The guide keeps `agent-browser` as the fallback for a test whose step no verb covers, with `setItem('cpc.theme','light')` for light and a scroll before a full-page shot. `GLOSSARY.md` gets the term **Evidence** in the Workflow section. The ticket writes a `steps.json` for each of the 21 site-redesign tests that ask for screenshots, commits them, and runs one full round to see the 15 minutes hold. It restores each PNG of site-redesign with `git restore`.

**Blocked by:** 01, 03, 04

**Status:** ready-for-agent

- [ ] `evidence.md` teaches each item above, and no step of it uses `removeItem('cpc.theme')`.
- [ ] `GLOSSARY.md` holds **Evidence**, and the tracker and glossary rules pass.
- [ ] The 21 `steps.json` files of site-redesign are committed, each narrowed to its Evidence line.
- [ ] One run of `pnpm --dir apps/site evidence site-redesign`, with `make api-evidence` running, prints a total of 15 min or less. The close comment records the total.
- [ ] The analyzer tests AT-20 and AT-21 of site-redesign get no 429 and each take less than 61 s.
- [ ] `git diff main -- .claude/plugin/skills/review` is empty.
