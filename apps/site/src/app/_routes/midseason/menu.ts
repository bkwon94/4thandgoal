/**
 * The menu link of the midseason package: the report of the season of the newest published week, with the default label of its menu item.
 * The registry of the client build imports it only when the client takes midseason.
 */
import type { Destination } from "@cpc/design/shell/nav";
import { midseasonSeasons } from "@/lib/data/midseason-data";
import { listWeeks } from "@/lib/data/week-data";
import { midseasonHref } from "@/lib/routes";

/* A client with no published week, or a latest season with no midseason file, has no report link yet. */
export const menuLink = (): Destination | null => {
  const latest = listWeeks().sort((a, b) => Number(b.season) - Number(a.season))[0];
  return latest && midseasonSeasons().includes(latest.season)
    ? { label: "Midseason Report", href: midseasonHref(latest.season) }
    : null;
};
