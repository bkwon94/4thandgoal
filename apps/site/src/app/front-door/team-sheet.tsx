/**
 * The sheet that asks for Your team on the first visit. It lists the teams of the league by name, with no skip, no close,
 * and no login, because every Suggestion of the front door comes from Your team (decision 08).
 */
"use client";

import { motion } from "framer-motion";
import { useEffect, useRef, useState, type KeyboardEvent } from "react";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import type { DoorTeam } from "@/lib/data/front-door-data";
import { FAST, QUICK, SHEET_SPRING, SMOOTH, fadeIn, staggerOf } from "./motion";

/* The check lands, then the sheet leaves, so the tap reads as done before the page changes. */
const PICK_BEAT_MS = 420;

/* 1st, 2nd, 3rd, 11th, 12th: the place of a team in the standings. */
function ordinal(n: number): string {
  const tens = n % 100;
  if (tens >= 11 && tens <= 13) return `${n}th`;
  return `${n}${{ 1: "st", 2: "nd", 3: "rd" }[n % 10] ?? "th"}`;
}

export function TeamSheet({ siteName, teams, current, onPick }: { siteName: string; teams: DoorTeam[]; current: number | null; onPick: (id: number) => void }) {
  const off = useMotionOff();
  const [chosen, setChosen] = useState<number | null>(current);
  const panel = useRef<HTMLDivElement>(null);

  // The sheet takes the focus, and the page under it stops its scroll while the sheet is open.
  useEffect(() => {
    panel.current?.focus({ preventScroll: true });
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

  // The sheet is modal, so Tab cycles inside it. It has no close, so Escape does nothing.
  const trap = (event: KeyboardEvent<HTMLDivElement>) => {
    if (event.key !== "Tab") return;
    const buttons = [...(panel.current?.querySelectorAll<HTMLButtonElement>("button") ?? [])];
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
      className="fixed inset-0 z-50 flex items-end justify-center bg-scrim tablet:items-center tablet:p-sp-6"
      // With motion off, the scrim and the sheet show at once, so a scan of the floor never reads them in mid-fade.
      initial={off ? false : { opacity: 0 }}
      animate={{ opacity: 1, transition: fadeIn(FAST) }}
      exit={{ opacity: 0, transition: fadeIn(FAST) }}
    >
      <motion.div
        ref={panel}
        role="dialog"
        aria-modal="true"
        aria-labelledby="your-team-title"
        aria-describedby="your-team-line"
        tabIndex={-1}
        onKeyDown={trap}
        className="flex max-h-[88dvh] w-full max-w-sheet flex-col rounded-t-hero border border-b-0 border-rule bg-card text-ink shadow-sheet outline-none tablet:max-h-[80dvh] tablet:rounded-hero tablet:border-b"
        initial={off ? false : { y: "100%" }}
        animate={off ? { opacity: 1, transition: fadeIn(FAST) } : { y: 0, transition: SHEET_SPRING }}
        exit={off ? { opacity: 0, transition: fadeIn(QUICK) } : { y: "100%", transition: { duration: 0.35, ease: SMOOTH } }}
      >
        {/* The grabber says "sheet" to a thumb. The sheet has no close, so the grabber drags nothing. */}
        <span aria-hidden className="mx-auto mt-sp-2 h-sp-1 w-sp-6 flex-none rounded-pill bg-rule tablet:hidden" />
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
    </motion.div>
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
