/**
 * The week card of The Race: the Score to beat of the next week against the opponent and the median, the result tiles with
 * the odds of the Goal after each, and the root-for list of every other game for the chosen result. A tap on a tile sets it.
 */
"use client";

import { AnimatePresence, motion } from "framer-motion";
import { useId, useState } from "react";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { cn } from "@cpc/design/lib/utils";
import { Toggle, ToggleGroup } from "@cpc/design/ui/toggle-group";
import type {
  CardGoal,
  ScoreToBeat,
  SetResult,
  WeekCard as Card,
  WeekSim,
} from "../schema/sim-types";
import { CARD, LABEL, PRESS, chanceText, nameOf, oddsText } from "./format";
import { type GoalKey, goalName, seedOf } from "./goals";
import type { Choice } from "./use-what-if";

/* The look of a result tile, which the tiles of a bracket game share. The press of PRESS scales the tile. The fill of
   the set result fades with it, in the same 140 ms, so the tap shows before the answer comes. */
export const TILE = cn(
  PRESS,
  "group min-h-touch gap-sp-1 rounded-report px-sp-3 py-sp-3 flex flex-col border text-left",
  "[transition:var(--press),background-color_140ms_ease-out,border-color_140ms_ease-out,color_140ms_ease-out]",
  "border-rule bg-page text-ink hover-fine:border-ink-2 data-pressed:border-accent data-pressed:bg-accent data-pressed:text-on-dark hover-fine:data-pressed:border-accent",
);

/* A game whose two results move the odds by less than this many points does not matter (decision 06). */
const FLAT = 1;

type Result = Card["results"][number];

/* The value of a result in the toggle group, such as "win-above", or "win" with no median game. */
const keyOf = ({ game, median }: Pick<Result, "game" | "median">) =>
  median === null ? game : `${game}-${median}`;

/* The name of a result on its tile, such as "Win and beat the median" or "Lose, but beat the median". */
export function resultWords({ game, median }: Pick<Result, "game" | "median">): string {
  const win = game === "win";
  if (median === null) return win ? "Win" : "Lose";
  if (median === "above") return win ? "Win and beat the median" : "Lose, but beat the median";
  return win ? "Win, but miss the median" : "Lose and miss the median";
}

/* The line of the tiebreak gap, such as "Points For break a tie. You trail Teez Nuts by 10.2." */
export function tieText(sim: WeekSim, gap: NonNullable<CardGoal["tiebreak"]>): string {
  const side = gap.points >= 0 ? "lead" : "trail";
  return `Points For break a tie. You ${side} ${nameOf(sim, gap.roster_id)} by ${Math.abs(gap.points).toFixed(1)}.`;
}

/* The index of the most likely result, which the root-for list shows before a tap. */
const likeliest = (results: Result[]) =>
  results.reduce((best, result, i) => (result.chance > results[best].chance ? i : best), 0);

