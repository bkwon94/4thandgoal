/**
 * Tests for the DOM that the preload of `bun test` gives each test file. It must act as a browser does where a test sees it:
 * a canceled animation, the frame rate, the page URL, the storage spies, and a short print of each node in a failed expect.
 */
import { afterEach, describe, expect, it, spyOn } from "bun:test";

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

  it("runs about 60 frames per second, as a browser does", async () => {
    let frames = 0;
    let running = true;
    const loop = () => {
      frames += 1;
      if (running) requestAnimationFrame(loop);
    };
    requestAnimationFrame(loop);
    await new Promise((resolve) => setTimeout(resolve, 200));
    running = false;
    // 200 ms is 12 frames at 60 per second. The bounds leave room for a slow timer on a busy machine.
    expect(frames).toBeGreaterThanOrEqual(3);
    expect(frames).toBeLessThanOrEqual(14);
  });

  it("gives each callback of one frame the same time, and runs no canceled callback", async () => {
    const times: number[] = [];
    requestAnimationFrame((time) => times.push(time));
    const canceled = requestAnimationFrame(() => times.push(-1));
    requestAnimationFrame((time) => times.push(time));
    cancelAnimationFrame(canceled);
    await new Promise((resolve) => setTimeout(resolve, 50));
    expect(times).toHaveLength(2);
    expect(times[0]).toBe(times[1]);
  });

  it("has a page URL, so a relative image src fires no error", async () => {
    expect(location.href).toBe("http://localhost:3000/");
    const errors: Event[] = [];
    const image = document.createElement("img");
    image.addEventListener("error", (event) => errors.push(event));
    image.src = "/avatars/1.png";
    document.body.append(image);
    await new Promise((resolve) => setTimeout(resolve, 50));
    image.remove();
    expect(image.src).toBe("http://localhost:3000/avatars/1.png");
    expect(errors).toEqual([]);
  });

  it("lets a spy on the prototype of Storage act after the first call", () => {
    localStorage.setItem("key", "real");
    expect(localStorage.getItem("key")).toBe("real");
    const spy = spyOn(Storage.prototype, "getItem").mockImplementation(() => "fake");
    expect(localStorage.getItem("key")).toBe("fake");
    spy.mockRestore();
    expect(localStorage.getItem("key")).toBe("real");
    localStorage.clear();
  });

  it("prints a node in short form when an expect fails", () => {
    const box = document.createElement("section");
    box.setAttribute("aria-label", "What-if");
    document.body.append(box);
    let message = "";
    try {
      expect(box).toBeNull();
    } catch (error) {
      message = (error as Error).message;
    }
    box.remove();
    // Bun prints each own property of an object, and a happy-dom node reaches the whole window. That print is megabytes.
    expect(message).toContain("<section");
    expect(message.length).toBeLessThan(10_000);
  });
});
