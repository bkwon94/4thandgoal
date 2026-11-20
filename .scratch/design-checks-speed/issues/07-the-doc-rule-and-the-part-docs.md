# 07: The doc rule and the use lines of each part

Spec: `.scratch/design-checks-speed/PRD.md`. Acceptance tests AT-10, AT-11, and AT-15.

**App:** site

**What to build:** A plugin rule fails a component file of `ui` or `parts` whose top docstring has no `Use it when:` line or no `Do not use it when:` line. Each part file gets both lines. "Do not use it when" names the part to use instead where one exists. The READMEs keep their "Knows" lists.

**Blocked by:** 01

**Status:** ready-for-agent

- [x] A fixture part with no `Use it when:` line fails with the doc rule and the file.
- [x] Each component file of `ui` and `parts` has both lines.
- [x] Each README keeps its "Knows" list.
- [x] The lint of all site code exits 0.
