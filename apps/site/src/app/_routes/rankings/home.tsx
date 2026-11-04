/**
 * The home section of the rankings package: the Power Rankings chapter beside the Tools chapter, with the top three.
 * The registry of the client build imports it only when the client takes rankings.
 */
import { Reveal } from "@cpc/design/parts/reveal";
import { Chapter } from "@cpc/design/parts/chapter";
import { Label } from "@cpc/design/parts/label";
import { stagger } from "@cpc/design/lib/motion";
import { Movement } from "@/components/rankings/power-rankings";
import { biggestMover } from "@/lib/format/rankings";
import { loadRankings } from "@/lib/data/rankings-data";
import { rankingsHref } from "@/lib/routes";
import type { HomeSection } from "@/lib/client-values";
import { HomeRow } from "@/app/home-row";

/* A missing season file hides the chapter, so the page ships before the pipeline writes the file. */
export const homeSection = (): HomeSection | null => {
  const rankings = loadRankings()?.weeks.at(-1);
  if (!rankings) return null;
  const mover = biggestMover(rankings);
  return {
    place: "beside",
    chapter: (step) => (
      <Chapter>
        <Label heading>Power Rankings</Label>
        <Reveal delay={stagger(step)}>
          <HomeRow href={rankingsHref()} first>
            <b className="mb-sp-1 block text-lead leading-tight group-hover:text-accent-ink">Top Three</b>
            <ol className="m-0 mb-sp-1 list-none p-0">
              {rankings.rows.slice(0, 3).map((row) => (
                <li key={row.roster_id} className="text-meta text-ink-2 tabular-nums">
                  <span className="mr-sp-1 text-mute">{row.rank}</span>
                  {row.name}
                </li>
              ))}
            </ol>
            {mover && (
              <span className="block text-meta text-mute tabular-nums">
                Biggest mover: <Movement movement={mover.movement} /> {mover.name}
              </span>
            )}
            <span className="block text-meta text-mute">See all twelve teams.</span>
          </HomeRow>
        </Reveal>
      </Chapter>
    ),
  };
};
