/**
 * The home section of the rankings package: the Power Rankings chapter beside the Tools chapter, with the top three.
 * The registry of the client build imports it only when the client takes rankings.
 */
import { Reveal } from "@cpc/design/parts/reveal";
import { Chapter } from "@cpc/design/parts/chapter";
import { Label } from "@cpc/design/parts/label";
import { stagger } from "@cpc/design/lib/motion";
import { TopThree } from "@cpc/rankings/chapters/top-three";
import { loadRankings } from "@/lib/data/rankings-data";
import { rankingsHref } from "@/lib/routes";
import type { HomeSection } from "@/lib/client-values";
import { HomeRow } from "@/app/home-row";

/* A missing season file hides the chapter, so the page ships before the pipeline writes the file. */
export const homeSection = (): HomeSection | null => {
  const rankings = loadRankings()?.weeks.at(-1);
  if (!rankings) return null;
  return {
    place: "beside",
    chapter: (step) => (
      <Chapter>
        <Label heading>Power Rankings</Label>
        <Reveal delay={stagger(step)}>
          <HomeRow href={rankingsHref()} first>
            <TopThree week={rankings} />
          </HomeRow>
        </Reveal>
      </Chapter>
    ),
  };
};
