/**
 * The hero of a manager page: the avatar, the team name, the owner, the record, and the standing, then the grade letter
 * as the big number with the grade text beside it, the three tiles Playoff, Bye, and Seed, and a W or L chip for each week.
 */
import { Avatar } from "@cpc/league/avatar";
import { Hero } from "@cpc/design/parts/hero";
import { Rise } from "@cpc/design/parts/rise";
import { Tile } from "@cpc/design/parts/tile";
import { ordinal, record } from "@cpc/design/format/format";
import { cn } from "@cpc/design/lib/utils";
import type { Manager, SeasonWeek } from "../schema/manager-types";
import { GradeMark, GradePopover } from "./grade-popover";
import { OddsCount } from "./odds-count";
import { stableId } from "@cpc/design/lib/stable-id";

/* A change in words. Positive is up, so the odds change reads up or down. */
function changeWords(change: number): string {
  if (change === 0) return "no change";
  return change > 0 ? `up ${change}` : `down ${Math.abs(change)}`;
}

/* The small caps line of the hero, such as the "GRADE" label. Each text line of a hero sits on a plate, so the grid
   and the glow never sit under a letter and axe can read the contrast (ticket 04). */
const HERO_CAPS = "plate w-fit font-mono text-meta leading-tight font-bold tracking-wide text-accent-text uppercase";

/* The chip of one week. A win takes the brand fill and a loss the raised fill of the hero. A bye or a tie has no
   result, so it shows a dash. Each chip has its own fill, so it needs no plate. The week number sits under the chip. */
function WeekChip({ week }: { week: SeasonWeek }) {
  const letter = week.won === null ? "—" : week.won ? "W" : "L";
  return (
    <li className="flex flex-col items-center gap-sp-1">
      <span
        data-result={week.won === null ? "none" : week.won ? "win" : "loss"}
        {...stableId("result", week.week)}
        className={cn(
          "flex size-avatar items-center justify-center rounded-sm font-mono text-meta leading-none font-bold text-on-dark",
          week.won ? "bg-accent" : "border border-rule-dark bg-chip-dark",
        )}
      >
        {letter}
      </span>
      <span className="plate font-mono text-meta leading-none text-on-dark-2 tabular-nums">{week.week}</span>
    </li>
  );
}

export function ManagerHero({ manager, avatar, teams }: { manager: Manager; avatar: string; teams: number }) {
  const { grade, odds } = manager;
  return (
    <Hero label={manager.team.name}>
      <Rise step={0} className="flex items-center gap-sp-4">
        {/* The team name sits next to the avatar, so the image is decorative. */}
        <Avatar src={avatar} size="headshot" />
        <div className="min-w-0">
          {/* The name wraps and never cuts off. The balance splits a long name into even lines. */}
          <h1 className="plate m-0 w-fit text-score leading-tight font-bold text-balance break-words tablet:text-headline">
            {manager.team.name}
          </h1>
          <div className="plate mt-sp-2 w-fit text-meta leading-tight text-on-dark-2">{manager.team.owner}</div>
          <div className="plate mt-sp-1 w-fit font-mono text-body leading-tight text-on-dark tabular-nums">
            {`${record(manager.wins, manager.losses)} · ${ordinal(manager.standing)} of ${teams}`}
          </div>
        </div>
      </Rise>
      <Rise step={1} className="mt-sp-6">
        <div className={cn(HERO_CAPS, "flex items-center")}>
          Grade
          {grade && <GradeMark />}
        </div>
        <div className="mt-sp-2 flex flex-wrap items-center gap-x-sp-5 gap-y-sp-2">
          {/* The letter opens the grade popover, which says what each part of the grade ranks.
              The leading stays at 1, so the plate of the letter holds its whole glyph box and axe can read it. */}
          <div className="font-mono text-hero leading-none font-bold">
            {grade ? (
              <GradePopover grade={grade} teams={teams} />
            ) : (
              <span aria-label="No grade" className="plate">
                —
              </span>
            )}
          </div>
          {grade && (
            <div className="plate max-w-measure min-w-0 flex-1 text-lead leading-body text-on-dark-2">{grade.read}</div>
          )}
        </div>
      </Rise>
      <Rise step={2} className="mt-sp-6">
        <div role="group" aria-label="Hero Numbers" className="grid grid-cols-3 gap-sp-2">
          <Tile
            tone="hero"
            label="Playoff"
            value={odds ? <OddsCount value={odds.playoff} /> : "—"}
            note={odds && manager.odds_change !== null ? changeWords(manager.odds_change) : undefined}
            stable="odds-playoff"
          />
          <Tile tone="hero" label="Bye" value={odds ? `${odds.bye}%` : "—"} stable="odds-bye" />
          <Tile tone="hero" label="Seed" value={odds && odds.seed !== null ? ordinal(odds.seed) : "—"} stable="odds-seed" />
        </div>
      </Rise>
      {manager.weeks.length > 0 && (
        <Rise step={3} className="mt-sp-5">
          <ol aria-label="Results By Week" className="m-0 flex list-none flex-wrap gap-sp-2 p-0">
            {manager.weeks.map((week) => (
              <WeekChip key={week.week} week={week} />
            ))}
          </ol>
        </Rise>
      )}
    </Hero>
  );
}
