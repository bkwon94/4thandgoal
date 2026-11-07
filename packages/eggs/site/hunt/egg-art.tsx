/**
 * The art of the hunt: the black egg with the grid and the CPC house on it, and the letter tiles in the colors of the logo.
 * A claimed letter is a white or ink square, and the new letter is the red square.
 */
"use client";

import { useId } from "react";
import { cn } from "@cpc/design/lib/utils";
import type { Slot } from "./slots";

// The outline of the egg, and the zigzag where it cracks. Both halves clip the same art along the zigzag.
const EGG_PATH = "M90 8 C136 8 168 92 168 138 C168 184 134 212 90 212 C46 212 12 184 12 138 C12 92 44 8 90 8 Z";
const ZIGZAG = "170,140 152,128 132,146 112,128 92,146 72,128 52,146 32,128 12,140";
const TOP_HALF = `-40,-40 220,-40 220,140 ${ZIGZAG} -40,140`;
const BOTTOM_HALF = `-40,260 220,260 220,140 ${ZIGZAG} -40,140`;

/* The egg. It bobs while it waits, and on a crack the zigzag draws and the two halves fly apart.
   With motion off it takes no motion class, so it shows at rest. */
export function Egg({ cracking, motion }: { cracking: boolean; motion: boolean }) {
  const id = useId().replaceAll(":", "");
  const ref = (name: string) => `url(#${name}-${id})`;
  return (
    <svg
      viewBox="0 0 180 220"
      className={cn("relative h-55 w-45 overflow-visible", motion && !cracking && "egg-bob")}
      aria-hidden="true"
    >
      <defs>
        <path id={`egg-${id}`} d={EGG_PATH} />
        <clipPath id={`clip-${id}`}>
          <use href={`#egg-${id}`} />
        </clipPath>
        <pattern id={`grid-${id}`} width="14" height="14" patternUnits="userSpaceOnUse">
          <path d="M14 0H0V14" className="fill-none stroke-grid" strokeWidth="1" />
        </pattern>
        <radialGradient id={`glow-${id}`} cx="78%" cy="86%" r="72%">
          <stop offset="0" style={{ stopColor: "var(--color-accent)", stopOpacity: 0.8 }} />
          <stop offset="1" style={{ stopColor: "var(--color-accent)", stopOpacity: 0 }} />
        </radialGradient>
        <linearGradient id={`shade-${id}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" style={{ stopColor: "var(--color-chip-dark)" }} />
          <stop offset="1" style={{ stopColor: "var(--color-band)" }} />
        </linearGradient>
        <clipPath id={`top-${id}`}>
          <polygon points={TOP_HALF} />
        </clipPath>
        <clipPath id={`bottom-${id}`}>
          <polygon points={BOTTOM_HALF} />
        </clipPath>
        <g id={`art-${id}`}>
          <use href={`#egg-${id}`} fill={ref("shade")} />
          <g clipPath={ref("clip")}>
            <rect width="180" height="220" fill={ref("grid")} />
            <rect width="180" height="220" fill={ref("glow")} />
          </g>
          {/* The CPC house: the roof, then a white square and a red square, as in the logo. */}
          <path d="M64 100 L90 82 L116 100" className="fill-none stroke-on-dark" strokeWidth="4" strokeLinejoin="round" />
          <path d="M90 82 V102" className="stroke-on-dark" strokeWidth="3" />
          <rect x="67" y="104" width="21" height="21" className="fill-on-dark" />
          <rect x="92" y="104" width="21" height="21" className="fill-accent" />
          <path d="M50 42 C58 30 70 22 82 19" className="fill-none stroke-on-dark" strokeOpacity=".45" strokeWidth="5" strokeLinecap="round" />
          <use href={`#egg-${id}`} className="fill-none stroke-accent-text" strokeOpacity=".75" strokeWidth="1.5" />
        </g>
      </defs>
      <g className={cn("egg-half", cracking && "egg-split-top")}>
        <use href={`#art-${id}`} clipPath={ref("top")} />
      </g>
      <g className={cn("egg-half", cracking && "egg-split-bottom")}>
        <use href={`#art-${id}`} clipPath={ref("bottom")} />
      </g>
      {cracking && (
        <polyline
          points={[...ZIGZAG.split(" ")].reverse().join(" ")}
          className="egg-crack fill-none stroke-accent-text"
          strokeWidth="3"
          strokeLinejoin="round"
        />
      )}
    </svg>
  );
}

/* The grid and the glow of the hero behind the art of an egg card (the class egg-art-ground of globals.css).
   It comes first in its parent, before the positioned art, and the inset keeps the box of the ground off each line of text. */
export function ArtGround({ inset }: { inset: string }) {
  return <span aria-hidden="true" className={cn("egg-art-ground hero-texture", inset)} />;
}

/* The tiles of one egg word in a row. The page tone sits on a card of the claim sheet, the hero tone on a hero card.
   The tile of the new letter is red. In the sheet it is a ghost that pulses until the manager picks the word.
   The row is art, so a screen reader reads the count beside it instead. */
export function SlotRow({
  slots,
  tone,
  picked = false,
  landing = false,
  faded = false,
}: {
  slots: Slot[];
  tone: "page" | "hero";
  // True when the manager picked this word, so the new letter is a red tile that beats.
  picked?: boolean;
  // True on the hero card of a claim, so the red tile drops into its slot with a burst.
  landing?: boolean;
  // True on the card of a word with no open slot, so a held tile takes the muted fill of the faded card.
  faded?: boolean;
}) {
  // The sizes fit the 11 tiles of CORNERSTONE in one row on a 375px phone. The row is a grid of one column per letter,
  // and each column takes the tile width at most. On a narrower phone each column shrinks by the same amount, so the
  // row never wraps and never leaves its card: a wrap left two tiles alone on a second row. Each tile fills its column,
  // so the filled tile and the empty slots have one width. The gap keeps two dashed borders apart, so each empty slot
  // reads as its own box.
  const width = tone === "page" ? "1.625rem" : "1.5rem";
  const size = tone === "page" ? "h-6.5 text-row" : "h-7.5 text-body";
  return (
    <div
      aria-hidden="true"
      className="grid max-w-full gap-sp-2"
      style={{ gridTemplateColumns: `repeat(${slots.length}, minmax(0, ${width}))` }}
    >
      {slots.map((slot, index) => {
        const box = cn("relative inline-flex w-full items-center justify-center rounded-letter font-mono font-bold", size);
        if (slot.kind === "held") {
          return (
            <span key={index} className={cn(box, tone === "page" ? (faded ? "bg-mute text-page" : "bg-ink text-page") : "bg-on-dark text-band")}>
              {slot.letter}
            </span>
          );
        }
        if (slot.kind === "new") {
          if (tone === "page" && !picked) {
            return (
              <span key={index} className={cn(box, "egg-ghost border-2 border-dashed border-accent text-accent-ink")}>
                {slot.letter}
              </span>
            );
          }
          return (
            <span key={index} className={cn(box, "bg-accent text-on-dark shadow-orb", picked && "egg-beat", landing && "egg-land")}>
              {landing && <span className="egg-burst egg-burst-land" />}
              <span className="relative">{slot.letter}</span>
            </span>
          );
        }
        return (
          <span
            key={index}
            className={cn(box, "border-2 border-dashed", tone === "page" ? "border-rule" : "border-rule-dark")}
          />
        );
      })}
    </div>
  );
}
