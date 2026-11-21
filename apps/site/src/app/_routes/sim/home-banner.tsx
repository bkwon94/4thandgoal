/**
 * The home part of the sim package: the Announcement of the season sim on the home page. It reads the newest week sim
 * file at build time and passes the browser only the few numbers of the art. The registry imports it only when the client takes sim.
 */
import { previewOf } from "@cpc/sim/announcement/preview";
import { clientValues } from "@/generated/client-values";
import { latestWeekSim } from "@/lib/data/sim-data";
import { listWeeks } from "@/lib/data/week-data";
import { simHref } from "@/lib/routes";
import { SimAnnouncement } from "./announcement";

/* The season of the newest published week, the same season as the menu link. A season with no week sim file has no
   sim page, so it has no Announcement. */
export function HomeBanner() {
  const season = listWeeks().sort((a, b) => Number(b.season) - Number(a.season))[0]?.season;
  const sim = season === undefined ? null : latestWeekSim(season);
  if (season === undefined || sim === null) return null;
  return (
    <SimAnnouncement
      data={previewOf(sim)}
      siteName={clientValues.copy.siteName}
      href={simHref(season)}
    />
  );
}
