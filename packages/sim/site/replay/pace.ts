/**
 * The pace of the replay and the motion props of each part. Full motion moves and fades; reduced motion only fades,
 * on the same timeline; a skip shows each part at rest at once.
 */
import type { TargetAndTransition, Transition } from "framer-motion";
import { EASE_OUT, INSTANT } from "@cpc/design/lib/motion";

export type Pace = {
  // True when the reader asks for reduced motion: each beat fades, with no movement (decision 13).
  off: boolean;
  // True after a skip: each part shows at rest at once.
  still: boolean;
};

/* The fade of a beat under reduced motion. It is short, so the beat still reads on the same timeline. */
const FADE = 0.3;

/* A spring with a bounce of 0.3 or less, the cap of decision 13. */
export const SPRING: Transition = { type: "spring", bounce: 0.25, duration: 0.6 };

/* The props of a part that enters from `from`, such as { x: -24 } or { scale: 0.6 }. Under reduced motion the part only
   fades in, and after a skip it shows at rest. */
export function enter(
  pace: Pace,
  from: { x?: number | string; y?: number | string; scale?: number; scaleX?: number; scaleY?: number },
  { duration = 0.5, delay = 0, spring = false }: { duration?: number; delay?: number; spring?: boolean } = {},
) {
  const rest = Object.fromEntries(Object.keys(from).map((key) => [key, key.startsWith("scale") ? 1 : 0]));
  if (pace.still) return { initial: false as const, animate: { opacity: 1, ...rest }, transition: INSTANT };
  if (pace.off) {
    return { initial: { opacity: 0 }, animate: { opacity: 1 } satisfies TargetAndTransition, transition: { duration: FADE, delay } };
  }
  return {
    initial: { opacity: 0, ...from },
    animate: { opacity: 1, ...rest } satisfies TargetAndTransition,
    transition: spring ? { ...SPRING, delay } : { duration, delay, ease: EASE_OUT },
  };
}
