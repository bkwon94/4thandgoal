/**
 * The block of a free answer: a ranked list, a small table, or a player card that Claude shows under its lead line,
 * in the style of the rows of the data block. It holds the shape of the `data-block` part and its short text for a turn.
 */
"use client";

import { motion } from "framer-motion";
import type { ReactNode } from "react";
import { z } from "zod";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { VERY_SLOW, riseIn, staggerOf } from "./motion";

const listBlockSchema = z.object({
  kind: z.literal("list"),
  title: z.string(),
  rows: z.array(z.object({ rank: z.number(), name: z.string(), tag: z.string(), value: z.string(), note: z.string().optional() })),
});
const tableBlockSchema = z.object({ kind: z.literal("table"), title: z.string(), columns: z.array(z.string()), rows: z.array(z.array(z.string())) });
const playerBlockSchema = z.object({
  kind: z.literal("player"),
  name: z.string(),
  position: z.string(),
  nfl_team: z.string().optional(),
  fantasy_team: z.string().optional(),
  can_play_now: z.boolean(),
  status: z.string(),
  stats: z.array(z.object({ label: z.string(), value: z.string() })),
  note: z.string().optional(),
});

/* The block contract of the site: one union over `kind`, for the `data-block` part of the API stream. The kind picks
   the shape. A new block joins with its schema here, its line in blockText, and its view in BlockView, and TypeScript
   flags a kind that misses either. A personal Topic sends its stats and rows on the same part as the kind "rows",
   which is outside this union, so it never reads as an answer block. */
export const answerBlockSchema = z.discriminatedUnion("kind", [listBlockSchema, tableBlockSchema, playerBlockSchema]);
export type AnswerBlock = z.infer<typeof answerBlockSchema>;

/* The block of a data part, or null for a part of another shape. */
export function answerBlockOf(data: unknown): AnswerBlock | null {
  const parsed = answerBlockSchema.safeParse(data);
  return parsed.success ? parsed.data : null;
}

/* The block as one short line of plain text, so the turn of the Answer carries it and a follow-up has context. */
export function blockText(block: AnswerBlock): string {
  switch (block.kind) {
    case "list":
      return `${block.title}: ${block.rows.map((row) => `${row.rank}. ${row.name}, ${row.tag}, ${row.value}${row.note ? ` (${row.note})` : ""}`).join("; ")}.`;
    case "table":
      return `${block.title}: ${[block.columns, ...block.rows].map((row) => row.join(" | ")).join("; ")}.`;
    case "player": {
      const head = [block.name, block.position, block.nfl_team, block.fantasy_team ?? "free agent"].filter(Boolean).join(", ");
      const stats = block.stats.map((stat) => `${stat.label} ${stat.value}.`);
      return [`${head}, ${block.can_play_now ? "can play now" : "can't play now"} (${block.status}).`, ...stats, ...(block.note ? [block.note] : [])].join(" ");
    }
  }
}

/* The quiet mono label over a block, as the label of a stat of the data block. */
function Label({ id, children }: { id?: string; children: ReactNode }) {
  return (
    <p id={id} className="m-0 truncate font-mono text-meta leading-tight tracking-caps text-mute uppercase">
      {children}
    </p>
  );
}

/* One part of a block. A live block settles in after the words of its lead line: the label first, then each row rises
   from a soft blur on the stagger of the rows. A kept block shows at once. */
function Rise({ live, index, as = "div", className, children, ...rest }: { live: boolean; index: number; as?: "div" | "li" | "tr"; className?: string; children: ReactNode } & Record<string, unknown>) {
  const off = useMotionOff();
  const Tag = motion[as] as typeof motion.div;
  // The words of the lead line sweep in for up to --duration-very-slow, so the block starts as they settle.
  const motionProps = live ? riseIn(off, { text: true, delay: VERY_SLOW * 0.6 + staggerOf(index) }) : {};
  return (
    <Tag className={className} {...motionProps} {...rest}>
      {children}
    </Tag>
  );
}

function ListView({ block, live }: { block: Extract<AnswerBlock, { kind: "list" }>; live: boolean }) {
  const id = `block-${block.title}`.replace(/\W+/g, "-");
  return (
    <div className="flex min-w-0 flex-col gap-sp-2" data-block="list">
      <Rise live={live} index={0}>
        <Label id={id}>{block.title}</Label>
      </Rise>
      <ul aria-labelledby={id} className="m-0 flex list-none flex-col border-t border-rule p-0">
        {block.rows.map((row, index) => (
          <Rise key={`${row.rank}-${row.name}`} as="li" live={live} index={index + 1} className="grid grid-cols-[1.5rem_minmax(0,1fr)_auto] items-center gap-x-sp-3 border-b border-rule py-sp-2 last:border-b-0">
            <span className="font-mono text-meta leading-tight text-mute tabular-nums">{row.rank}</span>
            <span className="flex min-w-0 flex-col">
              <span className="flex min-w-0 items-baseline gap-sp-2">
                <span className="truncate text-row leading-tight font-semibold text-ink">{row.name}</span>
                <span className="flex-none font-mono text-meta leading-tight text-mute">{row.tag}</span>
              </span>
              {row.note && <span className="truncate font-mono text-meta leading-tight text-mute">{row.note}</span>}
            </span>
            <span className="font-mono text-row leading-tight text-ink-2 tabular-nums">{row.value}</span>
          </Rise>
        ))}
      </ul>
    </div>
  );
}

