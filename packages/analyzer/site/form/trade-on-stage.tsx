/**
 * The trade on the stage: one column for each side of the Stack, with the name of each player that the side gets.
 * It fills the feature slot of the title hero, so the reader sees the trade grow on the hero before the grade.
 */
"use client";

import { AnimatePresence, motion } from "framer-motion";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { enterExit } from "@cpc/design/lib/motion";

/* One side on the stage: its column label, such as "Teehee gets", and each player it gets. */
export type StageSide = { id: number; label: string; players: { id: string; name: string; meta: string }[] };

/* The cards of the form under the hero say the same trade to a screen reader, so the stage is art and hidden from one.
   Two sides sit side by side at each width. A third and a fourth side wrap to a second row on a phone, and the tablet
   tier puts every side in one row. A long name wraps whole and never truncates, so each name stays readable at 375px. */
export function TradeOnStage({ sides }: { sides: StageSide[] }) {
  const off = useMotionOff();
  return (
    <div aria-hidden="true" className="grid grid-cols-2 gap-sp-3 tablet:auto-cols-fr tablet:grid-flow-col tablet:gap-sp-6">
      {sides.map((side) => (
        <div key={side.id} className="flex min-w-0 flex-col gap-sp-2">
          <span className="w-fit font-mono text-meta leading-tight font-bold tracking-wide break-words text-on-dark-muted uppercase">
            {side.label}
          </span>
          <ul className="m-0 flex list-none flex-col gap-sp-2 p-0">
            <AnimatePresence initial={false}>
              {side.players.map((player) => (
                <motion.li
                  key={player.id}
                  layout={!off}
                  data-mesh-hole
                  {...enterExit(off)}
                  className="flex min-w-0 flex-col rounded-tile border border-rule-dark bg-band px-sp-3 py-sp-2"
                >
                  <span className="text-row leading-tight font-extrabold tracking-snug break-words text-on-dark">{player.name}</span>
                  <span className="text-meta leading-tight text-on-dark-2">{player.meta}</span>
                </motion.li>
              ))}
            </AnimatePresence>
            {/* A side with no player yet keeps the shape of a chip, so its label never floats over an empty column. */}
            {side.players.length === 0 && (
              <li className="rounded-tile border border-dashed border-rule-dark px-sp-3 py-sp-2 text-meta leading-tight text-on-dark-muted">
                No player yet
              </li>
            )}
          </ul>
        </div>
      ))}
    </div>
  );
}
