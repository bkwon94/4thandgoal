/**
 * The motion of the front door, on the tokens of transitions-dev and the springs of apple-design (decision 07).
 * Under reduced motion each part keeps its fade and drops each move, blur, and spring (AT-46).
 */
import type { Transition } from "framer-motion";

/* --ease-smooth-out of the motion tokens, for each enter and exit. */
export const SMOOTH = [0.22, 1, 0.36, 1] as const;

/* The sheet follows a thumb, so it gets a hair of bounce: damping about 0.85, as a drawer of iOS. */
export const SHEET_SPRING: Transition = { type: "spring", bounce: 0.12, duration: 0.45 };

/* The one shared layout spring of the front door: the ask box glides from the center to the bottom on it, and a tapped
   Suggestion morphs into its question on it. Critically damped, as a reposition of apple-design. */
export const GLIDE: Transition = { type: "spring", bounce: 0, duration: 0.45 };

/* "More" springs open from its pill with a hair of bounce, as the Morph Navbar of scrolltide. Only the open springs: a
   close never bounces, so it gets out of the way. */
export const MORE_SPRING: Transition = { type: "spring", bounce: 0.15, duration: 0.4 };

/* The layoutId that a Suggestion chip and the question of its Answer share, so the chip morphs into the question. */
export const morphId = (key: string) => `suggestion-${key}`;

/* The halo of the send button, from 0 for an empty field to 1 at 24 letters: about one short question. */
export const haloOf = (question: string) => Math.min(1, question.trim().length / 24);

/* The tokens in seconds: --duration-stagger, --duration-quick, --duration-fast, --duration-slow, --duration-very-slow. */
export const STAGGER = 0.04;
export const QUICK = 0.15;
export const FAST = 0.25;
export const SLOW = 0.4;
export const VERY_SLOW = 0.5;

/* The rows of a long list stop their stagger at the seventh row, so the last row never shows late. */
export const staggerOf = (index: number) => Math.min(index, 6) * STAGGER;

/* A short fade-in, the same with motion on or off, so reduced motion keeps the fade. */
export const fadeIn = (duration: number, delay = 0): Transition => ({ duration, ease: SMOOTH, delay });

/* The props of a part that rises in from --distance-base, or from --distance-medium with a --blur-medium for a text reveal.
   With motion off, only the opacity moves. */
export function riseIn(off: boolean, { delay = 0, text = false }: { delay?: number; text?: boolean } = {}) {
  const from = off ? { opacity: 0 } : text ? { opacity: 0, y: 12, filter: "blur(3px)" } : { opacity: 0, y: 8 };
  const to = off ? { opacity: 1 } : text ? { opacity: 1, y: 0, filter: "blur(0px)" } : { opacity: 1, y: 0 };
  return { initial: from, animate: to, transition: fadeIn(text ? VERY_SLOW : 0.35, delay) };
}
