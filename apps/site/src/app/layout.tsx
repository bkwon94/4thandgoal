/**
 * Root layout for the app. It sets the viewport meta, loads globals.css and the fonts, and sets the first paint of the brand.
 * Every page of the site uses it.
 */
import "./globals.css";
import type { Viewport } from "next";
import type { ReactNode } from "react";
import { usageCode } from "@/lib/config";
import { pageParts } from "@/generated/registry";
import { stableId } from "@cpc/design/lib/stable-id";
import { paintOf } from "@cpc/design/lib/theme";
import { UsageScript } from "@cpc/design/shell/usage-script";
import { fontVariables } from "./fonts/fonts";
import { takesEggs } from "./shell-props";
import { SITE_VIEWPORT } from "./viewport";

export const viewport: Viewport = SITE_VIEWPORT;

export default function RootLayout({ children }: { children: ReactNode }) {
  // Every brand ships dark on <html>, and the boot script removes the class for a stored light choice (ADR 0024).
  const paint = paintOf();
  const eggs = takesEggs();
  return (
    // suppressHydrationWarning: the boot script may remove the dark class before React hydrates.
    // The server markup has the class, so the two differ on purpose.
    <html lang="en" className={[paint.rootClass, fontVariables].filter(Boolean).join(" ")} suppressHydrationWarning {...(eggs ? { "data-eggs": "" } : {})}>
      <head>
        {/* Inline and first in the head, so a stored light choice applies before the body paints. */}
        <script dangerouslySetInnerHTML={{ __html: paint.bootScript }} />
        <UsageScript code={usageCode} />
      </head>
      <body>
        {/* Every browser honors noscript. The (scripting: none) query in globals.css does not reach older browsers,
            so this rule shows every reveal box at rest when scripts are off. */}
        <noscript>
          <style>{"[data-reveal]{opacity:1!important;transform:none!important}"}</style>
        </noscript>
        {children}
        {/* The empty space after the last chapter of an eggs client. It is a target of the egg hunt on every page, so
            it marks no egg. A client without eggs gets no extra gap. */}
        {eggs && <div aria-hidden="true" className="h-sp-6" {...stableId("page-end")} />}
        {/* The part of each package that every page mounts, such as the egg hunt. A client without one mounts none. */}
        {pageParts.map((Part, index) => (
          <Part key={index} />
        ))}
      </body>
    </html>
  );
}
