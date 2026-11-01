/**
 * The placeholder of the trade form while the teams load: the heading line, the two sides, and the button.
 * Each side has the label and the height of a real team picker, so the page does not jump when the teams arrive.
 */
"use client";

import { SIDE_TITLES } from "@/components/analyzer/trade-form";
import { useMotionOff } from "@/lib/motion";
import { cn } from "@/lib/utils";

/* The form starts with two sides, so the placeholder shows their titles. */
const SIDES = SIDE_TITLES.slice(0, 2);

/* One row in the shape of a team picker: the avatar circle and the team name line. */
function SkeletonRow() {
  return (
    <div className="flex h-touch items-center gap-sp-3 rounded-card bg-gry px-sp-3">
      <div className="size-avatar flex-none rounded-full bg-wht" />
      <div className="h-sp-3 w-1/2 rounded-sm bg-wht" />
    </div>
  );
}

export function TeamsSkeleton() {
  const off = useMotionOff();
  return (
    <div
      role="status"
      aria-busy="true"
      aria-label="Loading teams"
      // The pulse tells the reader the page works. With motion off, the rows stay still.
      // From the tablet tier the sides sit side by side, as in the form.
      className={cn("flex flex-col gap-sp-5 tablet:grid tablet:grid-cols-2", !off && "animate-pulse")}
    >
      {/* A blank line in the heading type, so the heading takes its real height. */}
      <p aria-hidden="true" className="m-0 text-stat leading-stat font-black tablet:col-span-2">
        <span className="inline-block w-1/2 rounded-sm bg-gry">&nbsp;</span>
      </p>
      {SIDES.map((label) => (
        <div key={label} aria-hidden="true" className="flex flex-col gap-sp-3">
          <p className="m-0 p-0 text-label font-bold tracking-wide text-red-ink uppercase">{label}</p>
          <SkeletonRow />
        </div>
      ))}
      <div aria-hidden="true" className="h-touch rounded-card bg-gry tablet:col-span-2" />
    </div>
  );
}
