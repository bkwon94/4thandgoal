/**
 * The hero scene: the client leaf that holds the canvas of the first hero of a page, so `Hero` stays a server component.
 * It takes the plain data of one scene (ADR 0012) and starts the runner of `scene-canvas.ts` on a `2d` context (ADR 0027).
 */
"use client";

import { useEffect, useRef } from "react";
import { useMotionOff } from "../hooks/use-motion-off";
import { runScene } from "./scene-canvas";
import type { HeroScene } from "./scene-math";

export function HeroSceneCanvas({ scene }: { scene: HeroScene }) {
  const holder = useRef<HTMLDivElement>(null);
  const canvas = useRef<HTMLCanvasElement>(null);
  const probe = useRef<HTMLSpanElement>(null);
  const motionOff = useMotionOff();

  useEffect(() => {
    if (!holder.current || !canvas.current || !probe.current) return;
    // A browser with no canvas gets no context, and the hero keeps its static grid.
    const ctx = canvas.current.getContext("2d");
    if (!ctx) return;
    return runScene({ canvas: canvas.current, ctx, holder: holder.current, probe: probe.current, scene, motionOff });
  }, [scene, motionOff]);

  return (
    // The scene is art. The hero text tells the same story, so a screen reader skips the canvas.
    <div ref={holder} aria-hidden="true" className="relative h-hero-scene tablet:h-hero-scene-wide">
      {/* pan-y gives an up or down drag to the page scroll, so the scene never traps the scroll (story 32). */}
      <canvas ref={canvas} data-hero-scene className="absolute inset-0 size-full touch-pan-y" />
      {/* The probe: the canvas reads the three colors and the mono font from it once at mount (decision 03). */}
      <span ref={probe} className="hidden font-mono">
        <span className="text-accent" />
        <span className="text-on-dark" />
        <span className="text-on-dark-muted" />
      </span>
    </div>
  );
}
