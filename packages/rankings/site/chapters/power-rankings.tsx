/**
 * The power rankings Ladder: the hero for the team at rank 1, the week chips, one card for each other team, and the note on the four parts.
 * Each card is an Open card. A tap opens the ranks of Stand, Form, Sched, and Pts, the move, the bye and seed odds, the blurb, and a link to the manager page.
 * Every part number is a rank, never a score. The cards and the chips hold state, so this file is a client component.
 */
"use client";

import { useEffect, useRef, type ReactNode } from "react";
import { Chapter } from "@cpc/design/parts/chapter";
import { Hero } from "@cpc/design/parts/hero";
import { OpenCard } from "@cpc/design/parts/open-card";
import { BarFill } from "@cpc/design/parts/bar-fill";
import { Reveal } from "@cpc/design/parts/reveal";
import { Rise } from "@cpc/design/parts/rise";
import { Tile } from "@cpc/design/parts/tile";
import { Avatar } from "@cpc/league/avatar";
import { managerHrefOrNull } from "@cpc/league/hrefs";
import { avatarSrc } from "@cpc/league/images";
import { record } from "@cpc/design/format/format";
import { stagger } from "@cpc/design/lib/motion";
import type { Components, Odds, RankingsRow, RankingsWeek } from "../schema/rankings-types";
import { cn } from "@cpc/design/lib/utils";
import { useWeekChoice } from "./week-choice";
import { openId, stableId, stableKey, textId } from "@cpc/design/lib/stable-id";

/* The order and the names of the four part ranks. */
const COMPONENTS: { key: keyof Components; name: string }[] = [
  { key: "standing", name: "Stand" },
  { key: "form", name: "Form" },
  { key: "schedule_played", name: "Sched" },
  { key: "scoring", name: "Pts" },
];

/* The avatar of each roster id, with paths relative to the week folder, as the week page file holds them. */
type AvatarMap = Readonly<Record<string, string>>;

/* The rank in two digits, such as "02". The cards use the same width, so the ranks line up. */
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

/* The hero: the team at rank 1 of the chosen week, in the hero slots. The week is the eyebrow, the team name the title,
   and the record line the meta. The tiles take the hero tone, so they sit on the raised surface of the hero.
   The hero keeps the static grid: the Ladder under it already shows the race, so a scene would say it twice.
   The Ladder starts at rank 2, so the action slot holds the manager link of rank 1, the link that its card would hold.
   With no managers href the hero has no link and no action slot. */
function TopHero({ row, week, managersHref }: { row: RankingsRow; week: RankingsWeek; managersHref: string | null }) {
  const odds = row.odds;
  const href = managerHrefOrNull(managersHref, row.roster_id);
  return (
    <Hero
      label="Rank 1"
      eyebrow={`WEEK ${week.week} // POWER RANKINGS`}
      title={<span {...stableId("rank-hero", row.roster_id)}>{row.name}</span>}
      meta={
        <span className="font-mono tabular-nums">
          <RecordLine row={row} />
        </span>
      }
      stats={
        <Rise step={1} className="w-full tablet:w-auto">
          <div className="grid grid-cols-3 gap-sp-2">
            <Tile tone="hero" label="Playoff" value={playoffText(odds)} stable={stableKey("hero-tile", row.roster_id, "playoff")} />
            <Tile tone="hero" label="Bye" value={odds ? `${odds.bye}%` : <Missing what="No odds" />} stable={stableKey("hero-tile", row.roster_id, "bye")} />
            <Tile tone="hero" label="Seed" value={odds?.seed != null ? String(odds.seed) : <Missing what="No seed" />} stable={stableKey("hero-tile", row.roster_id, "seed")} />
          </div>
        </Rise>
      }
      action={
        href === null ? undefined : (
          <Rise step={2}>
            {/* A full pill and a 44px tap target in the brand color, as the buttons of the 404 page. */}
            <a
              href={href}
              className="press inline-flex min-h-touch items-center justify-center rounded-pill bg-accent px-sp-6 text-body font-bold text-on-dark no-underline"
            >
              Manager page
            </a>
          </Rise>
        )
      }
    />
  );
}

