/**
 * The one reduced-motion switch for the site.
 * Every animated component reads useMotionOff, so the reduced-motion media query turns every animation off.
 */
import { useReducedMotion } from "framer-motion";

/* True when the reader asks the system for reduced motion. Framer Motion reads the media query once, when a component mounts. */
export function useMotionOff(): boolean {
  return useReducedMotion() === true;
}
