/**
 * The seen key of the Tour for the specs of the front door. A spec that checks the front door under the Tour calls
 * skipTour before it opens the page, so it starts as a league mate who already saw the Tour.
 */
import type { Page } from "@playwright/test";
import { TOUR_SEEN_KEY } from "../src/app/front-door/tour-store";

export async function skipTour(page: Page) {
  await page.addInitScript((key) => localStorage.setItem(key, "1"), TOUR_SEEN_KEY);
}
