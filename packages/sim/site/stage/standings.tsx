/**
 * The parts of the Season screen and of "Sim week N": the live standings in the Race style, the key of the zone rules,
 * the games of one week with one median line, a score that counts up, and a text that swaps in place.
 */
"use client";

import { animate, AnimatePresence, motion, type Transition } from "framer-motion";
import { useEffect, useRef, useState } from "react";
import { oneDecimal, record } from "@cpc/design/format/format";
import { EASE_OUT } from "@cpc/design/lib/motion";
import { cn } from "@cpc/design/lib/utils";
import { PhotoFrame } from "@cpc/design/parts/photo-frame";
import type { Avatars } from "../page/sim-page";
import type { ReplayWeek, StandingRow, WeekTeam } from "../replay/season";
import type { Mark } from "./steps";

/* The motion of the parts. The FLIP reorder is critically damped, so a row lands in its place with no wobble. */
export const FLIP: Transition = { type: "spring", bounce: 0, duration: 0.55 };
export const FLIGHT: Transition = { type: "spring", bounce: 0.12, duration: 0.7 };
const SWAP: Transition = { duration: 0.2, ease: EASE_OUT };

/* The cross-fade under reduced motion, on the motion tokens of transitions-dev: the old state leaves on
   --duration-quick (150 ms) and the new state comes in on --duration-fast (250 ms), both on --ease-in-out. A part that
   would move or step to a new state fades out, changes, and fades in, so the new place shows only through a fade. */
export const FADE_OUT: Transition = { duration: 0.15, ease: "easeInOut" };
export const FADE_IN: Transition = { duration: 0.25, ease: "easeInOut" };

export const MONO = "font-mono tabular-nums";
export const EYEBROW = "font-mono text-meta leading-tight font-bold tracking-caps uppercase";

/* A score that counts up from zero once, when `live`. Otherwise it shows the score at rest. */
export function Score({
  value,
  live,
  delay = 0,
  className,
}: {
  value: number;
  live: boolean;
  delay?: number;
  className?: string;
}) {
  const box = useRef<HTMLSpanElement>(null);
  useEffect(() => {
    if (!live || box.current === null) return;
    const node = box.current;
    node.textContent = oneDecimal(0);
    const controls = animate(0, value, {
      duration: 0.6,
      delay,
      ease: EASE_OUT,
      onUpdate: (v) => (node.textContent = oneDecimal(v)),
    });
    return () => {
      controls.stop();
      node.textContent = oneDecimal(value);
    };
  }, [live, value, delay]);
  return (
    <span ref={box} data-score className={cn(MONO, "font-bold", className)}>
      {oneDecimal(value)}
    </span>
  );
}

/* Text that swaps in place: the old text leaves fast, the new text rises in with a short blur. Under reduced motion it only fades. */
export function SwapText({
  text,
  off,
  className,
}: {
  text: string;
  off: boolean;
  className?: string;
}) {
  return (
    <span className={cn("relative inline-grid", className)}>
      <AnimatePresence mode="popLayout" initial={false}>
        <motion.span
          key={text}
          initial={off ? { opacity: 0 } : { opacity: 0, y: 4, filter: "blur(2px)" }}
          animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
          exit={{ opacity: 0, transition: { duration: 0.12 } }}
          transition={SWAP}
          className="col-start-1 row-start-1 whitespace-nowrap"
        >
          {text}
        </motion.span>
      </AnimatePresence>
    </span>
  );
}

/* The W or L of the week beside the record. It flashes in, holds, and fades, so the row is quiet again by the next week. */
function ResultFlash({
  mark,
  week,
  show,
}: {
  mark: Mark | null;
  week: number | null;
  show: boolean;
}) {
  return (
    <span
      aria-hidden="true"
      className={cn(MONO, "text-meta w-[1.5ch] flex-none text-center font-bold")}
    >
      {show && mark !== null && week !== null && (
        <motion.span
          key={week}
          className={cn("block", mark.game === "W" ? "text-on-dark" : "text-on-dark-muted")}
          initial={{ opacity: 0 }}
          animate={{ opacity: [0, 1, 1, 0] }}
          transition={{ duration: 1.4, times: [0, 0.12, 0.7, 1], ease: EASE_OUT, delay: 0.45 }}
        >
          {mark.game}
        </motion.span>
      )}
    </span>
  );
}

/* A zone rule between two rows: a dashed rule under the bye seeds, and the red playoff line under the last seed.
   It sits in the gap between rows and carries no label, so it never covers a row. Under reduced motion it is a plain
   box, and a new place of the rule comes only with a new list, which fades in. */
