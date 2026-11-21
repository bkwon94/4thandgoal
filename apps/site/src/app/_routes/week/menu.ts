/**
 * The menu link of the week package: the report of the newest week, with the label "Week N", with the default label of its menu item.
 * It also gives the line of its page in the Site answer. The registry imports it only when the client takes week.
 */
import type { Destination } from "@cpc/design/shell/nav";
import type { SiteLine } from "@/lib/client-values";
import { listWeekSummaries } from "@/lib/data/week-data";

/* The newest published week is the current week. A client with no published week has no week link yet. */
export const menuLink = (): Destination | null => {
  const current = listWeekSummaries()[0];
  return current ? { label: `Week ${current.number}`, href: current.href } : null;
};

/* The line of the page in the Site answer of the front door: a page to read, with its fixed blurb. Code writes it, never Claude. */
export const siteLine: SiteLine = {
  blurb: "The recap, scores, and awards of the week.",
  tool: false,
};
