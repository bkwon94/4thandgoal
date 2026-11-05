/**
 * Loads the two fonts of the look from the site itself: Space Grotesk for text and JetBrains Mono for numbers.
 * The root layout puts fontVariables on <html>, so the font tokens of globals.css can name each CSS variable.
 */
import localFont from "next/font/local";
import "./fallback.css";

// One Latin variable woff2 file, cut by Google to weights 300 to 700. The default Arial fallback face of next/font has
// close metrics for a grotesk, so it keeps the text in place when the file swaps in.
export const spaceGrotesk = localFont({
  src: "./space-grotesk/space-grotesk-latin-variable.woff2",
  weight: "300 700",
  display: "swap",
  preload: true,
  variable: "--font-space-grotesk",
});

// One Latin variable woff2 file, cut by Google to weights 500 to 800. Arial is proportional, so the default fallback
// breaks the number columns. The fallback is a local monospace face of fallback.css, with the same 0.6 em advance.
export const jetbrainsMono = localFont({
  src: "./jetbrains-mono/jetbrains-mono-latin-variable.woff2",
  weight: "500 800",
  display: "swap",
  preload: true,
  adjustFontFallback: false,
  fallback: ["JetBrains Mono Fallback", "Menlo", "Courier New", "monospace"],
  variable: "--font-jetbrains-mono",
});

/* The class names that set --font-space-grotesk and --font-jetbrains-mono. */
export const fontVariables = `${spaceGrotesk.variable} ${jetbrainsMono.variable}`;
