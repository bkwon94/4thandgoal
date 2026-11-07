# 04: Every egg kind and the limit of the check

Spec: `.scratch/easter-eggs/PRD.md`. Acceptance tests AT-3, AT-4, AT-13, AT-19, AT-25, AT-27, AT-28, AT-29, AT-30, and AT-31.

**App:** both

**What to build:** Every action and condition of the catalog works, and a normal tap still does what it always does. The listener counts by a stable id that every element of each class of target carries, with an egg or not. So the source names no spot. The check route of the API matches each condition and has its own limit of 60 per hour.

**Blocked by:** 01

**Status:** ready-for-agent

- [x] The listener sends one check for a long press or hold of 1, 3, or 5 seconds, for a tap combo that ends with a double-tap, and for one selected word. A single tap sends no check.
- [x] The listener counts taps by the stable id, so taps across the frames of the sim count as one multi-tap.
- [x] Every class of target of the catalog carries a stable id on every page. The iOS callout is off on these targets and still on for links and images.
- [x] The check carries the open states, the sim outcome, the trade key, the scroll to the end, and the 404 page. The API matches each one, and checks the clock window in the timezone of the client.
- [x] The check route answers 429 with a retry-after on the 61st check in an hour from one address. The other routes keep their own limit.
- [ ] A grep of the repo and the built site finds no reason and no target of the test egg file.
