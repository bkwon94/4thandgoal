/**
 * The sheet that asks for Your team on the first visit, then for the league passphrase when the browser keeps none. It
 * lists the teams of the league by name, with no skip, no close, and no login, because every Suggestion of the front door
 * comes from Your team (decision 08). The passphrase step comes back on a wrong passphrase and from the header menu.
 */
"use client";

import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useRef, useState, type KeyboardEvent } from "react";
import { ArrowUpIcon } from "lucide-react";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { useKeyboardField } from "@cpc/design/shell/keyboard";
import type { DoorTeam } from "@/lib/data/front-door-data";
import { FAST, QUICK, SHEET_SPRING, SMOOTH, fadeIn, riseIn, staggerOf } from "./motion";

/* The check lands, then the sheet leaves, so the tap reads as done before the page changes. */
const PICK_BEAT_MS = 420;

/* 1st, 2nd, 3rd, 11th, 12th: the place of a team in the standings. */
function ordinal(n: number): string {
  const tens = n % 100;
  if (tens >= 11 && tens <= 13) return `${n}th`;
  return `${n}${{ 1: "st", 2: "nd", 3: "rd" }[n % 10] ?? "th"}`;
}

/* The passphrase step: `wrong` after the API turned the last one down. Only a step that the header menu opened has
   `leave`, the way out with no new passphrase. A question or a first visit needs the passphrase, so its step has none. */
export type PassphraseStep = { wrong: boolean; leave?: { label: string; onLeave: () => void }; onPassphrase: (value: string) => void };

export function TeamSheet({
  siteName,
  teams,
  current,
  onPick,
  passphrase = null,
}: {
  siteName: string;
  teams: DoorTeam[];
  current: number | null;
  onPick: (id: number) => void;
  // The passphrase step in place of the list of teams, or null for the list.
  passphrase?: PassphraseStep | null;
}) {
  const off = useMotionOff();
  const [chosen, setChosen] = useState<number | null>(current);
  const panel = useRef<HTMLDivElement>(null);

  // The sheet takes the focus, and the page under it stops its scroll while the sheet is open. A passphrase step that
  // opens the sheet focuses its own field first, so the sheet leaves the focus there.
  useEffect(() => {
    if (!panel.current?.contains(document.activeElement)) panel.current?.focus({ preventScroll: true });
    const root = document.documentElement;
    const before = root.style.overflow;
    root.style.overflow = "hidden";
    return () => {
      root.style.overflow = before;
    };
  }, []);

  const choose = (id: number) => {
    if (chosen !== null && chosen !== current) return;
    setChosen(id);
    window.setTimeout(() => onPick(id), PICK_BEAT_MS);
  };

  // The sheet is modal, so Tab cycles inside it. The list of teams has no close, so Escape leaves only a passphrase step
  // with a way out.
  const trap = (event: KeyboardEvent<HTMLDivElement>) => {
    if (event.key === "Escape") passphrase?.leave?.onLeave();
    if (event.key !== "Tab") return;
    const buttons = [...(panel.current?.querySelectorAll<HTMLElement>("button:not(:disabled), input") ?? [])];
    const first = buttons[0];
    const last = buttons.at(-1);
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
      // The foot of the sheet is --spacing-door-foot, which holds the height of the keyboard while a field has the focus, so the
      // passphrase field sits right above the keyboard on iOS (globals.css).
      className="fixed inset-x-0 top-0 bottom-door-foot z-50 flex items-end justify-center bg-scrim tablet:items-center tablet:p-sp-6"
      // With motion off, the scrim and the sheet show at once, so a scan of the floor never reads them in mid-fade.
      initial={off ? false : { opacity: 0 }}
      animate={{ opacity: 1, transition: fadeIn(FAST) }}
      exit={{ opacity: 0, transition: fadeIn(FAST) }}
    >
      <motion.div
        ref={panel}
        role="dialog"
        aria-modal="true"
        aria-labelledby={passphrase ? "passphrase-title" : "your-team-title"}
        aria-describedby={passphrase ? "passphrase-line" : "your-team-line"}
        tabIndex={-1}
        onKeyDown={trap}
        className="flex max-h-[88dvh] w-full max-w-sheet flex-col rounded-t-hero border border-b-0 border-rule bg-card text-ink shadow-sheet outline-none tablet:max-h-[80dvh] tablet:rounded-hero tablet:border-b"
        initial={off ? false : { y: "100%" }}
        animate={off ? { opacity: 1, transition: fadeIn(FAST) } : { y: 0, transition: SHEET_SPRING }}
        exit={off ? { opacity: 0, transition: fadeIn(QUICK) } : { y: "100%", transition: { duration: 0.35, ease: SMOOTH } }}
      >
        {/* The grabber says "sheet" to a thumb. The sheet has no close, so the grabber drags nothing. */}
        <span aria-hidden className="mx-auto mt-sp-2 h-sp-1 w-sp-6 flex-none rounded-pill bg-rule tablet:hidden" />
        {/* The steps cross-fade in the same sheet, so the passphrase reads as the next step of the team, not a new sheet. */}
        <AnimatePresence mode="wait" initial={false}>
        {passphrase ? (
          <motion.div key="passphrase" className="flex min-h-0 flex-col" {...riseIn(off)} exit={{ opacity: 0, transition: fadeIn(QUICK) }}>
            <PassphraseForm siteName={siteName} step={passphrase} />
          </motion.div>
        ) : (
        <motion.div key="team" className="flex min-h-0 flex-col" initial={false} exit={{ opacity: 0, transition: fadeIn(QUICK) }}>
        <div className="flex flex-none flex-col gap-sp-1 px-sp-5 pt-sp-4 pb-sp-3">
          <span className="font-mono text-meta leading-tight tracking-caps text-mute uppercase">{siteName}</span>
          <h2 id="your-team-title" className="m-0 text-score leading-tight font-bold tracking-tight">
            Which team is yours?
          </h2>
          <p id="your-team-line" className="m-0 text-lead leading-body text-ink-2">
            Pick once. This page then answers for your team.
          </p>
        </div>
        {/* The list scrolls inside the sheet. Its end keeps the home bar of an iPhone clear. */}
        <ul className="m-0 flex min-h-0 list-none flex-col gap-sp-1 overflow-y-auto overscroll-contain px-sp-3 pt-sp-1 pb-[calc(var(--spacing-sp-4)+env(safe-area-inset-bottom))] tablet:pb-sp-4">
          {teams.map((team, index) => {
            const picked = chosen === team.id;
            return (
              <motion.li
                key={team.id}
                // With motion off, a row shows at once, so a scan of the floor never reads a row in mid-fade.
                initial={off ? false : { opacity: 0, y: 8 }}
                animate={off ? { opacity: 1 } : { opacity: 1, y: 0 }}
                transition={fadeIn(0.35, 0.12 + staggerOf(index))}
              >
                <button
                  type="button"
                  aria-pressed={picked}
                  onClick={() => choose(team.id)}
                  className="press flex min-h-row-touch w-full items-center gap-sp-3 rounded-tile border border-transparent px-sp-3 text-left transition-colors duration-150 hover-fine:bg-raised aria-pressed:border-ink aria-pressed:bg-raised"
                >
                  {team.avatar ? (
                    <img src={team.avatar} alt="" width={28} height={28} className="size-avatar flex-none rounded-full bg-raised object-cover" />
                  ) : (
                    <span aria-hidden className="size-avatar flex-none rounded-full bg-raised" />
                  )}
                  <span className="min-w-0 flex-1 truncate text-body leading-tight font-semibold">{team.name}</span>
                  <span className="flex-none font-mono text-meta leading-tight text-mute tabular-nums">
                    {team.wins}-{team.losses} · {ordinal(team.rank)}
                  </span>
                  <PickMark on={picked} off={off} />
                </button>
              </motion.li>
            );
          })}
        </ul>
        </motion.div>
        )}
        </AnimatePresence>
      </motion.div>
    </motion.div>
  );
}