/* The chips of an open card: the four part ranks, the move, and the bye and seed odds. A week with no odds shows a dash. */
function chipsOf(row: RankingsRow): ReactNode[] {
  const odds = row.odds;
  return [
    // The egg hunt names each part of the rank by the same id as the tile of the ladder before it.
    ...COMPONENTS.map(({ key, name }) => <span {...stableId("ladder", row.roster_id, name)}>{`${name} ${row.components[key]}`}</span>),
    <>
      Move <Movement movement={row.movement} />
    </>,
    odds ? `Bye ${odds.bye}%` : <>Bye <Missing what="No odds" /></>,
    odds?.seed != null ? `Seed ${odds.seed}` : <>Seed <Missing what="No seed" /></>,
  ];
}

/* One card of the ladder on the Open card, in the full Showcase shell. The head is the button, so the whole head is the tap target.
   The rank sits large in a plain raised panel, the media of the shell. The team, the record, the move, the playoff chip, and the odds bar sit under it.
   The open panel holds the overview line, the chips, the blurb, and the manager link. */
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
  const href = managerHrefOrNull(managersHref, row.roster_id);
  return (
    // Each card reveals once with the capped stagger, so a card low in the list never shows late.
    <Reveal delay={stagger(index + 1)}>
      <OpenCard
        as="div"
        // The id names the team, so a check can open the card of one team by its control.
        panelId={`ladder-${row.roster_id}`}
        // The egg hunt names the toggle and the blurb by ids from the data.
        headMarks={openId("card", row.roster_id)}
        textMarks={row.blurb.length > 0 ? textId("blurb", blurbText(row)) : undefined}
        // The head takes the inset of the panel, so the rank panel and the open panel line up, as in the shell of the item.
        headClassName="p-sp-2 pb-0"
        head={
          <>
            <span
              data-rank-panel
              className="block rounded-tile bg-raised px-sp-4 py-sp-4 font-mono text-hero leading-none font-bold tracking-grade text-ink tabular-nums"
            >
              {twoDigits(row.rank)}
            </span>
            <span className="grid grid-cols-[auto_minmax(0,1fr)_auto] items-center gap-x-sp-3 px-sp-2">
              <Avatar src={avatarSrc(avatars, row.roster_id)} />
              <span className="flex min-w-0 flex-col">
                <span className="truncate text-row leading-tight font-bold text-ink">{row.name}</span>
                <span className="mt-sp-0 font-mono text-meta leading-tight text-ink-2 tabular-nums" {...stableId("movement", row.roster_id)}>
                  <RecordLine row={row} />
                </span>
              </span>
              <span className="rounded-pill bg-raised px-sp-3 py-sp-1 font-mono text-meta leading-tight font-bold text-ink tabular-nums">
                Playoff {playoffText(row.odds)}
              </span>
            </span>
            {row.odds && (
              <span aria-hidden className="mx-sp-2 block h-sp-1 overflow-hidden rounded-pill bg-raised">
                <BarFill data-odds-bar pct={playoffFill(row.odds)} className="block h-full rounded-pill bg-accent" />
              </span>
            )}
          </>
        }
        overview={
          <>
            Rank {row.rank} · <RecordLine row={row} />
          </>
        }
        chips={chipsOf(row)}
        text={row.blurb.length > 0 ? blurbText(row) : null}
        action={href === null ? null : { href, label: "Manager page", hiddenLabel: ` of ${row.name}` }}
      />
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
          {...openId("week", week)}
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
        <TopHero key={week.week} row={top} week={week} managersHref={managersHref} />
        {/* The blurb of rank 1 sits directly under the hero, outside its frame, so the hero stays as short as the others. */}
        {top.blurb.length > 0 && (
          <p className="mt-sp-4 mb-0 max-w-measure text-lead leading-body text-ink-2" {...textId("blurb", blurbText(top))}>{blurbText(top)}</p>
        )}
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
