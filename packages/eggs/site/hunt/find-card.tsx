/**
 * The find: the page blurs, a red ring ripples out from the spot, and a hero card rises in with the egg that bobs.
 * A tap cracks the egg, the halves fly apart, and the red letter tile springs up. Reduced motion shows the tile at rest.
 */
"use client";

import { useEffect, useState } from "react";
import { Hero } from "@cpc/design/parts/hero";
import { Label } from "@cpc/design/parts/label";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { cn } from "@cpc/design/lib/utils";
import { Egg } from "./egg-art";

/* The time from the tap to the letter, in ms: the crack draws, the halves part, and the tile lands. */
export const CRACK_MS = 1150;

/* The spot of the find on the screen, in px from the top left of the viewport. */
export type Origin = { x: number; y: number };

type FindCardProps = {
  letter: string;
  // The middle of the element of the find, so the ring ripples out from it. Null when the element is gone.
  origin: Origin | null;
  onClaim: () => void;
  onClose: () => void;
};

type Phase = "egg" | "cracking" | "letter";

export function FindCard({ letter, origin, onClaim, onClose }: FindCardProps) {
  const motion = !useMotionOff();
  const [phase, setPhase] = useState<Phase>("egg");

  useEffect(() => {
    if (phase !== "cracking") return;
    const timer = setTimeout(() => setPhase("letter"), CRACK_MS);
    return () => clearTimeout(timer);
  }, [phase]);

  // With motion off, the tap shows the letter at once, with no crack.
  const crack = () => setPhase(motion ? "cracking" : "letter");

  return (
    <div role="dialog" aria-modal="true" aria-labelledby="egg-find-title" className="fixed inset-0 z-50 grid place-items-center overflow-y-auto p-gutter">
      <div aria-hidden="true" className="egg-scrim fixed inset-0 bg-band/75" />
      {motion && origin && phase === "egg" && (
        <div aria-hidden="true">
          <span className="egg-ripple" style={{ left: origin.x, top: origin.y }} />
          <span className="egg-ripple egg-ripple-late" style={{ left: origin.x, top: origin.y }} />
        </div>
      )}
      <Hero label={phase === "letter" ? "Letter found" : "Egg found"} className="egg-hero-in egg-hero-in-late w-full max-w-sm">
        <div className="flex flex-col items-center gap-sp-4 text-center">
          <Label dark className="mb-0 self-start text-meta">
            <span className="plate">{phase === "letter" ? "Letter found" : "Egg found"}</span>
          </Label>
          <div className="relative flex h-58 w-50 items-center justify-center">
            {phase !== "letter" && (
              <button
                type="button"
                aria-label="Crack the egg"
                disabled={phase === "cracking"}
                onClick={crack}
                className="relative cursor-pointer"
              >
                <span aria-hidden="true" className="egg-halo" />
                <Egg cracking={phase === "cracking"} motion={motion} />
              </button>
            )}
            {phase !== "egg" && (
              <div className="absolute inset-0 flex items-center justify-center">
                {motion && <span aria-hidden="true" className="egg-burst" />}
                <span
                  data-testid="egg-letter"
                  className={cn(
                    "relative flex size-28 items-center justify-center rounded-letter bg-accent font-mono text-hero leading-hero font-bold text-on-dark shadow-orb",
                    motion && "egg-tile-rise",
                  )}
                >
                  {letter}
                </span>
              </div>
            )}
          </div>
          {phase === "letter" ? (
            <div className={cn("flex w-full flex-col items-center gap-sp-4", motion && "egg-fade-in")}>
              <div className="flex flex-col gap-sp-1">
                <h2 id="egg-find-title" className="text-score leading-tight font-bold">
                  <span className="plate box-decoration-clone">The letter {letter} is yours to claim.</span>
                </h2>
                <p className="text-lead text-on-dark-2">
                  <span className="plate box-decoration-clone">The first claim wins. Another manager can still beat you to it.</span>
                </p>
              </div>
              <button
                type="button"
                onClick={onClaim}
                className="press min-h-touch w-full rounded-pill bg-accent text-lead font-bold text-on-dark shadow-orb"
              >
                Claim {letter}
              </button>
            </div>
          ) : (
            <div className="flex flex-col gap-sp-1">
              <h2 id="egg-find-title" className="text-score leading-tight font-bold">
                <span className="plate">You found an egg</span>
              </h2>
              <p className="text-lead text-on-dark-2">
                <span className="plate">Tap it to crack it open.</span>
              </p>
            </div>
          )}
          <button
            type="button"
            onClick={onClose}
            className="press min-h-touch w-full rounded-pill border border-rule-dark bg-band text-body font-bold text-on-dark"
          >
            Close
          </button>
        </div>
      </Hero>
    </div>
  );
}