export function WeekCard({
  sim,
  card,
  goal,
  status,
  scoreToBeat,
  set,
  pending,
  onChoose,
}: {
  sim: WeekSim;
  card: Card;
  goal: GoalKey;
  // The status of the Goal for Your team. A Goal that is not open has no root-for list.
  status: "in" | "out" | "open";
  scoreToBeat: ScoreToBeat | undefined;
  // The set results of the What-if. The tile of the set result of the week shows as pressed.
  set: SetResult[];
  pending: boolean;
  onChoose: (choice: Choice) => void;
}) {
  const title = useId();
  const held = card.goals[goal];
  const chosen = set.find((result) => result.week === card.week);
  const chosenIndex = chosen ? card.results.findIndex((r) => keyOf(r) === keyOf(chosen)) : -1;
  // The last tapped tile keeps its root-for list when the call fails, so the tap still shows who to root for.
  const [picked, setPicked] = useState<number | null>(null);
  const shown = chosenIndex >= 0 ? chosenIndex : (picked ?? likeliest(card.results));
  const choose = (value: string[]) => {
    const index = card.results.findIndex((result) => keyOf(result) === value[0]);
    if (index < 0) {
      onChoose(null);
      return;
    }
    setPicked(index);
    onChoose({ game: card.results[index].game, median: card.results[index].median });
  };
  return (
    <article className={cn(CARD, "gap-sp-3")} aria-labelledby={title}>
      <h3 id={title} className="text-lead m-0 leading-tight font-bold text-balance">
        {`Week ${card.week} vs ${nameOf(sim, card.opponent)}`}
      </h3>
      {scoreToBeat && <ScoreTable sim={sim} beat={scoreToBeat} />}
      {held?.tiebreak && (
        <p className="text-meta text-mute m-0 text-pretty tabular-nums">
          {tieText(sim, held.tiebreak)}
        </p>
      )}
      <div className="gap-sp-2 flex flex-col">
        <p className="text-meta text-mute m-0 text-pretty">
          {`Tap a result to see your odds of ${goalName(goal)} after it.`}
        </p>
        <ToggleGroup
          aria-label="Results"
          value={chosen ? [keyOf(chosen)] : []}
          onValueChange={choose}
          loop
          className="gap-sp-2 grid grid-cols-2"
        >
          {card.results.map((result, i) => (
            <Toggle key={keyOf(result)} value={keyOf(result)} className={TILE}>
              <span data-result-name className="text-row leading-tight font-bold text-pretty">
                {resultWords(result)}
              </span>
              <span className="gap-x-sp-2 gap-y-sp-1 flex w-full flex-wrap items-end justify-between">
                <span
                  className={cn(
                    "text-stat font-mono leading-none font-bold tabular-nums transition-opacity duration-150 ease-out",
                    pending && i === chosenIndex && "opacity-50",
                  )}
                >
                  {oddsText(held?.odds[i] ?? null, result.about)}
                </span>
                <span className="text-meta text-mute group-data-pressed:text-on-dark leading-tight tabular-nums">
                  {chanceText(result.chance)}
                </span>
              </span>
            </Toggle>
          ))}
        </ToggleGroup>
      </div>
      <RootFor
        sim={sim}
        goal={goal}
        status={status}
        held={held}
        index={shown}
        result={card.results[shown]}
      />
    </article>
  );
}

