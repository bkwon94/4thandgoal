# 07: One `Avatar` and one `Headshot`

**What to build:** Two client parts with a size prop and the fallback swap on error. Every team image and every player image on the site calls one of them. The managers player headshot folds into the headshot part. The twelve team images and the seven player images built by hand go away.

**Blocked by:** 06

**Status:** ready-for-agent

- [ ] A grep for an `img` element outside the two parts, the logo, and the primitives finds nothing.
- [ ] The two parts have tests for the size, the alt text, and the fallback swap.
- [ ] The rendered markup is the same where the image was already correct. The ticket names any page where a missing `onError` swap now exists, which is the one allowed diff.
- [ ] `pnpm typecheck`, `pnpm test`, and `pnpm check:export` pass.
