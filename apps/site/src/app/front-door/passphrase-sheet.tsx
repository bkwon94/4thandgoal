/**
 * The modal that asks for the league passphrase before the first action of the front door, after a wrong passphrase,
 * and from the row of the header menu. It has the look and the motion of the team sheet, and it closes by "Not now" or Escape.
 */
"use client";

import { motion } from "framer-motion";
import { useEffect, useRef, useState, type KeyboardEvent } from "react";
import { ArrowUpIcon } from "lucide-react";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { useKeyboardField } from "@cpc/design/shell/keyboard";
import { FAST, QUICK, SHEET_SPRING, SMOOTH, fadeIn } from "./motion";

/* The ask box needs the passphrase, so only managers of the league ask. The browser keeps it under the same key as the
   trade analyzer, so a manager types it once per device. `wrong` is true after the API turned the last one down. */
export function PassphraseSheet({ siteName, wrong, onPassphrase, onClose }: { siteName: string; wrong: boolean; onPassphrase: (value: string) => void; onClose: () => void }) {
  const off = useMotionOff();
  const [value, setValue] = useState("");
  const typed = value.trim();
  const panel = useRef<HTMLDivElement>(null);
  // The field opens the keyboard as the ask box does, so the foot of the modal moves above the keyboard for it.
  const keyboard = useKeyboardField();

  // The field takes the focus by autoFocus, so the modal takes it only when the field has none. The page under the
  // modal stops its scroll while the modal is open.
  useEffect(() => {
    if (!panel.current?.contains(document.activeElement)) panel.current?.focus({ preventScroll: true });
    const root = document.documentElement;
    const before = root.style.overflow;
    root.style.overflow = "hidden";
    return () => {
      root.style.overflow = before;
    };
  }, []);

  // The modal holds the focus, so Tab cycles inside it. Escape closes it, as "Not now" does.
  const trap = (event: KeyboardEvent<HTMLDivElement>) => {
    if (event.key === "Escape") return onClose();
    if (event.key !== "Tab") return;
    const parts = [...(panel.current?.querySelectorAll<HTMLElement>("input, button:not(:disabled)") ?? [])];
    const first = parts[0];
    const last = parts.at(-1);
    if (!first || !last) return;
    if (event.shiftKey && (document.activeElement === first || document.activeElement === panel.current)) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  };

  return (
    <motion.div
      // The foot of the modal is --spacing-door-foot, which holds the height of the keyboard while a field has the focus,
      // so the field sits right above the keyboard on iOS (globals.css).
      className="fixed inset-x-0 top-0 bottom-door-foot z-50 flex items-end justify-center bg-scrim tablet:items-center tablet:p-sp-6"
      // With motion off, the scrim and the modal show at once, so a scan of the floor never reads them in mid-fade.
      initial={off ? false : { opacity: 0 }}
      animate={{ opacity: 1, transition: fadeIn(FAST) }}
      exit={{ opacity: 0, transition: fadeIn(FAST) }}
    >
      <motion.div
        ref={panel}
        role="dialog"
        aria-modal="true"
        aria-labelledby="passphrase-title"
        aria-describedby="passphrase-line"
        tabIndex={-1}
        onKeyDown={trap}
        className="flex w-full max-w-sheet flex-col rounded-t-hero border border-b-0 border-rule bg-card text-ink shadow-sheet outline-none tablet:rounded-hero tablet:border-b"
        initial={off ? false : { y: "100%" }}
        animate={off ? { opacity: 1, transition: fadeIn(FAST) } : { y: 0, transition: SHEET_SPRING }}
        exit={off ? { opacity: 0, transition: fadeIn(QUICK) } : { y: "100%", transition: { duration: 0.35, ease: SMOOTH } }}
      >
        <span aria-hidden className="mx-auto mt-sp-2 h-sp-1 w-sp-6 flex-none rounded-pill bg-rule tablet:hidden" />
        <div className="flex flex-none flex-col gap-sp-1 px-sp-5 pt-sp-4 pb-sp-3">
          <span className="font-mono text-meta leading-tight tracking-caps text-mute uppercase">{siteName}</span>
          <h2 id="passphrase-title" className="m-0 text-score leading-tight font-bold tracking-tight">
            What is the league passphrase?
          </h2>
          <p id="passphrase-line" className="m-0 text-lead leading-body text-ink-2">
            {wrong ? "That passphrase did not match. Type the league passphrase again." : "Type it once. This device keeps it."}
          </p>
        </div>
        {/* The end of the modal keeps the home bar of an iPhone clear. The keyboard covers the home bar, so the pad drops then. */}
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
              // The modal follows a question, a Topic tap, or the menu row, so the next keys go to the field.
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
            onClick={onClose}
            className="press flex min-h-touch items-center self-center rounded-pill px-sp-3 text-meta leading-tight font-semibold text-mute hover-fine:text-ink"
          >
            Not now
          </button>
        </div>
      </motion.div>
    </motion.div>
  );
}
