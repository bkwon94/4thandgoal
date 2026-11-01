/**
 * The black masthead at the top of every page: the brand link, the page subtitle, an optional week line, and the menu.
 * It matches the masthead of the source stylesheet, so a reader cannot tell the two apart.
 */
import type { ReactNode } from "react";
import { currentPage } from "@/components/current-page";
import { Menu, type Destinations } from "@/components/menu";
import { basePath } from "@/lib/config";
import { currentManagersHref } from "@/lib/data/manager-data";
import { currentWaiverHref } from "@/lib/data/waiver-data";
import { listWeekSummaries, type WeekSummary } from "@/lib/data/week-data";

/* The week line lives in its own file, so a client component can import it. The pages import it from here. */
export { WeekLine } from "@/components/week-line";

type MastheadProps = {
  // The brand line. It defaults to the league name, which every page shows.
  title?: string;
  // The page line under the brand. The home page leaves it out.
  subtitle?: string;
  // The week line under the brand. Pages with no week line leave it out.
  children?: ReactNode;
  // The waiver page link of the menu. Left out, the masthead reads the current week from public/, and a build with the flag off gets null.
  // A test passes a value to set the link without a temp public/ folder.
  waiverHref?: string | null;
  // The managers index link of the menu. Left out, the masthead reads public/, and a season with no managers file gets null.
  // A test passes a value to set the link without a temp public/ folder.
  managersHref?: string | null;
  // The published weeks, newest first. Left out, the masthead reads them from public/ at build time.
  // A test passes a list to set the menu without a temp public/ folder.
  weeks?: WeekSummary[];
  // The href of the open page, with the base path. A static export cannot read the request path, so each page passes its own.
  pageHref?: string;
};

/* The one list of destinations of the menu. The newest week is the current week, and the rest are the past weeks. */
function destinationsOf(weeks: WeekSummary[], waiverHref: string | null, managersHref: string | null): Destinations {
  const [current, ...past] = weeks;
  const week = (summary: WeekSummary) => ({ label: `Week ${summary.number}`, href: `${basePath}${summary.href}` });
  return {
    pages: [
      { label: "Home", href: `${basePath}/` },
      ...(current ? [week(current)] : []),
      { label: "Power Rankings", href: `${basePath}/rankings/` },
      ...(managersHref ? [{ label: "Managers", href: managersHref }] : []),
      { label: "Trade Analyzer", href: `${basePath}/analyze/` },
      ...(waiverHref ? [{ label: "Waiver Wire", href: waiverHref }] : []),
    ],
    pastWeeks: past.map(week),
  };
}

export function Masthead({
  title = "Cornerstone Fantasy Football League",
  subtitle,
  children,
  waiverHref = currentWaiverHref(),
  managersHref = currentManagersHref(),
  weeks = listWeekSummaries(),
  pageHref,
}: MastheadProps) {
  const destinations = destinationsOf(weeks, waiverHref, managersHref);
  return (
    // The black band spans the viewport at every tier. The inner box takes the page column, so the content lines up with the page below.
    <header className="bg-blk text-on-dark">
      <div className="mx-auto max-w-page px-gutter pt-sp-5 pb-sp-4">
        {/* The brand line: the home link on the left and the menu button at the right end, where a thumb finds it.
            From the desktop tier up the row of the menu takes the place of the button, on its own line under the brand line.
            The grid holds the brand link and the theme button in the first row and the row of the menu in the second. */}
        <div className="flex items-center justify-between gap-sp-3 desktop:grid desktop:grid-cols-[minmax(0,1fr)_auto] desktop:gap-y-sp-4">
          {/* A plain anchor, not next/link: the home page is a static page with no shared state, so the client router adds nothing. */}
          {/* The link is at least 44px tall, so it is a comfortable tap target on a phone. */}
          {/* In the grid of the desktop tier the link keeps the width of its content, so the empty space of the cell is no link. */}
          <a href={`${basePath}/`} className="flex min-h-touch items-center gap-sp-3 text-inherit no-underline desktop:justify-self-start">
            {/* The title next to the logo names the link, so the logo is decorative. */}
            <img src={`${basePath}/images/logo.png`} alt="" width={30} height={30} className="size-logo flex-none rounded-full" />
            <div className="h-divider w-px bg-mute" />
            <div>
              {/* The brand name stays as it is under a page translator. Where the title must wrap, the balance splits it into even lines. */}
              <div translate="no" className="text-meta leading-tight font-bold tracking-wide text-balance uppercase">
                {title}
              </div>
              {subtitle && <div className="text-label tracking-caps text-on-dark-muted uppercase">{subtitle}</div>}
            </div>
          </a>
          <Menu destinations={destinations} pageHref={pageHref} title={title} />
        </div>
        {/* The menu sheet needs the script, so a reader with scripts off gets the same destinations as a plain row of links. */}
        <noscript>
          <nav aria-label="Menu" className="mt-sp-3 flex flex-wrap gap-x-sp-4">
            {[...destinations.pages, ...destinations.pastWeeks].map((destination) => (
              <a
                key={destination.href}
                href={destination.href}
                aria-current={currentPage(destination, pageHref)}
                className="inline-flex min-h-touch items-center text-label font-bold tracking-caps text-on-dark uppercase no-underline aria-[current=page]:text-red-lt"
              >
                {destination.label}
              </a>
            ))}
          </nav>
        </noscript>
        {children && <div className="mt-sp-4">{children}</div>}
      </div>
    </header>
  );
}
