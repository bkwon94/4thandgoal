/**
 * The power rankings table: a light chapter with one row per team for the chosen week, in rank order, and a chip per week to choose it.
 * Each row shows the rank, the movement, the team, the record, the playoff odds, and the four component ranks.
 * Every component number is a rank, never a score.
 * The row button opens the blurb, and the chips choose the week. Both hold state, so this file is a client component.
 */
"use client";

import { motion } from "framer-motion";
import { useId, useState, type ReactNode } from "react";
import { Blurb } from "@/components/parts/blurb";
import { Chapter } from "@/components/parts/chapter";
import { Label } from "@/components/parts/label";
import { Reveal } from "@/components/parts/reveal";
import { Who } from "@/components/parts/who";
import { avatarSrc } from "@cpc/league/images";
import { record } from "@/lib/format/format";
import { useMotionOff } from "@/hooks/use-motion-off";
import { DURATION, EASE_OUT, INSTANT, stagger } from "@/lib/motion";
import type { Components, Odds, RankingsRow, RankingsWeek } from "@/lib/rankings-types";
import { managerHrefOrNull } from "@/lib/routes";
import { cn } from "@/lib/utils";
import type { AvatarMap } from "@/lib/week-types";
import { useSharedWeekChoice, useWeekChoice } from "./week-choice";

/* The order and the column names of the four component ranks. */
const COMPONENTS: { key: keyof Components; name: string }[] = [
  { key: "standing", name: "Stand" },
  { key: "form", name: "Form" },
  { key: "schedule_played", name: "Sched" },
  { key: "scoring", name: "Pts" },
];

/* The columns on a phone: rank, movement, team, record, playoff odds, and the chevron of the row control.
   The open row uses the same columns, so its component ranks and its blurb line up under the team.
   The team track is a plain 1fr, so its minimum is the longest word of the name. A name wraps at a space and never inside a word.
   The record takes the 40px rankings column, not the 44px standings column: "10-2" fits in 40px, and the 4px go to the team. */
const PHONE_COLS =
  "grid-cols-[var(--spacing-standings-rank)_var(--spacing-rankings-col)_1fr_var(--spacing-rankings-col)_var(--spacing-rankings-col)_var(--spacing-chevron)]";

/* The open row on a desktop: the phone tracks with the wide rank and the desktop column, so the blurb starts under the team.
   On a tablet the row keeps the phone tracks and the 8px gap, so the open row needs no change there. */
const OPEN_WIDE_COLS =
  "desktop:grid-cols-[var(--spacing-standings-rank-wide)_var(--spacing-rankings-col-desktop)_1fr_var(--spacing-rankings-col-desktop)_var(--spacing-rankings-col-desktop)_var(--spacing-chevron)]";

/* The same grid style as the standings. On a phone the four component columns do not fit beside the team,
   so the row keeps its phone columns and the component ranks move into the open row. From the page width up, they join the row.
   Ten columns need a tighter gap than the four-column standings, so the longest team name fits on two lines at 800.
   The page grid uses the same plain 1fr team track as the phone grid. At 480 the ten columns leave the team 102px,
   and the avatar, its gap, and the longest word "Unsolicited" need 101px, so no row grows past the others.
   From the tablet tier the gap widens to 8px and the component columns widen to hold their headers.
   From the desktop tier the wide rank and the desktop column spread the numbers.
   The team name stays on one line there. The rankings tokens in the stylesheet give the width left for the team at each tier. */
const GRID = `grid ${PHONE_COLS} page:grid-cols-[var(--spacing-standings-rank)_var(--spacing-rankings-col)_1fr_repeat(6,var(--spacing-rankings-col))_var(--spacing-chevron)] tablet:grid-cols-[var(--spacing-standings-rank)_var(--spacing-rankings-col)_1fr_repeat(2,var(--spacing-rankings-col))_repeat(4,var(--spacing-rankings-col-tablet))_var(--spacing-chevron)] desktop:grid-cols-[var(--spacing-standings-rank-wide)_var(--spacing-rankings-col-desktop)_1fr_repeat(6,var(--spacing-rankings-col-desktop))_var(--spacing-chevron)] items-center gap-x-sp-2 page:gap-x-sp-1 tablet:gap-x-sp-2 border-b border-rule text-row leading-tight tabular-nums`;

/* The arrow carries the direction in its shape, and the screen reader text names it, so the color is never the only sign.
   The count stays in the text color. The arrow sits on two surfaces: the white page in the light theme and the dark page #141414 in the dark theme.
   On the black card blue is about 5.06 to 1 and red about 5.04 to 1. On white blue is about 3.64 to 1 and red about 3.66 to 1.
   Both pairs pass the 3 to 1 rule for a graphic. No movement, and no last week in week 1, show a dash. */
