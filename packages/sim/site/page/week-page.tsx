/**
 * One week page of the sim page: the week card with a tile for each result of Your team, and the root-for card.
 * A tap on a tile sets that result as a What-if, and a tap on the set tile clears it.
 * On a phone the root-for card opens from one row. From the tablet tier it always shows, and on desktop it sits beside the week card.
 */
"use client";

import { ChevronDown } from "lucide-react";
import { useId, useState } from "react";
import { cn } from "@cpc/design/lib/utils";
import { Toggle, ToggleGroup } from "@cpc/design/ui/toggle-group";
import type { SetResult, WeekSim } from "../schema/sim-types";
import { useTabletUp } from "./parts";
import { CARD, PRESS, chanceText, nameOf, oddsText, resultName, winsText } from "./format";
import type { Choice } from "./use-what-if";

type PageWeek = WeekSim["pages"][number]["weeks"][number];
type WeekResult = PageWeek["results"][number];
type RootFor = PageWeek["root_for"][number];

/* The value of a result in the toggle group, such as "win-above", or "win" with no median game. */
const keyOf = ({ game, median }: Pick<WeekResult, "game" | "median">) => (median === null ? game : `${game}-${median}`);

export function WeekPage({
  sim,
  week,
  chosen = null,
  onChoose = () => {},
}: {
  sim: WeekSim;
  week: PageWeek;
  chosen?: SetResult | null;
  onChoose?: (choice: Choice) => void;
}) {
  const title = useId();
  const choose = (value: string[]) => {
    const result = week.results.find((entry) => keyOf(entry) === value[0]);
    onChoose(result === undefined ? null : { game: result.game, median: result.median });
  };
  return (
    <div className="grid w-full grid-cols-1 items-start gap-sp-3 desktop:grid-cols-2">
      <article className={CARD} aria-labelledby={title}>
        <h2 id={title} className="m-0 text-lead leading-tight font-bold text-balance">
          {`Week ${week.week} vs ${nameOf(sim, week.opponent)}`}
        </h2>
        <p className="m-0 pb-sp-1 text-meta text-pretty text-mute">Tap a result to see your odds if it happens.</p>
        <ToggleGroup
          aria-label="Results"
          value={chosen === null ? [] : [keyOf(chosen)]}
          onValueChange={choose}
          loop
          className="grid grid-cols-2 gap-sp-2"
        >
          {week.results.map((result) => (
            <ResultTile key={keyOf(result)} value={keyOf(result)} result={result} />
          ))}
        </ToggleGroup>
      </article>
      <RootForCard sim={sim} week={week} />
    </div>
  );
}

/* One result of the week: the odds after it, how likely it is, and the wins it adds. The pressed tile is the set result
   of the week. It fills with the accent at the press, so the tap shows before the answer comes. */
function ResultTile({ result, value }: { result: WeekResult; value: string }) {
  return (
    <Toggle
      value={value}
      className={cn(
        PRESS,
        "group flex min-h-touch flex-col gap-sp-1 rounded-report border px-sp-3 py-sp-3 text-left",
        // The press of PRESS scales the tile. The fill of the set result fades with it, in the same 140 ms.
        "[transition:var(--press),background-color_140ms_ease-out,border-color_140ms_ease-out,color_140ms_ease-out]",
        "border-rule bg-page text-ink hover-fine:border-ink-2 data-pressed:border-accent data-pressed:bg-accent data-pressed:text-on-dark hover-fine:data-pressed:border-accent",
      )}
    >
      <span data-result-name className="text-row leading-tight font-bold">
        {resultName(result)}
      </span>
      <span className="flex w-full flex-wrap items-end justify-between gap-x-sp-2 gap-y-sp-1">
        <span className="font-mono text-stat leading-none font-bold tabular-nums">
          {result.about && (
            <span className="block pb-sp-0 font-sans text-meta font-normal text-mute group-data-pressed:text-on-dark">about </span>
          )}
          {oddsText(result.playoff)}
        </span>
        <span className="flex flex-col items-end text-meta leading-tight text-mute tabular-nums group-data-pressed:text-on-dark">
          <span>{chanceText(result.chance)}</span>
          <span>{winsText(result.wins_added)}</span>
        </span>
      </span>
    </Toggle>
  );
}

