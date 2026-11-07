/**
 * Tests for the listener of the egg hunt. They fire real pointer events on a rendered page and read the checks that
 * it sends through its send port.
 */
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { EggCheck } from "../lib/api";
import { listenForEggs, SELECT_SETTLE_MS, TAP_GAP_MS } from "./listener";

let sent: EggCheck[];
let stop: () => void;

beforeEach(() => {
  vi.useFakeTimers();
  sent = [];
  document.body.innerHTML = `
    <table><tr>
      <td data-stable-id="luck-3"><span id="inner">+1.20</span></td>
      <td data-stable-id="luck-12">-0.40</td>
      <td data-stable-id="luck-7">+0.10</td>
      <td id="plain">9</td>
    </tr></table>
    <a id="link" href="#next">Next</a>
    <p data-stable-id="blurb-luck">Lil Fridge got lucky, and the luckiest team won.</p>
    <p data-stable-id="chapter-title">Lucky chapter title</p>
    <p id="plain-blurb">No stable id here, lucky or not.</p>`;
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

/* A press: the pointer goes down on the element, stays for `ms`, and comes up. */
function press(element: Element, ms: number) {
  element.dispatchEvent(new PointerEvent("pointerdown", { bubbles: true, isPrimary: true }));
  vi.advanceTimersByTime(ms);
  element.dispatchEvent(new PointerEvent("pointerup", { bubbles: true, isPrimary: true }));
  vi.advanceTimersByTime(TAP_GAP_MS + 1);
}

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

  it("sends one check on release for a long press of 1 second, with the hold rounded down", () => {
    press(cell("luck-3"), 1500);
    expect(sent).toEqual([
      { page: "/midseason/2026/", target: "luck-3", action: "hold1", conditions: { theme: "light" } },
    ]);
  });

  it("sends hold3 for a hold of 3.5 seconds and hold5 for a hold of 6 seconds", () => {
    press(cell("luck-3"), 3500);
    press(cell("luck-12"), 6000);
    expect(sent.map((check) => [check.target, check.action])).toEqual([
      ["luck-3", "hold3"],
      ["luck-12", "hold5"],
    ]);
  });

  it("sends no check before the release, and none for a press under 1 second", () => {
    cell("luck-3").dispatchEvent(new PointerEvent("pointerdown", { bubbles: true, isPrimary: true }));
    vi.advanceTimersByTime(4000);
    expect(sent).toEqual([]);
    cell("luck-3").dispatchEvent(new PointerEvent("pointerup", { bubbles: true, isPrimary: true }));
    press(cell("luck-12"), 900);
    expect(sent.map((check) => check.action)).toEqual(["hold3"]);
  });

  it("sends no check for a press that the browser cancels, such as a scroll", () => {
    cell("luck-3").dispatchEvent(new PointerEvent("pointerdown", { bubbles: true, isPrimary: true }));
    vi.advanceTimersByTime(2000);
    cell("luck-3").dispatchEvent(new PointerEvent("pointercancel", { bubbles: true, isPrimary: true }));
    cell("luck-3").dispatchEvent(new PointerEvent("pointerup", { bubbles: true, isPrimary: true }));
    vi.advanceTimersByTime(TAP_GAP_MS + 1);
    expect(sent).toEqual([]);
  });

  it("sends one check for a tap combo: tap A, tap B, then a double-tap on C, with the trail A, B", () => {
    tap(cell("luck-3"), 600);
    tap(cell("luck-12"), 600);
    tap(cell("luck-7"));
    tap(cell("luck-7"), TAP_GAP_MS + 1);
    expect(sent).toEqual([
      {
        page: "/midseason/2026/",
        target: "luck-7",
        action: "tap2",
        trail: ["luck-3", "luck-12"],
        conditions: { theme: "light" },
      },
    ]);
  });

  it("sends no trail when the combo takes more than 5 seconds from tap A to the double-tap", () => {
    tap(cell("luck-3"), 3000);
    tap(cell("luck-12"), 2000);
    tap(cell("luck-7"));
    tap(cell("luck-7"), TAP_GAP_MS + 1);
    expect(sent).toEqual([expect.objectContaining({ target: "luck-7", action: "tap2", trail: ["luck-12"] })]);
  });

  it("starts each combo fresh after a multi-tap, so one trail never carries into the next", () => {
    tap(cell("luck-3"), 600);
    tap(cell("luck-12"), 600);
    tap(cell("luck-7"));
    tap(cell("luck-7"), TAP_GAP_MS + 1);
    tap(cell("luck-3"));
    tap(cell("luck-3"), TAP_GAP_MS + 1);
    expect(sent[1]).toEqual({ page: "/midseason/2026/", target: "luck-3", action: "tap2", conditions: { theme: "light" } });
  });

  it("counts the taps of one stable id across a new node of the same data, as a frame of the sim makes", () => {
    tap(cell("luck-3"));
    // The frame replaces the row with a new node that renders the same data.
    const next = document.createElement("td");
    next.setAttribute("data-stable-id", "luck-3");
    cell("luck-3").replaceWith(next);
    tap(cell("luck-3"));
    tap(cell("luck-3"), TAP_GAP_MS + 1);
    expect(sent.map((check) => check.action)).toEqual(["tap3"]);
  });

  /* Select the text from `start` to `end` of the first text node of the element, then let the selection settle. */
  function select(element: Element, start: number, end: number) {
    const text = element.firstChild!;
    const range = document.createRange();
    range.setStart(text, start);
    range.setEnd(text, end);
    const selection = document.getSelection()!;
    selection.removeAllRanges();
    selection.addRange(range);
    document.dispatchEvent(new Event("selectionchange"));
    vi.advanceTimersByTime(SELECT_SETTLE_MS + 1);
  }

  const blurb = () => cell("blurb-luck");
  const at = (word: string) => blurb().textContent!.indexOf(word);

  it("sends one check with the word and the id of the blurb when the selection settles on one whole word", () => {
    select(blurb(), at("lucky"), at("lucky") + 5);
    expect(sent).toEqual([
      { page: "/midseason/2026/", target: "blurb-luck", action: "select", word: "lucky", conditions: { theme: "light" } },
    ]);
  });

  it("takes the word with its space after it, in lower case, as a double-click selects it", () => {
    select(blurb(), at("Fridge"), at("Fridge") + 7);
    expect(sent).toEqual([expect.objectContaining({ action: "select", word: "fridge" })]);
  });

  it("sends one check for one selection, however many times the browser fires the change", () => {
    select(blurb(), at("lucky"), at("lucky") + 5);
    document.dispatchEvent(new Event("selectionchange"));
    vi.advanceTimersByTime(SELECT_SETTLE_MS + 1);
    expect(sent).toHaveLength(1);
  });

  it("sends no check for a part of a word, for two words, or for a word with no stable id", () => {
    select(blurb(), at("luckiest"), at("luckiest") + 5);
    select(blurb(), at("got"), at("lucky") + 5);
    select(document.getElementById("plain-blurb")!, 24, 29);
    expect(sent).toEqual([]);
  });

  it("sends no check for a word in an element whose stable id is not a blurb id", () => {
    select(cell("chapter-title"), 0, 5);
    expect(sent).toEqual([]);
  });

  /* The conditions of the check of a double-tap on the Luck cell of roster 3. */
  function conditionsNow() {
    sent = [];
    tap(cell("luck-3"));
    tap(cell("luck-3"), TAP_GAP_MS + 1);
    return sent[0].conditions;
  }

  it("sends the open states: each open element with an open id, as an open fold, chip, or Show all marks it", () => {
    document.body.insertAdjacentHTML(
      "beforeend",
      `<button data-open-id="show-all-bench" aria-expanded="true">Show all</button>
       <button data-open-id="show-all-draft" aria-expanded="false">Show all</button>
       <button data-open-id="chip-def" aria-pressed="true">DEF</button>
       <details data-open-id="fold-handcuff" open><summary>Fold</summary></details>
       <div data-open-id="popover-grade" data-state="open"></div>`,
    );
    expect(conditionsNow().open).toEqual(["chip-def", "fold-handcuff", "popover-grade", "show-all-bench"]);
  });

  it("sends no open states when nothing is open, so the body stays short", () => {
    expect(conditionsNow()).toEqual({ theme: "light" });
  });

  it("sends the sim outcome and the trade of the analyzer from the marks on the root of each result", () => {
    document.body.insertAdjacentHTML(
      "beforeend",
      `<section data-sim-champion="12" data-sim-seeds="12:1 3:6"></section>
       <div data-trade-key="3:4046|12:6794" data-trade-answer="no"></div>`,
    );
    expect(conditionsNow()).toEqual({
      theme: "light",
      sim_champion: 12,
      sim_seeds: ["12:1", "3:6"],
      trade: "3:4046|12:6794",
      trade_answer: "no",
    });
  });

  it("sends the 404 page", () => {
    document.body.insertAdjacentHTML("beforeend", `<main data-not-found></main>`);
    expect(conditionsNow()).toEqual({ theme: "light", not_found: true });
  });

  it("sends the scroll to the end after the reader scrolls to the end of the page, and keeps it for the page", () => {
    const html = document.documentElement;
    Object.defineProperty(html, "scrollHeight", { configurable: true, value: 3000 });
    Object.defineProperty(window, "innerHeight", { configurable: true, value: 800 });
    window.scrollY = 1000;
    window.dispatchEvent(new Event("scroll"));
    expect(conditionsNow()).toEqual({ theme: "light" });
    window.scrollY = 2200;
    window.dispatchEvent(new Event("scroll"));
    window.scrollY = 0;
    window.dispatchEvent(new Event("scroll"));
    expect(conditionsNow()).toEqual({ theme: "light", scrolled_end: true });
  });
});
