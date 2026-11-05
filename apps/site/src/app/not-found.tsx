/**
 * The 404 page: the shell, and the hero with "404", a plain line about why, and the buttons to the latest week and home.
 * Next exports it as 404.html, which the Worker of each client serves for a path that no page has.
 */
import type { Metadata } from "next";
import { Hero } from "@cpc/design/parts/hero";
import { Rise } from "@cpc/design/parts/rise";
import { TopBand } from "@cpc/design/shell/top-band";
import { pageTitle, shellProps } from "@/app/shell-props";

export const metadata: Metadata = {
  title: pageTitle(undefined, "Page Not Found"),
};

/* The two buttons of the page. Each is a full pill and a 44px tap target. Each color pair holds 4.5 to 1 in the brand tests. */
const BUTTON =
  "press inline-flex min-h-touch items-center justify-center rounded-pill px-sp-6 text-body font-bold no-underline";

export default function NotFound() {
  const shell = shellProps();
  const latest = shell.menu.weeks[0];
  return (
    <>
      {/* The page is no destination, so it passes no page href, and no item of the shell is marked. */}
      <TopBand {...shell} />
      <main className="mx-auto w-full max-w-page px-gutter py-sp-6">
        <Hero label="Page not found">
          {/* Each line of text sits on a plate, so the grid and the glow never sit under a letter. */}
          <Rise step={0}>
            <div className="plate w-fit font-mono text-meta leading-tight font-bold tracking-wide text-accent-text uppercase">
              ERROR // PAGE NOT FOUND
            </div>
          </Rise>
          <Rise step={1}>
            <h1 className="plate mt-sp-4 mb-0 w-fit font-mono text-hero leading-none font-bold tracking-grade">404</h1>
          </Rise>
          <Rise step={2}>
            <p className="plate mt-sp-4 mb-0 w-fit max-w-measure text-lead leading-body text-on-dark-2">
              This page does not exist. The link may be old, or the week is not out yet.
            </p>
          </Rise>
          <Rise step={3} className="mt-sp-6 flex flex-wrap gap-sp-3">
            {/* A client with no published week has no week to go to, so it shows only the home button. */}
            {latest !== undefined && (
              <a href={latest.href} className={`${BUTTON} bg-accent text-on-dark`}>
                Go to Week {latest.number}
              </a>
            )}
            <a href={shell.brand.home} className={`${BUTTON} border border-rule-dark bg-chip-dark text-on-dark`}>
              Go Home
            </a>
          </Rise>
        </Hero>
      </main>
    </>
  );
}
