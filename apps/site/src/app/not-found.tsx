/**
 * The 404 page: the shell, and the hero with "404", a plain line about why, and the buttons to the latest week and home.
 * Next exports it as 404.html, which the Worker of each client serves for a path that no page has.
 */
import type { Metadata } from "next";
import { driftScene } from "@cpc/design/parts/drift-scene";
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
        <Hero
          label="Page not found"
          title="Page not found"
          // A lost page has no data to chart, so its lights drift and never settle (story 28).
          scene={driftScene()}
          meta="This page does not exist. The link may be old, or the week is not out yet."
          feature={
            /* The big "404" is art, so the title keeps the one title style of every hero. The plate keeps the grid
               and the glow from under each digit. The title names the page, so a screen reader skips the art. */
            <Rise step={1}>
              <div aria-hidden="true" className="plate w-fit font-mono text-hero leading-none font-bold tracking-grade">
                404
              </div>
            </Rise>
          }
          action={
            <Rise step={2} className="flex flex-wrap gap-sp-3">
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
          }
        />
      </main>
    </>
  );
}
