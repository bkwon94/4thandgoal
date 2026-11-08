/**
 * Position top 10, a chapter of Act I: the ten best players of one position by total league points, with a switch
 * for each position. It opens on RB. It is a client component, because the chosen position is state.
 */
"use client";

import { useState } from "react";
import { oneDecimal } from "@cpc/design/format/format";
import { cn } from "@cpc/design/lib/utils";
import { sleeperHeadshot } from "@cpc/league/images";
import { ReportCard } from "../report/report-card";
import { ReportPhoto } from "../report/report-photo";
import { ReportChapter } from "../report/report-chapter";
import type { PositionBoard, Top10Chapter, TopPlayer } from "../schema/midseason-types";
import { openId, stableId } from "@cpc/design/lib/stable-id";

/* The board that the chapter opens on (decision ticket 10). A league with no RB board opens on its first board. */
export const FIRST_POSITION = "RB";

/* The Sleeper CDN has no headshot for a DEF, whose id is its NFL team, so a DEF frame shows the initials of the team. */
const DEFENSE = "DEF";

/* One row: the rank, a small headshot, the player over his NFL team and the manager who has him, and the points. A player on the wire
   has his tag, such as "Free agent", in the second line in place of a manager, as a fact about him (decision ticket 15). */
function Row({ player }: { player: TopPlayer }) {
  return (
    <li
      className="grid grid-cols-[auto_auto_minmax(0,1fr)_auto] items-center gap-x-sp-3 border-b border-rule py-sp-2 last:border-b-0"
      {...stableId("top10", player.position, player.rank)}
    >
      <span className="font-mono text-meta text-mute tabular-nums">{String(player.rank).padStart(2, "0")}</span>
      <ReportPhoto
        src={player.position === DEFENSE ? null : sleeperHeadshot(player.player_id)}
        name={player.name}
        size="sm"
      />
      <span className="min-w-0">
        <span className="block truncate text-body leading-tight font-bold">{player.name}</span>
        <span className="block truncate text-meta leading-tight text-ink-2">
          {player.nfl_team ?? "No team"}
          {player.manager !== null && ` · ${player.manager}`}
          {player.tag !== null && (
            <>
              {" · "}
              <b className="font-semibold text-ink">{player.tag}</b>
            </>
          )}
        </span>
      </span>
      <span className="text-right">
        <span className="block font-mono text-body font-bold tabular-nums">{oneDecimal(player.points)}</span>
        <span className="block font-mono text-meta text-mute tabular-nums">{oneDecimal(player.points_per_game)} a game</span>
      </span>
    </li>
  );
}

export function Top10({ chapter }: { chapter: Top10Chapter }) {
  const boards: PositionBoard[] = chapter.facts.positions;
  const [chosen, setChosen] = useState(
    boards.some((board) => board.position === FIRST_POSITION) ? FIRST_POSITION : boards[0]?.position,
  );
  const board = boards.find((item) => item.position === chosen) ?? boards[0];
  const chosenIndex = Math.max(0, boards.findIndex((item) => item.position === board?.position));
  return (
    <ReportChapter id={chapter.key} title={chapter.title} note="Total league points" blurb={chapter.blurb}>
      {/* Each segment is a 44px text button, and aria-pressed tells a screen reader which one is chosen. A 2px accent
          underline slides under the chosen one. It is a CSS transition, so the reduced-motion rule of globals.css stops it. */}
      <div role="group" aria-label="Position" className="relative flex border-b border-rule">
        {boards.map(({ position }) => {
          const on = position === board?.position;
          return (
            <button
              key={position}
              type="button"
              aria-pressed={on}
              onClick={() => setChosen(position)}
              {...openId("chip", position)}
              className={cn(
                "press min-h-touch min-w-touch flex-1 cursor-pointer font-mono text-meta font-bold tracking-caps",
                on ? "text-ink" : "text-mute hover-fine:text-ink-2",
              )}
            >
              {position}
            </button>
          );
        })}
        <span
          aria-hidden="true"
          data-underline
          className="absolute -bottom-px h-sp-0 bg-accent transition-[left] duration-300 ease-rise"
          style={{ left: `${(chosenIndex * 100) / boards.length}%`, width: `${100 / boards.length}%` }}
        />
      </div>
      {board !== undefined && (
        <ReportCard className="py-sp-1">
          <ol aria-label={`${board.position} top 10`} className="m-0 list-none p-0">
            {board.players.map((player) => (
              <Row key={player.player_id} player={player} />
            ))}
          </ol>
        </ReportCard>
      )}
    </ReportChapter>
  );
}
