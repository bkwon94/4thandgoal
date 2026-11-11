/**
 * The front door at /: the sheet that asks for Your team on the first visit, then the Thread with the Suggestions and
 * the ask box. A tap on a Suggestion puts its Answer in the Thread, and a typed question goes to the route of the API.
 * The browser keeps Your team, the opened Topics, the league passphrase, and one Thread per team for the week.
 */
"use client";

import { AnimatePresence, motion } from "framer-motion";
import { Fragment, useEffect, useRef, useState } from "react";
import { ChevronsUpDownIcon } from "lucide-react";
import { clearPassphrase, getPassphrase, setPassphrase } from "@cpc/analyzer/lib/passphrase";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import type { DoorAnswer, DoorTeam } from "@/lib/data/front-door-data";
import { analyzeHref } from "@/lib/routes";
import { type AskTarget, AskError, askRoute } from "./ask-api";
import { AskBox } from "./ask-box";
import { turnsBefore } from "./chat-turns";
import { RETRY_LINE, TRADE_LINES, TRADE_TOPICS, TRADE_TOPIC_OF, type ThreadItem, ideasRequestOf, itemOfError, itemOfRoute, tradePartner, tradeRequestOf } from "./ask-thread";
import { FreeAnswerCard, FreeAnswerLive } from "./free-answer";
import { CapCard, MissCard, NoteCard, PassphraseCard, PendingCard } from "./miss-card";
import { keepFocus, closeKeyboard } from "./keyboard-tap";
import { GLIDE, riseIn } from "./motion";
import { PersonalAnswerCard, PersonalAnswerLive } from "./personal-answer";
import { PERSONAL_LINES, isPersonal } from "./personal-stream";
import { getOpened, markOpened } from "./opened-store";
import { Suggestions } from "./suggestions";
import { TeamSheet } from "./team-sheet";
import { type Entry, Thread, personalName } from "./thread";
import { clearThread, getThread, saveThread } from "./thread-store";
import { type KeyItem, type ServedSuggestions, checkCurrent, fetchSuggestions, staleLine } from "./suggestions-api";
import { dayOrder, pickSuggestions, topicName } from "./topics";
import { TradeCard } from "./trade-answer";
import { type TradeRead, type TradeRequest, type TradeSteps, addStep, endSteps, noSteps, streamTrade } from "./trade-api";
import { getYourTeam, setYourTeam } from "./your-team-store";

/* The two questions the empty screen offers, so a manager sees that the league is fair game, not only Your team. */
const EXAMPLES = ["who has the best roster", "week 1 results"];

/* The greeting changes with the hour, so the front door reads as a person and not a page. */
function greeting(hour: number): string {
  return hour < 5 ? "Late night" : hour < 12 ? "Good morning" : hour < 18 ? "Good afternoon" : "Good evening";
}

