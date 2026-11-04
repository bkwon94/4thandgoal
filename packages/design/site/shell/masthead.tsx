/**
 * The black masthead at the top of every page: the brand link, the page subtitle, an optional week line, and the menu.
 * It matches the masthead of the source stylesheet, so a reader cannot tell the two apart.
 */
import type { ReactNode } from "react";
import { currentPage } from "./current-page";
import { LinkRow, Menu, type Brand, type SiteMenu } from "./menu";
import { ThemeButton } from "./theme-button";

/* The week line lives in its own file, so a client component can import it. The pages import it from here. */
export { WeekLine } from "../parts/week-line";

type MastheadProps = {
  // The brand line. It defaults to the league name, which every page shows.
  title?: string;
  // The page line under the brand. The home page leaves it out.
  subtitle?: string;
  // The week line under the brand. Pages with no week line leave it out.
  children?: ReactNode;
  // The home link and the logo of the brand, each with the base path.
  brand: Brand;
  // The layout and the destinations of the menu. The app layer builds them from the menu of client.toml, so the masthead reads no file and builds no route.
  menu: SiteMenu;
  // The href of the open page, with the base path. A static export cannot read the request path, so each page passes its own.
  pageHref?: string;
};

export function Masthead({
  title = "Cornerstone Fantasy Football League",
  subtitle,
  children,
  brand,
  menu,
  pageHref,
}: MastheadProps) {
  const destinations = menu;
  const hamburger = menu.layout === "hamburger";
  // The bar and the tabs show their links as plain anchors with scripts off, so the noscript row lists only the past weeks.
  const noscriptLinks = hamburger ? [...destinations.pages, ...destinations.pastWeeks] : destinations.pastWeeks;
  return (
    // The black band spans the viewport at every tier. The inner box takes the page column, so the content lines up with the page below.
    <header className="bg-band text-on-dark">
      <div className="mx-auto max-w-page px-gutter pt-sp-5 pb-sp-4">
        {/* The brand line: the home link on the left and the menu button at the right end, where a thumb finds it.
            From the desktop tier up the row of the menu takes the place of the button, on its own line under the brand line.
            The grid holds the brand link and the theme button in the first row and the row of the menu in the second. */}
        {/* The bar and the tabs keep the brand line to the home link and the theme button, and put the row on its own line below. */}
        <div
          className={
            hamburger
              ? "flex items-center justify-between gap-sp-3 desktop:grid desktop:grid-cols-[minmax(0,1fr)_auto] desktop:gap-y-sp-4"
              : "flex items-center justify-between gap-sp-3"
          }
        >
          {/* A plain anchor, not next/link: the home page is a static page with no shared state, so the client router adds nothing. */}
          {/* The link is at least 44px tall, so it is a comfortable tap target on a phone. */}
          {/* In the grid of the desktop tier the link keeps the width of its content, so the empty space of the cell is no link. */}
          <a href={brand.home} className="flex min-h-touch items-center gap-sp-3 text-inherit no-underline desktop:justify-self-start">
            {/* The title next to the logo names the link, so the logo is decorative. */}
            <img src={brand.logo} alt="" width={30} height={30} className="size-logo flex-none rounded-full" />
            <div className="h-divider w-px bg-mute" />
            <div>
              {/* The brand name stays as it is under a page translator. Where the title must wrap, the balance splits it into even lines. */}
              <div translate="no" className="text-meta leading-tight font-bold tracking-wide text-balance uppercase">
                {title}
              </div>
              {subtitle && <div className="text-label tracking-caps text-on-dark-muted uppercase">{subtitle}</div>}
            </div>
          </a>
          {hamburger ? (
            <Menu destinations={destinations} pageHref={pageHref} title={title} brand={brand} />
          ) : (
            // The negative margin lines the icon up with the page edge, as the menu button does in the hamburger layout.
            <ThemeButton className="ml-auto -mr-sp-3 [@media(scripting:none)]:hidden" />
          )}
        </div>
        {menu.layout !== "hamburger" && <LinkRow destinations={destinations} pageHref={pageHref} layout={menu.layout} />}
        {/* The menu sheet needs the script, so a reader with scripts off gets the same destinations as a plain row of links. */}
        {noscriptLinks.length > 0 && (
          <noscript>
            <nav aria-label="Menu" className="mt-sp-3 flex flex-wrap gap-x-sp-4">
              {noscriptLinks.map((destination) => (
                <a
                  key={destination.href}
                  href={destination.href}
                  aria-current={currentPage(destination, pageHref)}
                  className="inline-flex min-h-touch items-center text-label font-bold tracking-caps text-on-dark uppercase no-underline aria-[current=page]:text-accent-text"
                >
                  {destination.label}
                </a>
              ))}
            </nav>
          </noscript>
        )}
        {children && <div className="mt-sp-4">{children}</div>}
      </div>
    </header>
  );
}