/* The Score to beat as a small table: the opponent, then the median in a league with a median game. */
function ScoreTable({ sim, beat }: { sim: WeekSim; beat: ScoreToBeat }) {
  const rows: [string, number, number][] = [
    [`Beat ${nameOf(sim, beat.opponent)}`, beat.win, beat.win_sure],
  ];
  if (beat.median !== null && beat.median_sure !== null)
    rows.push(["Beat the median", beat.median, beat.median_sure]);
  const num = "text-lead text-right font-mono font-bold tabular-nums";
  return (
    <table aria-label="Score to beat" className="w-full border-collapse">
      <thead>
        <tr>
          <th scope="col" className={cn(LABEL, "text-mute pb-sp-1 text-left")}>
            Score to beat
          </th>
          <th
            scope="col"
            className={cn(
              LABEL,
              "text-mute pb-sp-1 tablet:pl-sp-3 tablet:w-[6.5rem] w-[5.5rem] text-right whitespace-nowrap",
            )}
          >
            To win
          </th>
          <th
            scope="col"
            className={cn(
              LABEL,
              "text-mute pb-sp-1 tablet:pl-sp-3 tablet:w-[6.5rem] w-[5.5rem] text-right whitespace-nowrap",
            )}
          >
            To be sure
          </th>
        </tr>
      </thead>
      <tbody>
        {rows.map(([label, even, sure]) => (
          <tr key={label} className="border-rule border-t">
            <th
              scope="row"
              className="text-row py-sp-1 text-left leading-tight font-bold text-pretty"
            >
              {label}
            </th>
            <td className={cn(num, "py-sp-1")}>{even}</td>
            <td className={cn(num, "text-mute py-sp-1")}>{sure}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

/* The root-for list of one result: every other game with both results and their odds, a gray "Doesn't matter" on a game
   under 1 point, then the median rows. A new result fades the list in with the text swap of transitions-dev. */
function RootFor({
  sim,
  goal,
  status,
  held,
  index,
  result,
}: {
  sim: WeekSim;
  goal: GoalKey;
  status: "in" | "out" | "open";
  held: CardGoal | undefined;
  index: number;
  result: Result;
}) {
  const off = useMotionOff();
  const rows = held?.root_for[index] ?? [];
  const medians = held?.median_root[index] ?? [];
  const odds = held?.odds[index] ?? null;
  let note: string | null = null;
  if (seedOf(goal) !== null) note = "Pick Spot or Bye to see who to root for.";
  else if (status !== "open") note = `No game this week changes your odds of ${goalName(goal)}.`;
  else if (rows.length === 0) note = "No run has this result.";
  return (
    <section aria-label="Who to root for" className="border-rule pt-sp-3 border-t">
      <AnimatePresence initial={false} mode="wait">
        <motion.div
          key={`${goal}-${index}`}
          initial={off ? { opacity: 0 } : { opacity: 0, filter: "blur(2px)" }}
          animate={{ opacity: 1, filter: "blur(0px)" }}
          exit={{ opacity: 0, transition: { duration: 0.1 } }}
          transition={{ duration: 0.15, ease: "easeInOut" }}
          className="gap-sp-2 flex flex-col"
        >
          {note !== null ? (
            <p className="text-meta text-mute m-0 text-pretty">{note}</p>
          ) : (
            <>
              <p className="text-row m-0 leading-tight font-bold text-pretty">
                {`If you ${resultWords(result).toLowerCase()}, you sit at ${oddsText(odds)}. Root for:`}
              </p>
              <ul aria-label="Games to root for" className="m-0 flex list-none flex-col p-0">
                {rows.map((row) => (
                  <li
                    key={`${row.winner}-${row.loser}`}
                    className="border-rule py-sp-2 gap-sp-0 flex flex-col border-t first:border-t-0"
                  >
                    {row.odds - row.other < FLAT ? (
                      <span className="gap-sp-3 text-mute flex items-baseline justify-between">
                        <span className="text-row min-w-0 leading-tight text-pretty">
                          {`${nameOf(sim, row.winner)} vs ${nameOf(sim, row.loser)}`}
                        </span>
                        <span
                          className={cn(LABEL, "rounded-pill bg-raised px-sp-2 py-sp-0 flex-none")}
                        >
                          Doesn't matter
                        </span>
                      </span>
                    ) : (
                      <>
                        <span className="gap-sp-3 flex items-baseline justify-between">
                          <span className="text-row min-w-0 leading-tight font-bold text-pretty">
                            {`${nameOf(sim, row.winner)} beats ${nameOf(sim, row.loser)}`}
                          </span>
                          <span className="text-lead flex-none font-mono font-bold whitespace-nowrap tabular-nums">
                            <span className="text-mute">→</span> {`${row.odds}%`}
                          </span>
                        </span>
                        <span className="gap-sp-3 text-mute flex items-baseline justify-between">
                          <span className="text-meta min-w-0 leading-tight text-pretty">
                            {`${nameOf(sim, row.loser)} wins`}
                          </span>
                          <span className="text-meta flex-none font-mono whitespace-nowrap tabular-nums">
                            {`→ ${row.other}%`}
                          </span>
                        </span>
                      </>
                    )}
                  </li>
                ))}
              </ul>
              {medians.length > 0 && (
                <ul
                  aria-label="Median results to root for"
                  className="border-rule pt-sp-2 m-0 flex list-none flex-col border-t p-0"
                >
                  {medians.map((median) => (
                    <li
                      key={median.roster_id}
                      className="gap-sp-3 py-sp-1 flex items-baseline justify-between"
                    >
                      <span className="text-row min-w-0 leading-tight font-bold text-pretty">
                        {`${nameOf(sim, median.roster_id)} misses the median`}
                      </span>
                      <span className="text-lead flex-none font-mono font-bold whitespace-nowrap tabular-nums">
                        <span className="text-mute">→</span> {`${median.odds}%`}
                      </span>
                    </li>
                  ))}
                </ul>
              )}
            </>
          )}
        </motion.div>
      </AnimatePresence>
    </section>
  );
}