export function FrontDoor({
  siteName,
  week,
  teams,
  answers,
  personalHrefs = {},
  askTarget,
}: {
  siteName: string;
  week: number;
  teams: DoorTeam[];
  answers: Record<number, DoorAnswer[]>;
  // The page of each personal Topic of each team, by roster id. A team with no entry has no link.
  personalHrefs?: Record<number, Record<string, string | null>>;
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
  // The live facts and the urgent Topics of Your team from the API, once it answers. Until then, and with no
  // passphrase, the Suggestions come from the facts of the weekly build alone.
  const [served, setServed] = useState<{ team: number; suggestions: ServedSuggestions } | null>(null);
  // The kept personal and trade Answers whose roster changed, by the key of each, with the time that the API kept it.
  // The API keeps no trade Answer, so its time is null and the trade Answer gives the time of its own read.
  const [stale, setStale] = useState<Record<string, string | null>>({});
  const openedNow = useRef(opened);
  openedNow.current = opened;
  // A kept entry gets a fresh id on load, so a reply of the API never lands on an entry of an earlier visit.
  const load = (id: number): Entry[] => getThread(id, week).map((item) => ({ ...item, id: nextId.current++ }));

  useEffect(() => {
    const stored = getYourTeam();
    // A stored id of no team of the league, such as a roster of an old season, reads as no pick.
    const known = teams.some((team) => team.id === stored) ? stored : null;
    setTeamId(known);
    // The opened Topics and the Thread load with Your team in one render, so an opened Topic never flashes in the
    // Suggestions and a kept Thread never flashes empty.
    if (known !== null) {
      setOpened(getOpened(known, week));
      setThread(load(known));
    }
    const now = new Date();
    setHour(now.getHours());
    setDay(now.getDay());
  }, [teams, week]);

  // The browser keeps the Thread of Your team on each change. The Thread and Your team change in one render, so the
  // Thread of one team never lands under another team.
  useEffect(() => {
    if (teamId != null) saveThread(teamId, week, thread);
  }, [thread, teamId, week]);

  // On open, the API serves the Suggestions of Your team: the live fact of each personal Topic and the Topics that are
  // urgent. It also builds the Answer of the top Suggestion when it is a personal Topic, so the first tap shows it at
  // once. One call per team and day, so a tap never asks again. A failed call keeps the Suggestions of the build.
  useEffect(() => {
    const passphrase = getPassphrase();
    if (teamId == null || day === null || !passphrase) return;
    let live = true;
    fetchSuggestions(askTarget, passphrase, { roster_id: teamId, order: dayOrder(day), opened: openedNow.current })
      .then((suggestions) => live && setServed({ team: teamId, suggestions }))
      .catch(() => {});
    return () => {
      live = false;
    };
  }, [teamId, day, askTarget]);

  // The site asks the API whether the key of each personal and trade Answer of the Thread is still current. The check
  // costs nothing. It runs again only when the set of kept Answers changes. A trade Answer with no key never checks.
  const kept: KeyItem[] = thread.flatMap((entry): KeyItem[] => {
    if (teamId == null) return [];
    if (entry.kind === "personal" && entry.result)
      return [{ topic: entry.key, roster_id: teamId, team: entry.team === teamId ? null : entry.team, key: entry.result.key }];
    if (entry.kind === "trade" && entry.answer && entry.read)
      return [{ topic: TRADE_TOPIC_OF[entry.mode] as KeyItem["topic"], roster_id: teamId, team: tradePartner(entry.answer), key: entry.read.key }];
    return [];
  });
  const keptNow = useRef(kept);
  keptNow.current = kept;
  const keptSignature = kept.map((item) => item.key).join("|");
  useEffect(() => {
    const passphrase = getPassphrase();
    if (teamId == null || !passphrase || keptSignature === "") return;
    let live = true;
    checkCurrent(askTarget, passphrase, keptNow.current)
      .then((states) => {
        if (!live) return;
        setStale(Object.fromEntries(states.filter((state) => !state.current).map((state) => [state.key, state.kept_at])));
      })
      .catch(() => {});
    return () => {
      live = false;
    };
  }, [teamId, keptSignature, askTarget]);

  // A new Answer scrolls to its top, so the manager reads it from the question down.
  useEffect(() => {
    if (thread.length > 0) newest.current?.scrollIntoView?.({ behavior: off ? "auto" : "smooth", block: "start" });
  }, [thread, off]);

  const team = teams.find((candidate) => candidate.id === teamId) ?? null;
  const sheetOpen = teamId === null || picking;
  const mine = team ? (answers[team.id] ?? []) : [];
  const servedNow = served && team && served.team === team.id ? served.suggestions : null;
  const facts = { ...Object.fromEntries(mine.map((answer) => [answer.topic, answer.fact])), ...servedNow?.facts };
  const picks = day === null ? [] : pickSuggestions(day, facts, opened, servedNow?.urgent ?? []);
  const avatars = Object.fromEntries(teams.map((candidate) => [candidate.id, candidate.avatar]));
  const empty = thread.length === 0;
  // A miss and a cap line show their 3 closest Topics, so the chips of the dock hide and the Topics show only once
  // (AT-13).
  const last = thread.at(-1)?.kind;
  const missed = last === "miss" || last === "cap";
  /* Put the item in the place of its id. A new id appends. A reply after a change of Your team finds no place, so it
     never lands in the Thread of another team. */
  const put = (id: number, item: ThreadItem, append = false) =>
    setThread((entries) => {
      const at = entries.findIndex((entry) => entry.id === id);
      if (at < 0) return append ? [...entries, { ...item, id }] : entries;
      return entries.map((entry, index) => (index === at ? { ...item, id } : entry));
    });
  /* Run a trade Topic in the place of `id`: each step lands as it comes, then the whole Answer. A failure is an error
     line, never an Answer. Past a cap, the cap line takes the place of the Answer, with `closest` as its Topics. */
  const runTrade = async (id: number, question: string, request: TradeRequest, passphrase: string, closest: string[], append = false) => {
    let steps: TradeSteps = noSteps;
    let read: TradeRead | undefined;
    const show = (answer: Extract<ThreadItem, { kind: "trade" }>["answer"], first = false) =>
      put(id, { kind: "trade", mode: request.mode, question, steps: answer ? endSteps(steps) : steps.lines, answer, ...(read ? { read } : {}) }, first && append);
    show(null, true);
    try {
      await streamTrade(askTarget, passphrase, request, {
        onStep: (line, live) => {
          steps = addStep(steps, line, live);
          show(null);
        },
        onKey: (key) => {
          read = key;
        },
        onAnswer: (answer) => show(answer),
        onCap: (line) => put(id, { kind: "cap", question, line, closest }),
      });
    } catch (error) {
      if (error instanceof AskError && error.status === 401) clearPassphrase();
      put(id, itemOfError(error, question));
    }
  };
  /* Open the Answer of a Topic for `of`, Your team by default, or for the team that a typed question named. */
  const open = (key: string, of: number | null = null) => {
    if (!team) return;
    const owner = of ?? team.id;
    const mode = TRADE_TOPICS[key];
    if (mode) {
      setMoreOpen(false);
      const name = topicName(key);
      const partner = owner === team.id ? null : owner;
      // A tapped trade check names no trade, so it opens the Trade page with Your team and the team it is about.
      if (mode === "check") {
        put(nextId.current++, { kind: "trade", mode, question: name, steps: [], answer: { kind: "form", form: { asker: team.id, partner, gives: [], gets: [] } } }, true);
        return;
      }
      const passphrase = getPassphrase();
      if (!passphrase) return void put(nextId.current++, { kind: "passphrase", question: name, wrong: false }, true);
      // A trade Topic of Your team drops off the Suggestions until the API serves a new fact for it.
      if (owner === team.id && facts[key]) setOpened(markOpened(team.id, week, key, facts[key]));
      // A tapped Topic has no closest Topics of its own, so a cap line offers the Suggestions of the day. A trade
      // Topic past the cap stops at the same cap, so the cap line leaves each one out. Sell high speaks to the manager
      // of the roster as "you", so it always reads Your team.
      const closest = picks.filter((pick) => !TRADE_TOPICS[pick]);
      void runTrade(nextId.current++, name, mode === "sell" ? { mode, roster_id: team.id } : { mode, roster_id: team.id, partner }, passphrase, closest, true);
      return;
    }
    // A personal Topic builds live on the API, so it needs the passphrase as a typed question does.
    if (isPersonal(key)) {
      setMoreOpen(false);
      const name = topicName(key);
      if (!getPassphrase()) put(nextId.current++, { kind: "passphrase", question: name, wrong: false }, true);
      else {
        // A personal Topic of Your team drops off the Suggestions until the API serves a new fact for it.
        if (owner === team.id && facts[key]) setOpened(markOpened(team.id, week, key, facts[key]));
        put(nextId.current++, { kind: "personal", key, team: owner, question: null, result: null }, true);
      }
      return;
    }
    const answer = (answers[owner] ?? []).find((candidate) => candidate.topic === key);
    setMoreOpen(false);
    if (!answer) {
      // A closest Topic of a miss can be a live Topic, which this build cannot answer yet.
      const name = topicName(key);
      put(nextId.current++, { kind: "note", question: name, line: `${name} opens here soon.`, topic: null, team: null, retry: false }, true);
      return;
    }
    // Only a Topic of Your team drops off the Suggestions of Your team.
    if (owner === team.id) setOpened(markOpened(team.id, week, key, answer.fact));
    put(nextId.current++, { kind: "topic", key, team: owner, question: null }, true);
  };
  /* The earlier turns of the Thread before the item of `id`, so a follow-up reads like the whole question. */
  const turnsOf = (id: number) =>
    turnsBefore(thread, id, answers, (other) => (team && other !== team.id ? teams.find((candidate) => candidate.id === other)?.name : undefined));
  const send = async (id: number, question: string, append = false) => {
    if (!team) return;
    const passphrase = getPassphrase();
    if (!passphrase) {
      put(id, { kind: "passphrase", question, wrong: false }, append);
      return;
    }
    put(id, { kind: "pending", question }, append);
    try {
      const turns = turnsOf(id);
      const route = await askRoute(askTarget, passphrase, { question, roster_id: team.id, week, turns });
      const mode = route.route === "topic" && route.topic ? TRADE_TOPICS[route.topic] : undefined;
      // A trade Topic needs the trade judge, so the typed question goes on to its route with the team it names.
      if (mode === "check") return void (await runTrade(id, question, { mode, question, roster_id: team.id }, passphrase, route.closest));
      if (mode === "sell") return void (await runTrade(id, question, { mode, roster_id: team.id }, passphrase, route.closest));
      if (mode === "ideas") return void (await runTrade(id, question, ideasRequestOf(route, question, team.id, turns), passphrase, route.closest));
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
    // Each team keeps its own opened Topics and its own Thread, so a quick look at another team never erases a Thread.
    setOpened(getOpened(id, week));
    setThread(load(id));
    setMoreOpen(false);
    setPicking(false);
  };
  // Clear empties the Thread at once with no confirm, because the Answers of the league Topics come back with a tap.
  // The opened Topics stay, so the Suggestions stay fresh (decision 05).
  const clear = () => {
    if (!team) return;
    clearThread(team.id, week);
    setThread([]);
    setMoreOpen(false);
  };
  const changeTeam = team && (
    <button
      type="button"
      onClick={() => setPicking(true)}
      aria-label={`Your team: ${team.name}. Change the team`}
      className="press -ml-sp-2 flex min-h-touch min-w-0 items-center gap-sp-2 rounded-pill px-sp-2 text-meta leading-tight text-mute hover-fine:text-ink"
    >
      {team.avatar ? (
        <img src={team.avatar} alt="" width={20} height={20} className="size-sp-5 flex-none rounded-full bg-raised object-cover" />
      ) : (
        <span aria-hidden className="size-sp-5 flex-none rounded-full bg-raised" />
      )}
      <span className="truncate">{empty ? "Not your team? Change it" : team.name}</span>
      {/* In the Thread header the name alone could read as a label, so a small up-down mark says it opens a choice. */}
      {!empty && <ChevronsUpDownIcon aria-hidden className="size-sp-4 flex-none" strokeWidth={2.25} />}
    </button>
  );

  return (
    <>
      {/* The Thread fills the view between the top band and the dock. Empty, it holds the ask box at its center. With
          an Answer, it reads top to bottom, and the chips and the ask box sit at its foot, clear of the home bar. */}
      <section
        aria-label="Thread"
        className={`mx-auto flex min-h-door-fill w-full max-w-door desktop:min-h-door-fill-desktop flex-col px-gutter ${empty ? "justify-center pt-sp-6 pb-door-lift" : "justify-end pt-sp-2"}`}
      >
        {team && (
          <div key={team.id} className={`flex flex-col gap-sp-5 ${empty ? "" : "min-h-0 flex-1"}`}>
            {empty ? (
              <motion.div className="flex flex-col gap-sp-2" {...riseIn(off, { text: true })}>
                <span className="font-mono text-meta leading-tight tracking-caps text-mute uppercase">
                  {hour !== null ? `${greeting(hour)} · ` : ""}Week {week}
                </span>
                <h1 className="m-0 text-score leading-tight font-bold tracking-tight tablet:text-headline">
                  <span className="text-mute">Ask about</span> <span className="text-door-name">{team.name}</span>
                </h1>
                <p className="m-0 text-lead leading-tight text-mute">or any team in the league.</p>
                {/* Each example asks as a typed question does. The press keeps the focus in the field, so one tap works with
                    the keyboard open. The ask runs first, then the keyboard closes and the Answer shows. */}
                <p className="m-0 flex flex-wrap items-center gap-x-sp-1 text-body leading-tight text-mute">
                  <span>Try</span>
                  {EXAMPLES.map((example, index) => (
                    <Fragment key={example}>
                      {index > 0 && <span>or</span>}
                      <button
                        type="button"
                        onMouseDown={keepFocus}
                        onClick={() => {
                          ask(example);
                          closeKeyboard();
                        }}
                        className="press inline-flex min-h-touch items-center text-ink underline decoration-door-hair decoration-1 underline-offset-4 transition-colors duration-150 hover-fine:decoration-ink"
                      >
                        <span aria-hidden>&ldquo;</span>
                        {example}
                        <span aria-hidden>&rdquo;</span>
                      </button>
                    </Fragment>
                  ))}
                </p>
              </motion.div>
            ) : (
              <div className="flex flex-1 flex-col">
                <h1 className="sr-only">Ask about {team.name}</h1>
                {/* The Thread header sticks under the top band on the page color, so the team and Clear stay one tap
                    away while the Answers scroll under it. */}
                <header
                  aria-label="Thread header"
                  className="sticky top-band-height z-10 -mx-gutter flex min-h-door-head items-center justify-between gap-sp-3 bg-page/90 px-gutter backdrop-blur-md"
                >
                  {changeTeam}
                  <button
                    type="button"
                    onClick={clear}
                    className="press -mr-sp-2 flex min-h-touch flex-none items-center rounded-pill px-sp-3 text-meta leading-tight font-semibold text-mute hover-fine:text-ink"
                  >
                    Clear
                  </button>
                </header>
                <Thread
                  entries={thread}
                  answers={answers}
                  avatars={avatars}
                  newest={newest}
                  renderOther={(entry, ref) => {
                    switch (entry.kind) {
                      case "pending":
                        return <PendingCard ref={ref} question={entry.question} />;
                      case "passphrase":
                        return (
                          <PassphraseCard
                            ref={ref}
                            question={entry.question}
                            wrong={entry.wrong}
                            onPassphrase={(value) => {
                              setPassphrase(value);
                              void send(entry.id, entry.question);
                            }}
                          />
                        );
                      case "trade": {
                        const since = entry.read ? stale[entry.read.key] : undefined;
                        const { answer } = entry;
                        const passphrase = getPassphrase();
                        // Refresh runs the Topic again in the same place. The rosters changed, so its key is new. A
                        // stale trade Answer gives the time of its own read, because the API keeps no trade Answer.
                        const refresh =
                          since !== undefined && answer && entry.read && passphrase
                            ? { line: staleLine(since ?? entry.read.at), onRefresh: () => void runTrade(entry.id, entry.question, tradeRequestOf({ ...entry, answer }, team.id), passphrase, picks.filter((pick) => !TRADE_TOPICS[pick])) }
                            : null;
                        return <TradeCard ref={ref} question={entry.question} steps={entry.steps} answer={entry.answer} analyze={analyzeHref()} stale={refresh} />;
                      }
                      case "miss":
                        return <MissCard ref={ref} question={entry.question} closest={entry.closest} block={entry.block} avatars={avatars} onPick={(key) => open(key)} />;
                      case "cap":
                        return <CapCard ref={ref} question={entry.question} line={entry.line} closest={entry.closest} onPick={(key) => open(key)} />;
                      case "free": {
                        // A chip of the team that the question names opens the Topic of that team.
                        const shared = {
                          question: entry.question,
                          teamName: (id: number | null) => (id !== null && id !== team.id ? teams.find((other) => other.id === id)?.name : undefined),
                          onPick: (key: string, id: number | null) => open(key, id),
                        };
                        return entry.result ? (
                          <FreeAnswerCard ref={ref} result={entry.result} {...shared} />
                        ) : (
                          <FreeAnswerLive
                            ref={ref}
                            target={askTarget}
                            passphrase={getPassphrase() ?? ""}
                            body={{ roster_id: team.id, week, turns: turnsOf(entry.id) }}
                            onDone={(result) => put(entry.id, { kind: "free", question: entry.question, result })}
                            onMiss={(closest) => put(entry.id, { kind: "miss", question: entry.question, closest })}
                            onError={() => put(entry.id, { kind: "note", question: entry.question, line: RETRY_LINE, topic: null, team: null, retry: true })}
                            {...shared}
                          />
                        );
                      }
                      case "personal": {
                        // A tapped Topic shows its name, with the team after it when it is not Your team.
                        const other = entry.team !== team.id ? teams.find((candidate) => candidate.id === entry.team)?.name : undefined;
                        const shared = {
                          name: personalName(entry, other),
                          href: personalHrefs[entry.team]?.[entry.key] ?? null,
                          avatars,
                        };
                        const since = entry.result ? stale[entry.result.key] : undefined;
                        return entry.result ? (
                          <PersonalAnswerCard
                            ref={ref}
                            result={entry.result}
                            // Refresh streams a fresh Answer in the same place. The roster changed, so its key is new.
                            stale={since !== undefined ? { line: staleLine(since), onRefresh: () => put(entry.id, { ...entry, result: null }) } : null}
                            {...shared}
                          />
                        ) : (
                          <PersonalAnswerLive
                            ref={ref}
                            target={askTarget}
                            passphrase={getPassphrase() ?? ""}
                            // Only a typed question carries the turns and its text. A tapped Topic keeps its kept Answer (AT-8).
                            body={{ topic: entry.key, roster_id: team.id, team: entry.team === team.id ? null : entry.team, ...(entry.question !== null ? { turns: turnsOf(entry.id), question: entry.question } : {}) }}
                            onDone={(result) => put(entry.id, { ...entry, result })}
                            onMiss={(closest, block) => put(entry.id, { kind: "miss", question: shared.name, closest, ...(block ? { block } : {}) })}
                            // Past a cap, the API writes the line and sends the closest Topics of this Topic.
                            onCap={(cap) => put(entry.id, { kind: "cap", question: shared.name, line: cap.line, closest: cap.closest })}
                            // A retry sends the name of the Topic through the route, which opens the same Topic again.
                            onError={() => put(entry.id, { kind: "note", question: shared.name, line: RETRY_LINE, topic: null, team: null, retry: true })}
                            {...shared}
                          />
                        );
                      }
                      case "note":
                        return (
                          <NoteCard
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
                  }}
                />
              </div>
            )}
            <motion.div
              // The ask box and the chips glide from the center of the empty Thread to the bottom on the first Answer,
              // in one move on the shared layout spring. With motion off, the dock jumps to its place, and only the
              // fades of its parts run. Only the position animates: the dock changes its height when "More" opens, and a
              // size animation would stretch the ask box and the chips on the way. With motion off, the dock mounts again
              // at its new place, so each part fades in there and the ask box never jumps at full opacity (AT-46).
              key={off ? (empty ? "dock-center" : "dock-foot") : "dock"}
              layout={off ? false : "position"}
              transition={{ layout: GLIDE }}
              className={`flex flex-col gap-sp-3 ${empty ? "" : "sticky bottom-door-foot z-10 -mx-gutter bg-page/90 px-gutter pt-sp-3 pb-sp-3 backdrop-blur-md desktop:bottom-0"}`}
            >
              {!missed && (day === null || picks.length > 0 || moreOpen) ? (
                <motion.div {...riseIn(off, { delay: 0.06 })}>
                  {/* Until the browser reads the day, quiet placeholder chips hold the place of the chips. */}
                  <Suggestions picks={day === null ? null : picks} facts={{ ...TRADE_LINES, ...PERSONAL_LINES, ...facts }} moreOpen={moreOpen} wrap={empty} onMore={setMoreOpen} onPick={(key) => open(key)} />
                </motion.div>
              ) : null}
              <motion.div {...riseIn(off, { delay: 0.08 })}>
                {/* Send holds busy while a question routes, so a second tap never sends it twice. */}
                <AskBox onAsk={ask} pending={thread.some((entry) => entry.kind === "pending")} />
              </motion.div>
              {empty && (
                <motion.div className="flex" {...riseIn(off, { delay: 0.16 })}>
                  {changeTeam}
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
