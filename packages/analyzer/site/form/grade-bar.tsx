/**
 * The "Grade the Trade" bar: one wide button fixed on the dock of a phone and a tablet, and at the bottom of the screen from the desktop tier.
 * It stays in reach at every scroll. The analyzer page keeps the same space free under the page, so the bar covers no content.
 * The button wears the Ready halo, after the method of the Send Halo item: a ring that glows brighter as the trade fills.
 */
"use client";

type GradeBarProps = {
  // Each team gives and gets a player, so the trade can be graded.
  ready: boolean;
  grading: boolean;
  // The level of the Ready halo, from 0 to 1. It is 1 only when ready is true.
  level: number;
  onGrade: () => void;
};

export function GradeBar({ ready, grading, level, onGrade }: GradeBarProps) {
  return (
    // The bar sits one step above the dock on a phone and a tablet. The dock hides from the desktop tier, so the bar drops to the edge.
    <div className="fixed inset-x-sp-3 bottom-[calc(var(--spacing-dock-space)+var(--spacing-sp-2)+env(safe-area-inset-bottom))] z-30 mx-auto max-w-page desktop:bottom-[calc(var(--spacing-sp-4)+env(safe-area-inset-bottom))]">
      <div className="relative">
        {/* The Ready halo: an accent ring 2px out from the button, with the brand glow around it. Its opacity is the level,
            so the brightness tells how close the trade is to ready. The accent fill holds 3 to 1 against the page in both
            themes, so the ring reads in the light theme too. Only the opacity changes, and reduced motion makes it instant. */}
        <span
          aria-hidden="true"
          data-halo=""
          data-level={level.toFixed(3)}
          style={{ opacity: level }}
          className="pointer-events-none absolute -inset-sp-0 overflow-hidden rounded-pill bg-accent shadow-orb transition-opacity duration-300 ease-out"
        >
          {/* The sweep of the item: a light arc that orbits the ring. Only its transform moves. Reduced motion hides it,
              so the halo shows the level with no orbit. */}
          <span className="absolute top-1/2 left-1/2 aspect-square w-[140%] -translate-x-1/2 -translate-y-1/2 animate-spin bg-[conic-gradient(transparent_0_70%,var(--color-accent-text)_85%,transparent_100%)] [animation-duration:3.4s] motion-reduce:hidden" />
        </span>
        {/* The off bar is a plain opaque surface with no opacity, so its text keeps the contrast of its pair. */}
        <button
          type="button"
          disabled={!ready || grading}
          aria-busy={grading || undefined}
          onClick={onGrade}
          className="press relative min-h-touch w-full cursor-pointer rounded-pill border border-transparent bg-accent px-sp-4 text-lead font-bold text-on-dark focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent disabled:cursor-not-allowed disabled:border-rule disabled:bg-raised disabled:text-mute"
        >
          {grading ? "Grading…" : "Grade the Trade"}
        </button>
      </div>
    </div>
  );
}
