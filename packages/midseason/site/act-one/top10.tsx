/**
 * Position top 10, a chapter of Act I: the ten best players of one position by total league points, with a switch
 * for each position. It opens on RB. It is a client component, because the chosen position is state.
 */
"use client";

import { useState } from "react";
import { num, oneDecimal } from "@cpc/design/format/format";
import { cn } from "@cpc/design/lib/utils";
import { Card } from "@cpc/design/parts/card";
import { Tag } from "@cpc/design/parts/tag";
import { ReportChapter } from "../report/report-chapter";
import type { PositionBoard, Top10Chapter, TopPlayer } from "../schema/midseason-types";

/* The board that the chapter opens on (decision ticket 10). A league with no RB board opens on its first board. */
export const FIRST_POSITION = "RB";

/* One row: the rank, the player over his NFL team, the manager who has him or the free agent tag, and the points. */
function Row({ player }: { player: TopPlayer }) {
  return (
    <li className="grid grid-cols-[auto_minmax(0,1fr)_auto] items-center gap-x-sp-3 border-b border-rule py-sp-2 last:border-b-0">
      <span className="font-mono text-meta text-mute tabular-nums">{String(player.rank).padStart(2, "0")}</span>
      <span className="min-w-0">
        <span className="block truncate text-body leading-tight font-bold">{player.name}</span>
        <span className="block truncate text-meta leading-tight text-ink-2">
          {player.nfl_team ?? "No team"}
          {player.manager !== null && ` · ${player.manager}`}
          {player.tag !== null && <Tag className="text-meta">{player.tag}</Tag>}
        </span>
      </span>
      <span className="text-right">
        <span className="block font-mono text-body font-bold tabular-nums">{num(player.points)}</span>
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
  return (
    <ReportChapter id={chapter.key} title={chapter.title} note="Total league points" blurb={chapter.blurb} roast={chapter.roast}>
      {/* Each chip is a 44px pill. The chosen chip is filled, and aria-pressed tells a screen reader which one. */}
      <div role="group" aria-label="Position" className="flex gap-sp-2">
        {boards.map(({ position }) => {
          const on = position === board?.position;
          return (
            <button
              key={position}
              type="button"
              aria-pressed={on}
              onClick={() => setChosen(position)}
              className={cn(
                "press min-h-touch min-w-touch flex-1 cursor-pointer rounded-pill border font-mono text-meta font-bold",
                on ? "border-ink bg-ink text-page" : "border-rule bg-transparent text-ink-2",
              )}
            >
              {position}
            </button>
          );
        })}
      </div>
      {board !== undefined && (
        <Card className="py-sp-1">
          <ol aria-label={`${board.position} top 10`} className="m-0 list-none p-0">
            {board.players.map((player) => (
              <Row key={player.player_id} player={player} />
            ))}
          </ol>
        </Card>
      )}
    </ReportChapter>
  );
}
