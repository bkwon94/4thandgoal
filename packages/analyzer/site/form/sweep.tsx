/**
 * The sweep of a wait: a red bar that sweeps along a grey track, so a wait of 20 seconds or more reads as work in progress.
 * The grading hero and the finder share it. Only transform animates, and with motion off the track stays as a still grey line.
 */
"use client";

import { motion } from "framer-motion";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { DURATION, SWEEP_EASE } from "@cpc/design/lib/motion";
import { cn } from "@cpc/design/lib/utils";

/* The track color comes from the caller, because the hero needs a track that the band holds. */
export function Sweep({ track = "bg-card" }: { track?: string }) {
  const off = useMotionOff();
  return (
    <div aria-hidden="true" className={cn("relative h-sp-1 overflow-hidden rounded-pill", track)}>
      {!off && (
        <motion.div
          role="presentation"
          className="absolute inset-y-0 left-0 w-1/3 rounded-pill bg-accent"
          initial={{ x: "-100%" }}
          animate={{ x: "300%" }}
          transition={{ duration: DURATION.sweep, ease: SWEEP_EASE, repeat: Infinity }}
        />
      )}
    </div>
  );
}
