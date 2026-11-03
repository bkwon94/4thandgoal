/**
 * A red alert line for an error message. It renders a paragraph with role="alert".
 * The analyzer and the passphrase dialog share it.
 */
import type { ReactNode } from "react";

export function ErrorLine({ children }: { children: ReactNode }) {
  return (
    <p role="alert" className="m-0 text-body font-bold text-red-ink">
      {children}
    </p>
  );
}
