/**
 * The menu link of the rankings package: the power rankings page, with the default label of its menu item.
 * It also gives the line of its page in the Site answer. The registry imports it only when the client takes rankings.
 */
import type { Destination } from "@cpc/design/shell/nav";
import type { SiteLine } from "@/lib/client-values";
import { rankingsHref } from "@/lib/routes";

export const menuLink = (): Destination | null => ({
  label: "Power Rankings",
  href: rankingsHref(),
});

/* The line of the page in the Site answer of the front door: a page to read, with its fixed blurb. Code writes it, never Claude. */
export const siteLine: SiteLine = {
  blurb: "Every team ranked, with the weekly moves.",
  tool: false,
};
