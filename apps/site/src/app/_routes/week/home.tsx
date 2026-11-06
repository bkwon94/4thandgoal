/**
 * The home parts of the week package: the hero on the Matchup of the Week of the latest week with its four numbers,
 * and the Weekly Reports chapter with every published week, newest first. The registry imports it only when the client takes week.
 */
import { Blurb } from "@cpc/design/parts/blurb";
import { Card } from "@cpc/design/parts/card";
import { HomeMatchup } from "@cpc/week/chapters/home-matchup";
import { WeekNumbers } from "@cpc/week/chapters/week-numbers";
import type { WeekSummary } from "@cpc/week/schema/week-types";
import { latestAvatars } from "@/lib/data/rankings-data";
import { listWeeks, listWeekSummaries, loadWeek } from "@/lib/data/week-data";
import type { HomeSection } from "@/lib/client-values";
import { weekHref } from "@/lib/routes";
import { HomeChapter } from "@/app/home-chapter";

/* The week number with two digits, as the week chip writes it: "08". */
const twoDigits = (week: number) => String(week).padStart(2, "0");

/* The hero and the four numbers of the latest week. listWeeks sorts by season, then by week, so the last ref is the latest. */
function latestWeekPart(): HomeSection[] {
  const ref = listWeeks().at(-1);
  if (!ref) return [];
  const page = loadWeek(ref.season, ref.week);
  return [
    {
      place: "top",
      part: (
        <>
          <HomeMatchup
            week={page.week}
            pick={page.pick}
            avatars={latestAvatars(Number(ref.season))}
            blurb={page.blurbs.motw}
            href={weekHref(ref.season, ref.week)}
          />
          {page.matchups.length > 0 && (
            <HomeChapter id="numbers" title={`Week ${page.week} in four numbers`}>
              <WeekNumbers matchups={page.matchups} median={page.median} gameChanger={page.game_changer} />
            </HomeChapter>
          )}
        </>
      ),
    },
  ];
}

/* One row of the Weekly Reports card: the week number, the dates with the teams of the Matchup of the Week, and an arrow.
   The whole row is the link, so it is 44px tall or more. The arrow is drawn, because axe cannot read the contrast of a glyph. */
function WeekRow({ week }: { week: WeekSummary }) {
  return (
    <li className="border-t border-rule first:border-t-0">
      <a
        href={week.href}
        className="press group grid min-h-touch grid-cols-[auto_minmax(0,1fr)_auto] items-center gap-x-sp-3 py-sp-3 text-ink no-underline"
      >
        <span aria-hidden="true" className="font-mono text-stat font-bold tabular-nums">
          {twoDigits(week.number)}
        </span>
        <span className="flex min-w-0 flex-col gap-sp-0">
          <b className="text-lead leading-tight group-hover:text-accent-ink">Week {week.number}</b>
          <span className="text-meta leading-tight text-mute tabular-nums">{week.dates}</span>
          <span className="text-meta leading-tight text-mute">{`${week.pickTeams[0]} vs ${week.pickTeams[1]}`}</span>
        </span>
        <svg
          aria-hidden="true"
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          className="text-mute"
        >
          <path d="M5 12h14M13 6l6 6-6 6" />
        </svg>
      </a>
    </li>
  );
}

/* The Weekly Reports chapter. A client with no published week still shows the chapter, with a plain line. */
function weeklyReportsPart(): HomeSection {
  const weeks = listWeekSummaries();
  const note = weeks.length === 1 ? "1 week" : `${weeks.length} weeks`;
  return {
    place: "bottom",
    part: (
      <HomeChapter id="weeks" title="Weekly Reports" note={note}>
        {weeks.length === 0 ? (
          <Blurb className="text-lead">No weeks are published yet.</Blurb>
        ) : (
          <Card className="py-0">
            <ul className="m-0 list-none p-0">
              {weeks.map((week) => (
                <WeekRow key={week.href} week={week} />
              ))}
            </ul>
          </Card>
        )}
      </HomeChapter>
    ),
  };
}

export const homeSection = (): HomeSection[] => [...latestWeekPart(), weeklyReportsPart()];
