/**
 * The lineup block of Start or sit: each slot of the Week lineup in Sleeper order, a Q row that opens in place with its
 * Pivot, and the "Can't play" line. It holds the schema of the block, its short text for a turn, and its view.
 */
"use client";

import { useId, useState } from "react";
import { ChevronDownIcon, LockIcon } from "lucide-react";
import { z } from "zod";

const riskSchema = z.object({ tag: z.literal("Q"), body_part: z.string().nullable(), practice: z.string(), pivot: z.string() });

const lineupRowSchema = z.object({
  slot: z.string(),
  player: z.string().nullable(),
  player_id: z.string().nullable(),
  position: z.string().nullable(),
  nfl_team: z.string().nullable(),
  opponent: z.string().nullable(),
  // The kickoff in epoch ms, UTC. The view shows it in the time zone of the browser.
  kickoff: z.number().nullable(),
  projection: z.number().nullable(),
  // The game of the player has started, so he cannot move.
  locked: z.boolean(),
  risk: riskSchema.nullable(),
});

export const lineupBlockSchema = z.object({
  kind: z.literal("lineup"),
  topic: z.literal("start_sit"),
  team: z.number(),
  week: z.number(),
  total: z.number(),
  rows: z.array(lineupRowSchema),
  cannot_play: z.array(z.object({ name: z.string(), status: z.string(), body_part: z.string().nullable() })),
});
export type LineupBlock = z.infer<typeof lineupBlockSchema>;
type LineupRow = LineupBlock["rows"][number];
type Absent = LineupBlock["cannot_play"][number];

/* The words of the Sleeper statuses that are short codes. Every other status, such as Out or IR, reads as it is. */
const STATUS_WORDS: Record<string, string> = { Sus: "Suspended", NA: "Not active", DNR: "Did not report" };

/* One player of the "Can't play" line, such as "J. Jacobs Out (finger)". A bye names no body part, because the bye is
   the reason. */
export function absentText(absent: Absent): string {
  const status = STATUS_WORDS[absent.status] ?? absent.status;
  const part = absent.body_part && absent.status !== "Bye" ? ` (${absent.body_part.toLowerCase()})` : "";
  return `${absent.name} ${status}${part}`;
}

const points = (value: number) => value.toFixed(1);

/* The kickoff as the day and the time, such as "Sun 1:00 PM", in the time zone of the browser. */
export function kickoffText(ms: number): string {
  return new Intl.DateTimeFormat(undefined, { weekday: "short", hour: "numeric", minute: "2-digit" }).format(new Date(ms));
}

/* The block as one short line of plain text, so the turn of the Answer carries it. */
export function lineupText(block: LineupBlock): string {
  const rows = block.rows.map((row) => `${row.slot} ${row.player ?? "empty"}${row.projection === null ? "" : ` ${points(row.projection)}`}${row.risk ? " (Q)" : ""}`);
  const absent = block.cannot_play.length > 0 ? ` Can't play: ${block.cannot_play.map(absentText).join(", ")}.` : "";
  return `Week ${block.week} lineup by projection, ${points(block.total)} points: ${rows.join("; ")}.${absent}`;
}

/* The second line of a row: the NFL team, the opponent, and the kickoff, or the lock once the game has started. */
function RowMeta({ row }: { row: LineupRow }) {
  const game = [row.nfl_team, row.opponent && `vs ${row.opponent}`].filter(Boolean).join(" ");
  return (
    <span className="flex min-w-0 items-center gap-sp-1 truncate font-mono text-meta leading-tight text-mute">
      <span className="truncate">{game}</span>
      {row.locked ? (
        <span className="inline-flex flex-none items-center gap-sp-1">
          <span aria-hidden>·</span>
          <LockIcon aria-hidden className="size-sp-3" strokeWidth={2.5} />
          Locked
        </span>
      ) : (
        row.kickoff !== null && (
          <span className="flex-none">
            <span aria-hidden>· </span>
            {kickoffText(row.kickoff)}
          </span>
        )
      )}
    </span>
  );
}

