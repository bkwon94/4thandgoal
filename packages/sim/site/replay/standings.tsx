/**
 * The standings of the replay: one row per team, which reorders on a spring each week with an arrow for each change of
 * place. The final standings add the BYE plates, the cut line under the last seed, and the dimmed teams under the cut.
 */
import { motion } from "framer-motion";
import { oneDecimal, record } from "@cpc/design/format/format";
import { cn } from "@cpc/design/lib/utils";
import { enter, type Pace, SPRING } from "./pace";
import type { StandingRow } from "./season";

/* The marks of the final standings: the count of seeds and the count of byes. */
type Marks = { spots: number; byes: number };

const CELL = "font-mono text-meta tabular-nums whitespace-nowrap";

/* The arrow of a change of place. The arrow shape and the screen reader text carry the direction, so color is not the only sign. */
function Move({ move }: { move: number }) {
  if (move === 0) return <span aria-hidden="true" className="w-sp-4" />;
  const up = move > 0;
  return (
    <span className={cn(CELL, "w-sp-4 text-center", up ? "text-move-up" : "text-move-down")}>
      <span aria-hidden="true">{up ? "▲" : "▼"}</span>
      <span className="sr-only">{up ? `up ${move}` : `down ${-move}`}</span>
    </span>
  );
}

export function Standings({
  rows,
  label,
  pace,
  marks,
}: {
  rows: StandingRow[];
  // The name of the list, such as "Standings" or "Final standings".
  label: string;
  pace: Pace;
  // The marks of the final standings. With no marks, the list shows the move of each team.
  marks?: Marks;
}) {
  // The spring reorder moves the rows, so reduced motion and a skip put each row in its place at once.
  const moving = !pace.off && !pace.still;
  return (
    <ol aria-label={label} className="m-0 flex list-none flex-col p-0">
      {rows.map((row) => {
        const bye = marks !== undefined && row.place <= marks.byes;
        const cut = marks !== undefined && row.place === marks.spots;
        const out = marks !== undefined && row.place > marks.spots;
        return (
          <motion.li
            key={row.roster_id}
            layout={moving ? "position" : false}
            transition={SPRING}
            data-roster={row.roster_id}
            data-cut={cut || undefined}
            data-out={out || undefined}
            className={cn(
              "relative flex items-center gap-sp-2 border-b border-rule-dark py-sp-1 transition-colors duration-500",
              out ? "text-on-dark-muted" : "text-on-dark",
            )}
          >
            <span className={cn(CELL, "w-sp-5 text-on-dark-muted")}>{String(row.place).padStart(2, "0")}</span>
            {marks === undefined && <Move move={row.move} />}
            <span className="min-w-0 flex-1 truncate text-body leading-tight font-semibold">{row.name}</span>
            {bye && (
              <motion.span
                {...enter(pace, { x: 16 }, { delay: 0.5 })}
                className="rounded-sm bg-accent px-sp-2 font-mono text-meta font-bold tracking-caps text-white"
              >
                BYE
              </motion.span>
            )}
            <span className={cn(CELL, "w-sp-6 text-right font-bold")}>{record(row.wins, row.losses)}</span>
            <span className={cn(CELL, "hidden w-[4.5rem] text-right text-on-dark-2 tablet:inline")}>{oneDecimal(row.points)}</span>
            {cut && (
              // The cut line draws under the last seed, from the left.
              <motion.span
                aria-hidden="true"
                {...enter(pace, { scaleX: 0 }, { duration: 0.6, delay: 0.3 })}
                className="absolute inset-x-0 -bottom-px h-0.5 origin-left bg-accent"
              />
            )}
          </motion.li>
        );
      })}
    </ol>
  );
}
