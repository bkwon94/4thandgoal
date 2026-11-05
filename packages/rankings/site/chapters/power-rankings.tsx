/**
 * The power rankings Ladder: the hero for the team at rank 1, the week chips, one card for each other team, and the note on the four parts.
 * A tap on a card opens the ranks of Stand, Form, Sched, and Pts, the blurb, and a link to the manager page.
 * Every part number is a rank, never a score. The cards and the chips hold state, so this file is a client component.
 */
"use client";

import { motion } from "framer-motion";
import { useEffect, useId, useRef, useState, type ReactNode } from "react";
import { Card } from "@cpc/design/parts/card";
import { Chapter } from "@cpc/design/parts/chapter";
import { Hero } from "@cpc/design/parts/hero";
import { BarFill } from "@cpc/design/parts/bar-fill";
import { Reveal } from "@cpc/design/parts/reveal";
import { Rise } from "@cpc/design/parts/rise";
import { Tile } from "@cpc/design/parts/tile";
import { Avatar } from "@cpc/league/avatar";
import { managerHrefOrNull } from "@cpc/league/hrefs";
import { avatarSrc } from "@cpc/league/images";
import { record } from "@cpc/design/format/format";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { DURATION, EASE_OUT, INSTANT, stagger } from "@cpc/design/lib/motion";
import type { Components, Odds, RankingsRow, RankingsWeek } from "../schema/rankings-types";
import { cn } from "@cpc/design/lib/utils";
import { useWeekChoice } from "./week-choice";

/* The order and the names of the four part ranks. */
const COMPONENTS: { key: keyof Components; name: string }[] = [
  { key: "standing", name: "Stand" },
  { key: "form", name: "Form" },
  { key: "schedule_played", name: "Sched" },
  { key: "scoring", name: "Pts" },
];

/* The avatar of each roster id, with paths relative to the week folder, as the week page file holds them. */
type AvatarMap = Readonly<Record<string, string>>;

/* The rank in two digits, as the hero shows "01". The cards use the same width, so the ranks line up. */
const twoDigits = (rank: number) => String(rank).padStart(2, "0");

/* The arrow carries the direction in its shape, and the screen reader text names it, so the color is never the only sign.
   The count stays in the text color. No movement, and no last week in week 1, show a dash.
   The arrow is a drawn triangle, not a text glyph: axe cannot read the contrast of a glyph with no letters, and the floor
   fails on that incomplete result. A graphic needs 3 to 1, and both arrow colors pass it on the card and the hero. */
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
      <svg
        aria-hidden
        data-arrow={up ? "up" : "down"}
        viewBox="0 0 10 10"
        className={cn("size-[0.7em] fill-current", up ? "text-move-up" : "rotate-180 text-move-down")}
      >
        <path d="M5 1 9.5 9h-9z" />
      </svg>
      <span className="sr-only">{up ? "Up" : "Down"}</span>
      {Math.abs(movement)}
    </span>
  );
}

/* A dash with its screen reader text, for a value the file does not hold. */
function Missing({ what }: { what: string }) {
  return (
    <>
      <span aria-hidden>–</span>
      <span className="sr-only">{what}</span>
    </>
  );
}

/* The playoff odds read the percent while the race is open, and a word once the team has clinched or is out.
   A row from a week before the odds engine ran has no odds, so it shows a dash. */
function playoffText(odds: Odds | undefined): ReactNode {
  if (!odds) return <Missing what="No odds" />;
  if (odds.status === "in") return "In";
  if (odds.status === "out") return "Out";
  return `${odds.playoff}%`;
}

/* The playoff odds as a component, so a server part such as the top three of the home page can render them. */
export function PlayoffOdds({ odds }: { odds: Odds | undefined }) {
  return <>{playoffText(odds)}</>;
}

/* The part of the bar that the playoff odds fill: all of it for a clinched team, none of it for a team that is out. */
function playoffFill(odds: Odds): number {
  if (odds.status === "in") return 100;
  if (odds.status === "out") return 0;
  return odds.playoff;
}

/* The record and the movement on one line, as "9-3 · ▲4". */
export function RecordLine({ row }: { row: RankingsRow }) {
  return (
    <>
      <span>{record(row.wins, row.losses)}</span>
      <span aria-hidden> · </span>
      <Movement movement={row.movement} />
    </>
  );
}

/* The sentences join in their order in the file, as plain text. The fact IDs are for the checks, not the reader. */
const blurbText = (row: RankingsRow) => row.blurb.map((sentence) => sentence.text).join(" ");

/* The hero: the team at rank 1 of the chosen week. Each line of text sits on a plate, so the grid and the glow never sit
   under a letter. The tiles take the hero tone, so they sit on the raised surface of the hero. */
