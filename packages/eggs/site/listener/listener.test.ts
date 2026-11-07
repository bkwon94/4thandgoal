/**
 * Tests for the listener of the egg hunt. They fire real pointer events on a rendered page and read the checks that
 * it sends through its send port.
 */
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { EggCheck } from "../lib/api";
import { listenForEggs, TAP_GAP_MS } from "./listener";

let sent: EggCheck[];
let stop: () => void;

beforeEach(() => {
  vi.useFakeTimers();
  sent = [];
  document.body.innerHTML = `
    <table><tr>
      <td data-stable-id="luck-3"><span id="inner">+1.20</span></td>
      <td data-stable-id="luck-12">-0.40</td>
      <td id="plain">9</td>
    </tr></table>
    <a id="link" href="#next">Next</a>`;
  document.documentElement.classList.remove("dark");
  stop = listenForEggs(document, { page: () => "/midseason/2026/", send: (check) => sent.push(check) });
});

afterEach(() => {
  stop();
  vi.useRealTimers();
});

function tap(element: Element, gap = 100) {
  element.dispatchEvent(new PointerEvent("pointerup", { bubbles: true, isPrimary: true }));
  vi.advanceTimersByTime(gap);
}

const cell = (id: string) => document.querySelector(`[data-stable-id="${id}"]`)!;

describe("listenForEggs", () => {
  it("sends one check with the page, the stable id, the action, and the theme after three fast taps", () => {
    const target = document.getElementById("inner")!;
    tap(target);
    tap(target);
    tap(target, TAP_GAP_MS + 1);
    expect(sent).toEqual([
      { page: "/midseason/2026/", target: "luck-3", action: "tap3", conditions: { theme: "light" } },
    ]);
  });

  it("sends the dark theme when the page is dark", () => {
    document.documentElement.classList.add("dark");
    tap(cell("luck-3"));
    tap(cell("luck-3"), TAP_GAP_MS + 1);
    expect(sent[0]).toMatchObject({ action: "tap2", conditions: { theme: "dark" } });
  });

  it("sends no check for a single tap", () => {
    tap(cell("luck-3"), TAP_GAP_MS + 1);
    expect(sent).toEqual([]);
  });

  it("starts a new count when a tap lands more than 400 ms after the one before", () => {
    tap(cell("luck-3"), TAP_GAP_MS + 1);
    tap(cell("luck-3"));
    tap(cell("luck-3"), TAP_GAP_MS + 1);
    expect(sent.map((check) => check.action)).toEqual(["tap2"]);
  });

  it("starts a new count on another element", () => {
    tap(cell("luck-3"));
    tap(cell("luck-12"));
    tap(cell("luck-12"), TAP_GAP_MS + 1);
    expect(sent).toEqual([expect.objectContaining({ target: "luck-12", action: "tap2" })]);
  });

  it("sends no check for taps on an element with no stable id", () => {
    const plain = document.getElementById("plain")!;
    tap(plain);
    tap(plain, TAP_GAP_MS + 1);
    expect(sent).toEqual([]);
  });

  it("never blocks the default of a tap", () => {
    const event = new PointerEvent("pointerup", { bubbles: true, cancelable: true, isPrimary: true });
    document.getElementById("link")!.dispatchEvent(event);
    expect(event.defaultPrevented).toBe(false);
  });

  it("sends nothing after the stop", () => {
    stop();
    tap(cell("luck-3"));
    tap(cell("luck-3"), TAP_GAP_MS + 1);
    expect(sent).toEqual([]);
  });
});
