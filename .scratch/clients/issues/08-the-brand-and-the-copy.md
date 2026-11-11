# 08: The brand and the copy

Spec: `.scratch/clients/PRD.md`. Acceptance tests AT-5, AT-10, and AT-17.

**App:** site

**What to build:** The site build applies the brand and the copy of the client. The brand sets the color roles, the fonts, and the radii. The set count of the brand decides the theme button.

**Blocked by:** 07

**Status:** done

- [x] The design package exports a JSON Schema for `brand.toml`. A missing base role or an unknown role fails the check.
- [x] The build writes the CSS custom properties from the brand. Each derived role has its formula, and a brand can override it.
- [x] A test pins each CPC value of the brand to its value today.
- [x] A brand with two sets paints light first and shows the theme button (AT-5). A brand with one set shows no theme button (AT-10).
- [x] The fonts load from the client `assets/`. The build fetches no font from an outside host.
- [x] With no logo, the masthead shows the site name from `copy.toml` as text.
- [x] A contrast test lists each text pair of each brand at 4.5 or more (AT-17).

## Comments
- Closed by the merge of PR #3.
