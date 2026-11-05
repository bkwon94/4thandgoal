/**
 * The menu link of the week package: the report of the newest week, with the label "Week N", with the default label of its menu item.
 * The registry of the client build imports it only when the client takes week.
 */
import type { Destination } from "@cpc/design/shell/menu";
import { listWeekSummaries } from "@/lib/data/week-data";

/* The newest published week is the current week. A client with no published week has no week link yet. */
export const menuLink = (): Destination | null => {
  const current = listWeekSummaries()[0];
  return current ? { label: `Week ${current.number}`, href: current.href } : null;
};
