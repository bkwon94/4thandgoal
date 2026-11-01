/**
 * The points line of a manager page: the team's points per week against the league median, one dot per week, and a legend.
 * It is an inline SVG on a fixed viewBox, so it scales to the column width at each tier and paints in the theme tokens.
 */
"use client";

import { motion, type Variants } from "framer-motion";
import { type ReactNode, useId } from "react";
import { VIEW_MARGIN } from "@/components/parts/reveal";
import { count } from "@/lib/format/format";
import { useMotionOff } from "@/hooks/use-motion-off";
import { DURATION, EASE_OUT, INSTANT } from "@/lib/motion";
import { cn } from "@/lib/utils";
import type { SeasonWeek } from "@/lib/manager-types";

/* The drawing box. The SVG keeps this aspect ratio and scales to the column width. */
const WIDTH = 600;
const HEIGHT = 160;
/* The inset keeps the dots at the ends and the top and bottom inside the box. */
const PAD_X = 8;
const PAD_Y = 10;
/* The stroke of the draw mask, in viewBox units. It is wider than the team line at every tier, so the mask covers the line whole. */
const MASK_STROKE = 6;

/* The short summary a screen reader reads in place of the dots. */
function summary(weeks: SeasonWeek[]): string {
  const wins = weeks.filter((week) => week.won === true).length;
  const losses = weeks.filter((week) => week.won === false).length;
  const above = weeks.filter((week) => week.points > week.median).length;
  return (
    `Weeks ${weeks[0].week} to ${weeks.at(-1)!.week}: ${count(wins, "win", "wins")}, ${count(losses, "loss", "losses")}. ` +
    `Above the median in ${above} of ${weeks.length}.`
  );
}

/* The path through the points. One path with a stable d, so the draw motion animates its length. */
function pathOf(points: [number, number][]): string {
  return points.map(([x, y], i) => `${i === 0 ? "M" : "L"}${x.toFixed(1)} ${y.toFixed(1)}`).join(" ");
}

/* The team line draws from week 1 to now by its path length, over the reveal timing. With motion off it is whole at once. */
function drawOf(off: boolean): Variants {
  return {
    start: { pathLength: 0 },
    drawn: { pathLength: 1, transition: off ? INSTANT : { duration: DURATION.reveal, ease: EASE_OUT } },
  };
}

/* A dot fades in as the line reaches it. The delays spread the dots across the span of the draw, in week order. */
function dotOf(off: boolean, i: number, total: number): Variants {
  const delay = total === 1 ? 0 : (i * DURATION.reveal) / (total - 1);
  return {
    start: { opacity: 0 },
    drawn: { opacity: 1, transition: off ? INSTANT : { duration: DURATION.dot, ease: EASE_OUT, delay } },
  };
}

/* One sample of the legend: a tiny inline SVG in the classes of the chart, so it paints the same in both themes.
   The samples are decorative, because the word next to each one names it. */
function Sample({ children }: { children: ReactNode }) {
  return (
    <svg aria-hidden viewBox="0 0 16 10" className="block h-sp-3 w-sp-5 flex-none overflow-visible">
      {children}
    </svg>
  );
}

/* The legend under the chart: one quiet row that wraps on a phone. Each key is a sample of the mark and its word. */
function Legend() {
  const keys = [
    {
      label: "Points",
      sample: <line x1={0} y1={5} x2={16} y2={5} strokeWidth={1.5} className="stroke-ink" />,
    },
    {
      label: "League Median",
      sample: <line x1={0} y1={5} x2={16} y2={5} strokeWidth={1} strokeDasharray="4 3" className="stroke-mute" />,
    },
    { label: "Win", sample: <circle cx={8} cy={5} r={4} strokeWidth={1.5} className="fill-ink stroke-ink" /> },
    { label: "Loss", sample: <circle cx={8} cy={5} r={4} strokeWidth={1.5} className="fill-wht stroke-ink" /> },
  ];
  return (
    <ul aria-label="Legend" className="m-0 mt-sp-2 flex list-none flex-wrap gap-x-sp-4 gap-y-sp-1 p-0 text-meta text-mute">
      {keys.map(({ label, sample }) => (
        <li key={label} className="flex items-center gap-sp-1">
          <Sample>{sample}</Sample>
          {label}
        </li>
      ))}
    </ul>
  );
}

