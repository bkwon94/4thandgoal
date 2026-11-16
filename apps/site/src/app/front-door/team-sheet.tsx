/**
 * The sheet that asks for Your team. It lists the teams of the league by name. On the first visit it has no skip, no close,
 * and no login, because every Suggestion of the front door comes from Your team (decision 08). On a change of team it closes and keeps the old team.
 */
"use client";

import { motion } from "framer-motion";
import { XIcon } from "lucide-react";
import { useRef, useState } from "react";
import { Sheet, SheetBackdrop, SheetClose, SheetContent, SheetGrip, SheetTitle } from "@cpc/design/ui/sheet";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import type { DoorTeam } from "@/lib/data/front-door-data";
import { FAST, SMOOTH, fadeIn, staggerOf } from "./motion";

/* The check lands, then the sheet leaves, so the tap reads as done before the page changes. */
const PICK_BEAT_MS = 420;

/* 1st, 2nd, 3rd, 11th, 12th: the place of a team in the standings. */
function ordinal(n: number): string {
  const tens = n % 100;
  if (tens >= 11 && tens <= 13) return `${n}th`;
  return `${n}${{ 1: "st", 2: "nd", 3: "rd" }[n % 10] ?? "th"}`;
}

/* onClose comes only on a change of team. Without it, the sheet of the first visit is not dismissible: a drag, Escape, and a
   tap on the dim do nothing, and it has no close button. The Drawer owns the slide, the drag, the dim, the focus trap, and
   the fade under reduced motion. */
export function TeamSheet({
  siteName,
  teams,
  current,
  onPick,
  onClose,
}: {
  siteName: string;
  teams: DoorTeam[];
  current: number | null;
  onPick: (id: number) => void;
  onClose?: () => void;
}) {
  const off = useMotionOff();
  const [chosen, setChosen] = useState<number | null>(current);
  const [open, setOpen] = useState(true);
  // The team that a tap picked. The sheet leaves first, then onPick runs, so the page changes after the sheet is gone.
  const picked = useRef<number | null>(null);

  const choose = (id: number) => {
    if (chosen !== null && chosen !== current) return;
    setChosen(id);
    picked.current = id;
    window.setTimeout(() => setOpen(false), PICK_BEAT_MS);
  };

  // The sheet is gone, so the parent drops it. A pick keeps the new team, and a close keeps the old team.
  const left = (isOpen: boolean) => {
    if (isOpen) return;
    if (picked.current !== null) onPick(picked.current);
    else onClose?.();
  };

  return (
    <Sheet
      side="bottom"
      open={open}
      onOpenChange={setOpen}
      onOpenChangeComplete={left}
      dismissible={onClose !== undefined}
      container={typeof document === "undefined" ? undefined : document.body}
    >
      <SheetBackdrop />
      <SheetContent
        aria-describedby="your-team-line"
        className="mx-auto flex max-h-[88dvh] w-full max-w-sheet flex-col rounded-t-hero border border-b-0 border-rule bg-card shadow-sheet tablet:max-h-[80dvh]"
      >
        {/* The grip says "sheet" to a thumb. On a change of team the sheet drags down to close. On the first visit it has no
            close, so a drag springs back. */}
        <SheetGrip className="mt-sp-2 w-sp-6 h-sp-1" />
        {/* With a close, the right pad of the header clears the X, so a long title never runs under it. */}
        <div className={`relative flex flex-none flex-col gap-sp-1 px-sp-5 pt-sp-4 pb-sp-3 ${onClose ? "pr-[calc(var(--spacing-touch)+var(--spacing-sp-2))]" : ""}`}>
          {onClose && (
            <SheetClose
              aria-label="Close"
              className="press absolute top-sp-2 right-sp-2 flex size-touch items-center justify-center rounded-pill text-mute hover-fine:text-ink"
            >
              <XIcon aria-hidden className="size-sp-5" />
            </SheetClose>
          )}
          <span className="font-mono text-meta leading-tight tracking-caps text-mute uppercase">{siteName}</span>
          <SheetTitle className="m-0 text-score leading-tight font-bold tracking-tight">Which team is yours?</SheetTitle>
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
      </SheetContent>
    </Sheet>
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
