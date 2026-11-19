/**
 * The sim page of Your team, layout D "Cards" (decision 04): the header with the odds, the sentence that opens the ladder, the set
 * line of the What-if, the week switch, one page per week with the week card and the root-for card, and the two replay buttons.
 */
"use client";

import { AnimatePresence, motion } from "framer-motion";
import { Play, RotateCcw, Shuffle } from "lucide-react";
import { useState } from "react";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { PhotoFrame } from "@cpc/design/parts/photo-frame";
import { cn } from "@cpc/design/lib/utils";
import type { SetResult, WeekSim } from "../schema/sim-types";
import type { WhatIfApi } from "../lib/what-if-api";
import { SimStage, type StageAsk } from "../stage/sim-stage";
import { LABEL, PRESS, nameOf, oddsText, recordText, resultName } from "./format";
import { InPlayoffs, seasonLine } from "./in-playoffs";
import { LadderSheet } from "./ladder-sheet";
import { SoftText } from "./parts";
import { PlayoffsPage } from "./playoffs-page";
import { useWhatIf } from "./use-what-if";
import { PLAYOFFS, WeekSwitch, type WeekItem } from "./week-switch";
import { WeekPage } from "./week-page";

/* The avatar src of each team by roster id, with the base path, from the latest week. */
export type Avatars = Record<string, string>;

/* The entry of a week page: the page slide of transitions-dev, a short move from the side of the item with a soft blur. */
const ENTER = { duration: 0.25, ease: [0.22, 1, 0.36, 1] } as const;

/* The line of the set results, such as "Wk 11 win, beat median · Wk 12 lose". */
const setText = (set: SetResult[]) => set.map((result) => `Wk ${result.week} ${resultName(result).toLowerCase()}`).join(" · ");

/* `random` gives a number in [0, 1), as Math.random does. The replay draws its run with it, so a test can set it. */
export function SimPage({
  sim,
  you,
  avatars = {},
  whatIf,
  random = Math.random,
}: {
  sim: WeekSim;
  you: number;
  avatars?: Avatars;
  whatIf?: WhatIfApi;
  random?: () => number;
}) {
  if (sim.pages[you].playoffs) return <PlayoffSimPage sim={sim} you={you} avatars={avatars} whatIf={whatIf} random={random} />;
  return <RegularSimPage sim={sim} you={you} avatars={avatars} whatIf={whatIf} random={random} />;
}

/* The sim page with no regular week left: Your team with its title odds, then the playoff cards. No week switch and no
   ladder, because no regular week is left to win. A tap on a tile of the bracket game of Your team sets a What-if, with
   the set line and the line of a failed call of the regular weeks. Before the final, "Sim the season" replays the
   playoffs. After the final, no replay is left to play. */
function PlayoffSimPage({
  sim,
  you,
  avatars,
  whatIf,
  random,
}: {
  sim: WeekSim;
  you: number;
  avatars: Avatars;
  whatIf?: WhatIfApi;
  random: () => number;
}) {
  const file = sim.pages[you];
  const playoffs = file.playoffs!;
  const what = useWhatIf(file, whatIf);
  const shown = what.page.playoffs ?? playoffs;
  const name = nameOf(sim, you);
  const live = playoffs.alive && playoffs.champion === null;
  const game = playoffs.game;
  const chosen = game === null ? null : (what.set.find((result) => result.week === game.week) ?? null);
  const [replay, setReplay] = useState<StageAsk | null>(null);
  return (
    <div className="flex flex-col gap-sp-3 px-gutter pt-sp-4 pb-sp-6 tablet:px-0">
      <section aria-label="Your team" aria-busy={what.pending} className="flex w-full flex-col gap-sp-3">
        <div className="flex items-center gap-sp-3">
          <PhotoFrame src={avatars[String(you)] ?? null} name={name} size="md" decorative />
          <div className="min-w-0 flex-1">
            <h1 className="m-0 text-stat leading-tight font-bold text-balance">{name}</h1>
            <p className="m-0 text-meta text-pretty text-mute tabular-nums">{`${recordText(file.record)} · ${seasonLine(playoffs, you)}`}</p>
          </div>
          {live && (
            <div className="flex flex-none flex-col items-end">
              <SoftText
                text={oddsText(shown.title)}
                className={cn(
                  "justify-items-end font-mono text-score leading-none font-bold tabular-nums transition-opacity duration-150 ease-out",
                  what.pending && "opacity-50",
                )}
              />
              <span className={cn(LABEL, "pt-sp-1 text-mute")}>Title odds</span>
            </div>
          )}
        </div>
        <SetLine set={what.set} onReset={what.reset} />
        {what.down && (
          <p role="status" className="m-0 text-meta text-pretty text-mute">
            The What-if is not available now.
          </p>
        )}
      </section>
      <InPlayoffs
        sim={sim}
        you={you}
        avatars={avatars}
        shown={shown}
        whatIf={{ chosen, title: what.runs === null ? null : shown.title, onChoose: (choice) => game !== null && what.choose(game.week, choice) }}
      />
      {playoffs.champion === null && <SimButtons week={null} waiting={what.pending} onAsk={setReplay} />}
      {replay !== null && (
        <SimStage
          sim={sim}
          runs={what.runs ?? sim}
          avatars={avatars}
          yourTeam={you}
          ask={replay}
          random={random}
          onDone={() => setReplay(null)}
        />
      )}
    </div>
  );
}

