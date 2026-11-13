/**
 * The transaction feed of a free answer: a strip of the moves of each day over the header, then one row per move,
 * newest first, with a dot for its kind. A trade row shows what each side got. The API builds the block from Sleeper.
 */
"use client";

import { motion } from "framer-motion";
import type { ReactNode } from "react";
import { z } from "zod";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { SMOOTH, VERY_SLOW, riseIn, staggerOf } from "./motion";

const dayCountSchema = z.object({ day: z.string(), moves: z.number() });
const tradeRowSchema = z.object({ kind: z.literal("trade"), day: z.string(), sides: z.array(z.object({ team: z.string(), got: z.array(z.string()) })) });
const addRowSchema = z.object({
  kind: z.enum(["waiver", "free_agent"]),
  day: z.string(),
  team: z.string(),
  added: z.array(z.string()),
  dropped: z.array(z.string()),
  bid: z.number().nullable().optional(),
});
const moveRowSchema = z.discriminatedUnion("kind", [tradeRowSchema, addRowSchema]);

export const feedBlockSchema = z.object({
  kind: z.literal("feed"),
  title: z.string(),
  days: z.array(dayCountSchema),
  rows: z.array(moveRowSchema),
  more: z.number(),
});
export type FeedBlock = z.infer<typeof feedBlockSchema>;
type MoveRow = FeedBlock["rows"][number];

/* The word of each kind of move, for the legend and for a screen reader on each row. */
const KIND_WORDS: Record<MoveRow["kind"], string> = { trade: "Trade", waiver: "Waiver claim", free_agent: "Free agent" };

/* One move as plain words, so the turn of the Answer carries it. */
function moveText(row: MoveRow): string {
  if (row.kind === "trade") return `${row.day}, trade: ${row.sides.map((side) => `${side.team} got ${side.got.join(", ") || "nothing"}`).join("; ")}`;
  const parts = [row.added.length ? `added ${row.added.join(", ")}` : "", row.dropped.length ? `dropped ${row.dropped.join(", ")}` : ""].filter(Boolean);
  const bid = row.kind === "waiver" && row.bid != null ? ` for $${row.bid}` : "";
  return `${row.day}, ${KIND_WORDS[row.kind].toLowerCase()}: ${row.team} ${parts.join(" and ")}${bid}`;
}

/* The feed as one short line of plain text, for the turn of the Answer. */
export function feedText(block: FeedBlock): string {
  const more = block.more ? ` And ${block.more} more.` : "";
  return `${block.title}: ${block.rows.map(moveText).join("; ")}.${more}`;
}

/* The dot of a kind, told apart by its shape and its ink and not by color alone: a solid dot for a trade, a ring for a
   waiver claim, and a small gray dot for a free agent move. */
function KindDot({ kind }: { kind: MoveRow["kind"] }) {
  const shape = kind === "trade" ? "size-sp-2 bg-ink" : kind === "waiver" ? "size-sp-2 border-2 border-ink" : "size-1.5 bg-current text-mute";
  return (
    <span aria-hidden className="flex size-sp-3 flex-none items-center justify-center">
      <span className={`rounded-full ${shape}`} />
    </span>
  );
}

/* One part of the feed. A live part rises from a soft blur on the stagger of the rows, after the words of the lead line
   settle. A kept part shows at once. */
function Rise({ live, index, as = "div", className, children }: { live: boolean; index: number; as?: "div" | "li"; className?: string; children: ReactNode }) {
  const off = useMotionOff();
  const Tag = motion[as] as typeof motion.div;
  const motionProps = live ? riseIn(off, { text: true, delay: VERY_SLOW * 0.6 + staggerOf(index) }) : {};
  return (
    <Tag className={className} {...motionProps}>
      {children}
    </Tag>
  );
}

/* The height in px of the bar of the busiest day. The strip stays a small mark over the header. */
const STRIP_HEIGHT = 32;

/* The strip of the moves of each day. Each bar grows from the base line, and the busiest day takes the ink. A day with
   no move keeps a stub on the base line, so the gaps of the week show. The whole strip reads as one line of words. */
function DayStrip({ days, live }: { days: FeedBlock["days"]; live: boolean }) {
  const off = useMotionOff();
  const most = Math.max(1, ...days.map((day) => day.moves));
  const words = days.map((day) => `${day.day}: ${day.moves}`).join(", ");
  return (
    <div role="img" aria-label={`Moves per day. ${words}.`} className="flex items-end gap-sp-1">
      {days.map((day, index) => {
        const height = day.moves ? Math.max(4, Math.round((day.moves / most) * STRIP_HEIGHT)) : 2;
        // The bar grows on transform only, from its base, so it never moves the rows under it.
        const grow = live && !off ? { initial: { scaleY: 0 }, animate: { scaleY: 1 }, transition: { duration: VERY_SLOW, ease: SMOOTH, delay: VERY_SLOW * 0.6 + staggerOf(index) } } : {};
        return (
          <div key={day.day} className="flex min-w-0 flex-1 flex-col items-center gap-sp-1">
            <span className="font-mono text-meta leading-tight text-mute tabular-nums">{day.moves || ""}</span>
            <motion.span
              className={`block w-full max-w-sp-6 origin-bottom rounded-t-sm ${day.moves === 0 ? "bg-rule" : day.moves === most ? "bg-current text-ink" : "bg-current text-mute"}`}
              style={{ height }}
              {...grow}
            />
            <span className="font-mono text-meta leading-tight text-mute">{day.day.slice(0, 3)}</span>
          </div>
        );
      })}
    </div>
  );
}

