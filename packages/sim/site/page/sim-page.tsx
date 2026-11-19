/**
 * The sim page of Your team, layout D "Cards" (decision 04): the header with the odds, the sentence that opens the ladder,
 * the set line of the What-if, the week switch, and one page per week with the week card and the root-for card.
 */
"use client";

import { AnimatePresence, motion } from "framer-motion";
import { RotateCcw } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { PhotoFrame } from "@cpc/design/parts/photo-frame";
import { cn } from "@cpc/design/lib/utils";
import type { SetResult, WeekSim } from "../schema/sim-types";
import type { WhatIfApi } from "../lib/what-if-api";
import { LABEL, PRESS, nameOf, oddsText, recordText, resultName } from "./format";
import { LadderSheet } from "./ladder-sheet";
import { SoftText } from "./parts";
import { PlayoffsPage } from "./playoffs-page";
import { useWhatIf, type Choice } from "./use-what-if";
import { PLAYOFFS, WeekSwitch, type WeekItem } from "./week-switch";
import { WeekPage } from "./week-page";

/* The avatar src of each team by roster id, with the base path, from the latest week. */
export type Avatars = Record<string, string>;

/* The entry of a week page: the page slide of transitions-dev, a short move from the side of the item with a soft blur. */
const ENTER = { duration: 0.25, ease: [0.22, 1, 0.36, 1] } as const;

/* The beat between a tap on a tile and the open of the next week, so the press of the tile shows first. */
const ADVANCE_MS = 400;

/* The line of the set results, such as "Wk 11 win, beat median · Wk 12 lose". */
const setText = (set: SetResult[]) => set.map((result) => `Wk ${result.week} ${resultName(result).toLowerCase()}`).join(" · ");

export function SimPage({ sim, you, avatars = {}, whatIf }: { sim: WeekSim; you: number; avatars?: Avatars; whatIf?: WhatIfApi }) {
  const file = sim.pages[you];
  const name = nameOf(sim, you);
  const what = useWhatIf(file, whatIf);
  const page = what.page;
  const items: WeekItem[] = [...file.weeks.map((week) => week.week), PLAYOFFS];
  // The side the open page came from: 1 from the right for a later item, -1 from the left, and 0 for the first page,
  // which shows at rest.
  const [{ open, side }, setView] = useState<{ open: WeekItem; side: number }>({ open: items[0], side: 0 });
  const off = useMotionOff();
  const advance = useRef<number | undefined>(undefined);
  useEffect(() => () => window.clearTimeout(advance.current), []);
  // A failed What-if keeps the reader on the week of the tap, beside the line that says so.
  useEffect(() => {
    if (what.down) window.clearTimeout(advance.current);
  }, [what.down]);

  const openItem = (item: WeekItem) => {
    window.clearTimeout(advance.current);
    setView((was) =>
      item === was.open ? was : { open: item, side: items.indexOf(item) > items.indexOf(was.open) ? 1 : -1 },
    );
  };
  const choose = (week: number, choice: Choice) => {
    what.choose(week, choice);
    window.clearTimeout(advance.current);
    const next = items[items.indexOf(week) + 1];
    if (choice !== null && next !== undefined) advance.current = window.setTimeout(() => openItem(next), ADVANCE_MS);
  };
  const week = typeof open === "number" ? what.weekOf(open) : undefined;
  const chosen = typeof open === "number" ? what.set.find((result) => result.week === open) : undefined;

  return (
    <div className="flex flex-col gap-sp-3 px-gutter pt-sp-4 pb-sp-6 tablet:px-0">
      <section aria-label="Your team" aria-busy={what.pending} className="flex w-full flex-col gap-sp-3">
        <div className="flex items-center gap-sp-3">
          <PhotoFrame src={avatars[String(you)] ?? null} name={name} size="md" decorative />
          <div className="min-w-0 flex-1">
            <h1 className="m-0 text-stat leading-tight font-bold text-balance">{name}</h1>
            <p className="m-0 text-meta text-mute tabular-nums">{`${recordText(file.record)} · ${file.weeks_left} weeks left`}</p>
          </div>
          <div className="flex flex-none flex-col items-end">
            <SoftText
              text={oddsText(page.playoff)}
              className={cn(
                "justify-items-end font-mono text-score leading-none font-bold tabular-nums transition-opacity duration-150 ease-out",
                what.pending && "opacity-50",
              )}
            />
            <span className={cn(LABEL, "pt-sp-1 text-mute")}>Playoff odds</span>
          </div>
        </div>
        <LadderSheet
          page={page}
          medianGame={sim.parameters.median_game}
          sentence={<SoftText text={page.sentence} className={cn("transition-opacity duration-150 ease-out", what.pending && "opacity-50")} />}
        />
        <SetLine set={what.set} onReset={what.reset} />
        {what.down && (
          <p role="status" className="m-0 text-meta text-pretty text-mute">
            The What-if is not available now.
          </p>
        )}
      </section>

      <WeekSwitch items={items} open={open} onOpen={openItem} setWeeks={what.set.map((result) => result.week)} />

      <motion.div
        key={String(open)}
        initial={side === 0 ? false : off ? { opacity: 0 } : { opacity: 0, x: side * 8, filter: "blur(3px)" }}
        animate={{ opacity: 1, x: 0, filter: "blur(0px)" }}
        transition={off ? { duration: 0.15 } : ENTER}
      >
        {week !== undefined ? (
          <WeekPage sim={sim} week={week} chosen={chosen ?? null} onChoose={(choice) => choose(week.week, choice)} />
        ) : (
          <PlayoffsPage sim={sim} you={you} onOpen={openItem} />
        )}
      </motion.div>
    </div>
  );
}

/* The line at the top that lists each set result, with a Reset back to the numbers of the file. It grows from no
   height with the accordion of transitions-dev, so the page below moves down and does not jump. */
function SetLine({ set, onReset }: { set: SetResult[]; onReset: () => void }) {
  const off = useMotionOff();
  return (
    <AnimatePresence initial={false}>
      {set.length > 0 && (
        <motion.section
          aria-label="What-if"
          initial={off ? { opacity: 0 } : { opacity: 0, height: 0 }}
          animate={off ? { opacity: 1 } : { opacity: 1, height: "auto" }}
          exit={off ? { opacity: 0, transition: { duration: 0.1 } } : { opacity: 0, height: 0, transition: { duration: 0.15, ease: [0.22, 1, 0.36, 1] } }}
          transition={{ duration: 0.25, ease: [0.22, 1, 0.36, 1] }}
          className="overflow-hidden"
        >
          <div className="flex min-h-touch items-center gap-sp-2 rounded-report bg-card pl-sp-3">
            <p className="m-0 min-w-0 flex-1 py-sp-2 text-meta text-pretty">
              <span className="font-bold">What-if: </span>
              {setText(set)}
            </p>
            <button
              type="button"
              onClick={onReset}
              className={cn(
                PRESS,
                "flex min-h-touch flex-none items-center gap-sp-1 rounded-report px-sp-3 text-meta font-bold text-ink hover-fine:text-accent-ink",
              )}
            >
              <RotateCcw aria-hidden className="size-4" />
              Reset
            </button>
          </div>
        </motion.section>
      )}
    </AnimatePresence>
  );
}
