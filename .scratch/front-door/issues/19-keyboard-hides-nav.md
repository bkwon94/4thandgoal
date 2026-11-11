# 19: The keyboard hides the nav

Spec: `.scratch/front-door/PRD.md`. Source: H8 of `.scratch/front-door/HANDS-ON.md`.

**App:** site

**What to build:** On a phone, the keyboard opens when the reader taps the ask box, and the dock of the site covers the ask box. While the ask box has the focus, the dock tucks away, as the tab bar of a native app, and it comes back on blur. The foot of the Thread sticks right above the keyboard, through the inset of the visual viewport, because iOS Safari keeps the layout viewport at full height under the keyboard. The tuck slides and fades on the motion tokens. Under reduced motion, only the fade stays. On a wide screen with no on-screen keyboard, nothing changes.

**Blocked by:** None

**Status:** done

- [x] Focus on the ask box tucks the dock away, and the tucked dock is inert (vitest).
- [x] Blur of the ask box brings the dock back (vitest).
- [x] The foot of the Thread sits right above the keyboard: a Playwright run on an iPhone 13 viewport with a visual viewport 336 px shorter puts the foot bottom at the keyboard top.
- [x] Under `prefers-reduced-motion: reduce`, the dock fades with no slide.
- [ ] The commissioner checks it on a real iPhone.

## Comments
- Closes with the squash merge of the spec PR.
