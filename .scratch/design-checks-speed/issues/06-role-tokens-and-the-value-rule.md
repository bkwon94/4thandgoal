# 06: The wash role tokens and the value rule

Spec: `.scratch/design-checks-speed/PRD.md`. Acceptance tests AT-4, AT-5, AT-6, AT-7, AT-12, AT-16, AT-17, AT-18, and AT-38.

**App:** site

**What to build:** The look gets `--color-accent-wash`, `--color-accent-wash-chosen`, and `--color-accent-wash-hover`, with the dark values in the dark block of the stylesheet. The chips of the front door use them, with no `dark:` fill class. A plugin rule fails an arbitrary value in the color and spacing groups, and allows variants, layout values, and motion values. Each of the 32 uses gets a fix or a one-line ignore with a reason. A `calc` that equals a token becomes the token. The spacing scale keeps its names and values.

**Blocked by:** 01

**Status:** ready-for-agent

- [x] Fixtures with an arbitrary `bg-[color-mix(...)]` and an arbitrary `top-[calc(...)]` in a `cn(...)` call each fail with the rule and the line.
- [x] A fixture with only `data-[state=open]:`, `grid-cols-[...]`, and `transition-[...]` passes.
- [x] The fixture of the spacing value passes with a one-line ignore and a reason.
- [x] No site file holds the hand copy of the band height.
- [x] The chips at rest, chosen, and in hover have the same fill as on `main`, at 375, 768, and 1280 px, in the light and dark themes.
- [x] The glossary has the terms Role token and Scale step, and the spacing scale is the same as on `main`.
- [x] The lint of all site code exits 0.