function ZoneRule({
  at,
  rows,
  kind,
  off,
}: {
  at: number;
  rows: number;
  kind: "bye" | "playoff";
  off: boolean;
}) {
  const top = `${(at / rows) * 100}%`;
  const className = cn(
    "pointer-events-none absolute inset-x-0 z-10 -translate-y-1/2",
    kind === "bye"
      ? "border-on-dark-muted border-t border-dashed"
      : "rounded-report bg-accent h-0.5",
  );
  // A transition of no duration still tweens `top` over a few frames in WebKit, so reduced motion gets a plain box.
  if (off) return <div aria-hidden="true" style={{ top }} className={className} />;
  return (
    <motion.div
      aria-hidden="true"
      initial={false}
      animate={{ top }}
      transition={FLIP}
      className={className}
    />
  );
}

/* The key of the two zone rules, one short line under the title, so the rules need no labels of their own. */
export function ZoneKey({ byes, spots }: { byes: number; spots: number }) {
  return (
    <p className="gap-sp-3 text-meta text-on-dark-2 m-0 flex items-center leading-tight">
      {byes > 0 && (
        <span className="gap-sp-1 flex items-center whitespace-nowrap">
          <span aria-hidden="true" className="w-sp-3 border-on-dark-muted border-t border-dashed" />
          {`Top ${byes} bye`}
        </span>
      )}
      <span className="gap-sp-1 flex items-center whitespace-nowrap">
        <span aria-hidden="true" className="w-sp-3 rounded-report bg-accent h-0.5" />
        {`Top ${spots} in`}
      </span>
    </p>
  );
}

/* The first word or two of a name, so a fold line can hold two names. */
function foldName(name: string): string {
  const words = name.split(" ");
  let out = words[0];
  for (const w of words.slice(1)) {
    if ((out + " " + w).length > 11) break;
    out += ` ${w}`;
  }
  return out.length < name.length ? out.replace(/[.,]+$/, "") : name;
}

type Item =
  { kind: "row"; row: StandingRow } | { kind: "fold"; side: "top" | "bottom"; rows: StandingRow[] };

/* The rows past the playoff line that stay in full in the Race style (decision 04). */
const RACE_BELOW = 3;

/* The items of the list in place order. Each run of rows far from the playoff line folds into one item: the byes at
   the top, and the rows more than three below the line at the bottom. Your team never folds. At the cut every row
   shows, so each seed can fly to the bracket. */
function itemsOf(
  rows: StandingRow[],
  spots: number,
  byes: number,
  yourTeam: number,
  cut: boolean,
): Item[] {
  if (cut) return rows.map((row) => ({ kind: "row", row }));
  const items: Item[] = [];
  for (const row of rows) {
    const side =
      row.roster_id === yourTeam
        ? null
        : row.place <= byes
          ? "top"
          : row.place > spots + RACE_BELOW
            ? "bottom"
            : null;
    const last = items.at(-1);
    if (side === null) items.push({ kind: "row", row });
    else if (last?.kind === "fold" && last.side === side) last.rows.push(row);
    else items.push({ kind: "fold", side, rows: [row] });
  }
  return items;
}

/* The count of items whose places are all at or above `place`, so a rule sits under the last of them. */
const itemsAbove = (items: Item[], place: number) =>
  items.filter((it) => (it.kind === "row" ? it.row.place : it.rows.at(-1)!.place) <= place).length;

/* One fold line: the range of places, and the names of the byes or the plain words "out of it". */
function FoldLine({ item }: { item: Extract<Item, { kind: "fold" }> }) {
  const first = item.rows[0].place;
  const last = item.rows.at(-1)!.place;
  const range = first === last ? `${first}` : `${first}–${last}`;
  const words =
    item.side === "top"
      ? `byes: ${item.rows.map((r) => foldName(r.name)).join(", ")}`
      : "out of it";
  return (
    <span className="gap-sp-2 text-meta text-on-dark-2 flex min-w-0 flex-1 items-center leading-tight">
      <span className={cn(MONO, "flex-none")}>{range}</span>
      <span aria-hidden="true">·</span>
      <span className="min-w-0 truncate">{words}</span>
    </span>
  );
}

/* The live standings in the Race style: one row per team near the playoff line, which moves to its new place each
   week with a FLIP motion. Under reduced motion, the list fades out, takes the new order, and fades in. At the cut,
   the teams under the playoff line dim. Each team carries a shared id, so each seed flies from its row into the
   bracket. Each row is at most one touch target high, so a tall stage keeps the rows together at the top. */
