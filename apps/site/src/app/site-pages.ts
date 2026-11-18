/**
 * Builds the pages of the Site answer from the Menu that the shell shows: each item but Home, then the midseason report
 * and the sim. Each page takes the blurb and the Tool mark of its package, and the front door sends the list with each ask.
 */
import { clientValues } from "@/generated/client-values";
import { menuLinks, siteLines } from "@/generated/registry";
import type { MenuItem, MenuLinks, PackageName, SiteLines } from "@/lib/client-values";
import { homeHref } from "@/lib/routes";
import { menuPages } from "./shell-props";

/* One page of the Site answer: the package name as its key, the label and the link of the Menu, its blurb, and its
   Tool mark. */
export type SitePage = { key: PackageName; label: string; href: string; blurb: string; tool: boolean };

/* The label of the sim while it has no Menu link of its own and lives in the sim section of the midseason report. */
const SIM_LABEL = "Playoff Sim";

/* The pages of the Site answer, in the order of the Menu, then the midseason report, then the sim. A package with no
   site line, or with no page to link yet, gives no page. The sim links to the sim section of the midseason report,
   `#sim`, until the sim gets a Menu link of its own, which then wins. */
export function sitePages(items: MenuItem[], links: MenuLinks, lines: SiteLines, packages: PackageName[]): SitePage[] {
  const pages = menuPages(items, links, homeHref()).flatMap((item): SitePage[] => {
    const line = item.kind === "home" ? undefined : lines[item.kind];
    return line ? [{ key: item.kind as PackageName, label: item.label, href: item.href, ...line }] : [];
  });
  const shown = new Set(pages.map((page) => page.key));
  const add = (key: PackageName, label: string | undefined, href: string | undefined) => {
    const line = lines[key];
    if (line && label && href && !shown.has(key)) pages.push({ key, label, href, ...line });
  };
  const report = packages.includes("midseason") ? links.midseason?.() : null;
  if (report) add("midseason", report.label, report.href);
  if (packages.includes("sim")) {
    const own = links.sim?.();
    if (own) add("sim", own.label, own.href);
    else if (report && packages.includes("midseason")) add("sim", SIM_LABEL, `${report.href}#sim`);
  }
  return pages;
}

/* The pages of the Site answer of this client, from the Menu of the build. */
export function clientSitePages(): SitePage[] {
  return sitePages(clientValues.menu.items, menuLinks, siteLines, clientValues.packages);
}
