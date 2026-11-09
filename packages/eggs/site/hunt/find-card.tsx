/**
 * The find: the page blurs, a red ring ripples out from the spot, and a hero card rises in with the egg that bobs.
 * A tap cracks the egg from the tap point, the shell bursts, and the red letter tile grows out of that point. Reduced motion shows the tile at rest.
 */
"use client";

import { type MouseEvent, useEffect, useState } from "react";
import { HeroFrame } from "@cpc/design/parts/hero";
import { Label } from "@cpc/design/parts/label";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { cn } from "@cpc/design/lib/utils";
import { crackOf, EGG_MIDDLE, EGG_SIZE, freshSeed, tapPointOf, type Crack } from "./crack";
import { ArtGround, Egg } from "./egg-art";

/* The time from the tap to the letter, in ms: the egg squashes, the lines draw, the shell bursts at about 560 ms,
   and the tile grows. The keyframes of egg-* in globals.css hold the same times. */
export const CRACK_MS = 1300;

/* The size in px of the letter tile, the same as its class size-28. */
const TILE_PX = 112;
/* The top left of the tile in the middle of the egg art, so the tile can grow from a point of the art. */
const TILE_AT = { x: (EGG_SIZE.width - TILE_PX) / 2, y: (EGG_SIZE.height - TILE_PX) / 2 };

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
  // The crack of the tap. It stays set after the crack, so the tile keeps the tap point as the origin of its growth.
  const [crack, setCrack] = useState<Crack | null>(null);

  useEffect(() => {
    if (phase !== "cracking") return;
    const timer = setTimeout(() => setPhase("letter"), CRACK_MS);
    return () => clearTimeout(timer);
  }, [phase]);

  const crackEgg = (event: MouseEvent<HTMLButtonElement>) => {
    // With motion off, the tap shows the letter at once, with no crack.
    if (!motion) {
      setPhase("letter");
      return;
    }
    // Enter or Space clicks the button with a detail of 0 and no pointer, so a tap by the keyboard cracks from the middle.
    const point =
      event.detail === 0
        ? EGG_MIDDLE
        : tapPointOf(event.clientX, event.clientY, event.currentTarget.getBoundingClientRect());
    // A fresh seed on each tap, so each find cracks in a new way.
    setCrack(crackOf(point, freshSeed()));
    setPhase("cracking");
  };
  const tap = crack?.point ?? EGG_MIDDLE;

  return (
    <div role="dialog" aria-modal="true" aria-labelledby="egg-find-title" className="fixed inset-0 z-50 grid place-items-center overflow-y-auto p-gutter">
      <div aria-hidden="true" className="egg-scrim fixed inset-0 bg-band/75" />
      {motion && origin && phase === "egg" && (
        <div aria-hidden="true">
          <span className="egg-ripple" style={{ left: origin.x, top: origin.y }} />
          <span className="egg-ripple egg-ripple-late" style={{ left: origin.x, top: origin.y }} />
        </div>
      )}
      <HeroFrame label={phase === "letter" ? "Letter found" : "Egg found"} className="egg-hero egg-hero-in egg-hero-in-late w-full max-w-sm">
        <div className="flex flex-col items-center gap-sp-4 text-center">
          <Label dark className="mb-0 self-start text-meta">
            {phase === "letter" ? "Letter found" : "Egg found"}
          </Label>
          <div className="relative flex h-58 w-50 items-center justify-center">
            {/* The ground reaches past the art to the edges of the hero, and never above or below the art. */}
            <ArtGround inset="inset-y-0 -inset-x-16" />
            {phase !== "letter" && (
              <button
                type="button"
                aria-label="Crack the egg"
                disabled={phase === "cracking"}
                onClick={crackEgg}
                className="relative cursor-pointer"
              >
                <span aria-hidden="true" className="egg-halo" />
                <Egg crack={crack} motion={motion} />
              </button>
            )}
            {phase !== "egg" && (
              // The box of the egg art, so a point of the art is a point in px of this box.
              <div className="absolute top-1/2 left-1/2 flex h-55 w-45 -translate-x-1/2 -translate-y-1/2 items-center justify-center">
                {motion && <span aria-hidden="true" className="egg-flash" style={{ left: tap.x, top: tap.y }} />}
                <span
                  data-testid="egg-letter"
                  className={cn(
                    "relative flex size-28 items-center justify-center rounded-letter bg-accent font-mono text-hero leading-hero font-bold text-on-dark shadow-orb",
                    motion && "egg-tile-rise",
                  )}
                  // The tile sits in the middle of the art, so the tap point less the top left of the tile is a point of the tile.
                  style={motion ? { transformOrigin: `${tap.x - TILE_AT.x}px ${tap.y - TILE_AT.y}px` } : undefined}
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
                  The letter {letter} is yours to claim.
                </h2>
                <p className="text-lead text-on-dark-2">
                  The first claim wins. Another manager can still beat you to it.
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
                You found an egg
              </h2>
              <p className="text-lead text-on-dark-2">
                Tap it to crack it open.
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
      </HeroFrame>
    </div>
  );
}
