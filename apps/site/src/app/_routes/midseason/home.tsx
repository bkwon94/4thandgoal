/**
 * The home part of the midseason package: the takeover in place of the usual top through the takeover end week, then
 * the report tile. The registry of the client build imports it only when the client takes midseason.
 */
import { ReportTile } from "@cpc/midseason/home/report-tile";
import { Takeover, takeoverOn } from "@cpc/midseason/home/takeover";
import { loadMidseason } from "@/lib/data/midseason-data";
import { listWeeks, weekNumberOf } from "@/lib/data/week-data";
import type { HomeSection } from "@/lib/client-values";
import { midseasonHref } from "@/lib/routes";

/* The report of the season of the latest published week. A season with no midseason file gives no part.
   listWeeks sorts by season, then by week, so the last ref is the latest. */
export const homeSection = (): HomeSection[] => {
  const ref = listWeeks().at(-1);
  if (!ref) return [];
  const report = loadMidseason(ref.season);
  if (!report) return [];
  const href = midseasonHref(ref.season);
  if (takeoverOn(report, weekNumberOf(ref.week))) {
    return [{ place: "takeover", part: <Takeover report={report} href={href} /> }];
  }
  return [{ place: "middle", part: <ReportTile report={report} href={href} /> }];
};
