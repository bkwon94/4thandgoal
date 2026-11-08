/**
 * The Grade dial: four equal arcs, one for each part of the roster grade, each lit by the rank of the team on that part.
 * Each arc is a run of pill blades on a 210 degree arc, one blade per team, with the rank as text in the arc and the part and weight under it.
 */
"use client";

import { inView } from "framer-motion";
import { useEffect, useRef } from "react";
import { VIEW_MARGIN } from "@cpc/design/parts/reveal";
import { ordinal } from "@cpc/design/format/format";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { cn } from "@cpc/design/lib/utils";
import type { GradePart } from "../schema/manager-types";
import { GRADE_WEIGHTS } from "./grade-weights";
import { PART_NAMES } from "./part-names";

/* The drawing box of one arc, in viewBox units. The arc is 72% as high as it is wide, so the open end sits under the rank. */
const SIZE = 100;
const HEIGHT = SIZE * 0.72;
const CENTER = SIZE / 2;
/* The sweep of the arc in degrees, centered on the top, so the two ends dip a little under the line of the center. */
const SWEEP = 210;
/* The radius of the blades and the size of one blade. The ends of a blade are round, so each blade reads as a pill. */
const RADIUS = SIZE * 0.38;
const BLADE_W = SIZE * 0.07;
const BLADE_H = SIZE * 0.14;
/* The gap between two blades that light, in ms. The fill runs from the left end to the right end of the arc. */
const BLADE_STAGGER_MS = 22;

/* The count of lit blades: the count of teams plus one, minus the rank. Rank 1 lights every blade, and the last rank lights one. */
export function litCount(rank: number, teams: number): number {
  return Math.max(0, Math.min(teams, teams + 1 - rank));
}

/* The name a screen reader reads for one arc: the part, the rank, and the weight. */
function arcName(part: GradePart, teams: number): string {
  return `${PART_NAMES[part.key]}: ${ordinal(part.rank)} of ${teams}, ${GRADE_WEIGHTS[part.key]}% of the grade`;
}

/* The colors of each tone. The hero tone sits on the band color of a hero in both themes, so its text takes the on-dark
   roles on a plate, as every hero text does, and an unlit blade takes the rule color of the hero. */
const TONES = {
  page: { off: "bg-bar-off", ink: "text-ink", mute: "text-mute", plate: "" },
  hero: { off: "bg-rule-dark", ink: "text-on-dark", mute: "text-on-dark-2", plate: "plate" },
} as const;

type Tone = keyof typeof TONES;

type ArcProps = { part: GradePart; teams: number; size: "small" | "large"; off: boolean; tone: Tone };

/* One arc: the blades, the rank in the arc, and the part name and weight under it. */
function Arc({ part, teams, size, off, tone }: ArcProps) {
  const colors = TONES[tone];
  const lit = litCount(part.rank, teams);
  const step = teams > 1 ? SWEEP / (teams - 1) : 0;
  const large = size === "large";
  return (
    <div role="img" aria-label={arcName(part, teams)} className="flex flex-col items-center text-center">
      {/* The blades are HTML boxes, not SVG, because axe reads no contrast for text over an SVG node, and the rank sits
          inside the box of the arc. The box has the ratio of the drawing, so each blade keeps its place in viewBox units. */}
      <div className={cn("relative w-full", large ? "max-w-[10rem]" : "max-w-[6rem]")} style={{ aspectRatio: `${SIZE} / ${HEIGHT}` }}>
        {Array.from({ length: teams }, (_, i) => {
          const on = i < lit;
          return (
            <span
              key={i}
              data-blade
              data-on={on}
              // A lit blade stays dark while the dial waits for the view, then fills in a stagger from the left end.
              // With motion off the blade has no delay, and the reduced-motion rule of globals.css drops the duration.
              className={cn(
                "absolute rounded-pill transition-[background-color] duration-240 ease-[cubic-bezier(0.4,0,0.2,1)]",
                on ? cn("bg-accent", tone === "hero" ? "group-data-[wait]:bg-rule-dark" : "group-data-[wait]:bg-bar-off") : colors.off,
              )}
              style={{
                left: `${((CENTER - BLADE_W / 2) / SIZE) * 100}%`,
                top: `${((CENTER - RADIUS - BLADE_H / 2) / HEIGHT) * 100}%`,
                width: `${(BLADE_W / SIZE) * 100}%`,
                height: `${(BLADE_H / HEIGHT) * 100}%`,
                // The blade turns on the center of the arc, which sits RADIUS plus half a blade under the top of the blade.
                transformOrigin: `50% ${((RADIUS + BLADE_H / 2) / BLADE_H) * 100}%`,
                transform: `rotate(${-SWEEP / 2 + i * step}deg)`,
                ...(off ? {} : { transitionDelay: `${i * BLADE_STAGGER_MS}ms` }),
              }}
            />
          );
        })}
        {/* The rank sits in the open end of the arc, so a reader gets the rank without a count of blades. */}
        <div className="absolute inset-x-0 bottom-0 flex flex-col items-center leading-none">
          <span className={cn("font-extrabold tabular-nums", colors.ink, colors.plate, large ? "text-score" : "text-row")}>
            {ordinal(part.rank)}
          </span>
          {large && <span className={cn("mt-sp-1 text-meta tabular-nums", colors.mute, colors.plate)}>{`of ${teams}`}</span>}
        </div>
      </div>
      <div className={cn("mt-sp-2 text-meta leading-tight font-semibold", colors.ink, colors.plate)}>{PART_NAMES[part.key]}</div>
      <div className={cn("text-meta leading-tight tabular-nums", colors.mute, colors.plate)}>
        {large ? `${GRADE_WEIGHTS[part.key]}% of the grade` : `${GRADE_WEIGHTS[part.key]}%`}
      </div>
    </div>
  );
}

type GradeDialProps = {
  // The four parts of the grade, in the order projection, production, trade value, depth.
  parts: GradePart[];
  // The count of teams in the league, which is the count of blades of each arc.
  teams: number;
  // "large" is the 2x2 grid of Season So Far. "small" is one row of four, for a row of the Index list.
  size?: "small" | "large";
  // "page" sits on a card or the page. "hero" sits on the band color of a hero, such as the stage of the Index list.
  tone?: Tone;
};

export function GradeDial({ parts, teams, size = "large", tone = "page" }: GradeDialProps) {
  const off = useMotionOff();
  const ref = useRef<HTMLUListElement>(null);
  // The static HTML holds every arc lit, so a page with no script shows the grade.
  // Only a running script with motion allowed darkens the lit blades, then lights them once when the dial enters the viewport.
  // A browser with no IntersectionObserver never reports the viewport, so the dial stays lit and never waits.
  useEffect(() => {
    const list = ref.current;
    if (off || !list || typeof IntersectionObserver === "undefined") return;
    list.setAttribute("data-wait", "");
    // The callback returns nothing, so inView stops the watch after the first entry, and the fill plays once.
    const unwatch = inView(list, () => list.removeAttribute("data-wait"), { margin: VIEW_MARGIN });
    return () => {
      unwatch();
      list.removeAttribute("data-wait");
    };
  }, [off]);
  return (
    <ul
      ref={ref}
      aria-label="Grade Dial"
      className={cn(
        "group m-0 grid list-none p-0",
        size === "large" ? "grid-cols-2 gap-x-sp-4 gap-y-sp-6" : "grid-cols-4 gap-sp-2",
      )}
    >
      {parts.map((part) => (
        <li key={part.key}>
          <Arc part={part} teams={teams} size={size} off={off} tone={tone} />
        </li>
      ))}
    </ul>
  );
}
