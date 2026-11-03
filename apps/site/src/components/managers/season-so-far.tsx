/**
 * The Season So Far chapter of a manager page: the points line, the bench points, and the four season stats.
 * The three groups stack with air between them. Each line has one quiet label and one emphasis.
 */
import type { ReactNode } from "react";
import { Chapter } from "@/components/parts/chapter";
import { Label } from "@/components/parts/label";
import { num } from "@/lib/format/format";
import type { Bench, Manager, SeasonWeek } from "@/lib/manager-types";
import { PointsLine } from "./points-line";

/* The quiet label style of the page, as the hero's season numbers use it. */
const QUIET_LABEL = "text-label leading-tight font-semibold tracking-caps text-mute uppercase";

/* The bench points: the season total as the emphasis, and one quiet sentence that says what the total means. */
function BenchPoints({ bench }: { bench: Bench | null }) {
  if (bench === null) return <p className="m-0 text-meta text-mute">No bench data yet.</p>;
  const { worst } = bench;
  return (
    <div>
      <div className={QUIET_LABEL}>Points Left On The Bench</div>
      <div className="mt-sp-2 text-score leading-none font-extrabold text-ink tabular-nums">
        <span>{num(bench.total)}</span>
        <span className="text-meta font-semibold text-mute">{" points"}</span>
      </div>
      <p className="m-0 mt-sp-1 text-meta text-mute">
        {worst
          ? `Your best lineup would have scored ${num(bench.total)} more points this season. ` +
            `Worst in week ${worst.week}: ${num(worst.points)} points, ${worst.name} sat.`
          : "Your best lineup matched your starters every week."}
      </p>
    </div>
  );
}

/* The run of one result at the end of the season, such as "W3" or "L2". A week with no result ends the run,
   so a last week with no result gives no run and the dash. */
function streakOf(weeks: SeasonWeek[]): string {
  const last = weeks.at(-1)?.won ?? null;
  if (last === null) return "—";
  let run = 0;
  for (let i = weeks.length - 1; i >= 0 && weeks[i].won === last; i--) run++;
  return `${last ? "W" : "L"}${run}`;
}

/* The week of the most points, or of the fewest. A tie goes to the earlier week. */
function peakOf(weeks: SeasonWeek[], better: (a: number, b: number) => boolean): SeasonWeek {
  return weeks.reduce((peak, week) => (better(week.points, peak.points) ? week : peak));
}

/* One stat: one quiet label over it, the number as the one emphasis, and at most one quiet line under it. */
function Stat({ label, children, context }: { label: string; children: ReactNode; context?: string }) {
  return (
    <div className="min-w-0">
      <dt className={QUIET_LABEL}>{label}</dt>
      <dd className="m-0 mt-sp-2 text-score leading-none font-extrabold text-ink tabular-nums">{children}</dd>
      {context && <dd className="m-0 mt-sp-1 text-meta text-mute">{context}</dd>}
    </div>
  );
}

/* The four season stats from the points per week. A week above the median is a win against it, and any other week a loss. */
function SeasonNumbers({ weeks }: { weeks: SeasonWeek[] }) {
  if (weeks.length === 0) return null;
  const high = peakOf(weeks, (a, b) => a > b);
  const low = peakOf(weeks, (a, b) => a < b);
  const above = weeks.filter((week) => week.points > week.median).length;
  return (
    // A phone fits two stats per row whole. Four per row breaks the long labels mid-word, which reads as a defect.
    <dl role="group" aria-label="Season Numbers" className="m-0 grid grid-cols-2 gap-x-sp-2 gap-y-sp-4 tablet:grid-cols-4">
      <Stat label="Season High" context={`week ${high.week}`}>
        {num(high.points)}
      </Stat>
      <Stat label="Season Low" context={`week ${low.week}`}>
        {num(low.points)}
      </Stat>
      <Stat label="Streak">{streakOf(weeks)}</Stat>
      <Stat label="Against The Median" context="wins above the median">
        {`${above}-${weeks.length - above}`}
      </Stat>
    </dl>
  );
}

export function SeasonSoFar({ manager }: { manager: Manager }) {
  return (
    <Chapter reveal id="season">
      <Label heading>Season So Far</Label>
      <PointsLine weeks={manager.weeks} />
      {/* The space between the groups sets them apart, so the chapter reads as three groups. */}
      <div className="mt-sp-6">
        <BenchPoints bench={manager.bench} />
      </div>
      <div className="mt-sp-6">
        <SeasonNumbers weeks={manager.weeks} />
      </div>
    </Chapter>
  );
}
