/**
 * The front door at /: the sheet that asks for Your team on the first visit, then the empty Thread with the ask box at
 * its center. The browser keeps Your team, so a reload opens straight on the Thread.
 */
"use client";

import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useState } from "react";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import type { DoorTeam } from "@/lib/data/front-door-data";
import { AskBox } from "./ask-box";
import { riseIn } from "./motion";
import { TeamSheet } from "./team-sheet";
import { getYourTeam, setYourTeam } from "./your-team-store";

/* The greeting changes with the hour, so the front door reads as a person and not a page. */
function greeting(hour: number): string {
  return hour < 5 ? "Late night" : hour < 12 ? "Good morning" : hour < 18 ? "Good afternoon" : "Good evening";
}

export function FrontDoor({ siteName, week, teams }: { siteName: string; week: number; teams: DoorTeam[] }) {
  const off = useMotionOff();
  // undefined until the browser reads its store. The static page cannot know Your team, so it renders no team and no sheet.
  const [teamId, setTeamId] = useState<number | null | undefined>(undefined);
  const [picking, setPicking] = useState(false);
  const [hour, setHour] = useState<number | null>(null);

  useEffect(() => {
    const stored = getYourTeam();
    // A stored id of no team of the league, such as a roster of an old season, reads as no pick.
    setTeamId(teams.some((team) => team.id === stored) ? stored : null);
    setHour(new Date().getHours());
  }, [teams]);

  const team = teams.find((candidate) => candidate.id === teamId) ?? null;
  const sheetOpen = teamId === null || picking;
  const pick = (id: number) => {
    setYourTeam(id);
    setTeamId(id);
    setPicking(false);
  };

  return (
    <>
      {/* The empty Thread: the ask box sits at its center, between the top band and the dock, clear of the home bar. */}
      <section aria-label="Thread" className="mx-auto flex min-h-door-fill w-full max-w-door desktop:min-h-door-fill-desktop flex-col justify-center px-gutter pt-sp-6 pb-door-lift">
        {team && (
          <div key={team.id} className="flex flex-col gap-sp-5">
            <motion.div className="flex flex-col gap-sp-2" {...riseIn(off, { text: true })}>
              <span className="font-mono text-meta leading-tight tracking-caps text-mute uppercase">
                {hour !== null ? `${greeting(hour)} · ` : ""}Week {week}
              </span>
              <h1 className="m-0 text-score leading-tight font-bold tracking-tight tablet:text-headline">
                <span className="text-mute">Ask about</span> <span>{team.name}</span>
              </h1>
            </motion.div>
            <motion.div {...riseIn(off, { delay: 0.08 })}>
              <AskBox />
            </motion.div>
            <motion.div className="flex" {...riseIn(off, { delay: 0.16 })}>
              <button
                type="button"
                onClick={() => setPicking(true)}
                aria-label={`Your team: ${team.name}. Change the team`}
                className="press -ml-sp-2 flex min-h-touch items-center gap-sp-2 rounded-pill px-sp-2 text-meta leading-tight text-mute hover-fine:text-ink"
              >
                {team.avatar ? (
                  <img src={team.avatar} alt="" width={20} height={20} className="size-sp-5 flex-none rounded-full bg-raised object-cover" />
                ) : (
                  <span aria-hidden className="size-sp-5 flex-none rounded-full bg-raised" />
                )}
                <span>Not your team? Change it</span>
              </button>
            </motion.div>
          </div>
        )}
      </section>
      <AnimatePresence>
        {teamId !== undefined && sheetOpen && <TeamSheet key="sheet" siteName={siteName} teams={teams} current={team?.id ?? null} onPick={pick} />}
      </AnimatePresence>
    </>
  );
}
