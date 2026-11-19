/**
 * The menu link of the sim package: none, because the sim has no page of its own and adds no menu item (PRD).
 * It also gives the line of its page in the Site answer. The registry imports it only when the client takes sim.
 */
import type { Destination } from "@cpc/design/shell/nav";
import type { SiteLine } from "@/lib/client-values";

export const menuLink = (): Destination | null => null;

/* The line of the page in the Site answer of the front door: a Tool, with its fixed blurb. Code writes it, never Claude. */
export const siteLine: SiteLine = { blurb: "Plays out the rest of the season, game by game.", tool: true };
