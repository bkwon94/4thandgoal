/**
 * The row of the header menu of the front door that opens the passphrase modal, so a manager can change the league
 * passphrase. The top band and the front door are apart in the page, so the row reaches the front door here.
 */
"use client";

import { KeyRoundIcon } from "lucide-react";
import { MenuRow } from "@cpc/design/shell/menu-sheet";

const listeners = new Set<() => void>();

/* The front door listens for a tap on the row while it is on the page. */
export function onPassphraseRow(listener: () => void): () => void {
  listeners.add(listener);
  return () => {
    listeners.delete(listener);
  };
}

export function PassphraseRow() {
  return <MenuRow icon={KeyRoundIcon} label="Passphrase" note="Change the league passphrase" onClick={() => listeners.forEach((listener) => listener())} />;
}