/* The main line of a row: the slot, the player with his Q tag, and the projection. */
function RowLine({ row, open }: { row: LineupRow; open: boolean | null }) {
  return (
    <>
      <span className="font-mono text-meta leading-tight tracking-caps text-mute uppercase">{row.slot}</span>
      <span className="flex min-w-0 flex-col gap-sp-1">
        <span className="flex min-w-0 items-center gap-sp-2">
          <span className={`truncate text-row leading-tight font-semibold ${row.player ? "text-ink" : "text-mute"}`}>{row.player ?? "Empty"}</span>
          {row.risk && (
            <span aria-label="Questionable" className="flex-none rounded-letter bg-accent px-sp-1 font-mono text-meta leading-tight font-bold text-on-dark">
              Q
            </span>
          )}
        </span>
        {row.player && <RowMeta row={row} />}
      </span>
      <span className="flex items-center gap-sp-1">
        <span className="font-mono text-row leading-tight text-ink-2 tabular-nums">{row.projection === null ? "–" : points(row.projection)}</span>
        {open !== null && (
          <ChevronDownIcon
            aria-hidden
            className={`size-sp-4 text-mute transition-transform duration-200 ease-[cubic-bezier(0.22,1,0.36,1)] motion-reduce:transition-none ${open ? "rotate-180" : ""}`}
            strokeWidth={2.25}
          />
        )}
      </span>
    </>
  );
}

const ROW_GRID = "grid grid-cols-[3rem_minmax(0,1fr)_auto] items-center gap-x-sp-3 py-sp-2";

/* The detail of a Q row: the body part and the practice level, then the Pivot under a red rule. It opens taller in place
   and comes into focus from a blur, so only the rows under it move down. With reduced motion it shows with no move. */
function RiskDetail({ id, risk, open }: { id: string; risk: NonNullable<LineupRow["risk"]>; open: boolean }) {
  return (
    <div
      id={id}
      aria-hidden={!open}
      inert={!open}
      className={`grid transition-[grid-template-rows] duration-250 ease-[cubic-bezier(0.22,1,0.36,1)] motion-reduce:transition-none ${open ? "grid-rows-[1fr]" : "grid-rows-[0fr]"}`}
    >
      <div className="min-h-0 overflow-hidden">
        <div
          className={`ml-[calc(3rem+var(--spacing-sp-3))] flex flex-col gap-sp-2 pb-sp-3 transition-[opacity,filter] duration-250 ease-[cubic-bezier(0.22,1,0.36,1)] motion-reduce:blur-none motion-reduce:transition-none ${open ? "opacity-100 blur-none" : "opacity-0 blur-[4px]"}`}
        >
          <p className="m-0 font-mono text-meta leading-tight text-mute">{[risk.body_part, risk.practice].filter(Boolean).join(" · ")}</p>
          <p className="m-0 border-l-2 border-accent pl-sp-2 text-body leading-body text-ink">{risk.pivot}</p>
        </div>
      </div>
    </div>
  );
}

/* One slot of the lineup. A row with detail is a button that opens the detail in place. */
function Row({ row, open, onToggle }: { row: LineupRow; open: boolean; onToggle: () => void }) {
  const id = useId();
  if (!row.risk) {
    return (
      <li className={`${ROW_GRID} border-b border-rule last:border-b-0`} data-slot={row.slot}>
        <RowLine row={row} open={null} />
      </li>
    );
  }
  return (
    <li className="border-b border-rule last:border-b-0" data-slot={row.slot}>
      <button type="button" aria-expanded={open} aria-controls={id} onClick={onToggle} className={`${ROW_GRID} press w-full cursor-pointer bg-transparent text-left`}>
        <RowLine row={row} open={open} />
      </button>
      <RiskDetail id={id} risk={row.risk} open={open} />
    </li>
  );
}

/* The lineup block. The first row with detail opens on arrival, and a tap opens or closes any row with detail. */
export function LineupView({ block }: { block: LineupBlock }) {
  const first = block.rows.findIndex((row) => row.risk !== null);
  const [open, setOpen] = useState<ReadonlySet<number>>(() => new Set(first < 0 ? [] : [first]));
  const toggle = (index: number) =>
    setOpen((now) => {
      const next = new Set(now);
      if (!next.delete(index)) next.add(index);
      return next;
    });
  const label = `Week ${block.week} lineup`;
  return (
    <div className="flex min-w-0 flex-col gap-sp-2" data-block="lineup">
      <div className="flex items-baseline justify-between gap-sp-3">
        <p className="m-0 truncate font-mono text-meta leading-tight tracking-caps text-mute uppercase">{label}</p>
        <p className="m-0 flex-none font-mono text-meta leading-tight text-mute">
          By projection <span className="text-row font-bold text-ink tabular-nums">{points(block.total)}</span>
        </p>
      </div>
      <ul aria-label={label} className="m-0 flex list-none flex-col border-t border-rule p-0">
        {block.rows.map((row, index) => (
          <Row key={`${row.slot}-${index}`} row={row} open={open.has(index)} onToggle={() => toggle(index)} />
        ))}
      </ul>
      {block.cannot_play.length > 0 && (
        <p className="m-0 text-meta leading-tight text-ink-2">
          <span className="font-semibold text-ink">Can&apos;t play:</span> {block.cannot_play.map(absentText).join(", ")}
        </p>
      )}
    </div>
  );
}