function RegularSimPage({
  sim,
  you,
  avatars,
  whatIf,
  random,
}: {
  sim: WeekSim;
  you: number;
  avatars: Avatars;
  whatIf?: WhatIfApi;
  random: () => number;
}) {
  const file = sim.pages[you];
  const name = nameOf(sim, you);
  const what = useWhatIf(file, whatIf);
  const page = what.page;
  const items: WeekItem[] = [...file.weeks.map((week) => week.week), PLAYOFFS];
  // The side the open page came from: 1 from the right for a later item, -1 from the left, and 0 for the first page,
  // which shows at rest.
  const [{ open, side }, setView] = useState<{ open: WeekItem; side: number }>({ open: items[0], side: 0 });
  const off = useMotionOff();
  const [replay, setReplay] = useState<StageAsk | null>(null);

  const openItem = (item: WeekItem) => {
    setView((was) =>
      item === was.open ? was : { open: item, side: items.indexOf(item) > items.indexOf(was.open) ? 1 : -1 },
    );
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
          <WeekPage sim={sim} week={week} chosen={chosen ?? null} onChoose={(choice) => what.choose(week.week, choice)} />
        ) : (
          <PlayoffsPage sim={sim} page={page} team={(what.runs?.teams ?? sim.teams)[you]} onOpen={openItem} />
        )}
      </motion.div>

      <SimButtons week={typeof open === "number" ? open : null} waiting={what.pending} onAsk={setReplay} />
      {replay !== null && (
        <SimStage
          sim={sim}
          runs={what.runs ?? sim}
          avatars={avatars}
          yourTeam={you}
          ask={replay}
          random={random}
          onDone={() => setReplay(null)}
        />
      )}
    </div>
  );
}

/* The two buttons of the replay, in the flow under the week page and never fixed over content. The Playoffs page and
   the playoff weeks have only "Sim the season". While a What-if call runs, they wait, so the replay always plays a run of the set line. */
function SimButtons({ week, waiting, onAsk }: { week: number | null; waiting: boolean; onAsk: (ask: StageAsk) => void }) {
  const base = cn(
    PRESS,
    "flex min-h-touch flex-1 items-center justify-center gap-sp-2 rounded-report px-sp-3 text-body font-bold",
    "transition-opacity duration-150 ease-out disabled:opacity-50",
  );
  return (
    <div className="flex w-full gap-sp-2">
      {week !== null && (
        <button type="button" disabled={waiting} onClick={() => onAsk({ mode: "week", week })} className={cn(base, "border border-ink bg-page text-ink hover-fine:bg-card")}>
          <Play aria-hidden className="size-4" />
          {`Sim week ${week}`}
        </button>
      )}
      <button type="button" disabled={waiting} onClick={() => onAsk({ mode: "season" })} className={cn(base, "bg-accent text-on-dark hover-fine:opacity-90")}>
        <Shuffle aria-hidden className="size-4" />
        Sim the season
      </button>
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
