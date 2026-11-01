# 07: One `Avatar` and one `Headshot`

**What to build:** Two client parts with a size prop and the fallback swap on error. Every team image and every player image on the site calls one of them. The managers player headshot folds into the headshot part. The twelve team images and the seven player images built by hand go away.

**Blocked by:** 06

**Status:** done

- [ ] A grep for an `img` element outside the two parts, the logo, and the primitives finds nothing.
- [ ] The two parts have tests for the size, the alt text, and the fallback swap.
- [x] The rendered markup is the same where the image was already correct. Pages that gain the `onError` swap: both week pages through `Who`, the matchups, the trade avatars and cutouts, the awards, the game changer, and the position leaders; the rankings through `Who`; the managers index; the twelve manager pages through the hero avatar; the waiver page through the pick chip and the budget ring. The swap does not show in the HTML. The only HTML diff is the attribute order of the image preload links in `<head>`.
- [ ] `pnpm typecheck`, `pnpm test`, and `pnpm check:export` pass.

## Comments

- 2026-10-31: merged into `main` from branch `modular-07-images`, commits c0ab5f8, daee982, and 73abb60. 539 tests. Cost: about 0.3 KB gzip more JS per page, and hydration now covers each image part, 73 on a week page. The PRD makes both parts client parts by design. Two reviewers passed it after one fix pass.