export function Standings({
  rows,
  marks,
  week,
  spots,
  byes,
  yourTeam,
  avatars,
  off,
  cut,
}: {
  rows: StandingRow[];
  // The results of the week on the stage, or null before the first week.
  marks: Map<number, Mark> | null;
  week: number | null;
  spots: number;
  byes: number;
  yourTeam: number;
  avatars: Avatars;
  off: boolean;
  cut: boolean;
}) {
  const items = itemsOf(rows, spots, byes, yourTeam, cut);
  const count = items.length;
  const fade = off ? { duration: 0.2 } : { duration: 0.25, ease: EASE_OUT };
  const list = {
    "aria-label": "Standings",
    className: "relative m-0 grid min-h-0 w-full flex-1 list-none grid-cols-1 p-0",
    style: {
      gridTemplateRows: `repeat(${count}, minmax(0, 1fr))`,
      maxHeight: `calc(${count} * var(--spacing-touch))`,
    },
  };
  const body = (
    <>
      {byes > 0 && <ZoneRule at={itemsAbove(items, byes)} rows={count} kind="bye" off={off} />}
      <ZoneRule at={itemsAbove(items, spots)} rows={count} kind="playoff" off={off} />
      <AnimatePresence initial={false} mode="popLayout">
        {items.map((item) => {
          if (item.kind === "fold") {
            return (
              <motion.li
                key={`fold-${item.side}`}
                layout={off ? false : "position"}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0, transition: { duration: 0.15 } }}
                transition={{ layout: FLIP, ...fade }}
                className="pr-sp-2 pl-sp-3 relative flex min-h-0 items-center"
              >
                <FoldLine item={item} />
              </motion.li>
            );
          }
          const { row } = item;
          const you = row.roster_id === yourTeam;
          const seed = row.place <= spots;
          return (
            <motion.li
              key={row.roster_id}
              layout={off ? false : "position"}
              initial={{ opacity: 0 }}
              animate={{ opacity: cut && !seed ? 0.4 : 1 }}
              exit={{ opacity: 0, transition: { duration: 0.15 } }}
              transition={{ layout: FLIP, ...fade }}
              data-roster={row.roster_id}
              className="gap-sp-2 pr-sp-2 pl-sp-3 relative flex min-h-0 items-center"
            >
              {you && (
                <span
                  aria-hidden="true"
                  className="inset-y-sp-1 rounded-report bg-accent absolute left-0 w-1"
                />
              )}
              <span
                className={cn(
                  MONO,
                  "text-meta w-[2ch] flex-none text-right",
                  you ? "text-accent-text font-bold" : "text-on-dark-muted",
                )}
              >
                {row.place}
              </span>
              {/* The shared id is set from the mount of the row, because Framer Motion reads a shared id when the part
                  mounts. Only a seed finds a seat in the bracket, so only a seed flies. */}
              <motion.span
                layoutId={off ? undefined : `team-${row.roster_id}`}
                transition={{ layout: FLIP }}
                className="gap-sp-2 flex min-w-0 flex-1 items-center"
              >
                {/* Only Your team keeps its avatar, so it stands out and the other rows stay quiet. */}
                {you && (
                  <span data-avatar className="flex flex-none">
                    <PhotoFrame
                      src={avatars[String(row.roster_id)] ?? null}
                      name={row.name}
                      size="sm"
                      decorative
                    />
                  </span>
                )}
                <span
                  className={cn(
                    "text-row text-on-dark min-w-0 truncate leading-tight",
                    you ? "font-bold" : "font-semibold",
                  )}
                >
                  {row.name}
                  {you && <span className="sr-only"> (Your team)</span>}
                </span>
              </motion.span>
              <ResultFlash
                mark={marks?.get(row.roster_id) ?? null}
                week={week}
                show={row.move !== 0}
              />
              {/* The record changes on most rows each week, so it changes in place with no motion of its own. */}
              <span
                className={cn(
                  MONO,
                  "text-row text-on-dark w-[5ch] flex-none text-right font-bold whitespace-nowrap",
                )}
              >
                {record(row.wins, row.losses)}
              </span>
            </motion.li>
          );
        })}
      </AnimatePresence>
    </>
  );
  if (!off) return <ol {...list}>{body}</ol>;
  // Under reduced motion, each new order, and each new place of a rule, is a new list. The old list fades out before
  // the new one fades in, so no row and no rule jumps to its new place at full opacity.
  const order = items
    .map((item) =>
      item.kind === "row"
        ? `${item.row.roster_id}:${item.row.place}`
        : `${item.side}:${item.rows.length}`,
    )
    .join(",");
  return (
    <AnimatePresence mode="wait" initial={false}>
      <motion.ol
        key={`${order}${cut ? ":cut" : ""}`}
        {...list}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0, transition: FADE_OUT }}
        transition={FADE_IN}
      >
        {body}
      </motion.ol>
    </AnimatePresence>
  );
}

/* The gap in seconds between two games when the week plays, so the games reveal one by one. */
const GAME_GAP = 0.4;

/* One game as one row: team A, score A, score B, team B. After the count-up, the winner turns bold and the loser mutes.
   Your team always sits on the left of its own row. */
