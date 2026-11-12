/**
 * The lineup block of Start or sit: each slot of the Week lineup in Sleeper order, a Swap or a Q row that opens in place
 * with its reason or its Pivot, the "Can't play" line, and the toggle of the total. It holds the schema of the block, its
 * short text for a turn, and its view.
 */
"use client";

import { useId, useState } from "react";
import { ChevronDownIcon, LockIcon } from "lucide-react";
import { z } from "zod";

const riskSchema = z.object({ tag: z.literal("Q"), body_part: z.string().nullable(), practice: z.string(), pivot: z.string() });

/* The starter that a Swap benches, with his projection, and the checked sentence that gives the reason. The reason comes
   with the block after the check, so the first block of the stream has none. */
const swapSchema = z.object({ over: z.string(), over_projection: z.number(), reason: z.string().nullable() });

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
  // A block kept before the Swaps has none.
  swap: swapSchema.nullable().default(null),
});

export const lineupBlockSchema = z.object({
  kind: z.literal("lineup"),
  topic: z.literal("start_sit"),
  team: z.number(),
  week: z.number(),
  // The total by projection, and the total with the Swaps. A block kept before the Swaps has only the first.
  total: z.number(),
  swap_total: z.number().optional(),
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

/* The count of the Swaps as the toggle says it: "With 1 Swap", "With 2 Swaps". */
export const swapsLabel = (count: number) => `With ${count} ${count === 1 ? "Swap" : "Swaps"}`;

/* The block as one short line of plain text, so the turn of the Answer carries it. */
export function lineupText(block: LineupBlock): string {
  const rows = block.rows.map(
    (row) =>
      `${row.slot} ${row.player ?? "empty"}${row.projection === null ? "" : ` ${points(row.projection)}`}${row.risk ? " (Q)" : ""}${row.swap ? ` (Swap over ${row.swap.over})` : ""}`,
  );
  const absent = block.cannot_play.length > 0 ? ` Can't play: ${block.cannot_play.map(absentText).join(", ")}.` : "";
  const swaps = block.rows.filter((row) => row.swap).length;
  const total = swaps > 0 ? `${points(block.total)} points by projection, ${points(block.swap_total ?? block.total)} ${swapsLabel(swaps).toLowerCase()}` : `by projection, ${points(block.total)} points`;
  return `Week ${block.week} lineup ${swaps > 0 ? "with Swaps" : "by projection"}, ${total}: ${rows.join("; ")}.${absent}`;
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

/* The Swap line of a row: the starter that the Swap benches, struck through. */
function SwapLine({ swap }: { swap: NonNullable<LineupRow["swap"]> }) {
  return (
    <span className="truncate text-meta leading-tight text-ink-2">
      <span className="font-semibold text-accent-ink">Swap</span> over <s className="text-mute decoration-mute">{swap.over}</s>
    </span>
  );
}

/* The main line of a row: the slot, the player with his Q tag, his game, his Swap line, and the projection. */
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
        {row.swap && <SwapLine swap={row.swap} />}
      </span>
      <span className="flex items-center gap-sp-1">
        <span data-projection={row.projection ?? 0} className="font-mono text-row leading-tight text-ink-2 tabular-nums">
          {row.projection === null ? "–" : points(row.projection)}
        </span>
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

/* The detail of a row: a fact line, then the main line under a red rule. It opens taller in place and comes into focus
   from a blur, so only the rows under it move down. With reduced motion it shows with no move. */
function Detail({ id, open, fact, line }: { id: string; open: boolean; fact: string; line: string | null }) {
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
          <p className="m-0 font-mono text-meta leading-tight text-mute">{fact}</p>
          {line && (
            // The reason of a Swap comes after the check, so it lands in the open row with a soft focus from a blur.
            <p
              key={line}
              className="m-0 border-l-2 border-accent pl-sp-2 text-body leading-body text-ink transition-[opacity,filter] duration-250 ease-[cubic-bezier(0.22,1,0.36,1)] starting:opacity-0 starting:blur-[2px] motion-reduce:blur-none"
            >
              {line}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

/* The detail of a row with a Swap or a Q, or null for a row with neither. A Swap shows the two projections and its reason,
   and a Q shows the body part, the practice level, and the Pivot. */
function detailOf(row: LineupRow): { fact: string; line: string | null } | null {
  if (row.swap) return { fact: `${points(row.projection ?? 0)} against ${points(row.swap.over_projection)} for ${row.swap.over} by projection`, line: row.swap.reason };
  if (row.risk) return { fact: [row.risk.body_part, row.risk.practice].filter(Boolean).join(" · "), line: row.risk.pivot };
  return null;
}

/* One slot of the lineup. A row with detail is a button that opens the detail in place. */
function Row({ row, open, onToggle }: { row: LineupRow; open: boolean; onToggle: () => void }) {
  const id = useId();
  const detail = detailOf(row);
  if (!detail) {
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
      <Detail id={id} open={open} fact={detail.fact} line={detail.line} />
    </li>
  );
}

const DIGITS = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"];

/* One digit of the total as a column of 0 to 9 that rolls to its digit. The column slides on the compositor, so a new tap
   retargets it from where it is. Each column to the left starts a stagger later, so the change reads right to left. */
function DigitColumn({ digit, place }: { digit: number; place: number }) {
  return (
    <span className="relative inline-block h-[1em] overflow-hidden [mask-image:linear-gradient(transparent,black_20%,black_80%,transparent)]">
      <span
        className="flex flex-col transition-transform duration-250 ease-[cubic-bezier(0.22,1,0.36,1)] will-change-transform motion-reduce:transition-none"
        style={{ transform: `translateY(${-digit * 10}%)`, transitionDelay: `${place * 40}ms` }}
      >
        {DIGITS.map((d) => (
          <span key={d} className="block h-[1em]">
            {d}
          </span>
        ))}
      </span>
    </span>
  );
}

/* The total with its digits that roll on a change. The digits are hidden from a screen reader, which reads the value. The
   columns keep their place from the right, so 104.7 and 121.7 roll in the same columns. */
function RollingTotal({ value }: { value: number }) {
  const text = points(value);
  const chars = [...text];
  return (
    <span data-total={text} className="inline-flex text-row leading-none font-bold text-ink tabular-nums">
      <span className="sr-only">{text}</span>
      <span aria-hidden className="inline-flex">
        {chars.map((char, index) => {
          const place = chars.length - 1 - index;
          return /\d/.test(char) ? <DigitColumn key={`d${place}`} digit={Number(char)} place={place} /> : <span key={`s${place}`}>{char}</span>;
        })}
      </span>
    </span>
  );
}

/* The toggle of the header: the total by projection or the total with the Swaps. Two equal segments, so the pill slides
   by its own width on the compositor and a quick second tap retargets it. Reduced motion moves it with no slide. */
function TotalToggle({ swaps, withSwaps, onChange }: { swaps: number; withSwaps: boolean; onChange: (withSwaps: boolean) => void }) {
  const segment =
    "press relative z-1 min-h-touch cursor-pointer rounded-pill bg-transparent px-sp-3 font-mono text-meta leading-tight whitespace-nowrap transition-colors duration-150 aria-pressed:font-semibold aria-pressed:text-ink aria-[pressed=false]:text-mute";
  return (
    <span className="relative inline-grid grid-cols-2 rounded-pill bg-raised p-[2px]">
      <span
        aria-hidden
        className={`absolute inset-y-[2px] left-[2px] w-[calc(50%-2px)] rounded-pill border border-door-hair bg-card transition-transform duration-250 ease-[cubic-bezier(0.22,1,0.36,1)] motion-reduce:transition-none ${withSwaps ? "translate-x-full" : "translate-x-0"}`}
      />
      <button type="button" aria-pressed={!withSwaps} onClick={() => onChange(false)} className={segment}>
        By projection
      </button>
      <button type="button" aria-pressed={withSwaps} onClick={() => onChange(true)} className={segment}>
        {swapsLabel(swaps)}
      </button>
    </span>
  );
}

/* The lineup block. The first row with a Swap or a Q opens on arrival, and a tap opens or closes any row with detail.
   With a Swap, the header holds the toggle of the total, and the total with the Swaps shows first, because the rows show
   the lineup with the Swaps. */
export function LineupView({ block }: { block: LineupBlock }) {
  const first = block.rows.findIndex((row) => row.risk !== null || row.swap !== null);
  const swaps = block.rows.filter((row) => row.swap !== null).length;
  const [withSwaps, setWithSwaps] = useState(true);
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
      {swaps > 0 ? (
        <div role="group" aria-label="Lineup total" className="flex flex-col gap-sp-2">
          <div className="flex items-baseline justify-between gap-sp-3">
            <p className="m-0 truncate font-mono text-meta leading-tight tracking-caps text-mute uppercase">{label}</p>
            <RollingTotal value={withSwaps ? (block.swap_total ?? block.total) : block.total} />
          </div>
          <TotalToggle swaps={swaps} withSwaps={withSwaps} onChange={setWithSwaps} />
        </div>
      ) : (
        <div className="flex items-baseline justify-between gap-sp-3">
          <p className="m-0 truncate font-mono text-meta leading-tight tracking-caps text-mute uppercase">{label}</p>
          <p className="m-0 flex-none font-mono text-meta leading-tight text-mute">
            By projection <span className="text-row font-bold text-ink tabular-nums">{points(block.total)}</span>
          </p>
        </div>
      )}
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
