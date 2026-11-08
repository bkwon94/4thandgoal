# A part built from a Scrolltide item keeps its motion

ADR 0024 keeps the motion rule of the site: transform and opacity only, and a strong ease-out. The `card-polish` spec builds five parts from the methods of Scrolltide items. Brian wants each part to follow its item as far as possible. We decided that a part built from a Scrolltide item keeps the motion of its item, inside the hard rules below. The team writes its own code from the method, and no Scrolltide source enters the repo, because it is paid source and the repo is public.

## The hard rules

These still win over the item:

- The readability floor of ADR 0025: text sizes, AA contrast that axe can read, 44px tap targets, and no sideways scroll at 390px.
- Reduced motion turns each motion of the part to an instant change.
- The layout works first at 390px. A hover of the item becomes a tap on a phone.
- The hero stays the one loud surface of a page (ADR 0024).

## Consequences

- The Open card animates its height with `grid-template-rows` from `0fr` to `1fr`. It is the one height method of the site. The closed panel stays in the DOM with `inert` (decision 01 of `card-polish`).
- The details of an open card come into focus from a `filter: blur` of 6px, a beat behind the height.
- The Open card moves on a damped spring, sampled into a CSS `linear()` curve, with a small overshoot.
- An acceptance test of the spec records the frame rate of an open card on a throttled phone profile. If the blur fails it, the blur goes, and the spec records why.
- A part not built from a Scrolltide item keeps the rule of ADR 0024.

We rejected two alternatives:

- **Keep the rule of ADR 0024 for every part.** The parts lose the polish that made Brian choose the items.
- **Copy the Scrolltide source.** It is paid source, and the repo is public.
