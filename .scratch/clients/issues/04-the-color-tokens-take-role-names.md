# 04: The color tokens take role names

Spec: `.scratch/clients/PRD.md`. Acceptance tests AT-8.

**App:** site

**What to build:** Each color token of the site takes the role name of the spec, such as `accent` for `red`. The CPC look does not change.

**Blocked by:** none

**Status:** in-review

- [x] Each token and class of the brand table of the spec takes its new name. `ink` and `mute` keep their names.
- [x] The shadcn tokens `card` and `accent` point at the brand roles of the same name. The select item takes a focus fill with its own meaning.
- [x] A search of the site source finds no class or token of `red`, `blk`, `gry`, or `wht` (AT-8).
- [x] The week 8 page of CPC looks the same at 375, 768, and 1280 px, in both themes. The AT-3 pairs at `c5634be` show 0 changed pixels against the export of `main` at `003c70c`.
