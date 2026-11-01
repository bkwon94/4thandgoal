/**
 * The Top Performers chapter of a manager page: up to five players by points scored while started for the team.
 * Each row shows the points total and, under it, the points per game started.
 */
import { Chapter } from "@/components/parts/chapter";
import { Label } from "@/components/parts/label";
import { count, oneDecimal } from "@/lib/format/format";
import type { Manager } from "@/lib/manager-types";
import { PlayerRow, PlayerRows, playerMetaLine } from "./player-row";

export function TopPerformers({ manager }: { manager: Manager }) {
  return (
    <Chapter reveal id="top-performers">
      <Label heading>Top Performers</Label>
      <PlayerRows empty="No starts yet.">
        {manager.top_performers.map((performer) => (
          <PlayerRow
            key={performer.player_id}
            player={performer}
            meta={playerMetaLine(performer, count(performer.games, "start", "starts"))}
            points={performer.points}
            under={`${oneDecimal(performer.per_game)} a game`}
          />
        ))}
      </PlayerRows>
    </Chapter>
  );
}