/* The players of one side of a move, as one line that wraps. */
function Players({ sign, names }: { sign: string; names: string[] }) {
  if (names.length === 0) return null;
  return (
    <span className="flex min-w-0 gap-sp-1 font-mono text-meta leading-tight text-ink-2">
      <span aria-hidden className="flex-none text-mute">
        {sign}
      </span>
      <span className="min-w-0 break-words">{names.join(", ")}</span>
    </span>
  );
}

/* The name of the team of a move. The name of Your team takes the red of the site and the word "You", so it never rests
   on the red alone, as in the standings ladder and the rank mover list. The other names stay in ink. */
function TeamName({ name, you, children }: { name: string; you: boolean; children?: ReactNode }) {
  return (
    <span className={`truncate text-row leading-tight font-semibold ${you ? "text-accent-ink" : "text-ink"}`} {...(you ? { "data-you": "" } : {})}>
      {name}
      {you && <> <span className="font-mono text-meta tracking-caps uppercase">You</span></>}
      {children && <> {children}</>}
    </span>
  );
}

function MoveBody({ row, you }: { row: MoveRow; you?: string }) {
  if (row.kind === "trade") {
    return (
      <span className="flex min-w-0 flex-col gap-sp-2">
        {row.sides.map((side) => (
          <span key={side.team} className="flex min-w-0 flex-col gap-sp-1">
            <TeamName name={side.team} you={side.team === you}>
              <span className="font-normal text-mute">got</span>
            </TeamName>
            <Players sign="+" names={side.got.length ? side.got : ["nothing"]} />
          </span>
        ))}
      </span>
    );
  }
  return (
    <span className="flex min-w-0 flex-col gap-sp-1">
      <TeamName name={row.team} you={row.team === you} />
      <Players sign="+" names={row.added} />
      <Players sign="−" names={row.dropped} />
    </span>
  );
}

/* The feed: the title and the legend, the strip, then the rows, newest first, and the count of the moves past the
   rows. `you` is the name of Your team, because the block names each team by its name. */
export function FeedView({ block, live, you }: { block: FeedBlock; live: boolean; you?: string }) {
  const id = `block-${block.title}`.replace(/\W+/g, "-");
  const kinds = (["trade", "waiver", "free_agent"] as const).filter((kind) => block.rows.some((row) => row.kind === kind));
  return (
    <div className="flex min-w-0 flex-col gap-sp-3" data-block="feed">
      <Rise live={live} index={0} className="flex min-w-0 flex-col gap-sp-3">
        <div className="flex min-w-0 flex-wrap items-baseline justify-between gap-x-sp-3 gap-y-sp-1">
          <p id={id} className="m-0 truncate font-mono text-meta leading-tight tracking-caps text-mute uppercase">
            {block.title}
          </p>
          <ul aria-label="Kinds of move" className="m-0 flex list-none flex-wrap gap-x-sp-3 p-0">
            {kinds.map((kind) => (
              <li key={kind} className="flex items-center gap-sp-1 font-mono text-meta leading-tight text-mute">
                <KindDot kind={kind} />
                {KIND_WORDS[kind]}
              </li>
            ))}
          </ul>
        </div>
        {block.days.length > 0 && <DayStrip days={block.days} live={live} />}
      </Rise>
      <ul aria-labelledby={id} className="m-0 flex list-none flex-col border-t border-rule p-0">
        {block.rows.map((row, index) => (
          <Rise key={`${index}-${row.day}`} as="li" live={live} index={index + 1} className="grid grid-cols-[auto_minmax(0,1fr)_auto] items-start gap-x-sp-2 border-b border-rule py-sp-2 last:border-b-0">
            <span className="flex h-[1lh] items-center text-row leading-tight">
              <KindDot kind={row.kind} />
            </span>
            <span className="flex min-w-0 flex-col">
              <span className="sr-only">{KIND_WORDS[row.kind]}. </span>
              <MoveBody row={row} you={you} />
            </span>
            <span className="flex flex-col items-end gap-sp-1 text-right">
              <span className="font-mono text-meta leading-tight text-mute">{row.day.slice(0, 3)}</span>
              {row.kind === "waiver" && row.bid != null && <span className="font-mono text-row leading-tight text-ink-2 tabular-nums">${row.bid}</span>}
            </span>
          </Rise>
        ))}
      </ul>
      {block.more > 0 && (
        <Rise live={live} index={block.rows.length + 1}>
          <p className="m-0 font-mono text-meta leading-tight text-mute">
            {block.more} more {block.more === 1 ? "move" : "moves"} this week
          </p>
        </Rise>
      )}
    </div>
  );
}
