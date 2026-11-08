/**
 * The tile: a small card with one number, its label above it, and an optional note under it. The page tone sits on a card or the page, and the hero tone sits on the raised surface of the hero.
 * A Trend tile adds a small chart of the same number from week 1 to the page week, after the Lime Metrics method.
 */
import { useId, type ReactNode } from "react";
import { STABLE_ID } from "../lib/stable-id";
import { cn } from "../lib/utils";

/* One point of a trend: the week and its number. */
export type TrendPoint = { week: number; value: number };

/* The trend of a Trend tile. Bars light the bar of the page week. A step is a stepped area with the page week marked.
   Dots mark each week with a count above zero, for a rare count such as trades.
   The text is one sentence of the trend, so the chart is not the only source for a screen reader. */
export type TileTrend = { points: TrendPoint[]; week: number; kind: "bars" | "step" | "dots"; text: string };

type TileProps = {
  label: string;
  // The one number of the tile, such as "151.32" or "+18.4". The page formats it.
  value: ReactNode;
  // A short line under the number, such as the team that scored it.
  note?: ReactNode;
  // The chart under the note. A tile with no trend has no chart.
  trend?: TileTrend;
  tone?: "page" | "hero";
  // The stable id of the tile, from the data that it renders, so the egg hunt can name it.
  stable?: string;
  className?: string;
};

/* The colors of each tone. Each text role is a pair that brand-contrast.test.mjs holds at 4.5 to 1 on its surface. */
const TONES = {
  page: { box: "bg-raised text-ink", label: "text-mute", note: "text-ink-2" },
  hero: { box: "bg-chip-dark text-on-dark", label: "text-on-dark-muted", note: "text-on-dark-2" },
} as const;

/* The chart box in user units. The SVG stretches to the width of the tile, so the units set only the proportions. */
const CHART_W = 100;
const CHART_H = 32;
/* The gap between two bars as a part of one bar, as the method spaces them: about a quarter of the bar width. */
const BAR_GAP = 0.27;

/* Bars rise from zero, so the height of each bar reads as its number. The bar of the page week takes the accent. */
function Bars({ points, week }: { points: TrendPoint[]; week: number }) {
  const high = Math.max(...points.map((point) => point.value), 0);
  const width = CHART_W / (points.length + (points.length - 1) * BAR_GAP);
  return points.map((point, index) => {
    const height = high === 0 ? 0 : (point.value / high) * CHART_H;
    const lit = point.week === week;
    return (
      <rect
        key={point.week}
        data-week={point.week}
        data-value={point.value}
        data-lit={lit || undefined}
        x={index * width * (1 + BAR_GAP)}
        y={CHART_H - height}
        width={width}
        height={height}
        rx={1.5}
        // The quiet bars take the muted text color at low strength, so the lit bar is the one loud mark.
        className={lit ? "fill-accent" : "fill-current opacity-35"}
      />
    );
  });
}

/* A stepped line with an area that fades under it. Each week holds one flat step, and the step of the page week ends
   in an accent dot. The scale runs from the low to the high of the series, so a small change still shows. */
function Step({ points, week }: { points: TrendPoint[]; week: number }) {
  const fadeId = useId();
  const values = points.map((point) => point.value);
  const low = Math.min(...values);
  const high = Math.max(...values);
  // A pad of 2 units keeps the line off the top and the bottom edge.
  const y = (value: number) => (high === low ? CHART_H / 2 : 2 + ((high - value) * (CHART_H - 4)) / (high - low));
  const step = CHART_W / points.length;
  const line = points
    .map((point, index) => `${index === 0 ? `M0 ${y(point.value)}` : `V${y(point.value)}`} H${(index + 1) * step}`)
    .join(" ");
  const markIndex = points.findIndex((point) => point.week === week);
  return (
    <>
      <defs>
        <linearGradient id={fadeId} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="currentColor" stopOpacity={0.4} />
          <stop offset="100%" stopColor="currentColor" stopOpacity={0} />
        </linearGradient>
      </defs>
      <path data-step d={`${line} V${CHART_H} H0 Z`} fill={`url(#${fadeId})`} />
      <path d={line} fill="none" strokeWidth={1.5} strokeLinejoin="round" vectorEffect="non-scaling-stroke" className="stroke-ink" />
      {markIndex >= 0 && (
        <line
          x1={markIndex * step}
          x2={(markIndex + 1) * step}
          y1={y(points[markIndex].value)}
          y2={y(points[markIndex].value)}
          strokeWidth={3}
          strokeLinecap="round"
          vectorEffect="non-scaling-stroke"
          className="stroke-accent"
        />
      )}
    </>
  );
}

/* A thin base line with one dot for each week that has a count above zero. A rare count reads best as marks on a
   line, since a bar of 1 among zeros looks like noise. Each week holds one slot, as the bars do, and a dot of the
   page week takes the accent. */
function Dots({ points, week }: { points: TrendPoint[]; week: number }) {
  const slot = CHART_W / points.length;
  return (
    <>
      <line x1={0} x2={CHART_W} y1={CHART_H / 2} y2={CHART_H / 2} strokeWidth={1} vectorEffect="non-scaling-stroke" className="stroke-current opacity-35" />
      {points
        .map((point, index) => ({ point, x: (index + 0.5) * slot }))
        .filter(({ point }) => point.value > 0)
        .map(({ point, x }) => {
          const lit = point.week === week;
          return (
            // A zero-length line with a round cap draws a true circle, though the SVG stretches to the tile width.
            <line
              key={point.week}
              data-week={point.week}
              data-value={point.value}
              data-lit={lit || undefined}
              x1={x}
              x2={x}
              y1={CHART_H / 2}
              y2={CHART_H / 2}
              strokeWidth={8}
              strokeLinecap="round"
              vectorEffect="non-scaling-stroke"
              className={lit ? "stroke-accent" : "stroke-ink"}
            />
          );
        })}
    </>
  );
}

/* The chart of a Trend tile. The SVG is one image named by the text of the trend, so a screen reader reads one sentence. */
function TrendChart({ trend }: { trend: TileTrend }) {
  if (trend.points.length === 0) return null;
  return (
    <svg
      role="img"
      aria-label={trend.text}
      viewBox={`0 0 ${CHART_W} ${CHART_H}`}
      preserveAspectRatio="none"
      className="mt-sp-2 block h-8 w-full overflow-visible text-mute"
    >
      {trend.kind === "bars" && <Bars points={trend.points} week={trend.week} />}
      {trend.kind === "step" && <Step points={trend.points} week={trend.week} />}
      {trend.kind === "dots" && <Dots points={trend.points} week={trend.week} />}
    </svg>
  );
}

export function Tile({ label, value, note, trend, tone = "page", stable, className }: TileProps) {
  const colors = TONES[tone];
  return (
    <div className={cn("rounded-tile p-sp-4", colors.box, className)} {...(stable ? { [STABLE_ID]: stable } : {})}>
      {/* The label and the number are mono, so the numbers of a row of tiles line up. */}
      <div className={cn("font-mono text-meta leading-tight font-bold tracking-caps uppercase", colors.label)}>{label}</div>
      <div className="mt-sp-1 font-mono text-stat leading-stat font-bold tabular-nums">{value}</div>
      {note !== undefined && <div className={cn("mt-sp-1 text-meta leading-tight", colors.note)}>{note}</div>}
      {trend && <TrendChart trend={trend} />}
    </div>
  );
}
