/**
 * The sheet that asks for the league passphrase before the first action of the front door, and again after a wrong
 * passphrase. It is the shared Sheet, like the team sheet, and it closes by "Not now", Escape, or a drag down.
 */
"use client";

import { PendingButton } from "@cpc/design/ui/pending-button";
import { ArrowUpIcon } from "lucide-react";
import { useRef, useState } from "react";
import { Sheet, SheetBackdrop, SheetContent, SheetGrip, SheetTitle } from "@cpc/design/ui/sheet";
import { useKeyboardField } from "@cpc/design/shell/keyboard";

/* The ask box needs the passphrase, so only managers of the league ask. The browser keeps it under the same key as the
   trade analyzer, so a manager types it once per device. `wrong` is true after the API turned the last one down. The
   Drawer owns the slide, the drag, the dim, the stop of the page scroll, the focus trap, Escape, and the fade under
   reduced motion. */
export function PassphraseSheet({
  siteName,
  wrong,
  onPassphrase,
  onClose,
}: {
  siteName: string;
  wrong: boolean;
  onPassphrase: (value: string) => void;
  onClose: () => void;
}) {
  const [value, setValue] = useState("");
  const typed = value.trim();
  // The field opens the keyboard as the ask box does, so the root marks the keyboard open and the pad of the home bar drops.
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
        // The Drawer lifts its viewport by the --keyboard-inset that it reads from the visual viewport, so the field sits
        // right above the keyboard on iOS. The Drawer sets the top of the content inline, so a bottom offset here would
        // squash the content to its border and push the field off the screen.
        className="max-w-sheet rounded-t-hero border-rule bg-card shadow-sheet mx-auto flex w-full flex-col border border-b-0 p-0"
      >
        <SheetGrip className="mt-sp-2 h-sp-1 w-sp-6" />
        <div className="gap-sp-1 px-sp-5 pt-sp-4 pb-sp-3 flex flex-none flex-col">
          <span className="text-meta tracking-caps text-mute font-mono leading-tight uppercase">
            {siteName}
          </span>
          <SheetTitle className="text-score m-0 leading-tight font-bold tracking-tight">
            What is the league passphrase?
          </SheetTitle>
          <p id="passphrase-line" className="text-lead leading-body text-ink-2 m-0">
            {wrong
              ? "That passphrase did not match. Type the league passphrase again."
              : "Type it once. This device keeps it."}
          </p>
        </div>
        {/* The end of the sheet keeps the home bar of an iPhone clear. The keyboard covers the home bar, so the pad drops then. */}
        {/* oxlint-disable-next-line design/no-arbitrary-value -- the home bar of an iPhone needs the safe-area inset, which no token adds to a step */}
        <div className="gap-sp-2 px-sp-5 pt-sp-1 tablet:pb-sp-4 flex flex-col pb-[calc(var(--spacing-sp-4)+var(--spacing-door-safe))]">
          <form
            aria-label="League passphrase"
            className="min-h-ask gap-sp-2 rounded-pill border-rule bg-page py-sp-1 pr-sp-1 pl-sp-5 focus-within:border-ink flex items-center border transition-[border-color] duration-150"
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
              className="text-lead text-ink placeholder:text-mute min-w-0 flex-1 bg-transparent leading-tight outline-none focus-visible:outline-none"
            />
            <PendingButton
              type="submit"
              aria-label="Use this passphrase"
              disabled={!typed}
              className="press size-send bg-accent text-on-dark disabled:bg-raised disabled:text-mute flex flex-none items-center justify-center rounded-full transition-colors duration-150"
            >
              <ArrowUpIcon aria-hidden className="size-sp-5" strokeWidth={2.25} />
            </PendingButton>
          </form>
          <PendingButton
            type="button"
            onClick={close}
            className="press min-h-touch rounded-pill px-sp-3 text-meta text-mute hover-fine:text-ink flex items-center self-center leading-tight font-semibold"
          >
            Not now
          </PendingButton>
        </div>
      </SheetContent>
    </Sheet>
  );
}
