/**
 * One builder per destination. Each joins the base path to the route.
 * The app layer calls them, so a link change starts in this file.
 */
import { basePath } from "./config";

export const homeHref = () => `${basePath}/`;
export const rankingsHref = () => `${basePath}/rankings/`;
export const analyzeHref = () => `${basePath}/analyze/`;
/* The week is the folder name, such as week-06, as the published folders name it. */
export const weekHref = (season: string, week: string) => `${basePath}/${season}/${week}/`;
export const waiverHref = (season: string, week: string) => `${weekHref(season, week)}waiver/`;
export const managersHref = (season: string) => `${basePath}/${season}/managers/`;
export const managerHref = (season: string, rosterId: number) => `${managersHref(season)}${rosterId}/`;
/* The logo is a plain img on every page, so its src takes the base path like a link. */
export const logoSrc = () => `${basePath}/images/logo.png`;
