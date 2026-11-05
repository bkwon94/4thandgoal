/**
 * The menu link of the waiver package: the waiver page of the latest week with a waiver file, with the default label of its menu item.
 * The registry of the client build imports it only when the client takes waiver.
 */
import type { Destination } from "@cpc/design/shell/menu";
import { currentWaiverHref } from "@/lib/data/waiver-data";

export const menuLink = (): Destination | null => {
  const href = currentWaiverHref();
  return href === null ? null : { label: "Waiver Wire", href };
};
