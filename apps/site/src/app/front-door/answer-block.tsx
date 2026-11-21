/**
 * The block of an Answer: the schema union of every block kind, its short text for a turn, and its view.
 * It holds the shape of the `data-block` part, which Claude shows under its lead line.
 */
"use client";

import { motion } from "framer-motion";
import type { ReactNode } from "react";
import { z } from "zod";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { ladderBlockSchema, ladderText } from "@/lib/data/blocks/ladder-schema";
import { matchupBlockSchema, matchupText } from "@/lib/data/blocks/matchup-schema";
import { rankMoversBlockSchema, rankMoversText } from "@/lib/data/blocks/rank-movers-schema";
import { recapBlockSchema, recapText } from "@/lib/data/blocks/recap-schema";
import { scheduleBlockSchema, scheduleText } from "@/lib/data/blocks/schedule-schema";
import { ComparisonView, comparisonBlockSchema, comparisonText } from "./comparison-block";
import { FeedView, feedBlockSchema, feedText } from "./feed-block";
import { ByeGridView, byeGridBlockSchema, byeGridText } from "./bye-grid";
import { LineupView, lineupBlockSchema, lineupText } from "./lineup-block";
import { NflGameView, nflGameBlockSchema, nflGameText } from "./nfl-game-card";
import { VERY_SLOW, riseIn, staggerOf } from "./motion";
import { MatchupCard } from "./matchup-card";
import { RankMoverList } from "./rank-mover-list";
import { RecapCard } from "./recap-card";
import { ScheduleStrip } from "./schedule-strip";
import { TradeBlockView, tradeBlockSchema, tradeBlockText } from "./trade-block";
import { SlotRanksView, slotRanksBlockSchema, slotRanksText } from "./slot-rank-bars";
import { SellListView, sellListSchema, sellListText } from "./sell-list";
import { StandingsLadder } from "./standings-ladder";
import { WaiverListView, waiverListSchema, waiverListText } from "./waiver-list";

const listBlockSchema = z.object({
  kind: z.literal("list"),
  title: z.string(),
  rows: z.array(
    z.object({
      rank: z.number(),
      name: z.string(),
      tag: z.string(),
      value: z.string(),
      note: z.string().optional(),
    }),
  ),
});
const tableBlockSchema = z.object({
  kind: z.literal("table"),
  title: z.string(),
  columns: z.array(z.string()),
  rows: z.array(z.array(z.string())),
});
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
export const answerBlockSchema = z.discriminatedUnion("kind", [
  listBlockSchema,
  tableBlockSchema,
  playerBlockSchema,
  recapBlockSchema,
  tradeBlockSchema,
  feedBlockSchema,
  slotRanksBlockSchema,
  byeGridBlockSchema,
  waiverListSchema,
  sellListSchema,
  lineupBlockSchema,
  matchupBlockSchema,
  rankMoversBlockSchema,
  ladderBlockSchema,
  scheduleBlockSchema,
  nflGameBlockSchema,
  comparisonBlockSchema,
]);
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
      const head = [block.name, block.position, block.nfl_team, block.fantasy_team ?? "free agent"]
        .filter(Boolean)
        .join(", ");
      const stats = block.stats.map((stat) => `${stat.label} ${stat.value}.`);
      return [
        `${head}, ${block.can_play_now ? "can play now" : "can't play now"} (${block.status}).`,
        ...stats,
        ...(block.note ? [block.note] : []),
      ].join(" ");
    }
    case "recap":
      return recapText(block);
    case "trade":
      return tradeBlockText(block);
    case "feed":
      return feedText(block);
    case "slot_ranks":
      return slotRanksText(block);
    case "bye_grid":
      return byeGridText(block);
    case "waiver_list":
      return waiverListText(block);
    case "sell_list":
      return sellListText(block);
    case "lineup":
      return lineupText(block);
    case "matchup":
      return matchupText(block);
    case "rank_movers":
      return rankMoversText(block);
    case "ladder":
      return ladderText(block);
    case "schedule":
      return scheduleText(block);
    case "nfl_game":
      return nflGameText(block);
    case "comparison":
      return comparisonText(block);
  }
}

