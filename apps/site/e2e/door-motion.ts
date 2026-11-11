/**
 * The helpers of the motion tests of the front door: open the door with a kept passphrase, open a Topic, ask a question,
 * and sample a value of the page on each frame until it holds still.
 */
import { type Page, expect } from "@playwright/test";

/* Open the door at `href` and pick the first team, with a kept passphrase. The API calls fail, because the run uses no
   real API, so a typed question ends as a note, and its bubble still shows in the Thread. */
export async function openDoor(page: Page, href: string) {
  await page.route((url) => url.hostname !== "127.0.0.1", (route) => route.abort());
  await page.addInitScript(() => localStorage.setItem("cpc.passphrase", "test"));
  await page.goto(href);
  await page.getByRole("dialog").getByRole("button").first().click();
  await expect(page.getByRole("textbox", { name: "Ask a question" })).toBeVisible();
}

/* Open a league Topic from the list under "More", so the test needs no Suggestion of the day. */
export async function openTopic(page: Page, name: string) {
  await page.getByRole("button", { name: "More" }).click();
  await page.getByRole("list", { name: "All Topics" }).getByRole("button", { name: new RegExp(`^${name}:`) }).click();
  await expect(page.getByRole("article", { name })).toBeVisible();
}

/* Type a question into the ask box and send it. */
export async function askQuestion(page: Page, question: string) {
  await page.getByRole("textbox", { name: "Ask a question" }).fill(question);
  await page.getByRole("button", { name: "Send" }).click();
}

/* Start to run `read` in the page on each frame. `read` runs in the page, so it uses no value of the test. */
export async function startSamples<T>(page: Page, read: () => T) {
  await page.evaluate((source) => {
    const run = new Function(`return (${source})()`) as () => unknown;
    const store = window as unknown as { doorSamples: unknown[] };
    store.doorSamples = [];
    const tick = () => {
      store.doorSamples.push(run());
      requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }, read.toString());
}

/* Wait until the last `frames` samples are the same, and return each sample since the start. */
export async function samplesWhenStill<T>(page: Page, frames = 20): Promise<T[]> {
  return page.evaluate(
    (frames) =>
      new Promise<T[]>((done) => {
        const store = window as unknown as { doorSamples: T[] };
        const check = () => {
          const last = store.doorSamples.slice(-frames - 1).map((sample) => JSON.stringify(sample));
          const still = last.length > frames && last.every((sample) => sample === last[0]);
          if (still || store.doorSamples.length > 900) done([...store.doorSamples]);
          else requestAnimationFrame(check);
        };
        requestAnimationFrame(check);
      }),
    frames,
  );
}
