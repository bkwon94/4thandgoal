/**
 * The menu link of the managers package: the managers index of the latest season, with the default label of its menu item.
 * It also gives the line of its page in the Site answer. The registry imports it only when the client takes managers.
 */
import type { Destination } from "@cpc/design/shell/nav";
import type { SiteLine } from "@/lib/client-values";
import { currentManagersHref } from "@/lib/data/manager-data";

export const menuLink = (): Destination | null => {
  const href = currentManagersHref();
  return href === null ? null : { label: "Managers", href };
};

/* The line of the page in the Site answer of the front door: a page to read, with its fixed blurb. Code writes it, never Claude. */
export const siteLine: SiteLine = {
  blurb: "Each manager, with the grades of the season.",
  tool: false,
};
