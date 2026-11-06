/**
 * The week strip of the replay: two labeled groups, the regular season and the playoffs, with a gap between them.
 * The week on the stage takes the brand red, a played week stays bright, and a week still to come is dim.
 */
import { cn } from "@cpc/design/lib/utils";

function Group({ label, weeks, current, playoffs }: { label: string; weeks: number[]; current: number | null; playoffs?: boolean }) {
  return (
    <div className="flex flex-col gap-sp-1">
      <span className="font-mono text-meta font-bold tracking-caps text-on-dark-2 uppercase">{label}</span>
      <ol aria-label={label} className="m-0 flex list-none gap-sp-1 p-0">
        {weeks.map((week) => {
          const now = week === current;
          const played = current !== null && week < current;
          return (
            <li
              key={week}
              aria-current={now ? "step" : undefined}
              className={cn(
                "flex size-sp-6 items-center justify-center rounded-sm font-mono text-meta font-bold tabular-nums transition-colors duration-300",
                playoffs ? "border border-accent" : "border border-rule-dark",
                now ? "bg-accent text-white" : played ? "text-on-dark" : "text-on-dark-muted",
              )}
            >
              {week}
            </li>
          );
        })}
      </ol>
    </div>
  );
}

export function WeekStrip({ regular, playoffs, current }: { regular: number[]; playoffs: number[]; current: number | null }) {
  return (
    <div className="flex flex-wrap items-end gap-x-sp-6 gap-y-sp-2">
      <Group label="Regular season" weeks={regular} current={current} />
      <Group label="Playoffs" weeks={playoffs} current={current} playoffs />
    </div>
  );
}
