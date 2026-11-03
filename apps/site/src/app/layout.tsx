/**
 * Root layout for the app. It sets the viewport meta and loads globals.css.
 * Every page of the site uses it.
 */
import "./globals.css";
import type { Viewport } from "next";
import type { ReactNode } from "react";
import { usageCode } from "@/lib/config";
import { BOOT_SCRIPT } from "@/lib/theme";
import { usageScriptUrl } from "@/lib/usage";

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({ children }: { children: ReactNode }) {
  const usageUrl = usageScriptUrl(usageCode);
  return (
    // suppressHydrationWarning: the boot script may add the dark class before React hydrates.
    // The server markup has no class, so the two differ on purpose.
    <html lang="en" suppressHydrationWarning>
      <head>
        {/* Inline and first in the head, so the stored theme applies before the body paints. */}
        <script dangerouslySetInnerHTML={{ __html: BOOT_SCRIPT }} />
        {/* The count script skips localhost on its own, so dev builds send nothing. */}
        {usageUrl && <script async data-goatcounter={usageUrl} src="https://gc.zgo.at/count.js" />}
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
