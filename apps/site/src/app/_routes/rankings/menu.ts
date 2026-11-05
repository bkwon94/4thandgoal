/**
 * The menu link of the rankings package: the power rankings page, with the default label of its menu item.
 * The registry of the client build imports it only when the client takes rankings.
 */
import type { Destination } from "@cpc/design/shell/nav";
import { rankingsHref } from "@/lib/routes";

export const menuLink = (): Destination | null => ({ label: "Power Rankings", href: rankingsHref() });