/* The quiet mono label over a block, as the label of a stat of the data block. */
function Label({ id, children }: { id?: string; children: ReactNode }) {
  return (
    <p
      id={id}
      className="text-meta tracking-caps text-mute m-0 truncate font-mono leading-tight uppercase"
    >
      {children}
    </p>
  );
}

/* One part of a block. A live block settles in after the words of its lead line: the label first, then each row rises
   from a soft blur on the stagger of the rows. A kept block shows at once. */
function Rise({
  live,
  index,
  as = "div",
  className,
  children,
  ...rest
}: {
  live: boolean;
  index: number;
  as?: "div" | "li" | "tr";
  className?: string;
  children: ReactNode;
} & Record<string, unknown>) {
  const off = useMotionOff();
  const Tag = motion[as] as typeof motion.div;
  // The words of the lead line sweep in for up to --duration-very-slow, so the block starts as they settle.
  const motionProps = live
    ? riseIn(off, { text: true, delay: VERY_SLOW * 0.6 + staggerOf(index) })
    : {};
  return (
    <Tag className={className} {...motionProps} {...rest}>
      {children}
    </Tag>
  );
}

function ListView({
  block,
  live,
}: {
  block: Extract<AnswerBlock, { kind: "list" }>;
  live: boolean;
}) {
  const id = `block-${block.title}`.replace(/\W+/g, "-");
  return (
    <div className="gap-sp-2 flex min-w-0 flex-col" data-block="list">
      <Rise live={live} index={0}>
        <Label id={id}>{block.title}</Label>
      </Rise>
      <ul aria-labelledby={id} className="border-rule m-0 flex list-none flex-col border-t p-0">
        {block.rows.map((row, index) => (
          <Rise
            key={`${row.rank}-${row.name}`}
            as="li"
            live={live}
            index={index + 1}
            className="gap-x-sp-3 border-rule py-sp-2 grid grid-cols-[1.5rem_minmax(0,1fr)_auto] items-center border-b last:border-b-0"
          >
            <span className="text-meta text-mute font-mono leading-tight tabular-nums">
              {row.rank}
            </span>
            <span className="flex min-w-0 flex-col">
              <span className="gap-sp-2 flex min-w-0 items-baseline">
                <span className="text-row text-ink truncate leading-tight font-semibold">
                  {row.name}
                </span>
                <span className="text-meta text-mute flex-none font-mono leading-tight">
                  {row.tag}
                </span>
              </span>
              {row.note && (
                <span className="text-meta text-mute truncate font-mono leading-tight">
                  {row.note}
                </span>
              )}
            </span>
            <span className="text-row text-ink-2 font-mono leading-tight tabular-nums">
              {row.value}
            </span>
          </Rise>
        ))}
      </ul>
    </div>
  );
}

/* A table fits the card at 390 px: the columns share the width, and a long cell truncates whole with its full text in
   its title, so the card never scrolls sideways. The first column names each row, so it reads left and takes more room. */
