/**
 * The dialog that asks for the league passphrase. It holds one password field and one submit button.
 * The parent decides when it is open and what happens with the value, so the dialog stores nothing itself.
 */
"use client";

import { useState, type FormEvent } from "react";
import { ErrorLine } from "@/components/parts/error-line";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useMotionOff } from "@/lib/motion";
import { cn } from "@/lib/utils";

type PassphraseDialogProps = {
  open: boolean;
  // A line above the field, for the case where the last passphrase was wrong.
  error?: string;
  onSubmit: (passphrase: string) => void;
};

export function PassphraseDialog({ open, error, onSubmit }: PassphraseDialogProps) {
  const [value, setValue] = useState("");
  // The shadcn dialog fades and zooms with CSS. The one motion switch turns that off too.
  const stillClass = useMotionOff() && "data-open:animate-none data-closed:animate-none";

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = value.trim();
    if (!trimmed) return;
    setValue("");
    onSubmit(trimmed);
  }

  /* No onOpenChange: the page has nothing to show without a passphrase, so Escape and a tap outside must not close it. */
  return (
    <Dialog open={open}>
      <DialogContent
        showCloseButton={false}
        overlayClassName={cn(stillClass)}
        className={cn("gap-sp-4 rounded-card p-gutter", stillClass)}
      >
        <DialogHeader>
          <DialogTitle className="text-stat leading-stat font-black uppercase">League Passphrase</DialogTitle>
          <DialogDescription className="text-body text-mute">The league passphrase. Ask a league member.</DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="flex flex-col gap-sp-3">
          {error && <ErrorLine>{error}</ErrorLine>}
          <Label htmlFor="passphrase" className="text-label font-bold tracking-wide uppercase">
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
      </DialogContent>
    </Dialog>
  );
}
