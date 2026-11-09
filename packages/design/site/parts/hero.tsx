/**
 * The hero: the one loud surface of a page, with the grid texture, the brand glow, and the four corner brackets.
 * It sits on the band color in both themes, so the hero stays dark in light. The page fills the six hero slots.
 */
import type { ReactNode } from "react";
import { cn } from "../lib/utils";
import { HeroSceneCanvas } from "./hero-scene";
import type { HeroScene } from "./scene-math";

/* The six hero slots, in the slot order. Only the title is required. An absent slot renders no element and no gap.
   Hero takes no children, so a page cannot pass free content and every hero keeps the one structure. */
type HeroSlots = {
  // The small uppercase line above the title, such as "7-9 · 9th of 12".
  eyebrow?: ReactNode;
  title: ReactNode;
  // One or two lines next to the title, such as the owner or the reason of a verdict.
  meta?: ReactNode;
  // The unique part of the page, such as the team rows or the grade. The page lays it out.
  feature?: ReactNode;
  // A row of tiles.
  stats?: ReactNode;
  // The links, the buttons, and the share bar.
  action?: ReactNode;
  // The level of the title element. The level changes the element, not the look.
  level?: 1 | 2;
  // The data of the hero scene. The page sets it on its first hero only. A hero with no scene keeps the static grid.
  scene?: HeroScene;
  children?: never;
};

type HeroProps = HeroSlots & {
  // The name of the region, for a screen reader, such as "Page not found" or "Matchup of the Week".
  label: string;
  className?: string;
};

/* The four corner brackets. Each sits one step in from its corner, so no text sits on a bracket. */
const BRACKETS = [
  "top-sp-3 left-sp-3 border-t-2 border-l-2",
  "top-sp-3 right-sp-3 border-t-2 border-r-2",
  "bottom-sp-3 left-sp-3 border-b-2 border-l-2",
  "bottom-sp-3 right-sp-3 border-b-2 border-r-2",
];

/* The fixed style of each text slot. A page cannot pass a class to a slot, so every hero reads as one family. */
const EYEBROW = "plate w-fit font-mono text-meta leading-tight font-bold tracking-wide text-accent-text uppercase";
const TITLE = "plate m-0 w-fit font-sans text-headline leading-tight font-light tracking-tight text-balance break-words";
const META = "plate w-fit max-w-measure tablet:max-w-[24rem] text-lead leading-body text-on-dark-2";

/* The slots on a phone stack in one column. From the tablet tier up the hero takes two rows: the eyebrow and the title
   top left with the meta top right, the feature in the open middle, then the stats bottom left and the action bottom
   right. The grid keeps the markup in the slot order, so a screen reader reads the same order at each width.
   The title has the priority in the top row: the meta column takes the width of the meta up to 40 percent of the hero,
   so a long meta wraps and the title keeps its width. The action takes the free width of the bottom row, so content
   with no width of its own, such as the share bar, fills it. */
function Slots({ eyebrow, title, meta, feature, stats, action, level = 1, scene }: HeroSlots) {
  const Heading = level === 1 ? "h1" : "h2";
  return (
    <div className="flex flex-col gap-sp-6 tablet:grid tablet:grid-cols-[minmax(0,1fr)_fit-content(40%)] tablet:gap-x-sp-6">
      <div className="flex flex-col gap-sp-2 tablet:col-start-1">
        {eyebrow !== undefined && (
          <div data-hero-slot="eyebrow" className={EYEBROW}>
            {eyebrow}
          </div>
        )}
        <Heading data-hero-slot="title" className={TITLE}>
          {title}
        </Heading>
      </div>
      {meta !== undefined && (
        <div data-hero-slot="meta" className={cn(META, "tablet:col-start-2 tablet:justify-self-end")}>
          {meta}
        </div>
      )}
      {/* The scene is a band under the eyebrow, the title, and the meta on a phone, so the reader gets the words first
          (Brian, 2026-11-08). It fills the open middle from the tablet tier up. It has its own row, so no light sits under
          text (decision 06). */}
      {scene !== undefined && (
        <div className="tablet:col-span-2">
          <HeroSceneCanvas scene={scene} />
        </div>
      )}
      {feature !== undefined && (
        <div data-hero-slot="feature" className="tablet:col-span-2">
          {feature}
        </div>
      )}
      {(stats !== undefined || action !== undefined) && (
        <div className="relative flex flex-col gap-sp-6 tablet:col-span-2 tablet:flex-row tablet:items-end tablet:justify-between">
          {/* The faded hairline above the stats, from the tablet tier up only. It sits in the middle of the gap above
              the row and is transparent at both ends. */}
          {stats !== undefined && (
            <div
              aria-hidden="true"
              data-hero-rule
              className="pointer-events-none absolute inset-x-0 -top-sp-3 hidden h-px bg-linear-to-r from-transparent via-rule-dark to-transparent tablet:block"
            />
          )}
          {stats !== undefined && (
            <div data-hero-slot="stats" className="flex flex-wrap gap-sp-2">
              {stats}
            </div>
          )}
          {action !== undefined && (
            <div data-hero-slot="action" className="flex flex-wrap items-center gap-sp-2 tablet:grow tablet:justify-end">
              {action}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

/* The text of a hero sits on a plate of the band color (the plate utility of globals.css). The plate keeps the grid and
   the glow from under each letter, so the contrast of the text is the contrast of its role pair, and axe can read it.
   The art layer comes first in the markup and the content box is relative, so the content paints over the art.
   The frame takes free content for the parts of the egg hunt only: the find card, the end card, and the word cards.
   Each has its own tuned layout over the ground of the egg hunt. Every other hero uses Hero and its six slots. */
export function HeroFrame({ label, className, children }: { label: string; className?: string; children: ReactNode }) {
  return (
    <section
      aria-label={label}
      className={cn(
        "relative overflow-hidden rounded-hero border border-rule-dark bg-band px-hero-x py-hero-y text-on-dark",
        className,
      )}
    >
      <div aria-hidden="true">
        <div data-hero-art="texture" className="hero-texture pointer-events-none absolute inset-0" />
        {BRACKETS.map((place) => (
          <span
            key={place}
            data-hero-art="bracket"
            className={`pointer-events-none absolute size-bracket border-on-dark-muted ${place}`}
          />
        ))}
      </div>
      <div className="relative">{children}</div>
    </section>
  );
}

export function Hero({ label, className, ...slots }: HeroProps) {
  return (
    <HeroFrame label={label} className={className}>
      <Slots {...slots} />
    </HeroFrame>
  );
}
