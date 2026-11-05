/**
 * Root layout for the app. It sets the viewport meta, loads globals.css and the fonts, and sets the first paint of the brand.
 * Every page of the site uses it.
 */
import "./globals.css";
import type { Viewport } from "next";
import type { ReactNode } from "react";
import { usageCode } from "@/lib/config";
import { paintOf } from "@cpc/design/lib/theme";
import { UsageScript } from "@cpc/design/shell/usage-script";
import { fontVariables } from "./fonts/fonts";

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({ children }: { children: ReactNode }) {
  // Every brand ships dark on <html>, and the boot script removes the class for a stored light choice (ADR 0024).
  const paint = paintOf();
  return (
    // suppressHydrationWarning: the boot script may remove the dark class before React hydrates.
    // The server markup has the class, so the two differ on purpose.
    <html lang="en" className={[paint.rootClass, fontVariables].filter(Boolean).join(" ")} suppressHydrationWarning>
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
      </body>
    </html>
  );
}
