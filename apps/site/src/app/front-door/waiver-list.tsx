/**
 * The waiver list block: one row per free agent worth a claim, with his position, his NFL team, his projection, and
 * the slot he fills. The why of each row opens in place.
 */
"use client";

import { useId } from "react";
import { z } from "zod";
import { LedgerLabel, LedgerRow } from "./ledger-row";

/* The slot of a free agent who fills no starting slot now, such as a stash who is out. */
const BENCH = "Bench";

export const waiverListSchema = z.object({
  kind: z.literal("waiver_list"),
  // The one line over the rows, such as "2 free agents worth a claim".
  fact: z.string(),
  rows: z.array(
    z.object({
      name: z.string(),
      position: z.string(),
      nfl_team: z.string().nullable(),
      // The projection of the week.
      projection: z.number(),
      slot: z.string(),
      kind: z.enum(["add", "stash"]),
      why: z.array(z.string()),
    }),
  ),
  // The plain line of a list with no free agent worth a claim.
  empty: z.string().nullable(),
});
export type WaiverList = z.infer<typeof waiverListSchema>;
type WaiverRow = WaiverList["rows"][number];

const slotWord = (slot: string) => (slot === BENCH ? BENCH : `${slot} slot`);
const points = (projection: number) => projection.toFixed(1);

/* The list as one short line of plain text, so a turn of the Thread carries it. */
export function waiverListText(block: WaiverList): string {
  if (block.rows.length === 0) return block.empty ?? block.fact;
  const rows = block.rows.map((row) => [row.name, row.position, row.nfl_team, `${points(row.projection)} projected`, slotWord(row.slot)].filter(Boolean).join(", "));
  return `${block.fact}: ${rows.join("; ")}.`;
}

/* The head of one free agent: the slot he fills leads in red for a claim of this week, as the side of Your team, and in
   gray for a stash. The projection sits right, in tabular figures, so the rows line up. */
function WaiverHead({ row }: { row: WaiverRow }) {
  return (
    <span className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-x-sp-3">
      <span className="flex min-w-0 flex-col gap-sp-0">
        <span className="truncate text-row leading-tight font-semibold text-ink">{row.name}</span>
        <span className="truncate font-mono text-meta leading-tight text-mute">
          {[row.position, row.nfl_team].filter(Boolean).join(" · ")}
          {" · "}
          <span className={row.kind === "add" ? "text-accent-ink" : "text-mute"}>{slotWord(row.slot)}</span>
        </span>
      </span>
      <span className="flex flex-col items-end gap-sp-0">
        <span className="font-mono text-row leading-tight text-ink-2 tabular-nums">{points(row.projection)}</span>
        <span className="font-mono text-meta leading-tight text-mute">proj</span>
      </span>
    </span>
  );
}

/* The why of one free agent: the first line says the kind of the claim, and the facts follow it. */
function Why({ why }: { why: string[] }) {
  const [lead, ...rest] = why;
  return (
    <div className="flex flex-col gap-sp-2">
      {lead && <p className="m-0 text-body leading-tight font-semibold text-ink">{lead}</p>}
      {rest.length > 0 && (
        <ul className="m-0 flex list-disc flex-col gap-sp-1 pl-sp-4 text-body leading-body text-ink-2 marker:text-mute">
          {rest.map((line) => (
            <li key={line}>{line}</li>
          ))}
        </ul>
      )}
    </div>
  );
}

export function WaiverListView({ block, live }: { block: WaiverList; live: boolean }) {
  const id = useId();
  return (
    <div className="flex min-w-0 flex-col gap-sp-2" data-block="waiver_list">
      <LedgerLabel id={id}>{block.fact}</LedgerLabel>
      {block.rows.length > 0 ? (
        <ul aria-labelledby={id} className="m-0 flex list-none flex-col border-t border-rule p-0">
          {block.rows.map((row, index) => (
            <LedgerRow key={row.name} panelId={`${id}-row-${index}`} label={row.name} live={live} index={index} head={<WaiverHead row={row} />}>
              <Why why={row.why} />
            </LedgerRow>
          ))}
        </ul>
      ) : (
        block.empty && <p className="m-0 text-body leading-body text-ink-2">{block.empty}</p>
      )}
    </div>
  );
}
