/**
 * The week part of the sim package: the Sim tile of a week page, after Standings. It reads the week sim file of that week
 * at build time and passes the browser only the lines of the tile. The registry imports it only when the client takes sim.
 */
import { simTileOf } from "@cpc/sim/tile/tile";
import { WeekChapter } from "@cpc/week/parts/week-chapter";
import type { WeekTile } from "@/lib/client-values";
import { loadWeekSim } from "@/lib/data/sim-data";
import { simHref } from "@/lib/routes";
import { YourSimTile } from "./your-sim-tile";

/* The id and the heading of the tile, so the rail link and the chapter share one set of words. */
const CHAPTER = { id: "sim", label: "The Race" };

/* A week with no week sim file, such as a week before the sim, has no tile. */
export const weekTile: WeekTile = (season, week) => {
  const sim = loadWeekSim(season, week);
  if (sim === null) return null;
  return {
    chapter: CHAPTER,
    tile: (
      <WeekChapter id={CHAPTER.id} title={CHAPTER.label} note={`After week ${sim.week}`}>
        {/* The chapter rail marks a chapter only while its heading holds the top 30% of the view, and the next heading
            stays out of it. The tile alone is shorter than that band, so from the rail tier it keeps 30vh of height. */}
        <div className="rail:min-h-[30vh]">
          <YourSimTile data={simTileOf(sim)} href={simHref(season)} />
        </div>
      </WeekChapter>
    ),
  };
};
