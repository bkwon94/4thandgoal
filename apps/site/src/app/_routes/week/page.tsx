/**
 * The week page at /<season>/week-NN/, one static page per page.json in public/.
 * It renders the masthead with the week line and the week sections from that JSON.
 */
import type { Metadata } from "next";
import { Masthead, WeekLine } from "@/components/shell/masthead";
import { PageColumn } from "@/components/parts/page-column";
import { AllMatchups } from "@/components/week/all-matchups";
import { ChapterRail, type RailChapter } from "@/components/parts/chapter-rail";
import { Awards } from "@/components/week/awards";
import { GameChanger } from "@/components/week/game-changer";
import { MatchupOfTheWeek } from "@/components/week/matchup-of-the-week";
import { MedianGame } from "@/components/week/median-game";
import { NextWeek } from "@/components/week/next-week";
import { PositionLeaders } from "@/components/week/position-leaders";
import { Standings } from "@/components/week/standings";
import { Trades } from "@/components/week/trades";
import { WeekFooter } from "@/components/week/week-footer";
import { basePath } from "@/lib/config";
import { seasonManagersHref } from "@/lib/data/manager-data";
import { listWeekSummaries, listWeeks, loadWeek, type WeekRef } from "@/lib/data/week-data";
import { weekHref } from "@/lib/routes";
import { mastheadProps } from "@/app/masthead-props";

type Props = { params: Promise<WeekRef> };

export function generateStaticParams(): WeekRef[] {
  return listWeeks();
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { season, week } = await params;
  const page = loadWeek(season, week);
  return {
    title: `Week ${page.week} · Cornerstone Fantasy Football League`,
    description: page.summary,
    // The pipeline reads this meta from a week page to list the week on the home page.
    other: { "cornerstone-summary": page.summary },
  };
}

export default async function WeekPage({ params }: Props) {
  const { season, week } = await params;
  const page = loadWeek(season, week);
  // The page reads the managers file once, and the team names of its chapters link from the one href.
  const managersHref = seasonManagersHref(season);
  // The rail lists the chapters the page renders, in the same order, with the ids the chapters set.
  // The labels use the words of each chapter's own label.
  // Each id matches the Chapter id in that chapter's component.
  const chapters: RailChapter[] = [
    { id: "motw", label: "Matchup of the Week" },
    ...(page.game_changer ? [{ id: "game-changer", label: "Game Changer" }] : []),
    { id: "awards", label: "Awards" },
    ...(page.leaders.length > 0 ? [{ id: "leaders", label: "Position Leaders" }] : []),
    { id: "trades", label: "Trades" },
    { id: "matchups", label: "All Matchups" },
    { id: "median", label: "The Median Game" },
    { id: "standings", label: "Standings" },
    { id: "next-week", label: "Next Week" },
  ];
  // The footer links the nearest published weeks of the same season on each side. The list is newest first,
  // so the first lower number is the prior week and the last higher number is the next week.
  // Each href carries the base path, so the season folder does too.
  const seasonWeeks = listWeekSummaries().filter((summary) => summary.href.startsWith(`${basePath}/${season}/`));
  const prior = seasonWeeks.find((summary) => summary.number < page.week) ?? null;
  const next = seasonWeeks.filter((summary) => summary.number > page.week).at(-1) ?? null;
  return (
    <>
      <Masthead {...mastheadProps()} subtitle="League Weekly" pageHref={weekHref(season, week)}>
        <WeekLine label="WEEK" number={page.week} />
        <div className="mt-sp-1 text-meta text-on-dark-2 tabular-nums">
          {/* One string, so React writes one text node and the browser kerns the line as one run. */}
          {`${page.dates} · Published ${page.publish_date}`}
        </div>
      </Masthead>
      <PageColumn rail={<ChapterRail chapters={chapters} />}>
        {/* The masthead and the top story show at once. The hero plays its own motion on load.
            Each chapter below reveals once as it enters the view, as a unit or card by card. */}
        <MatchupOfTheWeek pick={page.pick} avatars={page.avatars} blurb={page.blurbs.motw} />
        {page.game_changer && (
          <GameChanger gameChanger={page.game_changer} headshots={page.headshots} blurb={page.blurbs.game_changer} />
        )}
        <Awards awards={page.awards} headshots={page.headshots} blurb={page.blurbs.awards} />
        {page.leaders.length > 0 && (
          <PositionLeaders leaders={page.leaders} headshots={page.headshots} blurb={page.blurbs.position_leaders} />
        )}
        <Trades trades={page.trades} avatars={page.avatars} managersHref={managersHref} />
        <AllMatchups matchups={page.matchups} avatars={page.avatars} managersHref={managersHref} />
        <MedianGame median={page.median} blurb={page.blurbs.median} />
        <Standings table={page.table} avatars={page.avatars} managersHref={managersHref} />
        <NextWeek week={page.week} games={page.next} avatars={page.avatars} blurb={page.blurbs.next_week} />
        <WeekFooter prior={prior} next={next} />
      </PageColumn>
    </>
  );
}
