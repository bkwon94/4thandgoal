/**
 * The menu link of the midseason package: the report of the season of the newest published week, with the default label of its menu item.
 * It also gives the line of its page in the Site answer. The registry imports it only when the client takes midseason.
 */
import type { Destination } from "@cpc/design/shell/nav";
import type { SiteLine } from "@/lib/client-values";
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

/* The line of the page in the Site answer of the front door: a page to read, with its fixed blurb. Code writes it, never Claude. */
export const siteLine: SiteLine = { blurb: "The midseason awards, grades, and roasts.", tool: false };
