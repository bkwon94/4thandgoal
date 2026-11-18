/**
 * The trade grade button sticks inside the page form and sits inline in the edit sheet footer.
 * The sticky bar rests at the end of its parent so it covers no content below.
 * The button wears the Ready halo, after the method of the Send Halo item: a ring that glows brighter as the trade fills.
 */
"use client";

import { PendingButton } from "@cpc/design/ui/pending-button";

type GradeBarProps = {
  // Each team gives and gets a player, so the trade can be graded.
  ready: boolean;
  grading: boolean;
  inEditSheet?: boolean;
  // The level of the Ready halo, from 0 to 1. It is 1 only when ready is true.
  level: number;
  // The Promise keeps the button pending until the grade settles.
  onGrade: () => Promise<void>;
};

export function GradeBar({ ready, grading, inEditSheet, level, onGrade }: GradeBarProps) {
  const button = (
    <div className={inEditSheet ? "relative flex-1" : "relative"}>
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
            so the halo shows the level with no orbit. At level 0 the button is off, so the arc stays out and does not spin. */}
        {level > 0 && (
          <span
            data-orbit=""
            className="absolute top-1/2 left-1/2 aspect-square w-[140%] -translate-x-1/2 -translate-y-1/2 animate-spin bg-[conic-gradient(transparent_0_70%,var(--color-accent-text)_85%,transparent_100%)] [animation-duration:3.4s] motion-reduce:hidden"
          />
        )}
      </span>
      {/* The off bar is a plain opaque surface with no opacity, so its text keeps the contrast of its pair. */}
      {/* A native disabled button leaves the tab order, so only the off bar is natively disabled. A grade that the finder
          starts has no press of this button to track, so the press does nothing while grading is true. */}
      {/* The label and the muted style of the off bar key off grading, not off the pending state of the press, for the
          same reason: a grade that the finder starts must show on the button too. */}
      <PendingButton
        disabled={!ready}
        pendingAnnouncement="Grading the trade"
        onClick={() => (grading ? undefined : onGrade())}
        className={`press relative min-h-touch w-full rounded-pill border px-sp-4 text-lead font-bold focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent disabled:cursor-not-allowed disabled:border-rule disabled:bg-raised disabled:text-mute aria-disabled:cursor-progress ${
          grading ? "cursor-progress border-rule bg-raised text-mute" : "cursor-pointer border-transparent bg-accent text-on-dark"
        }`}
      >
        {grading ? "Grading…" : inEditSheet ? "Regrade the Trade" : "Grade the Trade"}
      </PendingButton>
    </div>
  );

  if (inEditSheet) return button;

  return (
    <div className="sticky bottom-[calc(var(--spacing-sp-4)+env(safe-area-inset-bottom))] z-30 mx-auto mt-sp-4 max-w-page">
      {button}
    </div>
  );
}
