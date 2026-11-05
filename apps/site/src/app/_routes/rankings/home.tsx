/**
 * The home part of the rankings package: the Power Rankings chapter above the Tools chapter, with the top three.
 * The registry of the client build imports it only when the client takes rankings.
 */
import { TopThree } from "@cpc/rankings/chapters/top-three";
import { latestAvatars, loadRankings } from "@/lib/data/rankings-data";
import { rankingsHref } from "@/lib/routes";
import type { HomeSection } from "@/lib/client-values";
import { HomeChapter } from "@/app/home-chapter";

/* A missing season file hides the chapter, so the page ships before the pipeline writes the file. */
export const homeSection = (): HomeSection[] => {
  const rankings = loadRankings();
  const week = rankings?.weeks.at(-1);
  if (!rankings || !week) return [];
  return [
    {
      place: "middle",
      part: (
        <HomeChapter id="rankings" title="Power Rankings" note="Playoff odds">
          <TopThree week={week} avatars={latestAvatars(rankings.season)} href={rankingsHref()} />
        </HomeChapter>
      ),
    },
  ];
};
