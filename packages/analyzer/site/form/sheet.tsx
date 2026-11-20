/**
 * The sheet of the analyzer: a short panel that rises from the bottom over the dimmed page, with a title and a close button.
 * It is the shared Sheet. It closes with a drag down, the close button, Escape, a tap on the dim page, or a button of the caller, such as Done.
 */
"use client";

import { XIcon } from "lucide-react";
import { useEffect, useRef, type ReactNode } from "react";
import {
  Sheet as SharedSheet,
  SheetBackdrop,
  SheetClose,
  SheetContent,
  SheetGrip,
  SheetTitle,
} from "@cpc/design/ui/sheet";

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
  const asked = useRef(false);
  useEffect(() => {
    asked.current = false;
  }, [open]);
  // The Drawer owns the slide, the drag, the dim, the focus trap, and the fade under reduced motion, so the one motion switch needs no class here.
  return (
    <SharedSheet
      side="bottom"
      open={open}
      onOpenChange={(next) => {
        // A drag close reports twice before the caller turns open off, and the caller must hear one close.
        if (!next && !asked.current) {
          asked.current = true;
          onClose();
        }
      }}
      container={typeof document === "undefined" ? undefined : document.body}
    >
      <SheetBackdrop />
      <SheetContent className="max-w-page rounded-t-hero border-rule bg-page mx-auto flex max-h-[85dvh] w-full flex-col border border-b-0 pb-[env(safe-area-inset-bottom)]">
        {/* The grip says "sheet" to a thumb. A drag down on the sheet closes it. */}
        <SheetGrip className="mt-sp-2 h-sp-1 w-sp-6" />
        <div className="gap-sp-3 px-sp-4 pt-sp-3 flex items-center justify-between">
          <SheetTitle className="text-stat leading-stat m-0 min-w-0 truncate font-bold">
            {title}
          </SheetTitle>
          <SheetClose
            aria-label="Close"
            className="press -mr-sp-2 size-touch rounded-pill text-mute hover:text-ink focus-visible:outline-accent grid flex-none cursor-pointer place-items-center focus-visible:outline-2"
          >
            <XIcon aria-hidden="true" className="size-sp-5" />
          </SheetClose>
        </div>
        {/* min-h-0 lets the list shrink and scroll inside the sheet, so the title and the footer stay in view.
            Each child keeps its full height and the body scrolls instead. A row with its own overflow, such as the
            tabs that scroll sideways, has a min height of 0, so without shrink-0 it shrinks to 0 in a full sheet. */}
        <div className="gap-sp-3 px-sp-4 py-sp-3 flex min-h-0 flex-1 flex-col overflow-y-auto overscroll-contain *:shrink-0">
          {children}
        </div>
        {footer && <div className="border-rule px-sp-4 py-sp-3 border-t">{footer}</div>}
      </SheetContent>
    </SharedSheet>
  );
}
