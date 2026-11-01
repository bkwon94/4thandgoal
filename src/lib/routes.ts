/**
 * One builder per destination. Each puts the base path in front of the route.
 * No other module joins the base path to a route, so a link change touches only this file.
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
