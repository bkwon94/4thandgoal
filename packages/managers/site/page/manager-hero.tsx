/**
 * The hero of a manager page, in the hero slots: the record and the standing as the eyebrow, the team name, the owner,
 * then the avatar, the grade letter with the grade text, and a W or L chip for each week, then the tiles Playoff, Bye, and Seed.
 */
import { Avatar } from "@cpc/league/avatar";
import { Hero } from "@cpc/design/parts/hero";
import type { HeroScene } from "@cpc/design/parts/scene-math";
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

/* The small caps line of the hero, such as the "GRADE" label. The glow stays low in the corner, off each
   text line of a hero, so a line needs no plate (ADR 0036). */
const HERO_CAPS =
  "w-fit font-mono text-meta leading-tight font-bold tracking-wide text-accent-text uppercase";

/* The chip of one week. A win takes the brand fill and a loss the raised fill of the hero. A bye or a tie has no
   result, so it shows a dash. Each chip has its own fill. The week number sits under the chip. */
function WeekChip({ week }: { week: SeasonWeek }) {
  const letter = week.won === null ? "—" : week.won ? "W" : "L";
  return (
    <li className="gap-sp-1 flex flex-col items-center">
      <span
        data-result={week.won === null ? "none" : week.won ? "win" : "loss"}
        {...stableId("result", week.week)}
        className={cn(
          "size-avatar text-meta text-on-dark flex items-center justify-center rounded-sm font-mono leading-none font-bold",
          week.won ? "bg-accent" : "border-rule-dark bg-chip-dark border",
        )}
      >
        {letter}
      </span>
      <span className="text-meta text-on-dark-2 font-mono leading-none tabular-nums">
        {week.week}
      </span>
    </li>
  );
}

export function ManagerHero({
  manager,
  avatar,
  teams,
  through,
  scene,
}: {
  manager: Manager;
  avatar: string;
  teams: number;
  // The last week of the build. The grade is from that week, so the hero says so beside the grade.
  through: number;
  // The scene of the weeks. The manager page passes it, because this hero is the first hero of the page.
  scene?: HeroScene;
}) {
  const { grade, odds } = manager;
  return (
    <Hero
      label={manager.team.name}
      scene={scene}
      eyebrow={`${record(manager.wins, manager.losses)} · ${ordinal(manager.standing)} of ${teams}`}
      title={manager.team.name}
      meta={manager.team.owner}
      feature={
        <Rise step={1} className="gap-sp-5 flex flex-col">
          <div className="gap-x-sp-5 gap-y-sp-4 flex flex-wrap items-center">
            {/* The team name is the title of the hero, so the image is decorative. */}
            <Avatar src={avatar} size="headshot" />
            <div className="min-w-0 flex-1">
              <div className={cn(HERO_CAPS, "flex items-center")}>
                Grade
                {grade && <GradeMark />}
                {/* The grade reads the build, not the live league, so it names its week. */}
                {grade && (
                  <span className="ml-sp-3 text-on-dark-2 font-normal tracking-normal normal-case">
                    after week {through}
                  </span>
                )}
              </div>
              <div className="mt-sp-2 gap-x-sp-5 gap-y-sp-2 flex flex-wrap items-center">
                {/* The letter opens the grade popover, which says what each part of the grade ranks.
                    The leading stays at 1, so the letter keeps its own line box. */}
                <div className="text-hero font-mono leading-none font-bold">
                  {grade ? (
                    <GradePopover grade={grade} teams={teams} />
                  ) : (
                    <span aria-label="No grade">—</span>
                  )}
                </div>
                {grade && (
                  <div className="max-w-measure text-lead leading-body text-on-dark-2 min-w-0 flex-1">
                    {grade.read}
                  </div>
                )}
              </div>
            </div>
          </div>
          {manager.weeks.length > 0 && (
            <ol aria-label="Results By Week" className="gap-sp-2 m-0 flex list-none flex-wrap p-0">
              {manager.weeks.map((week) => (
                <WeekChip key={week.week} week={week} />
              ))}
            </ol>
          )}
        </Rise>
      }
      stats={
        <Rise step={2} className="tablet:w-auto w-full">
          <div role="group" aria-label="Hero Numbers" className="gap-sp-2 grid grid-cols-3">
            <Tile
              tone="hero"
              label="Playoff"
              value={odds ? <OddsCount value={odds.playoff} /> : "—"}
              note={
                odds && manager.odds_change !== null ? changeWords(manager.odds_change) : undefined
              }
              stable="odds-playoff"
            />
            <Tile tone="hero" label="Bye" value={odds ? `${odds.bye}%` : "—"} stable="odds-bye" />
            <Tile
              tone="hero"
              label="Seed"
              value={odds && odds.seed !== null ? ordinal(odds.seed) : "—"}
              stable="odds-seed"
            />
          </div>
        </Rise>
      }
    />
  );
}
