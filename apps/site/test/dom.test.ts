/**
 * Tests for the DOM that the preload of `bun test` gives each test file.
 * A canceled animation must act as it does in a browser, where its rejected `finished` promise reports no error.
 */
import { afterEach, describe, expect, it } from "bun:test";

const unhandled: unknown[] = [];
const record = (reason: unknown) => unhandled.push(reason);

afterEach(() => {
  process.off("unhandledRejection", record);
  unhandled.length = 0;
});

describe("the DOM of bun test", () => {
  it("reports no unhandled rejection when an animation is canceled", async () => {
    process.on("unhandledRejection", record);
    const box = document.createElement("div");
    document.body.append(box);

    const animation = box.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 1000 });
    animation.cancel();
    await new Promise((resolve) => setTimeout(resolve, 10));

    box.remove();
    expect(unhandled).toEqual([]);
    // The promise still rejects for a caller that reads it, as in a browser.
    await expect(animation.finished).rejects.toThrow("The animation was canceled.");
  });
});
