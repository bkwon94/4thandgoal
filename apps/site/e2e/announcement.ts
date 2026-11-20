/**
 * The seen keys of every Announcement for the specs of the front door. A spec that checks the front door under the
 * Announcements calls skipAnnouncements before it opens the page, so it starts as a league mate who saw each one.
 */
import type { Page } from "@playwright/test";
import { ANNOUNCEMENT_KEY_PREFIX } from "../src/app/use-announcement";

/* A spec cannot list the ids of the Announcements to come, and a new one opens on the load beat over the page that the
   spec checks. So each read of a key with the prefix gives "seen", and every other key reads as stored. */
export async function skipAnnouncements(page: Page) {
  await page.addInitScript((prefix) => {
    const read = Storage.prototype.getItem;
    Storage.prototype.getItem = function (key: string) {
      return key.startsWith(prefix) ? "seen" : read.call(this, key);
    };
  }, ANNOUNCEMENT_KEY_PREFIX);
}
