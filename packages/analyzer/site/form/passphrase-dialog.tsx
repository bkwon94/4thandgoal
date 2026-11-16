/**
 * The sheet that asks for the league passphrase. It is the shared Sheet. It holds one password field and one submit button.
 * The parent decides when it is open and what happens with the value, so the sheet stores nothing itself.
 */
"use client";

import { useState, type FormEvent } from "react";
import { ErrorLine } from "@cpc/design/parts/error-line";
import { Button } from "@cpc/design/ui/button";
import { Input } from "@cpc/design/ui/input";
import { Label } from "@cpc/design/ui/label";
import { Sheet, SheetBackdrop, SheetContent, SheetTitle } from "@cpc/design/ui/sheet";

type PassphraseDialogProps = {
  open: boolean;
  // A line above the field, for the case where the last passphrase was wrong.
  error?: string;
  onSubmit: (passphrase: string) => void;
};

export function PassphraseDialog({ open, error, onSubmit }: PassphraseDialogProps) {
  const [value, setValue] = useState("");

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = value.trim();
    if (!trimmed) return;
    setValue("");
    onSubmit(trimmed);
  }

  /* dismissible is false: the page has nothing to show without a passphrase, so Escape, a tap on the dim, and a drag
     must not close it. The sheet has no grip, because it does not drag. The Drawer owns the slide, the dim, the focus
     trap, and the fade under reduced motion. */
  return (
    <Sheet side="bottom" open={open} dismissible={false} container={typeof document === "undefined" ? undefined : document.body}>
      <SheetBackdrop />
      <SheetContent
        aria-describedby="passphrase-line"
        className="mx-auto flex w-full max-w-sheet flex-col gap-sp-4 rounded-t-hero border border-b-0 border-rule bg-card p-gutter pb-[calc(var(--spacing-gutter)+env(safe-area-inset-bottom))] shadow-sheet"
      >
        <div className="flex flex-col gap-sp-2">
          <SheetTitle className="m-0 text-stat leading-stat font-black uppercase">League Passphrase</SheetTitle>
          {/* One short line: axe reads the page under the sheet for each line of text, and two lines over different parts
              of the page leave the contrast as incomplete, which fails the readability floor. */}
          <p id="passphrase-line" className="m-0 text-lead text-mute">Ask a league member for it.</p>
        </div>
        <form onSubmit={handleSubmit} className="flex flex-col gap-sp-3">
          {error && <ErrorLine>{error}</ErrorLine>}
          <Label htmlFor="passphrase" className="min-h-touch text-meta font-bold tracking-wide uppercase">
            Passphrase
          </Label>
          <Input
            id="passphrase"
            type="password"
            autoComplete="off"
            value={value}
            onChange={(event) => setValue(event.target.value)}
            className="h-touch rounded-card px-sp-3 text-lead"
          />
          <Button type="submit" className="press h-touch rounded-card text-lead font-bold">
            Continue
          </Button>
        </form>
      </SheetContent>
    </Sheet>
  );
}
