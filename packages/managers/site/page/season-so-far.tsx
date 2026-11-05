/**
 * The Season So Far chapter of a manager page: the points line against the dashed median line, the season tiles, and the bench points.
 * The three groups stack with air between them. A filled dot of the line marks a win.
 */
import { Chapter } from "@cpc/design/parts/chapter";
import { Label } from "@cpc/design/parts/label";
import { Tile } from "@cpc/design/parts/tile";
import { num } from "@cpc/design/format/format";
import type { Bench, Manager, SeasonWeek } from "../schema/manager-types";
import { mediansOf } from "./medians";
import { PointsLine } from "./points-line";

/* The quiet label style of the bench points. */
const QUIET_LABEL = "text-meta leading-tight font-semibold tracking-caps text-mute uppercase";

/* The bench points: the season total as the emphasis, and one quiet sentence that says what the total means. */
function BenchPoints({ bench }: { bench: Bench | null }) {
  if (bench === null) return <div className="m-0 text-meta text-mute">No bench data yet.</div>;
  const { worst } = bench;
  return (
    <div>
      <div className={QUIET_LABEL}>Points Left On The Bench</div>
      <div className="mt-sp-2 text-score leading-none font-extrabold text-ink tabular-nums">
        <span>{num(bench.total)}</span>
        <span className="text-meta font-semibold text-mute">{" points"}</span>
      </div>
      <p className="m-0 mt-sp-1 text-lead leading-body text-mute">
        {worst
          ? `Your best lineup would have scored ${num(bench.total)} more points this season. ` +
            `Worst in week ${worst.week}: ${num(worst.points)} points, ${worst.name} sat.`
          : "Your best lineup matched your starters every week."}
      </p>
    </div>
  );
}

/* The week of the most points. A tie goes to the earlier week. */
function highOf(weeks: SeasonWeek[]): SeasonWeek {
  return weeks.reduce((peak, week) => (week.points > peak.points ? week : peak));
}

/* The three season tiles: the points for, the record against the median, and the high week.
   A week above the median is a win against it, and any other week a loss.
   A league with no median game has no record against the median, so it shows two tiles. */
function SeasonNumbers({ pointsFor, weeks }: { pointsFor: number; weeks: SeasonWeek[] }) {
  if (weeks.length === 0) return null;
  const high = highOf(weeks);
  const medians = mediansOf(weeks);
  const above = medians ? weeks.filter((week, i) => week.points > medians[i]).length : 0;
  return (
    <div role="group" aria-label="Season Numbers" className="grid grid-cols-2 gap-sp-2 tablet:grid-cols-3">
      <Tile label="Points For" value={num(pointsFor)} />
      {medians && <Tile label="Vs Median" value={`${above}-${weeks.length - above}`} />}
      <Tile label="High Week" value={num(high.points)} note={`week ${high.week}`} />
    </div>
  );
}

export function SeasonSoFar({ manager }: { manager: Manager }) {
  return (
    <Chapter reveal id="season">
      {/* The meta size keeps the heading over the text floor of 11px on a phone. */}
      <Label heading className="text-meta">Season So Far</Label>
      <PointsLine weeks={manager.weeks} />
      {/* The space between the groups sets them apart, so the chapter reads as three groups. */}
      <div className="mt-sp-6">
        <SeasonNumbers pointsFor={manager.points_for} weeks={manager.weeks} />
      </div>
      <div className="mt-sp-6">
        <BenchPoints bench={manager.bench} />
      </div>
    </Chapter>
  );
}