export function Movement({ movement }: { movement: number | null }) {
  if (movement === null || movement === 0) {
    return (
      <span>
        <span aria-hidden>–</span>
        <span className="sr-only">{movement === null ? "No last week" : "No change"}</span>
      </span>
    );
  }
  const up = movement > 0;
  return (
    <span className="inline-flex items-center gap-sp-0">
      <span aria-hidden className={up ? "text-move-up" : "text-move-down"}>
        {up ? "▲" : "▼"}
      </span>
      <span className="sr-only">{up ? "Up" : "Down"}</span>
      {Math.abs(movement)}
    </span>
  );
}

/* The playoff cell reads the number while the race is open, and a word once the team has clinched or is out.
   A row from a week before the odds engine ran has no odds, so its cell shows a dash, as a row with no movement does. */
function playoffCell(row: RankingsRow): ReactNode {
  if (!row.odds) {
    return (
      <>
        <span aria-hidden>–</span>
        <span className="sr-only">No odds</span>
      </>
    );
  }
  if (row.odds.status === "in") return "In";
  if (row.odds.status === "out") return "Out";
  return String(row.odds.playoff);
}

/* The bye line of the open row: the bye odds, and the seed the team gets most often when it has one. */
function byeLine(odds: Odds): string {
  return odds.seed === null ? `Bye ${odds.bye}%` : `Bye ${odds.bye}%, most often the ${odds.seed} seed`;
}

/* The component cells of the open row on a phone. The line sits under the team, the record, and the playoff odds, and each cell names its column.
   From the page width up, the line hides, because the same ranks sit in the row under the header. */
function ComponentCells({ cells }: { cells: { name: string; value: ReactNode }[] }) {
  return (
    <span className="col-span-3 col-start-3 grid grid-cols-4 gap-x-sp-2 pt-sp-1 page:hidden">
      {cells.map(({ name, value }) => (
        <span key={name} className="text-right">
          <span className="mr-sp-1 text-label tracking-caps text-mute uppercase">{name}</span>
          {value}
        </span>
      ))}
    </span>
  );
}

/* One team. The row control opens the bye line and the blurb, and on a phone the component ranks above them.
   A row with no blurb and no odds has nothing to open from the page width up, so its control shows on a phone only. */
function Row({
  row,
  avatars,
  index,
  managersHref,
}: {
  row: RankingsRow;
  avatars: AvatarMap;
  index: number;
  managersHref: string | null;
}) {
  const [open, setOpen] = useState(false);
  const off = useMotionOff();
  const panelId = useId();
  const hasBlurb = row.blurb.length > 0;
  return (
    // Each row reveals once with the capped stagger, so a row low in the list never shows late.
    // The row and its open part share the bottom rule, so the rule moves to the reveal box.
    <Reveal className="border-b border-rule" delay={stagger(index + 1)}>
      {/* The grid is the positioned box of the control, so a tap anywhere on the row opens it. 44px is the smallest comfortable touch target. */}
      <div className={cn(GRID, "relative min-h-touch border-b-0 py-sp-1")}>
        <span>{row.rank}</span>
        <Movement movement={row.movement} />
        <Who src={avatarSrc(avatars, row.roster_id)} name={row.name} href={managerHrefOrNull(managersHref, row.roster_id)} />
        <span className="text-right">{record(row.wins, row.losses)}</span>
        <span className="text-right">{playoffCell(row)}</span>
        {/* The header names these columns, so the cells hold only the rank. On a phone they move into the open row. */}
        {COMPONENTS.map(({ key }) => (
          <span key={key} className="hidden text-right page:block">
            {row.components[key]}
          </span>
        ))}
        {/* The after box stretches the button over the whole row, so the touch target is the row and not only the chevron. */}
        <button
          type="button"
          aria-expanded={open}
          aria-controls={panelId}
          aria-label={`More on ${row.name}`}
          onClick={() => setOpen(!open)}
          className={cn(
            "flex cursor-pointer justify-end border-0 bg-transparent p-0 text-mute after:absolute after:inset-0",
            "[-webkit-tap-highlight-color:transparent]",
            !hasBlurb && !row.odds && "page:hidden",
          )}
        >
          {/* The same turned square as the recap button. With motion off it turns at once, with no transition class. */}
          <span
            aria-hidden
            className={cn(
              "inline-block size-chevron border-r-2 border-b-2 border-current",
              !off && "transition-[translate,rotate] duration-200 ease-out",
              open ? "translate-y-px -rotate-135" : "-translate-y-sp-0 rotate-45",
            )}
          />
        </button>
      </div>
      {/* The open part animates height, the same exception as the recap panel of a matchup row.
          It stays in the DOM when closed, so find-in-page still finds the blurb. aria-hidden and inert hide it from assistive tech. */}
      <motion.div
        id={panelId}
        aria-hidden={!open}
        inert={!open}
        initial={false}
        animate={open ? { height: "auto", opacity: 1 } : { height: 0, opacity: 0 }}
        transition={off ? INSTANT : { duration: DURATION.collapse, ease: EASE_OUT }}
        className="overflow-hidden"
      >
        {/* From the desktop tier the open row takes the wide rank and movement tracks of the row, so the blurb still starts under the team. */}
        <div className={cn("grid gap-x-sp-2 gap-y-sp-2 pb-sp-2", PHONE_COLS, OPEN_WIDE_COLS)}>
          <ComponentCells cells={COMPONENTS.map(({ key, name }) => ({ name, value: row.components[key] }))} />
          {/* The bye line shows at every width, because the row line has no room for the bye odds and the seed. */}
          {row.odds && (
            <Blurb className="col-[3/-1] text-meta">
              {byeLine(row.odds)}
            </Blurb>
          )}
          {/* The sentences join in their order in the file, as plain text. The fact IDs are for the checks, not the reader. */}
          {hasBlurb && (
            <Blurb className="col-[3/-1]">
              {row.blurb.map((sentence) => sentence.text).join(" ")}
            </Blurb>
          )}
        </div>
      </motion.div>
    </Reveal>
  );
}

