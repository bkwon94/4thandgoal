/**
 * The one reveal of the site: content fades and rises in once, when it enters the viewport or when it mounts.
 * It is the client leaf of the static pages, so the sections around it stay server components.
 */
"use client";

import { motion } from "framer-motion";
import { useEffect, type ReactNode } from "react";
import { DURATION, EASE_OUT, INSTANT, RISE, useMotionOff } from "@/lib/motion";

/* The content reveals a little after its top edge enters the screen, so the reader sees the motion and not only its end. */
export const VIEW_MARGIN = "0% 0% -8% 0%";

const HIDDEN = { opacity: 0, y: RISE };
const SHOWN = { opacity: 1, y: 0 };
// A box with no rise only fades in, for a backdrop such as the hero glow.
const FADE_HIDDEN = { opacity: 0 };
const FADE_SHOWN = { opacity: 1 };

/* Sets data-hydrated on the root once the script runs. The attribute turns off the CSS safety rule in globals.css,
   so Framer Motion owns every reveal after hydration. The set is the same each time, so the first caller is enough. */
export function useMarkHydrated() {
  useEffect(() => {
    document.documentElement.setAttribute("data-hydrated", "");
  }, []);
}

type RevealProps = {
  children?: ReactNode;
  // "view" waits for the viewport. "mount" plays at once, for the content of a route.
  trigger?: "view" | "mount";
  // False fades the box in with no rise.
  rise?: boolean;
  // The stagger of a card in a list, in seconds.
  delay?: number;
  duration?: number;
  // The layout classes of the revealed box. Only opacity and transform animate, so the box keeps its size and place.
  className?: string;
};

export function Reveal({
  children,
  trigger = "view",
  rise = true,
  delay = 0,
  duration = DURATION.reveal,
  className,
}: RevealProps) {
  const off = useMotionOff();
  useMarkHydrated();
  // The static HTML holds the start state, and the first client render must match it, so the start state is the same
  // with motion off. With motion off the content then goes to rest at once on mount and never waits for the viewport.
  // The data-reveal rule in globals.css shows the content at rest before the script loads, for reduced motion and no script.
  // A browser with no IntersectionObserver never reports the viewport, so the content plays on mount and never stays hidden.
  const watch = trigger === "view" && typeof IntersectionObserver !== "undefined";
  const shown = rise ? SHOWN : FADE_SHOWN;
  const play = off || !watch ? { animate: shown } : { whileInView: shown, viewport: { once: true, margin: VIEW_MARGIN } };
  return (
    <motion.div
      data-reveal
      className={className}
      initial={rise ? HIDDEN : FADE_HIDDEN}
      {...play}
      transition={off ? INSTANT : { duration, ease: EASE_OUT, delay }}
    >
      {children}
    </motion.div>
  );
}
