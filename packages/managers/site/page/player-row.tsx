/**
 * One player row of the Best Adds and the Top Performers chapters, in the shape of the Position Leaders rows.
 * The round photo frame, the name over one quiet line, and at the right end the points over one quiet line.
 */
import type { ReactNode } from "react";
import { num } from "@cpc/design/format/format";
import type { ManagerPlayer } from "../schema/manager-types";
import { PhotoFrame } from "@cpc/design/parts/photo-frame";
import { sleeperHeadshot } from "@cpc/league/images";
import { stableId } from "@cpc/design/lib/stable-id";

/* The quiet line of a row. A null position adds no part, so the line starts at the next part. */
export function playerMetaLine(player: ManagerPlayer, ...parts: string[]): string {
  return [player.position, ...parts].filter(Boolean).join(" · ");
}

/* The photo of a player in the frame. The Sleeper CDN has no headshot of a defense, so a defense gets null, and the
   frame shows the initials of the team in place of a broken image. */
function photoOf(player: ManagerPlayer): string | null {
  return player.position === "DEF" ? null : sleeperHeadshot(player.player_id);
}

/* Each line carries data-line, so the tests read the lines of a row in order. */
export function PlayerRow({
  player,
  meta,
  points,
  under,
  stable,
}: {
  player: ManagerPlayer;
  meta: string;
  points: number;
  under: string;
  // The stable id of the row, from its chapter and its player, so the egg hunt can name it.
  stable?: string;
}) {
  return (
    <li className="flex items-center gap-sp-2 border-t border-rule py-sp-2 tabular-nums first:border-t-0" {...(stable ? stableId(stable) : {})}>
      {/* The name sits next to the frame, so the frame is decorative. */}
      <PhotoFrame src={photoOf(player)} name={player.name} decorative />
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
  if (children.length === 0) return <div className="m-0 text-body text-mute">{empty}</div>;
  return <ol className="m-0 list-none p-0 text-row leading-tight">{children}</ol>;
}
