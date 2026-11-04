/**
 * The menu link of the analyzer package: the Trade Analyzer page, with the default label of its menu item.
 * The registry of the client build imports it only when the client takes analyzer.
 */
import type { Destination } from "@cpc/design/shell/menu";
import { analyzeHref } from "@/lib/routes";

export const menuLink = (): Destination | null => ({ label: "Trade Analyzer", href: analyzeHref() });
