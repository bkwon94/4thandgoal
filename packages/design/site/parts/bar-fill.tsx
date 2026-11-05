/**
 * The one bar fill of the look: the fill of a bar at its percent, which grows once from 0 when it enters the viewport.
 * The growth is a scale only, so the fill keeps its exact width or height, and reduced motion or no script shows it at rest.
 */
"use client";

import { animate, inView } from "framer-motion";
import { type ComponentProps, useEffect, useRef } from "react";
import { useMotionOff } from "../hooks/use-motion-off";
import { DURATION, RISE_EASE } from "../lib/motion";
import { cn } from "../lib/utils";
import { VIEW_MARGIN } from "./reveal";

type BarFillProps = Omit<ComponentProps<"span">, "style"> & {
  // The fill in percent of its track.
  pct: number;
  // "x" fills from the left, for a flat bar. "y" fills from the bottom, for a standing bar.
  axis?: "x" | "y";
};

export function BarFill({ pct, axis = "x", className, ...rest }: BarFillProps) {
  const off = useMotionOff();
  const ref = useRef<HTMLSpanElement>(null);
  // The static HTML holds the fill at rest, with no scale, so a page with no script shows the full bar.
  // Only a running script with motion allowed sets the fill to 0 and grows it, once, when it enters the viewport.
  // A browser with no IntersectionObserver never reports the viewport, so the fill grows on mount and never stays at 0.
  useEffect(() => {
    const fill = ref.current;
    if (off || !fill) return;
    const scale = axis === "x" ? "scaleX" : "scaleY";
    fill.style.transform = `${scale}(0)`;
    let stop = () => {};
    const grow = () => {
      const growth = animate(fill, { [scale]: [0, 1] }, { duration: DURATION.rise, ease: RISE_EASE });
      stop = () => growth.stop();
    };
    let unwatch = () => {};
    // The watch is on the track, because a fill at scale 0 has no area to enter the viewport.
    // The callback returns nothing, so inView stops the watch after the first entry, and the fill grows once.
    if (typeof IntersectionObserver === "undefined") grow();
    else unwatch = inView(fill.parentElement ?? fill, grow, { margin: VIEW_MARGIN });
    return () => {
      unwatch();
      stop();
    };
  }, [off, axis]);
  const size = axis === "x" ? { width: `${pct}%` } : { height: `${pct}%` };
  return (
    <span
      ref={ref}
      data-bar-fill
      className={cn(axis === "x" ? "origin-left" : "origin-bottom", className)}
      style={size}
      {...rest}
    />
  );
}
