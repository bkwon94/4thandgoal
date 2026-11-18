# 07: The smoke run in the 4ag skills

Spec: `.scratch/trusted-green/PRD.md`. Acceptance tests AT-12 and AT-13.

**App:** both

**What to build:** `4ag:implement` runs one smoke run after the last ticket, before the Judge, and writes its shots and log into the smoke folder of the evidence. `4ag:quick` runs one before the quick Judge, and names it in a `Smoke:` block. A red smoke run stops the work before the Judge. The quick Judge asks a third question for each item that touches the site or the API. `format.md` names the `Rebuild:` block of approved diffs.

**Blocked by:** 06

**Status:** ready-for-agent

- [ ] The skill text of `4ag:implement` names the smoke run, the smoke folder, and the stop on a red run.
- [ ] `format.md` of `4ag:quick` names the `Smoke:` block and the `Rebuild:` block.
- [ ] The quick Judge brief holds "Does the smoke run show the changed flow at work?"
- [ ] A rule test checks each of the three boxes above.
