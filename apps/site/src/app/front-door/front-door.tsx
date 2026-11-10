/**
 * The front door at /: the sheet that asks for Your team on the first visit, then the Thread with the Suggestions and
 * the ask box. A tap on a Suggestion puts its Answer in the Thread, and a typed question goes to the route of the API.
 * The browser keeps Your team, the opened Topics, and the league passphrase.
 */
"use client";

import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useRef, useState } from "react";
import { clearPassphrase, getPassphrase, setPassphrase } from "@cpc/analyzer/lib/passphrase";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import type { DoorAnswer, DoorTeam } from "@/lib/data/front-door-data";
import { AnswerCard } from "./answer-card";
import { type AskTarget, AskError, askRoute } from "./ask-api";
import { AskBox } from "./ask-box";
import { type ThreadItem, itemOfError, itemOfRoute } from "./ask-thread";
import { MissCard, NoteCard, PassphraseCard, PendingCard } from "./miss-card";
import { riseIn } from "./motion";
import { getOpened, markOpened } from "./opened-store";
import { Suggestions } from "./suggestions";
import { TeamSheet } from "./team-sheet";
import { TOPICS, pickSuggestions } from "./topics";
import { getYourTeam, setYourTeam } from "./your-team-store";

/* The ask box and the chips glide from the center of the empty Thread to the bottom on the first Answer, on one
   critically damped spring, as a reposition of apple-design. */
const COMPOSER_GLIDE = { type: "spring", bounce: 0, duration: 0.45 } as const;

/* One item of the Thread with its id, so a reply of the API lands in the place of its question. */
type Entry = ThreadItem & { id: number };

/* The greeting changes with the hour, so the front door reads as a person and not a page. */
function greeting(hour: number): string {
  return hour < 5 ? "Late night" : hour < 12 ? "Good morning" : hour < 18 ? "Good afternoon" : "Good evening";
}

export function FrontDoor({
  siteName,
  week,
  teams,
  answers,
  askTarget,
}: {
  siteName: string;
  week: number;
  teams: DoorTeam[];
  answers: Record<number, DoorAnswer[]>;
  askTarget: AskTarget;
}) {
  const off = useMotionOff();
  // The day and the opened Topics live in the browser, so the static page renders no Suggestion until it reads them.
  const [day, setDay] = useState<number | null>(null);
  const [opened, setOpened] = useState<Record<string, string>>({});
  const [thread, setThread] = useState<Entry[]>([]);
  const nextId = useRef(0);
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
  // A miss shows its 3 closest Topics, so the chips of the dock hide and the Topics show only once (AT-13).
  const missed = thread.at(-1)?.kind === "miss";
  /* Put the item in the place of its id. A new id appends. A reply after a change of Your team finds no place, so it
     never lands in the Thread of another team. */
  const put = (id: number, item: ThreadItem, append = false) =>
    setThread((entries) => {
      const at = entries.findIndex((entry) => entry.id === id);
      if (at < 0) return append ? [...entries, { ...item, id }] : entries;
      return entries.map((entry, index) => (index === at ? { ...item, id } : entry));
    });
  /* Open the Answer of a Topic for `of`, Your team by default, or for the team that a typed question named. */
  const open = (key: string, of: number | null = null) => {
    if (!team) return;
    const owner = of ?? team.id;
    const answer = (answers[owner] ?? []).find((candidate) => candidate.topic === key);
    setMoreOpen(false);
    if (!answer) {
      // A closest Topic of a miss can be a live Topic, which this build cannot answer yet.
      const name = TOPICS.find((topic) => topic.key === key)?.name ?? key;
      put(nextId.current++, { kind: "note", question: name, line: `${name} opens here soon.`, topic: null, team: null, retry: false }, true);
      return;
    }
    // Only a Topic of Your team drops off the Suggestions of Your team.
    if (owner === team.id) setOpened(markOpened(team.id, week, key, answer.fact));
    put(nextId.current++, { kind: "topic", key, team: owner, question: null }, true);
  };
  const send = async (id: number, question: string, append = false) => {
    if (!team) return;
    const passphrase = getPassphrase();
    if (!passphrase) {
      put(id, { kind: "passphrase", question, wrong: false }, append);
      return;
    }
    put(id, { kind: "pending", question }, append);
    try {
      const route = await askRoute(askTarget, passphrase, { question, roster_id: team.id, week });
      put(id, itemOfRoute(route, question, team.id, answers));
    } catch (error) {
      if (error instanceof AskError && error.status === 401) clearPassphrase();
      put(id, itemOfError(error, question));
    }
  };
  const ask = (question: string) => {
    setMoreOpen(false);
    void send(nextId.current++, question, true);
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
                {thread.map((entry, index) => {
                  const ref = index === thread.length - 1 ? newest : undefined;
                  switch (entry.kind) {
                    case "topic": {
                      const answer = (answers[entry.team] ?? []).find((candidate) => candidate.topic === entry.key);
                      const name = entry.question ?? TOPICS.find((topic) => topic.key === entry.key)?.name ?? entry.key;
                      return answer ? <AnswerCard key={entry.id} ref={ref} name={name} answer={answer} avatars={avatars} /> : null;
                    }
                    case "pending":
                      return <PendingCard key={entry.id} ref={ref} question={entry.question} />;
                    case "passphrase":
                      return (
                        <PassphraseCard
                          key={entry.id}
                          ref={ref}
                          question={entry.question}
                          wrong={entry.wrong}
                          onPassphrase={(value) => {
                            setPassphrase(value);
                            void send(entry.id, entry.question);
                          }}
                        />
                      );
                    case "miss":
                      return <MissCard key={entry.id} ref={ref} question={entry.question} closest={entry.closest} onPick={(key) => open(key)} />;
                    case "note":
                      return (
                        <NoteCard
                          key={entry.id}
                          ref={ref}
                          question={entry.question}
                          line={entry.line}
                          topic={entry.topic ?? undefined}
                          team={entry.team !== null && entry.team !== team.id ? teams.find((other) => other.id === entry.team)?.name : undefined}
                          onPick={(key) => open(key, entry.team)}
                          action={entry.retry ? { label: "Ask again", onClick: () => void send(entry.id, entry.question) } : undefined}
                        />
                      );
                  }
                })}
              </div>
            )}
            <motion.div
              layout={!off}
              transition={COMPOSER_GLIDE}
              className={`flex flex-col gap-sp-3 ${empty ? "" : "sticky bottom-door-foot z-10 -mx-gutter bg-page/90 px-gutter pt-sp-3 pb-sp-3 backdrop-blur-md desktop:bottom-0"}`}
            >
              {!missed && (picks.length > 0 || moreOpen) ? (
                <motion.div {...riseIn(off, { delay: 0.06 })}>
                  <Suggestions picks={picks} facts={facts} moreOpen={moreOpen} onMore={setMoreOpen} onPick={(key) => open(key)} />
                </motion.div>
              ) : null}
              <motion.div {...riseIn(off, { delay: 0.08 })}>
                <AskBox onAsk={ask} />
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
