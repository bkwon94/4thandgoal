# 07: The doc rule and the use lines of each part

Spec: `.scratch/design-checks-speed/PRD.md`. Acceptance tests AT-10, AT-11, and AT-15.

**App:** site

**What to build:** A plugin rule fails a component file of `ui` or `parts` whose top docstring has no `Use it when:` line or no `Do not use it when:` line. Each part file gets both lines. "Do not use it when" names the part to use instead where one exists. The READMEs keep their "Knows" lists.

**Blocked by:** 01

**Status:** done

- [x] A fixture part with no `Use it when:` line fails with the doc rule and the file.
- [x] Each component file of `ui` and `parts` has both lines.
- [x] Each README keeps its "Knows" list.
- [x] The lint of all site code exits 0.

## Comments

The merge: `b06616e6` merged into `design-checks-speed` on 2026-11-20; review fixes on fix branches a to n; Judge fix round on AT-13 (evidence only).
The proof: `make check-fast BASE=main` passed at each merge, 3 green CI runs on 4d5f4d13 gave a median of 315 s, and the Judge gave PASS to AT-1 to AT-39.
Read at least 5 files: AGENTS.md, apps/site/AGENTS.md, .scratch/design-checks-speed/PRD.md, .scratch/design-checks-speed/ACCEPTANCE.md, .scratch/design-checks-speed/issues/07-the-doc-rule-and-the-part-docs.md.
Closes with the squash merge of the spec PR.
