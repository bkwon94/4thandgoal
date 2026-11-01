/**
 * The power rankings page at /rankings/, read from the season rankings file at build time.
 * It shows the last week in the file with a chip per week, or a short empty state when the pipeline has not written the file yet.
 */
import type { Metadata } from "next";
import { Masthead } from "@/components/shell/masthead";
import { PageColumn } from "@/components/parts/page-column";
import { PowerRankings } from "@/components/rankings/power-rankings";
import { ChosenWeekLine, WeekChoiceProvider } from "@/components/rankings/week-choice";
import { Blurb } from "@/components/parts/blurb";
import { Chapter } from "@/components/parts/chapter";
import { Label } from "@/components/parts/label";
import { seasonManagersHref } from "@/lib/data/manager-data";
import { latestAvatars, loadRankings } from "@/lib/data/rankings-data";
import { rankingsHref } from "@/lib/routes";
import { mastheadProps } from "@/app/masthead-props";

export const metadata: Metadata = {
  title: "Power Rankings · Cornerstone Fantasy Football League",
};

export default function RankingsPage() {
  const rankings = loadRankings();
  return (
    <>
      {rankings && rankings.weeks.length > 0 ? (
        // The provider holds the chosen week, so the masthead week line and the table read the same week.
        <WeekChoiceProvider weeks={rankings.weeks}>
          <Masthead {...mastheadProps()} subtitle="Power Rankings" pageHref={rankingsHref()}>
            <ChosenWeekLine />
          </Masthead>
          <PageColumn>
            <PowerRankings
              weeks={rankings.weeks}
              avatars={latestAvatars(rankings.season)}
              managersHref={seasonManagersHref(String(rankings.season))}
            />
          </PageColumn>
        </WeekChoiceProvider>
      ) : (
        <>
          <Masthead {...mastheadProps()} subtitle="Power Rankings" pageHref={rankingsHref()} />
          <PageColumn>
            <Chapter>
              <Label heading>Power Rankings</Label>
              <Blurb>No power rankings are published yet.</Blurb>
            </Chapter>
          </PageColumn>
        </>
      )}
    </>
  );
}
