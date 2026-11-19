/**
 * The menu link of the analyzer package: the Trade Analyzer page, with the default label of its menu item.
 * It also gives the line of its page in the Site answer. The registry imports it only when the client takes analyzer.
 */
import type { Destination } from "@cpc/design/shell/nav";
import type { SiteLine } from "@/lib/client-values";
import { analyzeHref } from "@/lib/routes";

export const menuLink = (): Destination | null => ({ label: "Trade Analyzer", href: analyzeHref() });

/* The line of the page in the Site answer of the front door: a Tool, with its fixed blurb. Code writes it, never Claude. */
export const siteLine: SiteLine = { blurb: "Grades a trade between two or more teams.", tool: true };