function TopHero({ row, week }: { row: RankingsRow; week: number }) {
  const odds = row.odds;
  return (
    <Hero label="Rank 1">
      <Rise step={0}>
        <h1 className="plate m-0 w-fit font-mono text-meta leading-tight font-bold tracking-wide text-accent-text uppercase">
          WEEK {week} // POWER RANKINGS
        </h1>
      </Rise>
      <Rise step={1}>
        <div className="plate mt-sp-4 w-fit font-mono text-hero leading-none font-bold tracking-grade">{twoDigits(row.rank)}</div>
      </Rise>
      <Rise step={2}>
        <h2 className="plate mt-sp-3 mb-0 w-fit text-headline leading-tight font-bold">{row.name}</h2>
        <div className="plate mt-sp-2 w-fit font-mono text-lead leading-tight text-on-dark-2 tabular-nums">
          <RecordLine row={row} />
        </div>
      </Rise>
      <Rise step={3} className="mt-sp-5 grid grid-cols-3 gap-sp-2">
        <Tile tone="hero" label="Playoff" value={playoffText(odds)} />
        <Tile tone="hero" label="Bye" value={odds ? `${odds.bye}%` : <Missing what="No odds" />} />
        <Tile tone="hero" label="Seed" value={odds?.seed != null ? String(odds.seed) : <Missing what="No seed" />} />
      </Rise>
      {row.blurb.length > 0 && (
        <Rise step={4}>
          <p className="plate mt-sp-5 mb-0 w-fit max-w-measure text-lead leading-body text-on-dark-2">{blurbText(row)}</p>
        </Rise>
      )}
    </Hero>
  );
}

/* One card of the ladder. The head is the button, so the whole head is the tap target, never under 44px tall.
   The open part animates height, the same exception as the recap panel of a game card. It stays in the DOM when closed,
   so find-in-page still finds the blurb. aria-hidden and inert hide it from assistive tech. The brand edge marks the open card. */
