/**
 * The week strip of the replay: two labeled groups, the regular season and the playoffs, with a gap between them.
 * The week on the stage takes the brand red, a played week stays bright, and a week still to come is dim.
 */
import { cn } from "@cpc/design/lib/utils";

function Group({
  label,
  weeks,
  current,
  playoffs,
}: {
  label: string;
  weeks: number[];
  current: number | null;
  playoffs?: boolean;
}) {
  return (
    <div className="gap-sp-1 flex flex-col">
      <span className="text-meta tracking-caps text-on-dark-2 font-mono font-bold uppercase">
        {label}
      </span>
      <ol aria-label={label} className="gap-sp-1 m-0 flex list-none p-0">
        {weeks.map((week) => {
          const now = week === current;
          const played = current !== null && week < current;
          return (
            <li
              key={week}
              aria-current={now ? "step" : undefined}
              className={cn(
                "size-sp-6 rounded-report text-meta flex items-center justify-center font-mono font-bold tabular-nums transition-colors duration-300",
                playoffs ? "border-accent border" : "border-rule-dark border",
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

export function WeekStrip({
  regular,
  playoffs,
  current,
}: {
  regular: number[];
  playoffs: number[];
  current: number | null;
}) {
  return (
    <div className="gap-x-sp-6 gap-y-sp-2 flex flex-wrap items-end">
      <Group label="Regular season" weeks={regular} current={current} />
      <Group label="Playoffs" weeks={playoffs} current={current} playoffs />
    </div>
  );
}