/* The step of the league passphrase. The ask box needs it, so only managers of the league ask. The browser keeps it,
   under the same key as the trade analyzer, so a manager types it once. */
function PassphraseForm({ siteName, step }: { siteName: string; step: PassphraseStep }) {
  const [value, setValue] = useState("");
  const typed = value.trim();
  // The field opens the keyboard as the ask box does, so the foot of the sheet moves above the keyboard for it.
  const keyboard = useKeyboardField();
  return (
    <>
      <div className="flex flex-none flex-col gap-sp-1 px-sp-5 pt-sp-4 pb-sp-3">
        <span className="font-mono text-meta leading-tight tracking-caps text-mute uppercase">{siteName}</span>
        <h2 id="passphrase-title" className="m-0 text-score leading-tight font-bold tracking-tight">
          What is the league passphrase?
        </h2>
        <p id="passphrase-line" className="m-0 text-lead leading-body text-ink-2">
          {step.wrong ? "That passphrase did not match. Type the league passphrase again." : "Type it once. This phone keeps it."}
        </p>
      </div>
      {/* The end of the step keeps the home bar of an iPhone clear. The keyboard covers the home bar, so the pad drops then. */}
      <div className="flex flex-col gap-sp-2 px-sp-5 pt-sp-1 pb-[calc(var(--spacing-sp-4)+var(--spacing-door-safe))] tablet:pb-sp-4">
        <form
          aria-label="League passphrase"
          className="flex min-h-ask items-center gap-sp-2 rounded-pill border border-rule bg-page py-sp-1 pr-sp-1 pl-sp-5 transition-[border-color] duration-150 focus-within:border-ink"
          onSubmit={(event) => {
            event.preventDefault();
            if (typed) step.onPassphrase(typed);
          }}
        >
          <input
            type="password"
            value={value}
            onChange={(event) => setValue(event.target.value)}
            aria-label="League passphrase"
            placeholder="League passphrase"
            autoComplete="current-password"
            // The step follows a tap on a team, a question, or the menu row, so the next keys go to the field.
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
        {step.leave && (
          <button
            type="button"
            onClick={step.leave.onLeave}
            className="press flex min-h-touch items-center self-center rounded-pill px-sp-3 text-meta leading-tight font-semibold text-mute hover-fine:text-ink"
          >
            {step.leave.label}
          </button>
        )}
      </div>
    </>
  );
}

/* The mark of the picked row: the ring fills with ink, then the check draws in (transitions-dev, checkbox check).
   With motion off, the check shows at once. The mark has no bounce (decision 07). */
function PickMark({ on, off }: { on: boolean; off: boolean }) {
  return (
    <span
      aria-hidden
      className={`flex size-sp-5 flex-none items-center justify-center rounded-full border transition-colors duration-150 ${on ? "border-ink bg-ink text-card" : "border-rule"}`}
    >
      <svg viewBox="0 0 16 16" className="size-sp-3" fill="none">
        <motion.path
          d="M3.5 8.5l3 3 6-7"
          stroke="currentColor"
          strokeWidth={2}
          strokeLinecap="round"
          strokeLinejoin="round"
          initial={false}
          animate={{ pathLength: on ? 1 : 0, opacity: on ? 1 : 0 }}
          transition={off ? { duration: 0 } : { pathLength: { duration: FAST, ease: SMOOTH, delay: 0.08 }, opacity: { duration: 0.05, delay: 0.08 } }}
        />
      </svg>
    </span>
  );
}