export function PointsLine({ weeks }: { weeks: SeasonWeek[] }) {
  const titleId = useId();
  const descId = useId();
  const maskId = useId();
  const off = useMotionOff();
  if (weeks.length === 0) return null;

  // One scale for both lines, so the team line and the median line read against each other.
  const values = weeks.flatMap((week) => [week.points, week.median]);
  const low = Math.min(...values);
  const high = Math.max(...values);
  const x = (i: number) => (weeks.length === 1 ? WIDTH / 2 : PAD_X + (i * (WIDTH - 2 * PAD_X)) / (weeks.length - 1));
  const y = (v: number) => (high === low ? HEIGHT / 2 : PAD_Y + ((high - v) * (HEIGHT - 2 * PAD_Y)) / (high - low));
  const team = weeks.map((week, i): [number, number] => [x(i), y(week.points)]);
  const median = weeks.map((week, i): [number, number] => [x(i), y(week.median)]);
  const first = weeks[0].week;
  const last = weeks.at(-1)!.week;

  // The draw plays once when the chart enters the viewport, as the reveal of the chapter does.
  // With motion off, or with no IntersectionObserver, the line goes to its final state on mount and never waits.
  const watch = !off && typeof IntersectionObserver !== "undefined";
  const play = watch ? { whileInView: "drawn", viewport: { once: true, margin: VIEW_MARGIN } } : { animate: "drawn" };

  return (
    <div>
      {/* The title names the line and the desc sums it up, so the dots carry no text each.
          The SVG holds the start state and the trigger, and the team line and the dots follow it by their variants. */}
      <motion.svg
        initial="start"
        {...play}
        role="img"
        aria-labelledby={titleId}
        aria-describedby={descId}
        viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
        className="block h-auto w-full overflow-visible"
      >
        <title id={titleId}>Points per week against the league median</title>
        <desc id={descId}>{summary(weeks)}</desc>
        {/* The strokes keep their width at every tier, so both lines stay thin as the SVG scales. */}
        <path
          d={pathOf(median)}
          fill="none"
          strokeWidth={1}
          strokeDasharray="4 3"
          vectorEffect="non-scaling-stroke"
          className="stroke-mute"
        />
        {/* The median line shows at once. The team line draws through a mask that grows by its path length.
            The mask path has no non-scaling stroke, because the browser scales the dash of a non-scaling stroke to the screen,
            and the draw then stops short of the last week on a wide column. data-draw lets globals.css show the line whole with no script. */}
        <mask id={maskId} maskUnits="userSpaceOnUse">
          <motion.path data-draw variants={drawOf(off)} d={pathOf(team)} fill="none" stroke="white" strokeWidth={MASK_STROKE} />
        </mask>
        <path
          d={pathOf(team)}
          mask={`url(#${maskId})`}
          fill="none"
          strokeWidth={1.5}
          vectorEffect="non-scaling-stroke"
          className="stroke-ink"
        />
        {/* A win is filled and a loss is hollow. A week with no result, a bye or a tie, is a small mute ring.
            The hollow dots fill with the page color, so the line does not show through them.
            The data-reveal rule in globals.css shows the dots with reduced motion or with no script. */}
        {weeks.map((week, i) => {
          const result = week.won === null ? "none" : week.won ? "win" : "loss";
          return (
            <motion.circle
              key={week.week}
              data-reveal
              variants={dotOf(off, i, weeks.length)}
              data-result={result}
              cx={team[i][0]}
              cy={team[i][1]}
              r={result === "none" ? 3 : 5}
              strokeWidth={1.5}
              vectorEffect="non-scaling-stroke"
              className={cn(
                result === "win" && "fill-ink stroke-ink",
                result === "loss" && "fill-wht stroke-ink",
                result === "none" && "fill-wht stroke-mute",
              )}
            />
          );
        })}
      </motion.svg>
      {/* The first and the last week are the only axis labels. The desc already names them, so a screen reader skips them. */}
      <div aria-hidden className="mt-sp-1 flex justify-between text-meta text-mute tabular-nums">
        <span>{`Week ${first}`}</span>
        {last !== first && <span>{`Week ${last}`}</span>}
      </div>
      <Legend />
    </div>
  );
}
