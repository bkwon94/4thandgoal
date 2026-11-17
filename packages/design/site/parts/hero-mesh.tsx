/**
 * The mesh: the live grid art of a hero, as a client leaf that holds the canvas, so `Hero` stays a server component.
 * The page passes it as the art of a hero, and it starts the runner of `mesh-canvas.ts` on a `2d` context.
 */
"use client";

import { useEffect, useRef } from "react";
import { useMotionOff } from "../hooks/use-motion-off";
import { type MeshDrive, runMesh } from "./mesh-canvas";

/* `drive` sets the weights and the pulses of the mesh over time. With none, the mesh is the calm, flat grid of idle.
   A new drive starts the runner again, so a caller keeps one drive for the life of a state, such as one grade wait. */
export function HeroMesh({ drive }: { drive?: MeshDrive }) {
  const canvas = useRef<HTMLCanvasElement>(null);
  const probe = useRef<HTMLSpanElement>(null);
  const motionOff = useMotionOff();

  useEffect(() => {
    const hero = canvas.current?.closest("section");
    // The runner pauses out of view with an IntersectionObserver. A browser with none, such as jsdom, draws no mesh,
    // so the mesh never runs where it cannot pause. A browser with no canvas gets no context. Either way the hero shows
    // its band color with the brackets.
    if (!canvas.current || !probe.current || !hero || typeof IntersectionObserver === "undefined") return;
    const ctx = canvas.current.getContext("2d");
    if (!ctx) return;
    return runMesh({ canvas: canvas.current, ctx, hero, probe: probe.current, motionOff, drive });
  }, [motionOff, drive]);

  return (
    <>
      <canvas ref={canvas} data-hero-mesh className="absolute inset-0 block size-full" />
      {/* The probe: the runner reads the grid, the glow, the dot, and the pulse colors from it, and again on a switch of the theme. */}
      <span ref={probe} className="hidden">
        <span className="text-grid" />
        <span className="text-accent-glow" />
        <span className="text-on-dark-muted" />
        <span className="text-accent-text" />
      </span>
    </>
  );
}