/* One chip per week in the file. The chosen chip paints ink on the page color, so it is black on white in the light theme and white on black in the dark theme.
   The off chip paints the grey, which re-points one step off the page in the dark theme.
   aria-pressed names the chosen chip, so the fill is never the only sign. */
function WeekChips({ weeks, chosen, choose }: { weeks: RankingsWeek[]; chosen: number; choose: (week: number) => void }) {
  return (
    <div role="group" aria-label="Week" className="mb-sp-3 flex flex-wrap gap-sp-1">
      {weeks.map(({ week }) => (
        <button
          key={week}
          type="button"
          aria-pressed={week === chosen}
          aria-label={`Week ${week}`}
          onClick={() => choose(week)}
          className={cn(
            "press min-h-touch min-w-touch cursor-pointer rounded-card border-0 px-sp-3 text-row font-extrabold tabular-nums",
            "focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent",
            week === chosen ? "bg-ink text-page" : "bg-card text-ink",
          )}
        >
          {week}
        </button>
      ))}
    </div>
  );
}

/* The table reads the shared choice of the page when a provider holds one, so the masthead week line follows the chips.
   Outside a provider it keeps a choice of its own. Both hooks run on every render, as the rules of hooks ask.
   The managers href is the managers index of the season. With null the team names render as plain text. */
export function PowerRankings({
  weeks,
  avatars,
  managersHref = null,
}: {
  weeks: RankingsWeek[];
  avatars: AvatarMap;
  managersHref?: string | null;
}) {
  const shared = useSharedWeekChoice();
  const own = useWeekChoice(weeks);
  const { week, choose } = shared ?? own;
  return (
    <Chapter>
      {/* The label, the method note, and the header reveal first, then the rows stagger in after them, as the trades chapter does.
          The note sits above the table, so a reader knows what each column ranks before the first row. */}
      <Reveal delay={stagger(0)}>
        <Label heading>Power Rankings</Label>
        <WeekChips weeks={weeks} chosen={week.week} choose={choose} />
        <Blurb className="mb-sp-3 text-meta">
          Each column ranks the team from 1 to 12: standing, recent form, schedule played, and scoring. Form reads the last 3 weeks: the head-to-head record and streak, the median game at half the weight, and the all-play record, and it carries 60 percent of the score. Pts ranks scoring: points for and the all-play record.
        </Blurb>
        {/* The header names the component columns only from the page width up. On a phone the component ranks show in the open row, and each cell names itself. */}
        <div
          aria-hidden
          // cn drops the leading of the grid when a new text size follows, so the header sets it again.
          className={cn(GRID, "pt-0 pb-sp-2 text-label leading-tight tracking-caps text-mute uppercase")}
        >
          <span>#</span>
          <span>+/-</span>
          <span>Team</span>
          <span className="text-right">W-L</span>
          {/* The playoff header is wider than its column. The soft hyphen breaks it as "Play-" over "off %", never at a random letter. */}
          <span className="text-right">Play&shy;off %</span>
          {COMPONENTS.map(({ name }) => (
            <span key={name} className="hidden text-right page:block">
              {name}
            </span>
          ))}
          {/* The empty cell over the column of the row control. */}
          <span />
        </div>
      </Reveal>
      {/* The key starts each week with closed rows, so an open row of one week never carries into the next. */}
      <ol key={week.week} className="m-0 list-none p-0">
        {week.rows.map((row, index) => (
          <li key={row.roster_id}>
            <Row row={row} avatars={avatars} index={index} managersHref={managersHref} />
          </li>
        ))}
      </ol>
      <Blurb className="mt-sp-1 text-meta">
        Playoff odds from 5,000 simulated seasons.
      </Blurb>
    </Chapter>
  );
}
