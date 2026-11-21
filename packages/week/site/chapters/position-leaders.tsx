/**
 * Position leaders: a chip for each position, and the top three started players of the chosen position,
 * then the sentences of the blurb on that position.
 * It is a client component, because the chosen chip is state.
 */
"use client";

import { Button } from "@cpc/design/ui/button";
import { useState } from "react";
import { num } from "@cpc/design/format/format";
import { cn } from "@cpc/design/lib/utils";
import { Card } from "@cpc/design/parts/card";
import { PhotoFrame } from "@cpc/design/parts/photo-frame";
import type { HeadshotMap, LeaderBoard, LeaderRow } from "../schema/week-types";
import { photoOf } from "../parts/photo";
import { WeekChapter } from "../parts/week-chapter";
import { openId, stableId, textId } from "@cpc/design/lib/stable-id";

/* One row: the rank, the round photo, the player over the fantasy team, and the points. A long name cuts at its end. */
function Row({
  row,
  position,
  headshots,
}: {
  row: LeaderRow;
  position: string;
  headshots: HeadshotMap;
}) {
  return (
    <li
      className="gap-sp-3 py-sp-2 grid list-none grid-cols-[auto_auto_minmax(0,1fr)_auto] items-center"
      {...stableId("leader", position, row.rank)}
    >
      <span className="text-meta text-mute font-mono tabular-nums">{row.rank}</span>
      <PhotoFrame src={photoOf(headshots, row.player_id)} name={row.player} size="md" />
      <span className="min-w-0">
        <span data-player className="text-body block truncate leading-tight font-bold">
          {row.player}
        </span>
        <span className="text-meta text-mute block truncate leading-tight">{row.team}</span>
      </span>
      <span className="text-body font-mono font-bold tabular-nums">{num(row.points)}</span>
    </li>
  );
}

/* A sentence ends at ".", "!", or "?" and a space, but not at the dot of a name such as "Harold Fannin Jr.". */
const SENTENCE_END = /(?<=[.!?])(?<!\b(?:Jr|Sr|St)\.)\s+/;

/* The pipeline writes one blurb for the whole chapter, with no text per position.
   So the chapter shows only the sentences of the blurb that name the leader of the chosen board, in their order.
   The leader, not any of the three, because a sentence on the top quarterback can name a receiver of the same roster.
   A position whose leader no sentence names, such as DEF, shows no prose, so the text never describes another position. */
function blurbFor(blurb: string | undefined, board: LeaderBoard | undefined): string | null {
  const leader = board?.rows[0]?.player;
  if (!blurb || !leader) return null;
  const sentences = blurb.split(SENTENCE_END).filter((sentence) => sentence.includes(leader));
  return sentences.length > 0 ? sentences.join(" ") : null;
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
  const text = blurbFor(blurb, board);
  return (
    <WeekChapter id="leaders" title="Position leaders">
      {/* Each chip is a 44px pill. The chosen chip is filled, and aria-pressed tells a screen reader which one. */}
      <div className="gap-sp-2 flex">
        {leaders.map(({ position }) => {
          const on = position === board?.position;
          return (
            <Button
              variant="plain"
              key={position}
              type="button"
              aria-pressed={on}
              {...openId("chip", position)}
              onClick={() => setChosen(position)}
              className={cn(
                "press min-h-touch min-w-touch rounded-pill text-meta flex-1 cursor-pointer border font-mono font-bold",
                on ? "border-ink bg-ink text-page" : "border-rule text-ink-2 bg-transparent",
              )}
            >
              {position}
            </Button>
          );
        })}
      </div>
      {board && (
        <Card className="py-sp-2">
          {board.rows.length > 0 ? (
            <ol aria-label={`${board.position} leaders`} className="m-0 p-0">
              {board.rows.map((row) => (
                <Row key={row.rank} row={row} position={board.position} headshots={headshots} />
              ))}
            </ol>
          ) : (
            <div className="py-sp-2 text-meta text-mute">No starters this week</div>
          )}
        </Card>
      )}
      {text && (
        <p
          className="max-w-measure text-lead leading-body text-ink-2 m-0"
          {...textId("blurb", text)}
        >
          {text}
        </p>
      )}
    </WeekChapter>
  );
}
