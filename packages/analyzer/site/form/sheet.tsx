/**
 * The sheet of the analyzer: a short panel that rises from the bottom over the dimmed page, with a title and a close button.
 * It closes with the close button, Escape, a tap on the dim page, or a button of the caller, such as Done.
 */
"use client";

import { XIcon } from "lucide-react";
import type { ReactNode } from "react";
import { Dialog, DialogClose, DialogOverlay, DialogPopup, DialogPortal, DialogTitle } from "@cpc/design/ui/dialog";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { cn } from "@cpc/design/lib/utils";

type SheetProps = {
  open: boolean;
  title: string;
  // Each way out calls it. The caller keeps its state, so a close never drops a pick.
  onClose: () => void;
  children: ReactNode;
  // The row under the list, such as the Done button. It stays in view while the list scrolls.
  footer?: ReactNode;
};

export function Sheet({ open, title, onClose, children, footer }: SheetProps) {
  // The sheet rises with CSS. The one motion switch turns that off too.
  const still = useMotionOff() && "data-open:animate-none data-closed:animate-none";
  return (
    <Dialog
      open={open}
      onOpenChange={(next) => {
        if (!next) onClose();
      }}
    >
      <DialogPortal>
        {/* The dim page is a plain dark layer with no blur, so a tap on it reads as a tap outside the sheet. */}
        <DialogOverlay data-slot="sheet-backdrop" className={cn("bg-black/60 supports-backdrop-filter:backdrop-blur-none", still)} />
        <DialogPopup
          className={cn(
            "fixed inset-x-0 bottom-0 z-50 mx-auto flex max-h-[85dvh] w-full max-w-page flex-col rounded-t-hero border border-b-0 border-rule bg-page pb-[env(safe-area-inset-bottom)] text-ink outline-none",
            "duration-200 data-open:animate-in data-open:slide-in-from-bottom data-closed:animate-out data-closed:slide-out-to-bottom",
            still,
          )}
        >
          <div className="flex items-center justify-between gap-sp-3 px-sp-4 pt-sp-3">
            <DialogTitle className="m-0 min-w-0 truncate text-stat leading-stat font-bold">{title}</DialogTitle>
            <DialogClose
              aria-label="Close"
              className="press -mr-sp-2 grid size-touch flex-none cursor-pointer place-items-center rounded-pill text-mute hover:text-ink focus-visible:outline-2 focus-visible:outline-accent"
            >
              <XIcon aria-hidden="true" className="size-sp-5" />
            </DialogClose>
          </div>
          {/* min-h-0 lets the list shrink and scroll inside the sheet, so the title and the footer stay in view.
              Each child keeps its full height and the body scrolls instead. A row with its own overflow, such as the
              tabs that scroll sideways, has a min height of 0, so without shrink-0 it shrinks to 0 in a full sheet. */}
          <div className="flex min-h-0 flex-1 flex-col gap-sp-3 overflow-y-auto px-sp-4 py-sp-3 *:shrink-0">{children}</div>
          {footer && <div className="border-t border-rule px-sp-4 py-sp-3">{footer}</div>}
        </DialogPopup>
      </DialogPortal>
    </Dialog>
  );
}
