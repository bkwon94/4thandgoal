/**
 * Builds the masthead props that every page shares: the published weeks and the links of the menu.
 * It reads public/ at build time in the app layer, so the masthead itself reads no file and builds no route.
 */
import type { MastheadLinks } from "@/components/shell/masthead";
import { menuHrefs } from "@/generated/registry";
import { listWeekSummaries } from "@/lib/data/week-data";
import { homeHref, logoSrc } from "@/lib/routes";
import type { WeekSummary } from "@/lib/week-types";

export function mastheadProps(): { weeks: WeekSummary[]; links: MastheadLinks } {
  // The registry holds only the packages of the client, so an omitted package has no link and no code in the bundle.
  return {
    weeks: listWeekSummaries(),
    links: {
      brand: { home: homeHref(), logo: logoSrc() },
      rankings: menuHrefs.rankings?.() ?? null,
      analyze: menuHrefs.analyzer?.() ?? null,
      managers: menuHrefs.managers?.() ?? null,
      waiver: menuHrefs.waiver?.() ?? null,
    },
  };
}
