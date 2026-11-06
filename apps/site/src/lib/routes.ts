/**
 * One builder per href or src. Each client serves at the root of its own host, so each route starts at /.
 * The app layer calls them, so a link change starts in this file.
 */
import { managerHrefFrom, managerHrefOrNull } from "@cpc/league/hrefs";

export const homeHref = () => "/";
export const rankingsHref = () => "/rankings/";
export const analyzeHref = () => "/analyze/";
/* The week is the folder name, such as week-06, as the published folders name it. */
export const weekHref = (season: string, week: string) => `/${season}/${week}/`;
export const waiverHref = (season: string, week: string) => `${weekHref(season, week)}waiver/`;
export const managersHref = (season: string) => `/${season}/managers/`;
/* The midseason report of one season, such as /midseason/2026/. */
export const midseasonHref = (season: string) => `/midseason/${season}/`;
export const managerHref = (season: string, rosterId: number) => managerHrefFrom(managersHref(season), rosterId);
/* The builders from a managers index href need no other value, so the league package holds them for the package parts.
   The app parts take them from here, so a link change still starts in this file. */
export { managerHrefFrom, managerHrefOrNull };
/* The logo is a plain img on every page, and its src is a path from the root. A client with no logo gives null. */
export const logoSrc = (logo: string | null) => logo;
