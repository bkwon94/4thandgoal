/**
 * The median game: a bar for each team with its avatar, against the median line, then the blurb.
 * The bar widths and the line position come from the JSON as percents of the top score.
 */
import { num } from "@cpc/design/format/format";
import { cn } from "@cpc/design/lib/utils";
import { BarFill } from "@cpc/design/parts/bar-fill";
import { Card } from "@cpc/design/parts/card";
import type { AvatarMap, Median } from "../schema/week-types";
import { Avatar } from "@cpc/league/avatar";
import { avatarSrc } from "@cpc/league/images";
import { WeekChapter } from "../parts/week-chapter";

/* A week with no median game has no median chapter. */
export function MedianGame({ median, avatars, blurb }: { median: Median | null; avatars: AvatarMap; blurb?: string }) {
  if (median === null) return null;
  return (
    <WeekChapter id="median" title="The median game" note={`Line ${num(median.value)}`}>
      <Card>
        <ul aria-label="Scores against the median" className="m-0 flex list-none flex-col gap-sp-3 p-0">
          {median.bars.map((bar) => (
            // The name column is fixed, so every track starts at one place and the line falls at one place in each.
            <li
              key={bar.team.roster_id}
              className="grid grid-cols-[auto_minmax(0,6.5rem)_minmax(0,1fr)_auto] items-center gap-sp-2 tablet:grid-cols-[auto_minmax(0,12rem)_minmax(0,1fr)_auto]"
            >
              <Avatar src={avatarSrc(avatars, bar.team.roster_id)} />
              <span className="truncate text-meta leading-tight text-ink-2">{bar.team.name}</span>
              {/* The track and the line are a graphic. The word after the score says above or below for a screen reader. */}
              <span aria-hidden="true" className="relative h-sp-2 rounded-pill bg-raised">
                <BarFill
                  pct={bar.pct}
                  className={cn("absolute inset-y-0 left-0 rounded-pill", bar.above ? "bg-accent" : "bg-bar-off")}
                />
                <span
                  className="absolute -inset-y-sp-1 w-sp-0 bg-ink"
                  style={{ left: `${median.line_pct}%` }}
                />
              </span>
              <span className="text-right font-mono text-meta font-bold tabular-nums">
                {num(bar.score)}
                <span className="sr-only">{bar.above ? "Above" : "Below"}</span>
              </span>
            </li>
          ))}
        </ul>
      </Card>
      {blurb && <p className="m-0 max-w-measure text-lead leading-body text-ink-2">{blurb}</p>}
    </WeekChapter>
  );
}
