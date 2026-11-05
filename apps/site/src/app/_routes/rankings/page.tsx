/**
 * The power rankings page at /rankings/, read from the season rankings file at build time.
 * It reads the file and the masthead values, and the rankings package renders the page from them.
 */
import type { Metadata } from "next";
import { RankingsScreen } from "@cpc/rankings/chapters/rankings-screen";
import { seasonManagersHref } from "@/lib/data/manager-data";
import { latestAvatars, loadRankings } from "@/lib/data/rankings-data";
import { rankingsHref } from "@/lib/routes";
import { mastheadProps, pageTitle } from "@/app/masthead-props";

export const metadata: Metadata = {
  title: pageTitle(undefined, "Power Rankings"),
};

export default function RankingsPage() {
  const rankings = loadRankings();
  const filled = rankings && rankings.weeks.length > 0 ? rankings : null;
  return (
    <RankingsScreen
      rankings={filled}
      avatars={filled ? latestAvatars(filled.season) : {}}
      managersHref={filled ? seasonManagersHref(String(filled.season)) : null}
      masthead={mastheadProps()}
      pageHref={rankingsHref()}
    />
  );
}
