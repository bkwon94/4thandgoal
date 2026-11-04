/**
 * The Best Adds chapter of a manager page: up to three adds by points scored for the team since the add.
 * Each row shows the points and, under them, the projection over the same weeks.
 */
import { count, oneDecimal } from "@cpc/design/format/format";
import type { Manager } from "@/lib/manager-types";
import { PlayerChapter } from "./player-chapter";
import { playerMetaLine } from "./player-row";

export function BestAdds({ manager }: { manager: Manager }) {
  const items = manager.best_adds.map((add) => ({
    player: add,
    meta: playerMetaLine(add, `Added week ${add.week}`, count(add.games, "game", "games")),
    points: add.points,
    under: `${oneDecimal(add.projection)} proj`,
  }));
  return <PlayerChapter id="best-adds" title="Best Adds" empty="No adds yet." items={items} />;
}
