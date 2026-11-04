/**
 * The menu link of the managers package: the managers index of the latest season, with the default label of its menu item.
 * The registry of the client build imports it only when the client takes managers.
 */
import type { Destination } from "@cpc/design/shell/menu";
import { currentManagersHref } from "@/lib/data/manager-data";

export const menuLink = (): Destination | null => {
  const href = currentManagersHref();
  return href === null ? null : { label: "Managers", href };
};
