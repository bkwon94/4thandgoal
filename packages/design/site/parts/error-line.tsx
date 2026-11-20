/**
 * A red alert line for an error message. It renders a paragraph with role="alert".
 * The analyzer and the passphrase dialog share it.
 * Use it when: a form or a dialog shows one error message.
 * Do not use it when: the text is not an error. Use `Blurb`.
 */
import type { ReactNode } from "react";

export function ErrorLine({ children }: { children: ReactNode }) {
  return (
    <p role="alert" className="text-body text-accent-ink m-0 font-bold">
      {children}
    </p>
  );
}
