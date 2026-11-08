/**
 * The menu link of the eggs package: none, because the egg board is not a menu item, so the dock keeps its five items.
 * The registry of the client build imports it only when the client takes eggs.
 */
import type { Destination } from "@cpc/design/shell/nav";

export const menuLink = (): Destination | null => null;