function LadderCard({
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
  const href = managerHrefOrNull(managersHref, row.roster_id);
  return (
    // Each card reveals once with the capped stagger, so a card low in the list never shows late.
    <Reveal delay={stagger(index + 1)}>
      <Card as="div" edge={open} className="overflow-hidden p-0">
        <button
          type="button"
          aria-expanded={open}
          aria-controls={panelId}
          onClick={() => setOpen(!open)}
          className={cn(
            "grid min-h-touch w-full cursor-pointer grid-cols-[auto_auto_minmax(0,1fr)_auto] items-center gap-x-sp-3",
            "border-0 bg-transparent p-sp-4 text-left text-ink [-webkit-tap-highlight-color:transparent]",
            "focus-visible:outline-2 focus-visible:outline-offset-[-2px] focus-visible:outline-accent",
          )}
        >
          <span className="font-mono text-row font-bold text-mute tabular-nums">{twoDigits(row.rank)}</span>
          <Avatar src={avatarSrc(avatars, row.roster_id)} />
          <span className="flex flex-col">
            <span className="text-row leading-tight font-bold">{row.name}</span>
            <span className="mt-sp-0 font-mono text-meta leading-tight text-ink-2 tabular-nums">
              <RecordLine row={row} />
            </span>
          </span>
          <span className="flex flex-col items-end">
            <span className="sr-only">Playoff odds </span>
            <span className="font-mono text-row font-bold tabular-nums">{playoffText(row.odds)}</span>
            {row.odds && (
              <span aria-hidden className="mt-sp-1 block h-sp-1 w-rankings-col overflow-hidden rounded-pill bg-raised">
                <BarFill data-odds-bar pct={playoffFill(row.odds)} className="block h-full rounded-pill bg-accent" />
              </span>
            )}
          </span>
        </button>
        <motion.div
          id={panelId}
          aria-hidden={!open}
          inert={!open}
          initial={false}
          animate={open ? { height: "auto", opacity: 1 } : { height: 0, opacity: 0 }}
          transition={off ? INSTANT : { duration: DURATION.collapse, ease: EASE_OUT }}
          className="overflow-hidden"
        >
          <div className="px-sp-4 pb-sp-4">
            <div className="grid grid-cols-2 gap-sp-2 page:grid-cols-4">
              {COMPONENTS.map(({ key, name }) => (
                <Tile key={key} label={name} value={row.components[key]} />
              ))}
            </div>
            {row.blurb.length > 0 && (
              <p className="mt-sp-3 mb-0 max-w-measure text-lead leading-body text-ink-2">{blurbText(row)}</p>
            )}
            {href !== null && (
              <a
                href={href}
                className="mt-sp-2 inline-flex min-h-touch items-center font-mono text-meta font-bold tracking-wide text-accent-ink uppercase no-underline hover-fine:underline"
              >
                Manager page
                {/* A drawn arrow, for the same reason as the movement arrow: axe cannot read the contrast of a glyph. */}
                <svg aria-hidden viewBox="0 0 10 10" className="ml-sp-1 size-[0.8em] fill-none stroke-current stroke-[1.5]">
                  <path d="M1 5h8M5.5 1.5 9 5l-3.5 3.5" />
                </svg>
              </a>
            )}
          </div>
        </motion.div>
      </Card>
    </Reveal>
  );
}

/* One chip per week in the file. The chosen chip paints ink on the page color, so it is black on white in the light theme and white on black in the dark theme.
   The off chip paints the grey, which re-points one step off the page in the dark theme.
   aria-pressed names the chosen chip, so the fill is never the only sign.
   The chips keep one row. A season longer than the width scrolls inside the row, so the page never scrolls sideways.
   The 4px inset keeps the focus ring inside the row, because a box that scrolls clips what passes its edge. */
function WeekChips({ weeks, chosen, choose }: { weeks: RankingsWeek[]; chosen: number; choose: (week: number) => void }) {
  const row = useRef<HTMLDivElement>(null);

  // The chosen week, the latest on load, can sit past the right edge of a phone. The row scrolls to show it in full.
  // Only the row scrolls, so the page keeps its place. The row is relative, so it is the offset parent of each chip.
  useEffect(() => {
    const box = row.current;
    const chip = box?.querySelector<HTMLElement>('[aria-pressed="true"]');
    if (!box || !chip) return;
    const end = chip.offsetLeft + chip.offsetWidth - box.clientWidth;
    if (end > box.scrollLeft) box.scrollLeft = end;
    else if (chip.offsetLeft < box.scrollLeft) box.scrollLeft = chip.offsetLeft;
  }, [chosen]);

  return (
    <div ref={row} role="group" aria-label="Week" className="relative -m-sp-1 mb-sp-3 flex gap-sp-1 overflow-x-auto p-sp-1">
      {weeks.map(({ week }) => (
        <button
          key={week}
          type="button"
          aria-pressed={week === chosen}
          aria-label={`Week ${week}`}
          onClick={() => choose(week)}
          className={cn(
            "press min-h-touch min-w-touch flex-none cursor-pointer rounded-card border-0 px-sp-3 text-row font-extrabold tabular-nums",
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

/* The Ladder of the chosen week. The hero and the cards read the same choice, so a chip moves both.
   The managers href is the managers index of the season. With null the cards show no manager link. */
export function PowerRankings({
  weeks,
  avatars,
  managersHref = null,
}: {
  weeks: RankingsWeek[];
  avatars: AvatarMap;
  managersHref?: string | null;
}) {
  const { week, choose } = useWeekChoice(weeks);
  const [top, ...rest] = week.rows;
  return (
    <>
      {/* On a phone the chapters fill the width, so the hero takes the gutter. From the tablet tier the main spaces it as a card. */}
      <div className="px-gutter pt-sp-5 tablet:px-0">
        <TopHero key={week.week} row={top} week={week.week} />
      </div>
      <Chapter>
        <Reveal delay={stagger(0)}>
          <div className="mb-sp-3 flex items-baseline justify-between gap-sp-3">
            <h2 className="m-0 font-mono text-meta leading-tight font-bold tracking-wide text-accent-ink uppercase">The Ladder</h2>
            <span className="font-mono text-meta leading-tight text-mute uppercase">Odds = playoff</span>
          </div>
          <WeekChips weeks={weeks} chosen={week.week} choose={choose} />
        </Reveal>
        {/* The key starts each week with closed cards, so an open card of one week never carries into the next. */}
        <ol key={week.week} className="m-0 flex list-none flex-col gap-sp-2 p-0">
          {rest.map((row, index) => (
            <li key={row.roster_id}>
              <LadderCard row={row} avatars={avatars} index={index} managersHref={managersHref} />
            </li>
          ))}
        </ol>
      </Chapter>
      <Chapter>
        <p className="m-0 max-w-measure text-lead leading-body text-ink-2">
          Each team gets a rank from 1 to 12 in four parts: standing, recent form, schedule played, and scoring. Form reads the last 3 weeks: the head-to-head record and streak, the median game at half the weight, and the all-play record, and it carries 60 percent of the score. Pts ranks scoring: points for and the all-play record.
        </p>
        <p className="mt-sp-3 mb-0 text-lead leading-body text-mute">Playoff odds from 5,000 simulated seasons.</p>
      </Chapter>
    </>
  );
}
