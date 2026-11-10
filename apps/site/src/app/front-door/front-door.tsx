/**
 * The front door at /: the sheet that asks for Your team on the first visit, then the Thread with the Suggestions and
 * the ask box. A tap on a Suggestion puts its Answer in the Thread. The browser keeps Your team and the opened Topics.
 */
"use client";

import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useRef, useState } from "react";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import type { DoorAnswer, DoorTeam } from "@/lib/data/front-door-data";
import { AnswerCard } from "./answer-card";
import { AskBox } from "./ask-box";
import { riseIn } from "./motion";
import { getOpened, markOpened } from "./opened-store";
import { Suggestions } from "./suggestions";
import { TeamSheet } from "./team-sheet";
import { TOPICS, pickSuggestions } from "./topics";
import { getYourTeam, setYourTeam } from "./your-team-store";

/* The ask box and the chips glide from the center of the empty Thread to the bottom on the first Answer, on one
   critically damped spring, as a reposition of apple-design. */
const COMPOSER_GLIDE = { type: "spring", bounce: 0, duration: 0.45 } as const;

/* The greeting changes with the hour, so the front door reads as a person and not a page. */
function greeting(hour: number): string {
  return hour < 5 ? "Late night" : hour < 12 ? "Good morning" : hour < 18 ? "Good afternoon" : "Good evening";
}

export function FrontDoor({
  siteName,
  week,
  teams,
  answers,
}: {
  siteName: string;
  week: number;
  teams: DoorTeam[];
  answers: Record<number, DoorAnswer[]>;
}) {
  const off = useMotionOff();
  // The day and the opened Topics live in the browser, so the static page renders no Suggestion until it reads them.
  const [day, setDay] = useState<number | null>(null);
  const [opened, setOpened] = useState<Record<string, string>>({});
  const [thread, setThread] = useState<string[]>([]);
  const [moreOpen, setMoreOpen] = useState(false);
  const newest = useRef<HTMLElement>(null);
  // undefined until the browser reads its store. The static page cannot know Your team, so it renders no team and no sheet.
  const [teamId, setTeamId] = useState<number | null | undefined>(undefined);
  const [picking, setPicking] = useState(false);
  const [hour, setHour] = useState<number | null>(null);

  useEffect(() => {
    const stored = getYourTeam();
    // A stored id of no team of the league, such as a roster of an old season, reads as no pick.
    const known = teams.some((team) => team.id === stored) ? stored : null;
    setTeamId(known);
    // The opened Topics load with Your team in one render, so an opened Topic never flashes in the Suggestions.
    if (known !== null) setOpened(getOpened(known, week));
    const now = new Date();
    setHour(now.getHours());
    setDay(now.getDay());
  }, [teams, week]);

  // A new Answer scrolls to its top, so the manager reads it from the question down.
  useEffect(() => {
    if (thread.length > 0) newest.current?.scrollIntoView?.({ behavior: off ? "auto" : "smooth", block: "start" });
  }, [thread, off]);

  const team = teams.find((candidate) => candidate.id === teamId) ?? null;
  const sheetOpen = teamId === null || picking;
  const mine = team ? (answers[team.id] ?? []) : [];
  const facts = Object.fromEntries(mine.map((answer) => [answer.topic, answer.fact]));
  const picks = day === null ? [] : pickSuggestions(day, facts, opened);
  const avatars = Object.fromEntries(teams.map((candidate) => [candidate.id, candidate.avatar]));
  const empty = thread.length === 0;
  const open = (key: string) => {
    const answer = mine.find((candidate) => candidate.topic === key);
    if (!team || !answer) return;
    setOpened(markOpened(team.id, week, key, answer.fact));
    setThread((keys) => [...keys, key]);
    setMoreOpen(false);
  };
  const pick = (id: number) => {
    setYourTeam(id);
    setTeamId(id);
    // Each team keeps its own opened Topics, so a change of Your team reads the record of that team.
    setOpened(getOpened(id, week));
    setThread([]);
    setMoreOpen(false);
    setPicking(false);
  };

  return (
    <>
      {/* The Thread fills the view between the top band and the dock. Empty, it holds the ask box at its center. With
          an Answer, it reads top to bottom, and the chips and the ask box sit at its foot, clear of the home bar. */}
      <section
        aria-label="Thread"
        className={`mx-auto flex min-h-door-fill w-full max-w-door desktop:min-h-door-fill-desktop flex-col px-gutter pt-sp-6 ${empty ? "justify-center pb-door-lift" : "justify-end"}`}
      >
        {team && (
          <div key={team.id} className={`flex flex-col gap-sp-5 ${empty ? "" : "min-h-0 flex-1"}`}>
            {empty ? (
              <motion.div className="flex flex-col gap-sp-2" {...riseIn(off, { text: true })}>
                <span className="font-mono text-meta leading-tight tracking-caps text-mute uppercase">
                  {hour !== null ? `${greeting(hour)} · ` : ""}Week {week}
                </span>
                <h1 className="m-0 text-score leading-tight font-bold tracking-tight tablet:text-headline">
                  <span className="text-mute">Ask about</span> <span>{team.name}</span>
                </h1>
              </motion.div>
            ) : (
              <div className="flex flex-1 flex-col gap-sp-6">
                <h1 className="sr-only">Ask about {team.name}</h1>
                {thread.map((key, index) => {
                  const answer = mine.find((candidate) => candidate.topic === key);
                  const name = TOPICS.find((topic) => topic.key === key)?.name ?? key;
                  return answer ? (
                    <AnswerCard key={index} ref={index === thread.length - 1 ? newest : undefined} name={name} answer={answer} avatars={avatars} />
                  ) : null;
                })}
              </div>
            )}
            <motion.div
              layout={!off}
              transition={COMPOSER_GLIDE}
              className={`flex flex-col gap-sp-3 ${empty ? "" : "sticky bottom-door-foot z-10 -mx-gutter bg-page/90 px-gutter pt-sp-3 pb-sp-3 backdrop-blur-md desktop:bottom-0"}`}
            >
              {picks.length > 0 || moreOpen ? (
                <motion.div {...riseIn(off, { delay: 0.06 })}>
                  <Suggestions picks={picks} facts={facts} moreOpen={moreOpen} onMore={setMoreOpen} onPick={open} />
                </motion.div>
              ) : null}
              <motion.div {...riseIn(off, { delay: 0.08 })}>
                <AskBox />
              </motion.div>
              {empty && (
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
              )}
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
