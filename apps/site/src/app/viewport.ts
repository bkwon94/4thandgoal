/**
 * The viewport of every page. The root layout exports it, and its own module keeps it testable without the fonts.
 * viewport-fit=cover gives the page the safe area of an iPhone, so the ask box of the front door clears the home bar.
 */
import type { Viewport } from "next";

export const SITE_VIEWPORT: Viewport = {
  width: "device-width",
  initialScale: 1,
  // With cover, env(safe-area-inset-bottom) holds the height of the home bar. The dock and the sheet of Your team
  // already add it, so no part sits under the bar (decision 07 of front-door).
  viewportFit: "cover",
  // Chrome on Android then shrinks the layout viewport with the keyboard, so the ask box of the front door sticks right
  // above it. iOS Safari ignores it, and the front door pins the ask box through the inset of the visual viewport.
  interactiveWidget: "resizes-content",
};