function TableView({
  block,
  live,
}: {
  block: Extract<AnswerBlock, { kind: "table" }>;
  live: boolean;
}) {
  const first = block.columns.length > 2 ? "34%" : "50%";
  return (
    <div className="gap-sp-2 flex min-w-0 flex-col" data-block="table">
      <Rise live={live} index={0}>
        <Label>{block.title}</Label>
      </Rise>
      <table
        aria-label={block.title}
        className="border-rule w-full table-fixed border-collapse border-t"
      >
        <colgroup>
          <col style={{ width: first }} />
          {block.columns.slice(1).map((column, index) => (
            <col key={`${column}-${index}`} />
          ))}
        </colgroup>
        <thead>
          <tr className="border-rule border-b">
            {block.columns.map((column, index) => (
              <th
                key={`${column}-${index}`}
                scope="col"
                title={column}
                className={`py-sp-2 text-meta tracking-caps text-mute truncate font-mono leading-tight font-normal uppercase ${index === 0 ? "text-left" : "pl-sp-2 text-right"}`}
              >
                {column}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {block.rows.map((row, rowIndex) => (
            <Rise
              key={rowIndex}
              as="tr"
              live={live}
              index={rowIndex + 1}
              className="border-rule border-b last:border-b-0"
            >
              {row.map((cell, index) => (
                <td
                  key={index}
                  title={cell}
                  className={`py-sp-2 text-row truncate leading-tight ${index === 0 ? "text-ink text-left font-semibold" : "pl-sp-2 text-ink-2 text-right font-mono tabular-nums"}`}
                >
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

function PlayerView({
  block,
  live,
}: {
  block: Extract<AnswerBlock, { kind: "player" }>;
  live: boolean;
}) {
  const team = block.fantasy_team ?? "Free agent";
  return (
    <div
      role="group"
      aria-label={block.name}
      className="gap-sp-3 border-rule pt-sp-3 flex min-w-0 flex-col border-t"
      data-block="player"
    >
      <Rise live={live} index={0} className="gap-sp-1 flex min-w-0 flex-col">
        <p className="text-stat text-ink m-0 truncate leading-tight font-bold">{block.name}</p>
        <p className="text-meta text-mute m-0 truncate font-mono leading-tight">
          {[block.position, block.nfl_team, team].filter(Boolean).join(" · ")}
        </p>
      </Rise>
      <Rise live={live} index={1}>
        {/* The status reads in words and in color, so it never rests on color alone. */}
        <p className="gap-sp-2 text-row text-ink m-0 inline-flex items-center leading-tight font-semibold">
          <span
            aria-hidden
            className={`size-sp-2 flex-none rounded-full ${block.can_play_now ? "bg-move-up" : "bg-move-down"}`}
          />
          {block.can_play_now ? "Can play now" : "Can't play now"}
          <span className="text-meta text-mute font-mono font-normal">{block.status}</span>
        </p>
      </Rise>
      {block.stats.length > 0 && (
        <dl className="gap-x-sp-4 gap-y-sp-3 m-0 grid grid-cols-2">
          {block.stats.map((stat, index) => (
            <Rise
              key={stat.label}
              live={live}
              index={index + 2}
              className="gap-sp-1 flex min-w-0 flex-col"
            >
              <dt className="text-meta tracking-caps text-mute truncate font-mono leading-tight uppercase">
                {stat.label}
              </dt>
              <dd className="text-row m-0 truncate leading-tight font-bold tabular-nums">
                {stat.value}
              </dd>
            </Rise>
          ))}
        </dl>
      )}
      {block.note && (
        <Rise live={live} index={block.stats.length + 2}>
          <p className="text-body leading-body text-ink-2 m-0">{block.note}</p>
        </Rise>
      )}
    </div>
  );
}

/* The component of each kind of block. `you` is the name of Your team, for a block that names each team only by its name. */
export function BlockView({
  block,
  live,
  you,
}: {
  block: AnswerBlock;
  live: boolean;
  you?: string;
}) {
  switch (block.kind) {
    case "list":
      return <ListView block={block} live={live} />;
    case "table":
      return <TableView block={block} live={live} />;
    case "player":
      return <PlayerView block={block} live={live} />;
    case "recap":
      return <RecapCard block={block} live={live} />;
    case "trade":
      return <TradeBlockView block={block} live={live} />;
    case "feed":
      return <FeedView block={block} live={live} you={you} />;
    case "slot_ranks":
      return <SlotRanksView block={block} live={live} />;
    case "bye_grid":
      return <ByeGridView block={block} live={live} />;
    case "waiver_list":
      return <WaiverListView block={block} live={live} />;
    case "sell_list":
      return <SellListView block={block} live={live} />;
    case "lineup":
      return <LineupView block={block} />;
    case "matchup":
      return <MatchupCard block={block} live={live} />;
    case "rank_movers":
      return <RankMoverList block={block} live={live} />;
    case "ladder":
      return <StandingsLadder block={block} live={live} />;
    case "schedule":
      return <ScheduleStrip block={block} live={live} />;
    case "nfl_game":
      return <NflGameView block={block} live={live} />;
    case "comparison":
      return <ComparisonView block={block} live={live} />;
  }
}
