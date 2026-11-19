/**
 * The menu link of the sim package: the sim page of the season of the newest published week, "Season sim".
 * The registry of the client build imports it only when the client takes sim.
 */
import type { Destination } from "@cpc/design/shell/nav";
import { weekSimSeasons } from "@/lib/data/sim-data";
import { listWeeks } from "@/lib/data/week-data";
import { simHref } from "@/lib/routes";

/* A client with no published week, or a latest season with no week sim file, has no sim link yet. */
export const menuLink = (): Destination | null => {
  const latest = listWeeks().sort((a, b) => Number(b.season) - Number(a.season))[0];
  return latest && weekSimSeasons().includes(latest.season) ? { label: "Season sim", href: simHref(latest.season) } : null;
};
