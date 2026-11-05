/**
 * One builder per href or src. Each joins the base path to the route.
 * The app layer calls them, so a link change starts in this file.
 */
import { managerHrefFrom, managerHrefOrNull } from "@cpc/league/hrefs";
import { basePath } from "./config";

export const homeHref = () => `${basePath}/`;
export const rankingsHref = () => `${basePath}/rankings/`;
export const analyzeHref = () => `${basePath}/analyze/`;
/* The week is the folder name, such as week-06, as the published folders name it. */
export const weekHref = (season: string, week: string) => `${basePath}/${season}/${week}/`;
export const waiverHref = (season: string, week: string) => `${weekHref(season, week)}waiver/`;
export const managersHref = (season: string) => `${basePath}/${season}/managers/`;
export const managerHref = (season: string, rosterId: number) => managerHrefFrom(managersHref(season), rosterId);
/* The builders from a managers index href need no base path, so the league package holds them for the package parts.
   The app parts take them from here, so a link change still starts in this file. */
export { managerHrefFrom, managerHrefOrNull };
/* The logo is a plain img on every page, so its src takes the base path like a link. A client with no logo gives null. */
export const logoSrc = (logo: string | null) => (logo === null ? null : `${basePath}${logo}`);
