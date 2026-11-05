/**
 * Position leaders: a chip for each position, and the top three started players of the chosen position, then the blurb.
 * It is a client component, because the chosen chip is state.
 */
"use client";

import { useState } from "react";
import { num } from "@cpc/design/format/format";
import { cn } from "@cpc/design/lib/utils";
import { Card } from "@cpc/design/parts/card";
import { PhotoFrame } from "@cpc/design/parts/photo-frame";
import type { HeadshotMap, LeaderBoard, LeaderRow } from "../schema/week-types";
import { photoOf } from "../parts/photo";
import { WeekChapter } from "../parts/week-chapter";

/* One row: the rank, the round photo, the player over the fantasy team, and the points. A long name cuts at its end. */
function Row({ row, headshots }: { row: LeaderRow; headshots: HeadshotMap }) {
  return (
    <li className="grid list-none grid-cols-[auto_auto_minmax(0,1fr)_auto] items-center gap-sp-3 py-sp-2">
      <span className="font-mono text-meta text-mute tabular-nums">{row.rank}</span>
      <PhotoFrame src={photoOf(headshots, row.player_id)} name={row.player} size="md" />
      <span className="min-w-0">
        <span data-player className="block truncate text-body leading-tight font-bold">
          {row.player}
        </span>
        <span className="block truncate text-meta leading-tight text-mute">{row.team}</span>
      </span>
      <span className="font-mono text-body font-bold tabular-nums">{num(row.points)}</span>
    </li>
  );
}

export function PositionLeaders({
  leaders,
  headshots,
  blurb,
}: {
  leaders: LeaderBoard[];
  headshots: HeadshotMap;
  blurb?: string;
}) {
  const [chosen, setChosen] = useState(leaders[0]?.position);
  const board = leaders.find((item) => item.position === chosen) ?? leaders[0];
  return (
    <WeekChapter id="leaders" title="Position leaders">
      {/* Each chip is a 44px pill. The chosen chip is filled, and aria-pressed tells a screen reader which one. */}
      <div className="flex gap-sp-2">
        {leaders.map(({ position }) => {
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
      {board && (
        <Card className="py-sp-2">
          {board.rows.length > 0 ? (
            <ol aria-label={`${board.position} leaders`} className="m-0 p-0">
              {board.rows.map((row) => (
                <Row key={row.rank} row={row} headshots={headshots} />
              ))}
            </ol>
          ) : (
            <div className="py-sp-2 text-meta text-mute">No starters this week</div>
          )}
        </Card>
      )}
      {blurb && <p className="m-0 max-w-measure text-lead leading-body text-ink-2">{blurb}</p>}
    </WeekChapter>
  );
}
