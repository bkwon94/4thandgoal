/**
 * Builds the masthead props that every page shares: the published weeks and the links of the menu.
 * It reads public/ at build time in the app layer, so the masthead itself reads no file and builds no route.
 */
import type { MastheadLinks } from "@/components/masthead";
import { currentManagersHref } from "@/lib/data/manager-data";
import { currentWaiverHref } from "@/lib/data/waiver-data";
import { listWeekSummaries } from "@/lib/data/week-data";
import { analyzeHref, homeHref, logoSrc, rankingsHref } from "@/lib/routes";
import type { WeekSummary } from "@/lib/week-types";

export function mastheadProps(): { weeks: WeekSummary[]; links: MastheadLinks } {
  return {
    weeks: listWeekSummaries(),
    links: {
      home: homeHref(),
      rankings: rankingsHref(),
      analyze: analyzeHref(),
      logo: logoSrc(),
      managers: currentManagersHref(),
      waiver: currentWaiverHref(),
    },
  };
}
