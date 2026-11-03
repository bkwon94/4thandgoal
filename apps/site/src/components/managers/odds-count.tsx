/**
 * The playoff percent of the manager hero. On load it counts from zero to the percent once, over the decision timing.
 * The static HTML and a reader with motion off get the final number at once, and the percent sign never moves.
 */
"use client";

import { animate, motion, useMotionValue, useTransform } from "framer-motion";
import { useEffect } from "react";
import { useMotionOff } from "@/hooks/use-motion-off";
import { DURATION, EASE_OUT } from "@/lib/motion";

export function OddsCount({ value }: { value: number }) {
  const off = useMotionOff();
  // The value starts at the final number, so the server and a test with motion off render the final number.
  const count = useMotionValue(value);
  const shown = useTransform(count, (latest) => Math.round(latest));
  useEffect(() => {
    if (off) return;
    // The count starts on mount only, so a scroll never plays it again. The first frame sets zero.
    const controls = animate(count, value, { from: 0, duration: DURATION.decision, ease: EASE_OUT });
    return () => controls.stop();
  }, [off, value, count]);
  return (
    <>
      <motion.span>{shown}</motion.span>%
    </>
  );
}
