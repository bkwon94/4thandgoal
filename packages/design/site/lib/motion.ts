/**
 * The shared motion timings and the pure helpers that build motion props.
 * The reduced-motion switch is useMotionOff in the hooks folder. A helper that builds motion props takes its result as the off flag.
 */
import { type TargetAndTransition, type Transition } from "framer-motion";

/* The brand ease-out from --ease-out in globals.css. Framer Motion needs the curve as numbers, not as a CSS value. */
export const EASE_OUT = [0.23, 1, 0.32, 1] as const;

/* A transition that ends at once. A component uses it for every animation when motion is off. */
export const INSTANT: Transition = { duration: 0 };

/* A short rise for content that enters. Framer Motion accepts a CSS variable for y, so the distance comes from the spacing token. */
export const RISE = "var(--spacing-sp-2)";

/* A short drop for content that enters from above, such as the menu sheet under the masthead. It mirrors the rise. */
export const DROP = "calc(var(--spacing-sp-2) * -1)";

/* The ease of the loading sweep. The bar travels both ways, so it eases in and out. */
export const SWEEP_EASE = "easeInOut";

/* The ease of the waiver drift. A headshot drifts there and back, so it eases in and out at each end. */
export const DRIFT_EASE = "easeInOut";

/* Durations in seconds. The page enter is short, so the content is ready to tap almost at once. */
export const DURATION = {
  // The content of the route fades and rises in once.
  page: 0.3,
  // A picker list opens or closes. A layout change needs a little more time than a press.
  collapse: 0.24,
  // The menu sheet leaves. It is faster than its entry, so a back-out feels instant.
  sheetExit: 0.16,
  // The menu button icon turns from three lines into a cross. It is short, because it only confirms the tap.
  iconMorph: 0.16,
  // The Past weeks popover scales in from its trigger. It is short, because the reader asked for it with a click.
  popover: 0.16,
  // The Past weeks popover leaves. It is faster than its entry, so a back-out feels instant, as the sheet exit does.
  popoverExit: 0.1,
  // The compact bar slides in from above or leaves. It takes the press timing, so the bar answers the scroll at once.
  bar: 0.14,
  // The decision word lands. It is a little slower than the rest, so the call lands with a beat.
  decision: 0.36,
  // The fairness line lands under the decision. It is a little faster than the decision word, so the decision stays the lead.
  fairness: 0.3,
  // One pass of the loading sweep. It repeats while the grade runs.
  sweep: 1.4,
  // A section or a card enters the viewport. It is a little slower than the page enter, because the reader watches it arrive.
  reveal: 0.4,
  // A part of the game changer hero enters. It is the slowest reveal, because the hero is the top story of the week page.
  hero: 0.5,
  // A dot of the points line fades in as the drawn line reaches it. It is short, so each dot lands close behind the line.
  dot: 0.16,
} as const;

/* The gap between two cards that enter together, in seconds. It is short, so a fast scroll never waits on motion. */
export const REVEAL_STAGGER = 0.05;

/* The last step of a stagger. Card ten waits no longer than card four, so a card in a long list never shows late. */
const STAGGER_CAP = 4;

/* The delay of the card at a position in a list. */
export function stagger(index: number): number {
  return Math.min(index, STAGGER_CAP) * REVEAL_STAGGER;
}

/* The delays of the three hero parts, in seconds. The glow comes first, the cutout next, and the points last. */
export const HERO_DELAY = { glow: 0, cutout: 0.08, points: 0.24 } as const;

/* A side or a picked row enters and leaves in about 200 ms with the brand ease-out. The exit is faster, so a remove feels instant.
   No spring, because an overshoot on a form reads as a wobble. */
const ENTER: Transition = { duration: 0.2, ease: EASE_OUT };
const EXIT: Transition = { duration: 0.15, ease: EASE_OUT };

/* The props of a list item that rises in and fades out. With motion off, the item shows at rest and leaves at once. */
export function enterExit(off: boolean) {
  return {
    initial: off ? (false as const) : { opacity: 0, y: RISE },
    animate: { opacity: 1, y: 0 } satisfies TargetAndTransition,
    exit: { opacity: 0, transition: off ? INSTANT : EXIT } satisfies TargetAndTransition,
    transition: off ? INSTANT : ENTER,
  };
}

/* The props of content that fades and rises in once. With motion off, the content shows at rest and the transition is instant. */
export function rise(off: boolean, { duration, delay = 0 }: { duration: number; delay?: number }) {
  return {
    initial: off ? (false as const) : { opacity: 0, y: RISE },
    animate: { opacity: 1, y: 0 } satisfies TargetAndTransition,
    transition: off ? INSTANT : { duration, ease: EASE_OUT, delay },
  };
}
