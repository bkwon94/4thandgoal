/**
 * The median game: three KPI cells, a bar chart of every score against the dashed median line, and the blurb.
 * The bar widths and the line position come from the JSON as percents of the top score.
 */
import { gap, num } from "@/lib/format/format";
import { cn } from "@/lib/utils";
import type { Median } from "@/lib/week-types";
import { Blurb } from "@/components/parts/blurb";
import { Chapter } from "@/components/parts/chapter";
import { Label } from "@/components/parts/label";

function Kpi({ value, label }: { value: string; label: string }) {
  return (
    <div className="rounded-card bg-gry px-sp-2 py-sp-3 text-center">
      <div className="text-stat leading-stat font-black tabular-nums">{value}</div>
      <div className="mt-sp-1 text-label leading-tight tracking-caps text-mute uppercase">{label}</div>
    </div>
  );
}

/* A week with no median game has no median chapter. */
export function MedianGame({ median, blurb }: { median: Median | null; blurb?: string }) {
  if (median === null) return null;
  return (
    <Chapter reveal id="median">
      <Label heading>The Median Game</Label>
      <div className="grid grid-cols-[1fr_1fr_1fr] gap-sp-2">
        <Kpi value={num(median.value)} label="Median" />
        <Kpi value={gap(median.above.gap)} label={`${median.above.team.name}, closest win`} />
        <Kpi value={gap(median.below.gap)} label={`${median.below.team.name}, closest miss`} />
      </div>
      <div className="relative mt-sp-3">
        {/* The plot box matches the bar column, so the median line shares the bars' percent scale. */}
        <div className="pointer-events-none absolute inset-y-0 left-0 right-[calc(var(--spacing-val-col)+var(--spacing-sp-2))]">
          <div
            className="absolute inset-y-0 border-l-2 border-dashed border-ink"
            style={{ left: `${median.line_pct}%` }}
            title={`Median ${num(median.value)}`}
          />
        </div>
        {median.bars.map((bar) => (
          <div
            key={bar.team.roster_id}
            // From the tablet tier a taller bar and more space between bars keep each bar readable across the width.
            className="grid grid-cols-[1fr_var(--spacing-val-col)] items-end gap-sp-2 py-sp-1 tablet:py-sp-2 text-meta tabular-nums"
          >
            <div>
              <div className="mb-sp-0 text-meta leading-tight text-ink-2">{bar.team.name}</div>
              <div
                className={cn("h-median-bar tablet:h-median-bar-wide rounded-sm", bar.above ? "bg-red" : "bg-bar-off")}
                style={{ width: `${bar.pct}%` }}
              />
            </div>
            <b className="text-right leading-(--spacing-median-bar) tablet:leading-(--spacing-median-bar-wide)">{num(bar.score)}</b>
          </div>
        ))}
      </div>
      <p className="mx-0 mt-sp-2 mb-0 text-meta text-mute">{`Dashed line: median ${num(median.value)}.`}</p>
      {blurb && <Blurb className="mt-sp-3">{blurb}</Blurb>}
    </Chapter>
  );
}
