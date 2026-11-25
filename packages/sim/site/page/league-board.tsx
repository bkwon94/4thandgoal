/**
 * The League board of The Race: one bar per team with its odds of the Goal, in odds order. Each bar is ink at 80%, and only
 * Your team takes the accent and the "You" tag. A tap on Your team opens the Your team card, and a tap on another team opens
 * its sheet.
 */
"use client";

import { LayoutGroup, motion } from "framer-motion";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { cn } from "@cpc/design/lib/utils";
import { BarChart, BarChartBar } from "@cpc/design/ui/bar-chart";
import type { BoardTeam, WeekSim } from "../schema/sim-types";
import { CARD, LABEL, PRESS, nameOf, oddsText, recordText } from "./format";
import { type GoalKey, boardOdds, boardOrder, goalName } from "./goals";

/* --ease-smooth-out of transitions-dev, for each move of a row and each fill of a bar. */
const EASE = [0.22, 1, 0.36, 1] as const;

const ROW = cn(
  PRESS,
  "min-h-touch rounded-report hover-fine:bg-raised w-full text-left transition-[background-color] duration-150 ease-out",
  "px-sp-2 py-sp-2 gap-x-sp-3 gap-y-sp-1 grid grid-cols-[1fr_3.25rem] items-center",
);

/* A bar that fills to its percent from the left. A Goal change moves each bar with a stagger of 40 ms, the stagger token of
   transitions-dev. Reduced motion sets the fill at once. */
function OddsBar({ value, index, mine }: { value: number; index: number; mine: boolean }) {
  return (
    <span aria-hidden className="rounded-pill bg-bar-off h-sp-2 col-span-2 block overflow-hidden">
      <span
        data-tone={mine ? "accent" : "ink"}
        className={cn(
          "rounded-pill block h-full origin-left transition-transform duration-400 ease-[cubic-bezier(0.22,1,0.36,1)] motion-reduce:transition-none",
          mine ? "bg-accent" : "bg-ink/80",
        )}
        style={{
          transform: `scaleX(${Math.min(100, Math.max(0, value)) / 100})`,
          transitionDelay: `${index * 40}ms`,
        }}
      />
    </span>
  );
}

export function LeagueBoard({
  sim,
  board,
  you,
  goal,
  onYou,
  onOther,
}: {
  sim: WeekSim;
  // The board odds of a What-if answer. Without it, the board shows the file.
  board?: BoardTeam[];
  you: number;
  goal: GoalKey;
  onYou: () => void;
  onOther: (id: number) => void;
}) {
  const off = useMotionOff();
  const order = boardOrder(sim, goal, board);
  const name = goalName(goal);
  return (
    <section className={cn(CARD, "px-sp-2")} aria-labelledby="league-board-title">
      <div className="px-sp-2">
        <h2 id="league-board-title" className="text-lead m-0 leading-tight font-bold">
          League board
        </h2>
        <p className="text-meta text-mute m-0 text-pretty">{`Each team's odds of ${name}.`}</p>
      </div>
      <LayoutGroup>
        <BarChart
          aria-label={`League board: odds of ${name}`}
          value={null}
          onValueChange={(value: string | null) => {
            if (value === null) return;
            if (Number(value) === you) onYou();
            else onOther(Number(value));
          }}
          className="flex flex-col"
        >
          {order.map((team, index) => {
            const id = team.roster_id;
            const odds = boardOdds(team, goal);
            const mine = id === you;
            const record = sim.records[id];
            return (
              <motion.div
                key={id}
                layout={off ? false : "position"}
                transition={{ duration: 0.4, ease: EASE }}
              >
                <BarChartBar
                  value={String(id)}
                  data-roster={id}
                  data-odds={odds}
                  aria-haspopup={mine ? undefined : "dialog"}
                  aria-label={`${nameOf(sim, id)}${mine ? ", your team" : ""}: ${oddsText(odds)} odds of ${name}`}
                  className={ROW}
                >
                  <span className="gap-sp-1 flex min-w-0 flex-col">
                    <span className="gap-sp-2 flex min-w-0 items-baseline">
                      <span
                        className={cn(
                          "text-row min-w-0 truncate leading-tight font-bold",
                          mine && "text-accent-ink",
                        )}
                      >
                        {nameOf(sim, id)}
                      </span>
                      {mine && <span className={cn(LABEL, "text-ink flex-none")}>You</span>}
                    </span>
                    {record && (
                      <span className="text-meta text-mute tabular-nums">
                        {recordText([record[0], record[1]])}
                      </span>
                    )}
                  </span>
                  <span className="text-lead text-right font-mono font-bold tabular-nums">
                    {oddsText(odds)}
                  </span>
                  <OddsBar value={odds} index={index} mine={mine} />
                </BarChartBar>
              </motion.div>
            );
          })}
        </BarChart>
      </LayoutGroup>
    </section>
  );
}
