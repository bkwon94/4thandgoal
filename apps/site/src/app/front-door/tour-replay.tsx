/**
 * The two replay controls of the Tour: the "Show the tour" row of the menu sheet, and the "?" button of the top band on desktop.
 * The front door page passes them into the shell through its slots, so the shell names no Tour.
 */
"use client";

import { PendingButton } from "@cpc/design/ui/pending-button";
import { CircleHelpIcon } from "lucide-react";
import { useCloseMenuSheet } from "@cpc/design/shell/menu-sheet";
import { replayTour } from "./tour";

/* The row at the foot of the menu sheet. It closes the sheet first, and the Tour starts once the sheet finishes its
   exit, so the Tour never starts under the modal sheet. It has the look of a row of the pages. */
export function TourRow() {
  const closeThen = useCloseMenuSheet();
  return (
    <PendingButton
      type="button"
      onClick={() => (closeThen ? closeThen(replayTour) : replayTour())}
      className="press min-h-dock gap-sp-3 rounded-tile px-sp-2 text-ink hover-fine:bg-raised flex w-full items-center text-left"
    >
      <span
        aria-hidden
        className="size-touch rounded-tile bg-raised text-ink-2 flex flex-none items-center justify-center"
      >
        <CircleHelpIcon className="size-sp-5" />
      </span>
      <span className="text-body truncate leading-tight font-semibold">Show the tour</span>
    </PendingButton>
  );
}

/* The "?" button beside the theme button. The desktop tier shows no menu button, so the button shows only there, and a
   phone and a tablet reach the Tour from the menu sheet. It hides with scripts off, as the theme button does. */
export function TourButton() {
  return (
    <PendingButton
      type="button"
      aria-label="Show the tour"
      onClick={replayTour}
      className="press size-touch text-ink hover-fine:text-accent-ink desktop:flex hidden flex-none items-center justify-center [@media(scripting:none)]:hidden"
    >
      <CircleHelpIcon aria-hidden className="size-sp-5" />
    </PendingButton>
  );
}
