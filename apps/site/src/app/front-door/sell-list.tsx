/**
 * The sell list block: one row per player of Your team to sell, with his ranks and the headline of why. The bullets of
 * each row open in place. A roster with no clear sell shows its plain line.
 */
"use client";

import { useId } from "react";
import { z } from "zod";
import { Headshot } from "@cpc/league/headshot";
import { LedgerLabel, LedgerRow } from "./ledger-row";

/* The label over the rows. The card around the list names the Topic, so the label names only what the rows are. */
export const SELL_LIST_LABEL = "Players to sell";

export const sellListSchema = z.object({
  kind: z.literal("sell_list"),
  team: z.number(),
  rows: z.array(
    z.object({
      player_id: z.string(),
      name: z.string(),
      position: z.string(),
      nfl_team: z.string(),
      headshot: z.string(),
      season_rank: z.string().nullable(),
      recent_rank: z.string().nullable(),
      headline: z.string(),
      bullets: z.array(z.object({ text: z.string(), mark: z.enum(["for", "against", "even"]) })),
    }),
  ),
  // The plain line of a roster with no clear sell.
  empty: z.string().nullable(),
});
export type SellList = z.infer<typeof sellListSchema>;
type SellRow = SellList["rows"][number];

/* The ranks of a player, the Season rank first, then the Recent rank when the document sends one. */
function ranksOf(row: SellRow): string | null {
  const ranks = [row.season_rank && `Season ${row.season_rank}`, row.recent_rank && `Recent ${row.recent_rank}`].filter(Boolean);
  return ranks.length > 0 ? ranks.join(" · ") : null;
}

/* The list as one short line of plain text, so a turn of the Thread carries it. */
export function sellListText(block: SellList): string {
  if (block.rows.length === 0) return block.empty ?? "No clear sell";
  return `${SELL_LIST_LABEL}: ${block.rows.map((row) => [row.name, ranksOf(row), row.headline].filter(Boolean).join(", ")).join("; ")}`;
}

/* A bullet for the sell leads in red, a bullet against it in ink, and an even one in gray. The text says the same, so
   the mark never rests on color alone. */
const MARK_DOT: Record<SellRow["bullets"][number]["mark"], string> = { for: "bg-accent", against: "bg-ink", even: "bg-mute" };

/* The head of one player: who leads, then his ranks, then the headline of why under them. */
function SellHead({ row }: { row: SellRow }) {
  const ranks = ranksOf(row);
  return (
    <span className="flex min-w-0 flex-col gap-sp-2">
      <span className="flex min-w-0 items-center gap-sp-3">
        <Headshot src={row.headshot} size="avatar" lazy className="flex-none rounded-full bg-page object-cover object-top" />
        <span className="flex min-w-0 flex-col gap-sp-0">
          <span className="truncate text-row leading-tight font-semibold text-ink">{row.name}</span>
          <span className="truncate font-mono text-meta leading-tight text-mute">
            {row.position} · {row.nfl_team}
            {ranks && <span className="text-ink-2 tabular-nums">{` · ${ranks}`}</span>}
          </span>
        </span>
      </span>
      <span className="text-body leading-body text-ink-2">{row.headline}</span>
    </span>
  );
}

export function SellListView({ block, live }: { block: SellList; live: boolean }) {
  const id = useId();
  return (
    <div className="flex min-w-0 flex-col gap-sp-2" data-block="sell_list">
      <LedgerLabel id={id}>{SELL_LIST_LABEL}</LedgerLabel>
      {block.rows.length > 0 ? (
        <ul aria-labelledby={id} className="m-0 flex list-none flex-col border-t border-rule p-0">
          {block.rows.map((row, index) => (
            <LedgerRow key={row.player_id} panelId={`${id}-row-${index}`} label={`Sell ${row.name}`} live={live} index={index} head={<SellHead row={row} />}>
              <ul className="m-0 flex list-none flex-col gap-sp-2 p-0">
                {row.bullets.map((bullet) => (
                  <li key={bullet.text} className="grid grid-cols-[auto_minmax(0,1fr)] items-start gap-x-sp-2 text-body leading-body text-ink-2">
                    <span aria-hidden className={`mt-[0.55em] size-sp-2 flex-none rounded-full ${MARK_DOT[bullet.mark]}`} />
                    <span>{bullet.text}</span>
                  </li>
                ))}
              </ul>
            </LedgerRow>
          ))}
        </ul>
      ) : (
        block.empty && <p className="m-0 text-body leading-body text-ink-2">{block.empty}</p>
      )}
    </div>
  );
}
