/**
 * The sim page of Your team, layout D "Cards" (decision 04): the header with the odds, the sentence that opens the ladder,
 * the week switch, and one page per week with the week card and the root-for card. It reads only the page block of sim.json.
 */
"use client";

import { motion } from "framer-motion";
import { useState } from "react";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { PhotoFrame } from "@cpc/design/parts/photo-frame";
import { cn } from "@cpc/design/lib/utils";
import type { WeekSim } from "../schema/sim-types";
import { LABEL, nameOf, oddsText, recordText } from "./format";
import { InPlayoffs, seasonLine } from "./in-playoffs";
import { LadderSheet } from "./ladder-sheet";
import { PlayoffsPage } from "./playoffs-page";
import { PLAYOFFS, WeekSwitch, type WeekItem } from "./week-switch";
import { WeekPage } from "./week-page";

/* The avatar src of each team by roster id, with the base path, from the latest week. */
export type Avatars = Record<string, string>;

/* The entry of a week page: the page slide of transitions-dev, a short move from the side of the item with a soft blur. */
const ENTER = { duration: 0.25, ease: [0.22, 1, 0.36, 1] } as const;

export function SimPage({ sim, you, avatars = {} }: { sim: WeekSim; you: number; avatars?: Avatars }) {
  if (sim.pages[you].playoffs) return <PlayoffSimPage sim={sim} you={you} avatars={avatars} />;
  return <RegularSimPage sim={sim} you={you} avatars={avatars} />;
}

/* The sim page with no regular week left: Your team with its title odds, then the playoff cards. No week switch and no
   ladder, because no regular week is left to win. */
function PlayoffSimPage({ sim, you, avatars }: { sim: WeekSim; you: number; avatars: Avatars }) {
  const page = sim.pages[you];
  const playoffs = page.playoffs!;
  const name = nameOf(sim, you);
  const live = playoffs.alive && playoffs.champion === null;
  return (
    <div className="flex flex-col gap-sp-3 px-gutter pt-sp-4 pb-sp-6 tablet:px-0">
      <section aria-label="Your team" className="flex w-full items-center gap-sp-3">
        <PhotoFrame src={avatars[String(you)] ?? null} name={name} size="md" decorative />
        <div className="min-w-0 flex-1">
          <h1 className="m-0 text-stat leading-tight font-bold text-balance">{name}</h1>
          <p className="m-0 text-meta text-pretty text-mute tabular-nums">{`${recordText(page.record)} · ${seasonLine(playoffs, you)}`}</p>
        </div>
        {live && (
          <div className="flex flex-none flex-col items-end">
            <span className="font-mono text-score leading-none font-bold tabular-nums">{oddsText(playoffs.title)}</span>
            <span className={cn(LABEL, "pt-sp-1 text-mute")}>Title odds</span>
          </div>
        )}
      </section>
      <InPlayoffs sim={sim} you={you} avatars={avatars} />
    </div>
  );
}

function RegularSimPage({ sim, you, avatars }: { sim: WeekSim; you: number; avatars: Avatars }) {
  const page = sim.pages[you];
  const name = nameOf(sim, you);
  const items: WeekItem[] = [...page.weeks.map((week) => week.week), PLAYOFFS];
  // The side the open page came from: 1 from the right for a later item, -1 from the left, and 0 for the first page,
  // which shows at rest.
  const [{ open, side }, setView] = useState<{ open: WeekItem; side: number }>({ open: items[0], side: 0 });
  const off = useMotionOff();

  const openItem = (item: WeekItem) => {
    if (item === open) return;
    setView({ open: item, side: items.indexOf(item) > items.indexOf(open) ? 1 : -1 });
  };
  const week = page.weeks.find((entry) => entry.week === open);

  return (
    <div className="flex flex-col gap-sp-3 px-gutter pt-sp-4 pb-sp-6 tablet:px-0">
      <section aria-label="Your team" className="flex w-full flex-col gap-sp-3">
        <div className="flex items-center gap-sp-3">
          <PhotoFrame src={avatars[String(you)] ?? null} name={name} size="md" decorative />
          <div className="min-w-0 flex-1">
            <h1 className="m-0 text-stat leading-tight font-bold text-balance">{name}</h1>
            <p className="m-0 text-meta text-mute tabular-nums">{`${recordText(page.record)} · ${page.weeks_left} weeks left`}</p>
          </div>
          <div className="flex flex-none flex-col items-end">
            <span className="font-mono text-score leading-none font-bold tabular-nums">{oddsText(page.playoff)}</span>
            <span className={cn(LABEL, "pt-sp-1 text-mute")}>Playoff odds</span>
          </div>
        </div>
        <LadderSheet page={page} medianGame={sim.parameters.median_game} />
      </section>

      <WeekSwitch items={items} open={open} onOpen={openItem} />

      <motion.div
        key={String(open)}
        initial={side === 0 ? false : off ? { opacity: 0 } : { opacity: 0, x: side * 8, filter: "blur(3px)" }}
        animate={{ opacity: 1, x: 0, filter: "blur(0px)" }}
        transition={off ? { duration: 0.15 } : ENTER}
      >
        {week !== undefined ? (
          <WeekPage sim={sim} week={week} />
        ) : (
          <PlayoffsPage sim={sim} you={you} onOpen={openItem} />
        )}
      </motion.div>
    </div>
  );
}