/* A table fits the card at 390 px: the columns share the width, and a long cell truncates whole with its full text in
   its title, so the card never scrolls sideways. The first column names each row, so it reads left and takes more room. */
function TableView({ block, live }: { block: Extract<AnswerBlock, { kind: "table" }>; live: boolean }) {
  const first = block.columns.length > 2 ? "34%" : "50%";
  return (
    <div className="flex min-w-0 flex-col gap-sp-2" data-block="table">
      <Rise live={live} index={0}>
        <Label>{block.title}</Label>
      </Rise>
      <table aria-label={block.title} className="w-full table-fixed border-collapse border-t border-rule">
        <colgroup>
          <col style={{ width: first }} />
          {block.columns.slice(1).map((column, index) => (
            <col key={`${column}-${index}`} />
          ))}
        </colgroup>
        <thead>
          <tr className="border-b border-rule">
            {block.columns.map((column, index) => (
              <th key={`${column}-${index}`} scope="col" title={column} className={`truncate py-sp-2 font-mono text-meta leading-tight font-normal tracking-caps text-mute uppercase ${index === 0 ? "text-left" : "pl-sp-2 text-right"}`}>
                {column}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {block.rows.map((row, rowIndex) => (
            <Rise key={rowIndex} as="tr" live={live} index={rowIndex + 1} className="border-b border-rule last:border-b-0">
              {row.map((cell, index) => (
                <td key={index} title={cell} className={`truncate py-sp-2 text-row leading-tight ${index === 0 ? "text-left font-semibold text-ink" : "pl-sp-2 text-right font-mono text-ink-2 tabular-nums"}`}>
                  {cell}
                </td>
              ))}
            </Rise>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function PlayerView({ block, live }: { block: Extract<AnswerBlock, { kind: "player" }>; live: boolean }) {
  const team = block.fantasy_team ?? "Free agent";
  return (
    <div role="group" aria-label={block.name} className="flex min-w-0 flex-col gap-sp-3 border-t border-rule pt-sp-3" data-block="player">
      <Rise live={live} index={0} className="flex min-w-0 flex-col gap-sp-1">
        <p className="m-0 truncate text-stat leading-tight font-bold text-ink">{block.name}</p>
        <p className="m-0 truncate font-mono text-meta leading-tight text-mute">{[block.position, block.nfl_team, team].filter(Boolean).join(" · ")}</p>
      </Rise>
      <Rise live={live} index={1}>
        {/* The status reads in words and in color, so it never rests on color alone. */}
        <p className="m-0 inline-flex items-center gap-sp-2 text-row leading-tight font-semibold text-ink">
          <span aria-hidden className={`size-sp-2 flex-none rounded-full ${block.can_play_now ? "bg-move-up" : "bg-move-down"}`} />
          {block.can_play_now ? "Can play now" : "Can't play now"}
          <span className="font-mono text-meta font-normal text-mute">{block.status}</span>
        </p>
      </Rise>
      {block.stats.length > 0 && (
        <dl className="m-0 grid grid-cols-2 gap-x-sp-4 gap-y-sp-3">
          {block.stats.map((stat, index) => (
            <Rise key={stat.label} live={live} index={index + 2} className="flex min-w-0 flex-col gap-sp-1">
              <dt className="truncate font-mono text-meta leading-tight tracking-caps text-mute uppercase">{stat.label}</dt>
              <dd className="m-0 truncate text-row leading-tight font-bold tabular-nums">{stat.value}</dd>
            </Rise>
          ))}
        </dl>
      )}
      {block.note && (
        <Rise live={live} index={block.stats.length + 2}>
          <p className="m-0 text-body leading-body text-ink-2">{block.note}</p>
        </Rise>
      )}
    </div>
  );
}

/* The component of each kind of block. */
export function BlockView({ block, live }: { block: AnswerBlock; live: boolean }) {
  switch (block.kind) {
    case "list":
      return <ListView block={block} live={live} />;
    case "table":
      return <TableView block={block} live={live} />;
    case "player":
      return <PlayerView block={block} live={live} />;
  }
}
