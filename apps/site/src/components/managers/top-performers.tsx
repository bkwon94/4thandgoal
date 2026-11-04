/**
 * The Top Performers chapter of a manager page: up to five players by points scored while started for the team.
 * Each row shows the points total and, under it, the points per game started.
 */
import { count, oneDecimal } from "@cpc/design/format/format";
import type { Manager } from "@/lib/manager-types";
import { PlayerChapter } from "./player-chapter";
import { playerMetaLine } from "./player-row";

export function TopPerformers({ manager }: { manager: Manager }) {
  const items = manager.top_performers.map((performer) => ({
    player: performer,
    meta: playerMetaLine(performer, count(performer.games, "start", "starts")),
    points: performer.points,
    under: `${oneDecimal(performer.per_game)} a game`,
  }));
  return <PlayerChapter id="top-performers" title="Top Performers" empty="No starts yet." items={items} />;
}
