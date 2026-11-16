/**
 * The sheet that asks for the league passphrase before the first action of the front door, and again after a wrong
 * passphrase. It is the shared Sheet, like the team sheet, and it closes by "Not now", Escape, or a drag down.
 */
"use client";

import { ArrowUpIcon } from "lucide-react";
import { useRef, useState } from "react";
import { Sheet, SheetBackdrop, SheetContent, SheetGrip, SheetTitle } from "@cpc/design/ui/sheet";
import { useKeyboardField } from "@cpc/design/shell/keyboard";

/* The ask box needs the passphrase, so only managers of the league ask. The browser keeps it under the same key as the
   trade analyzer, so a manager types it once per device. `wrong` is true after the API turned the last one down. The
   Drawer owns the slide, the drag, the dim, the stop of the page scroll, the focus trap, Escape, and the fade under
   reduced motion. */
export function PassphraseSheet({ siteName, wrong, onPassphrase, onClose }: { siteName: string; wrong: boolean; onPassphrase: (value: string) => void; onClose: () => void }) {
  const [value, setValue] = useState("");
  const typed = value.trim();
  // The field opens the keyboard as the ask box does, so the foot of the sheet moves above the keyboard for it.
  const keyboard = useKeyboardField();
  // A drag close reports twice before the parent drops the sheet, and the parent must hear one close.
  const asked = useRef(false);
  const close = () => {
    if (asked.current) return;
    asked.current = true;
    onClose();
  };

  return (
    <Sheet
      side="bottom"
      open
      onOpenChange={(next) => {
        if (!next) close();
      }}
      container={typeof document === "undefined" ? undefined : document.body}
    >
      <SheetBackdrop />
      <SheetContent
        aria-describedby="passphrase-line"
        // The Drawer content is a relative box at the foot of the screen. Its bottom offset is --spacing-door-foot, which
        // holds the height of the keyboard while a field has the focus, so the field sits right above the keyboard on
        // iOS (globals.css). A transform moves the drag, so the offset and the drag do not meet.
        style={{ bottom: "var(--spacing-door-foot)" }}
        className="mx-auto flex w-full max-w-sheet flex-col rounded-t-hero border border-b-0 border-rule bg-card p-0 shadow-sheet"
      >
        <SheetGrip className="mt-sp-2 h-sp-1 w-sp-6" />
        <div className="flex flex-none flex-col gap-sp-1 px-sp-5 pt-sp-4 pb-sp-3">
          <span className="font-mono text-meta leading-tight tracking-caps text-mute uppercase">{siteName}</span>
          <SheetTitle className="m-0 text-score leading-tight font-bold tracking-tight">What is the league passphrase?</SheetTitle>
          <p id="passphrase-line" className="m-0 text-lead leading-body text-ink-2">
            {wrong ? "That passphrase did not match. Type the league passphrase again." : "Type it once. This device keeps it."}
          </p>
        </div>
        {/* The end of the sheet keeps the home bar of an iPhone clear. The keyboard covers the home bar, so the pad drops then. */}
        <div className="flex flex-col gap-sp-2 px-sp-5 pt-sp-1 pb-[calc(var(--spacing-sp-4)+var(--spacing-door-safe))] tablet:pb-sp-4">
          <form
            aria-label="League passphrase"
            className="flex min-h-ask items-center gap-sp-2 rounded-pill border border-rule bg-page py-sp-1 pr-sp-1 pl-sp-5 transition-[border-color] duration-150 focus-within:border-ink"
            onSubmit={(event) => {
              event.preventDefault();
              if (typed) onPassphrase(typed);
            }}
          >
            <input
              type="password"
              value={value}
              onChange={(event) => setValue(event.target.value)}
              aria-label="League passphrase"
              placeholder="League passphrase"
              autoComplete="current-password"
              // The sheet follows a question or a tap, so the next keys go to the field.
              autoFocus
              enterKeyHint="done"
              onFocus={keyboard.onFocus}
              onBlur={keyboard.onBlur}
              className="min-w-0 flex-1 bg-transparent text-lead leading-tight text-ink outline-none placeholder:text-mute focus-visible:outline-none"
            />
            <button
              type="submit"
              aria-label="Use this passphrase"
              disabled={!typed}
              className="press flex size-send flex-none items-center justify-center rounded-full bg-accent text-on-dark transition-colors duration-150 disabled:bg-raised disabled:text-mute"
            >
              <ArrowUpIcon aria-hidden className="size-sp-5" strokeWidth={2.25} />
            </button>
          </form>
          <button
            type="button"
            onClick={close}
            className="press flex min-h-touch items-center self-center rounded-pill px-sp-3 text-meta leading-tight font-semibold text-mute hover-fine:text-ink"
          >
            Not now
          </button>
        </div>
      </SheetContent>
    </Sheet>
  );
}
