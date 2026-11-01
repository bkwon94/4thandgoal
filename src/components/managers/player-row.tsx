/**
 * One player row of the Best Adds and the Top Performers chapters, in the shape of the Position Leaders rows.
 * The headshot, the name over one quiet line, and at the right end the points over one quiet line.
 */
import type { ReactNode } from "react";
import { num } from "@/lib/format/format";
import type { ManagerPlayer } from "@/lib/manager-types";
import { PlayerHeadshot } from "./player-headshot";

/* A count with its word, singular for one: "1 game", "3 games". */
export function count(n: number, word: string): string {
  return `${n} ${word}${n === 1 ? "" : "s"}`;
}

/* The quiet line of a row. A null position adds no part, so the line starts at the next part. */
export function metaLine(player: ManagerPlayer, ...parts: string[]): string {
  return [player.position, ...parts].filter(Boolean).join(" · ");
}

/* One decimal for a projection or a per game number, since a second decimal adds no news there: "26.3".
   The round comes first, because toFixed alone rounds 15.85 down to 15.8 by its binary value. */
export function oneDecimal(x: number): string {
  return (Math.round(x * 10) / 10).toFixed(1);
}

/* Each line carries data-line, so the tests read the lines of a row in order. */
export function PlayerRow({
  player,
  meta,
  points,
  under,
}: {
  player: ManagerPlayer;
  meta: string;
  points: number;
  under: string;
}) {
  return (
    <li className="flex items-center gap-sp-2 border-t border-rule py-sp-2 tabular-nums first:border-t-0">
      <PlayerHeadshot playerId={player.player_id} />
      <span className="flex min-w-0 flex-1 flex-col">
        <b data-line className="overflow-hidden font-extrabold text-ellipsis whitespace-nowrap">
          {player.name}
        </b>
        <Quiet>{meta}</Quiet>
      </span>
      {/* The points are the stat a reader scans for, so they take the body size and the heaviest weight in the row. */}
      <span className="flex flex-none flex-col items-end">
        <span data-line className="text-body font-extrabold">
          {num(points)}
        </span>
        <Quiet>{under}</Quiet>
      </span>
    </li>
  );
}

function Quiet({ children }: { children: ReactNode }) {
  return (
    <span data-line className="text-meta text-mute">
      {children}
    </span>
  );
}

/* The list of rows, or one quiet line when the list is empty. */
export function PlayerRows({ empty, children }: { empty: string; children: ReactNode[] }) {
  if (children.length === 0) return <p className="m-0 text-body text-mute">{empty}</p>;
  return <ol className="m-0 list-none p-0 text-row leading-tight">{children}</ol>;
}
