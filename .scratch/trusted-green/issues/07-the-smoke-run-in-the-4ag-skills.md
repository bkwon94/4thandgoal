# 07: The smoke run in the 4ag skills

Spec: `.scratch/trusted-green/PRD.md`. Acceptance tests AT-12 and AT-13.

**App:** both

**What to build:** `4ag:implement` runs one smoke run after the last ticket, before the Judge, and writes its shots and log into the smoke folder of the evidence. `4ag:quick` runs one before the quick Judge, and names it in a `Smoke:` block. A red smoke run stops the work before the Judge. The quick Judge asks a third question for each item that touches the site or the API. `format.md` names the `Rebuild:` block of approved diffs.

**Blocked by:** 06

**Status:** done

- [x] The skill text of `4ag:implement` names the smoke run, the smoke folder, and the stop on a red run.
- [x] `format.md` of `4ag:quick` names the `Smoke:` block and the `Rebuild:` block.
- [x] The quick Judge brief holds "Does the smoke run show the changed flow at work?"
- [x] A rule test checks each of the three boxes above.

## Comments

Closes with the squash merge of the spec PR: `trusted-green-07` (`19dab906`) merged into `trusted-green` as a fast-forward on 2026-11-18.
`scripts/test_skill_smoke.py` has 7 tests, and AT-12 and AT-13 have PASS.
`quick/SKILL.md` has no step that saves the rebuild output for the quick Judge.
The builder did not count the files it read; the ticket commit changed 6 files: .claude/plugin/skills/implement/SKILL.md, .claude/plugin/skills/implement/evidence.md, .claude/plugin/skills/quick/SKILL.md, .claude/plugin/skills/quick/format.md, .claude/plugin/skills/quick/judge.md, scripts/test_skill_smoke.py.