/* The results of other games that lift Your team back up after a loss. The header says what the loss costs. */
function RootForCard({ sim, week }: { sim: WeekSim; week: PageWeek }) {
  const [open, setOpen] = useState(false);
  const title = useId();
  const list = useId();
  const count = week.root_for.length;
  const wide = useTabletUp();
  const header = `If you lose, you drop to ${oddsText(week.loss_playoff, week.loss_about)}`;
  return (
    <article className={cn(CARD, "max-tablet:gap-0 max-tablet:py-0")} aria-labelledby={title}>
      <h2 className="m-0 text-lead leading-tight font-bold">
        {wide ? (
          // From the tablet tier the list always shows, so the header is plain text and no toggle.
          <span id={title} className="block text-balance">
            {header}
          </span>
        ) : (
          <button
            type="button"
            aria-expanded={open}
            aria-controls={list}
            onClick={() => setOpen((was) => !was)}
            className={cn(PRESS, "flex min-h-touch w-full items-center justify-between gap-sp-2 py-sp-2 text-left tablet:pointer-events-none tablet:min-h-0 tablet:py-0")}
          >
            <span id={title} className="min-w-0 text-balance">
              {header}
            </span>
            <span className="flex flex-none items-center gap-sp-1 text-meta font-bold text-mute tablet:hidden">
              <span className={cn(open && "sr-only")}>{count === 1 ? "1 game" : `${count} games`}</span>
              <ChevronDown aria-hidden className={cn("size-4 transition-[scale] duration-250 ease-[cubic-bezier(0.22,1,0.36,1)] motion-reduce:transition-none", open && "-scale-y-100")} />
            </span>
          </button>
        )}
      </h2>
      {/* The grid row grows from 0fr to 1fr, so the list opens with no measure of its height. */}
      <div
        id={list}
        className={cn(
          "grid transition-[grid-template-rows,opacity] duration-250 ease-[cubic-bezier(0.22,1,0.36,1)] motion-reduce:transition-none tablet:grid-rows-[1fr] tablet:opacity-100",
          open ? "grid-rows-[1fr] opacity-100" : "grid-rows-[0fr] opacity-0",
        )}
      >
        <div className={cn("min-h-0 overflow-hidden", !open && "max-tablet:invisible")}>
          <p className="m-0 pb-sp-1 text-meta text-pretty text-mute max-tablet:pt-sp-1">
            {count === 0 ? "No other game lifts you back up this week." : "These results lift you back up."}
          </p>
          {count > 0 && (
            <ul className="m-0 list-none p-0 max-tablet:pb-sp-3">
              {week.root_for.map((root) => (
                <RootForRow key={`${root.winner}-${root.loser}`} sim={sim} root={root} />
              ))}
            </ul>
          )}
        </div>
      </div>
    </article>
  );
}

/* One result to root for: who wins and why on the left, the odds after a loss and this result on the right.
   A long name wraps at a space, so no word of either name is cut. */
function RootForRow({ sim, root }: { sim: WeekSim; root: RootFor }) {
  return (
    <li className="flex items-center gap-sp-3 border-t border-rule py-sp-2 first:border-t-0">
      <span className="min-w-0 flex-1">
        <span className="block text-body leading-tight font-bold text-pretty">
          {`${nameOf(sim, root.winner)} beats ${nameOf(sim, root.loser)}`}
        </span>
        <span className="block pt-sp-0 text-meta leading-tight text-mute">{root.reason}</span>
      </span>
      <span className="flex-none text-right font-mono text-lead leading-tight font-bold tabular-nums">
        <span className="text-mute">→</span> {oddsText(root.playoff, root.about)}
      </span>
    </li>
  );
}
