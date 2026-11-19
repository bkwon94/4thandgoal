/**
 * The menu link of the sim package: the sim page of the season of the newest published week, "Season sim".
 * It also gives the line of its page in the Site answer. The registry imports it only when the client takes sim.
 */
import type { Destination } from "@cpc/design/shell/nav";
import type { SiteLine } from "@/lib/client-values";
import { weekSimSeasons } from "@/lib/data/sim-data";
import { listWeeks } from "@/lib/data/week-data";
import { simHref } from "@/lib/routes";

/* A client with no published week, or a latest season with no week sim file, has no sim link yet. */
export const menuLink = (): Destination | null => {
  const latest = listWeeks().sort((a, b) => Number(b.season) - Number(a.season))[0];
  return latest && weekSimSeasons().includes(latest.season) ? { label: "Season sim", href: simHref(latest.season) } : null;
};

/* The line of the page in the Site answer of the front door: a Tool, with its fixed blurb. Code writes it, never Claude. */
export const siteLine: SiteLine = { blurb: "Plays out the rest of the season, game by game.", tool: true };
