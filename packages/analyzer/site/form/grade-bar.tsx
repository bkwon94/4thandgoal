/**
 * The "Grade the Trade" bar: one wide button fixed on the dock of a phone, and at the bottom of the screen from the tablet tier.
 * It stays in reach at every scroll. The analyzer page keeps the same space free under the page, so the bar covers no content.
 */
"use client";

type GradeBarProps = {
  // Each team gives and gets a player, so the trade can be graded.
  ready: boolean;
  grading: boolean;
  onGrade: () => void;
};

export function GradeBar({ ready, grading, onGrade }: GradeBarProps) {
  return (
    // The bar sits one step above the dock on a phone. The dock hides from the tablet tier, so the bar drops to the edge.
    <div className="fixed inset-x-sp-3 bottom-[calc(var(--spacing-dock-space)+var(--spacing-sp-2)+env(safe-area-inset-bottom))] z-30 mx-auto max-w-page tablet:bottom-[calc(var(--spacing-sp-4)+env(safe-area-inset-bottom))]">
      {/* The off bar is a plain opaque surface with no opacity, so its text keeps the contrast of its pair. */}
      <button
        type="button"
        disabled={!ready || grading}
        aria-busy={grading || undefined}
        onClick={onGrade}
        className="press min-h-touch w-full cursor-pointer rounded-pill border border-transparent bg-accent px-sp-4 text-lead font-bold text-on-dark focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent disabled:cursor-not-allowed disabled:border-rule disabled:bg-raised disabled:text-mute"
      >
        {grading ? "Grading…" : "Grade the Trade"}
      </button>
    </div>
  );
}