function GameRow({
  a,
  b,
  played,
  live,
  delay,
  yours,
}: {
  a: WeekTeam;
  b: WeekTeam;
  played: boolean;
  live: boolean;
  delay: number;
  yours: boolean;
}) {
  // The result shows at once at rest, or after the count-up of this game when the week plays live.
  const [shown, setShown] = useState(!live);
  useEffect(() => {
    if (!live) return setShown(true);
    setShown(false);
    const timer = setTimeout(() => setShown(true), (delay + 0.6) * 1000);
    return () => clearTimeout(timer);
  }, [live, delay]);
  const decided = played && shown && a.score !== b.score;
  const tone = (team: WeekTeam, other: WeekTeam) =>
    !decided
      ? "font-semibold text-on-dark"
      : team.score > other.score
        ? "font-bold text-on-dark"
        : "font-normal text-on-dark-muted";
  const name = (team: WeekTeam, other: WeekTeam, side: "left" | "right") => (
    <span
      className={cn(
        "text-row min-w-0 truncate leading-tight transition-colors duration-300",
        side === "right" && "text-right",
        tone(team, other),
      )}
    >
      {team.name}
    </span>
  );
  const score = (team: WeekTeam, other: WeekTeam) =>
    played ? (
      <Score
        value={team.score}
        live={live}
        delay={delay}
        className={cn("text-row transition-colors duration-300", tone(team, other))}
      />
    ) : (
      <span className={cn(MONO, "text-row text-on-dark-muted")}>–</span>
    );
  return (
    <li
      className={cn(
        "gap-x-sp-2 px-sp-3 relative grid min-h-0 grid-cols-[minmax(0,1fr)_5ch_5ch_minmax(0,1fr)] items-center",
        // Your game sits on its own card; the other rows share plain rules between them.
        yours ? "rounded-report bg-chip-dark" : "border-rule-dark border-b last:border-b-0",
      )}
    >
      {yours && (
        <span
          aria-hidden="true"
          className="inset-y-sp-2 rounded-report bg-accent absolute left-0 w-1"
        />
      )}
      {name(a, b, "left")}
      <span className="text-right">{score(a, b)}</span>
      <span className="text-left">{score(b, a)}</span>
      {name(b, a, "right")}
      <span className="sr-only">
        {yours ? " Your game." : ""}
        {decided ? ` ${a.score > b.score ? a.name : b.name} wins.` : ""}
      </span>
    </li>
  );
}

/* The games of one week: one row per game, Your game first and marked. When the week plays, the scores count up one
   by one. One line under the games gives the median and where Your team landed. */
export function WeekGames({
  week,
  played,
  live,
  yourTeam,
}: {
  week: ReplayWeek;
  played: boolean;
  live: boolean;
  yourTeam: number;
}) {
  const games = week.games.map(({ teams }) => {
    const [a, b] = teams;
    // Your team sits on the left of its row, so the eye finds it at the same place each week.
    return b.roster_id === yourTeam ? ([b, a] as const) : ([a, b] as const);
  });
  const mine = games.findIndex(([a]) => a.roster_id === yourTeam);
  const ordered = mine < 0 ? games : [games[mine], ...games.filter((_, i) => i !== mine)];
  const count = ordered.length;
  const yours = mine < 0 ? null : games[mine][0];
  const side =
    yours === null || week.median === null
      ? null
      : yours.score > week.median
        ? "above"
        : yours.score < week.median
          ? "below"
          : "level with";
  return (
    <div className="gap-sp-2 flex min-h-0 flex-1 flex-col">
      <ul
        aria-label={`Week ${week.week} games`}
        className="m-0 grid min-h-0 w-full flex-1 list-none grid-cols-1 p-0"
        style={{
          gridTemplateRows: `repeat(${count}, minmax(0, 1fr))`,
          maxHeight: `calc(${count} * var(--spacing-row-touch))`,
        }}
      >
        {ordered.map(([a, b], i) => (
          <GameRow
            key={`${a.roster_id}-${b.roster_id}`}
            a={a}
            b={b}
            played={played}
            live={live}
            delay={live ? i * GAME_GAP : 0}
            yours={a.roster_id === yourTeam}
          />
        ))}
      </ul>
      {week.median !== null && (
        <motion.p
          key={played ? "played" : "draw"}
          initial={live ? { opacity: 0 } : false}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3, ease: EASE_OUT, delay: live ? count * GAME_GAP + 0.4 : 0 }}
          className={cn(MONO, "px-sp-3 text-meta text-on-dark-2 m-0 flex-none")}
        >
          {played
            ? `Median ${oneDecimal(week.median)}${side === null ? "" : ` · you were ${side}`}`
            : "Median –"}
        </motion.p>
      )}
    </div>
  );
}
