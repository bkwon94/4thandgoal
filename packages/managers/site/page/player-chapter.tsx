/**
 * A chapter of a manager page that lists players: the label, then one player row per item.
 * The Best Adds and the Top Performers chapters share it and differ only in their words and their rows.
 */
import type { ComponentProps } from "react";
import { Chapter } from "@cpc/design/parts/chapter";
import { Label } from "@cpc/design/parts/label";
import { PlayerRow, PlayerRows } from "./player-row";

export type PlayerChapterItem = ComponentProps<typeof PlayerRow>;

export function PlayerChapter({ id, title, empty, items }: { id: string; title: string; empty: string; items: PlayerChapterItem[] }) {
  return (
    <Chapter reveal id={id}>
      {/* The meta size keeps the heading over the text floor of 11px on a phone. */}
      <Label heading className="text-meta">{title}</Label>
      <PlayerRows empty={empty}>
        {items.map((item) => (
          <PlayerRow key={item.player.player_id} {...item} />
        ))}
      </PlayerRows>
    </Chapter>
  );
}
