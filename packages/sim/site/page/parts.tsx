/**
 * The small parts of the sim page: the bar of a percent, the soft swap of a text that changes, and the read of the
 * tablet tier. The bar and the swap take a value and return markup.
 */
import { AnimatePresence, motion, useIsPresent } from "framer-motion";
import { useSyncExternalStore } from "react";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { cn } from "@cpc/design/lib/utils";

/* The tablet tier, the same breakpoint as the tablet variant, --breakpoint-tablet in globals.css. */
const TABLET = "(min-width: 40rem)";

function onTierChange(change: () => void): () => void {
  const query = window.matchMedia(TABLET);
  query.addEventListener("change", change);
  return () => query.removeEventListener("change", change);
}

/* True from the tablet tier up. The static page and the first paint take the phone, and the CSS of each part shows the
   right tier before this reads the window. */
export function useTabletUp(): boolean {
  return useSyncExternalStore(onTierChange, () => window.matchMedia(TABLET).matches, () => false);
}

/* A thin bar that fills to its percent. The fill scales, so the bar keeps its width. */
export function Bar({ value, className }: { value: number | null; className?: string }) {
  return (
    <span aria-hidden className={cn("block h-sp-1 overflow-hidden rounded-pill bg-bar-off", className)}>
      <span
        className="block h-full origin-left rounded-pill bg-accent"
        style={{ transform: `scaleX(${Math.min(100, Math.max(0, value ?? 0)) / 100})` }}
      />
    </span>
  );
}

/* The text swap soft of transitions-dev: the old text blurs out and the new text blurs in at once, in one grid cell,
   so a number that a What-if changes reads as one value that moves. Under reduced motion the text swaps at once.
   The first paint shows the text at rest. */
const SWAP = { duration: 0.2, ease: "easeInOut" } as const;

export function SoftText({ text, className }: { text: string; className?: string }) {
  return (
    <span className={cn("inline-grid", className)}>
      <AnimatePresence initial={false} mode="sync">
        <SoftLayer key={text} text={text} />
      </AnimatePresence>
    </span>
  );
}

/* One text of the swap. The text on its way out leaves the accessibility tree at once, so a reader hears one value. */
function SoftLayer({ text }: { text: string }) {
  const off = useMotionOff();
  const present = useIsPresent();
  return (
    <motion.span
      aria-hidden={present ? undefined : true}
      className="[grid-area:1/1]"
      initial={off ? false : { opacity: 0, filter: "blur(2px)" }}
      animate={{ opacity: 1, filter: "blur(0px)" }}
      exit={off ? { opacity: 0, transition: { duration: 0 } } : { opacity: 0, filter: "blur(2px)" }}
      transition={SWAP}
    >
      {text}
    </motion.span>
  );
}
