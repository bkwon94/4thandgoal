/**
 * The week page at /<season>/week-NN/, one static page per page.json in public/.
 * It renders the shell, then one scroll from that JSON: the hero, the four numbers, the chapters, and the footer.
 */
import type { Metadata } from "next";
import { TopBand } from "@cpc/design/shell/top-band";
import { PageColumn } from "@cpc/design/parts/page-column";
import { AllMatchups } from "@cpc/week/chapters/all-matchups";
import { ChapterRail, type RailChapter } from "@cpc/design/parts/chapter-rail";
import { Awards } from "@cpc/week/chapters/awards";
import { GameChanger } from "@cpc/week/chapters/game-changer";
import { MatchupOfTheWeek } from "@cpc/week/chapters/matchup-of-the-week";
import { MedianGame } from "@cpc/week/chapters/median-game";
import { NextWeek } from "@cpc/week/chapters/next-week";
import { PositionLeaders } from "@cpc/week/chapters/position-leaders";
import { Standings } from "@cpc/week/chapters/standings";
import { Trades } from "@cpc/week/chapters/trades";
import { WeekFooter } from "@cpc/week/chapters/week-footer";
import { WeekNumbers } from "@cpc/week/chapters/week-numbers";
import { weekTrends } from "@cpc/week/chapters/week-trends";
import { matchupScene } from "@cpc/week/parts/matchup-scene";
import { loadSeasonWeeks, seasonManagersHref } from "@/lib/data/manager-data";
import { listWeekSummaries, listWeeks, loadWeek, type WeekRef } from "@/lib/data/week-data";
import { weekHref } from "@/lib/routes";
import { shellProps, pageTitle, weekSubtitle } from "@/app/shell-props";

type Props = { params: Promise<WeekRef> };

export function generateStaticParams(): WeekRef[] {
  return listWeeks();
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { season, week } = await params;
  const page = loadWeek(season, week);
  return {
    title: pageTitle(undefined, `Week ${page.week}`),
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
  // The Trend tiles of the week numbers read the saved weeks of every team. They stop at the page week.
  const teamWeeks = loadSeasonWeeks(season);
  const trends = teamWeeks === null ? null : weekTrends(teamWeeks, page.week);
  // The rail lists the chapters the page renders, in the same order, with the ids the chapters set.
  // The labels use the words of each chapter's own heading, and the hero takes the name of its region.
  // Each id matches the id in that chapter's component. A chapter with no data has no rail link.
  const chapters: RailChapter[] = [
    { id: "motw", label: "Matchup of the Week" },
    ...(page.matchups.length > 0 ? [{ id: "matchups", label: "Every game" }] : []),
    ...(page.game_changer ? [{ id: "game-changer", label: "Game Changer" }] : []),
    { id: "awards", label: "Awards" },
    ...(page.leaders.length > 0 ? [{ id: "leaders", label: "Position leaders" }] : []),
    ...(page.trades.length > 0 ? [{ id: "trades", label: "Trades" }] : []),
    // A league with no median game has median null, so the page has no median chapter and the rail no link to it.
    ...(page.median ? [{ id: "median", label: "The median game" }] : []),
    { id: "standings", label: "Standings" },
    { id: "next-week", label: "Next week" },
  ];
  // The footer links the nearest published weeks of the same season on each side. The list is newest first,
  // so the first lower number is the prior week and the last higher number is the next week.
  const seasonWeeks = listWeekSummaries().filter((summary) => summary.href.startsWith(`/${season}/`));
  const prior = seasonWeeks.find((summary) => summary.number < page.week) ?? null;
  const next = seasonWeeks.filter((summary) => summary.number > page.week).at(-1) ?? null;
  return (
    <>
      {/* The hero starts the page, so the top band holds no week line. */}
      <TopBand {...shellProps()} pageHref={weekHref(season, week)} />
      {/* The page color fills the width under the band, so the cards sit on the page in both themes. */}
      <div className="bg-page">
        <PageColumn rail={<ChapterRail chapters={chapters} />}>
          {/* One scroll with no tabs, in the order of the spec (decision 05). The hero and the four numbers rise in on load.
              Each chapter below rises in once as it enters the view. */}
          <div className="flex flex-col gap-sp-6 px-gutter pt-sp-4 pb-sp-6 tablet:px-0">
            <MatchupOfTheWeek
              week={page.week}
              dates={page.dates}
              publishDate={page.publish_date}
              pick={page.pick}
              avatars={page.avatars}
              headshots={page.headshots}
              blurb={page.blurbs.motw}
              // The hero of the Matchup is the first hero of the page, so it draws the scene of the week (decision 07).
              scene={matchupScene(page)}
            />
            <WeekNumbers
              matchups={page.matchups}
              median={page.median}
              gameChanger={page.game_changer}
              trends={trends}
            />
            {page.matchups.length > 0 && (
              <AllMatchups matchups={page.matchups} avatars={page.avatars} managersHref={managersHref} />
            )}
            {page.game_changer && (
              <GameChanger gameChanger={page.game_changer} headshots={page.headshots} blurb={page.blurbs.game_changer} />
            )}
            <Awards awards={page.awards} headshots={page.headshots} blurb={page.blurbs.awards} />
            {page.leaders.length > 0 && (
              <PositionLeaders leaders={page.leaders} headshots={page.headshots} blurb={page.blurbs.position_leaders} />
            )}
            <Trades trades={page.trades} avatars={page.avatars} managersHref={managersHref} />
            <MedianGame median={page.median} avatars={page.avatars} blurb={page.blurbs.median} />
            <Standings
              table={page.table}
              avatars={page.avatars}
              managersHref={managersHref}
              hasMedianGame={page.median !== null}
            />
            <NextWeek week={page.week} games={page.next} avatars={page.avatars} blurb={page.blurbs.next_week} />
            <WeekFooter prior={prior} next={next} />
          </div>
        </PageColumn>
      </div>
    </>
  );
}
