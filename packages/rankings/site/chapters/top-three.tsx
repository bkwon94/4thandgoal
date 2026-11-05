/**
 * The row of the Power Rankings chapter of the home page: the top three teams of the last week, and the biggest mover.
 * The home section of the app wraps it in the shared home row, so every row of the home page looks the same.
 */
import { biggestMover } from "../format/rankings";
import type { RankingsWeek } from "../schema/rankings-types";
import { Movement } from "./power-rankings";

export function TopThree({ week }: { week: RankingsWeek }) {
  const mover = biggestMover(week);
  return (
    <>
      <b className="mb-sp-1 block text-lead leading-tight group-hover:text-accent-ink">Top Three</b>
      <ol className="m-0 mb-sp-1 list-none p-0">
        {week.rows.slice(0, 3).map((row) => (
          <li key={row.roster_id} className="text-meta text-ink-2 tabular-nums">
            <span className="mr-sp-1 text-mute">{row.rank}</span>
            {row.name}
          </li>
        ))}
      </ol>
      {mover && (
        <span className="block text-meta text-mute tabular-nums">
          Biggest mover: <Movement movement={mover.movement} /> {mover.name}
        </span>
      )}
      <span className="block text-meta text-mute">See all twelve teams.</span>
    </>
  );
}
