/**
 * The Best Adds chapter of a manager page: up to three adds by points scored for the team since the add.
 * Each row shows the points and, under them, the projection over the same weeks.
 */
import { Chapter, Label } from "@/components/week/parts";
import { count, oneDecimal } from "@/lib/format/format";
import type { Manager } from "@/lib/manager-types";
import { PlayerRow, PlayerRows, playerMetaLine } from "./player-row";

export function BestAdds({ manager }: { manager: Manager }) {
  return (
    <Chapter reveal id="best-adds">
      <Label heading>Best Adds</Label>
      <PlayerRows empty="No adds yet.">
        {manager.best_adds.map((add) => (
          <PlayerRow
            key={add.player_id}
            player={add}
            meta={playerMetaLine(add, `Added week ${add.week}`, count(add.games, "game", "games"))}
            points={add.points}
            under={`${oneDecimal(add.projection)} proj`}
          />
        ))}
      </PlayerRows>
    </Chapter>
  );
}
