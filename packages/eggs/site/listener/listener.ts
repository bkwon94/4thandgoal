/**
 * The listener of the egg hunt: it reads fast taps, holds, tap combos, and a selected word on an element with a stable
 * id, and sends one egg check for each. It never blocks a tap, so a link, a toggle, or a chip still does what it always does.
 */
import { DARK_CLASS } from "@cpc/design/lib/theme";
import {
  NOT_FOUND,
  OPEN_ID,
  SIM_CHAMPION,
  SIM_SEEDS,
  STABLE_ID,
  TRADE_ANSWER,
  TRADE_KEY,
} from "@cpc/design/lib/stable-id";
import type { Conditions, EggCheck } from "../lib/api";

/* A tap counts toward a multi-tap when it lands within this gap of the tap before, on the same element. */
export const TAP_GAP_MS = 400;

/* The holds of a long press, longest first. A press sends the longest hold that it reaches, on release. */
export const HOLDS_S = [5, 3, 1] as const;

/* A tap combo is tap A, tap B, then a double-tap on C, all within this time from tap A to the last tap on C. */
export const COMBO_MS = 5000;

/* A selection sends its check when it has not changed for this time, so a drag of the handles sends one check. */
export const SELECT_SETTLE_MS = 600;

/* One word: letters and digits, with an apostrophe or a dash inside, such as "don't" or "co-op". */
const WORD = /^[\p{L}\p{N}]+(?:['’-][\p{L}\p{N}]+)*$/u;
const WORD_MARK = /[\p{L}\p{N}'’-]/u;

export { STABLE_ID };

export type ListenerPorts = {
  // The path of the page, such as /midseason/2026/.
  page: () => string;
  // Sends one egg check. The hunt sends it to the API.
  send: (check: EggCheck) => void;
};

/* The distance from the end of the page that still counts as the end, for a page that rounds its scroll. */
const END_SLACK_PX = 4;

/* True when an element with an open id is open: an open fold, a pressed chip, an expanded "Show all", or an open popover. */
function isOpen(element: Element): boolean {
  const on = (name: string) => element.getAttribute(name) === "true";
  const state = element.getAttribute("data-state");
  return on("aria-expanded") || on("aria-pressed") || on("aria-selected") || on("aria-checked")
    || element.hasAttribute("open") || state === "open" || state === "on";
}

/* The value of a mark on the first element that has it, or null. */
function mark(root: Document, name: string): string | null {
  return root.querySelector(`[${name}]`)?.getAttribute(name) ?? null;
}

/* The state of the conditions on the page now: the theme, the open states, the sim outcome, the trade of the analyzer,
   the scroll to the end, and the 404 page. A condition with no state on the page stays out, so the body stays short.
   The API checks the clock window and the weekday on its own clock. */
function conditions(root: Document, scrolledEnd: boolean): Conditions {
  const state: Conditions = { theme: root.documentElement.classList.contains(DARK_CLASS) ? "dark" : "light" };
  const open = [...root.querySelectorAll(`[${OPEN_ID}]`)].filter(isOpen).map((element) => element.getAttribute(OPEN_ID)!);
  if (open.length > 0) state.open = [...new Set(open)].sort();
  const champion = mark(root, SIM_CHAMPION);
  if (champion) state.sim_champion = Number(champion);
  const seeds = mark(root, SIM_SEEDS);
  if (seeds) state.sim_seeds = seeds.split(/\s+/).filter(Boolean);
  const trade = mark(root, TRADE_KEY);
  if (trade) state.trade = trade;
  const answer = mark(root, TRADE_ANSWER);
  if (answer) state.trade_answer = answer;
  if (scrolledEnd) state.scrolled_end = true;
  if (root.querySelector(`[${NOT_FOUND}]`)) state.not_found = true;
  return state;
}

/* The stable id of the element under an event, or null when no element with a stable id holds the event. */
function idOf(event: Event): string | null {
  const element = event.target instanceof Element ? event.target.closest(`[${STABLE_ID}]`) : null;
  return element?.getAttribute(STABLE_ID) || null;
}

/* The mark of a text node next to an offset, or "" at the edge of the node or for a node that is not text. */
function markAt(node: Node, offset: number): string {
  return node.nodeType === Node.TEXT_NODE ? (node.textContent ?? "").charAt(offset) : "";
}

/* The stable id and the word of a selection of one whole word in an element with a stable id, or null. A selection
   with a space at an end, as a double-click makes, keeps its word. A part of a word or two words is null. */
function selectedWord(root: Document): { id: string; word: string } | null {
  const selection = root.getSelection();
  if (!selection || selection.isCollapsed || selection.rangeCount === 0) return null;
  const text = selection.toString();
  const word = text.trim();
  if (!WORD.test(word)) return null;
  const range = selection.getRangeAt(0);
  // A space at an end of the selection already parts the word from the next mark, so only a bare end needs a check.
  if (text.startsWith(word) && WORD_MARK.test(markAt(range.startContainer, range.startOffset - 1))) return null;
  if (text.endsWith(word) && WORD_MARK.test(markAt(range.endContainer, range.endOffset))) return null;
  const node = range.commonAncestorContainer;
  const element = (node instanceof Element ? node : node.parentElement)?.closest(`[${STABLE_ID}]`);
  const id = element?.getAttribute(STABLE_ID);
  return id ? { id, word: word.toLowerCase() } : null;
}

/* The hold that a press of `ms` reaches, or null for a press under the shortest hold. */
function holdOf(ms: number): number | null {
  return HOLDS_S.find((hold) => ms >= hold * 1000) ?? null;
}

/* Listen on `root` and return the stop. Only a run of 2 or more taps or a long press sends a check, so a normal tap
   sends none. */
export function listenForEggs(root: Document, ports: ListenerPorts): () => void {
  // The run of fast taps on one stable id: its count and the time of its last tap.
  let run: { id: string; count: number; at: number } | null = null;
  // The single taps before the run, oldest first, for the trail of a tap combo. Only the last two count.
  let singles: { id: string; at: number }[] = [];
  let timer: ReturnType<typeof setTimeout> | undefined;
  // The press that is down now: its stable id and the time it went down.
  let down: { id: string; at: number } | null = null;

  // The wait for the selection to settle, and the key of the last selection that sent a check.
  let settle: ReturnType<typeof setTimeout> | undefined;
  let lastSelection = "";
  // The page where the reader scrolled to the end. A new page starts with no scroll to the end.
  let endOf: string | null = null;

  function send(target: string, action: string, extra: { trail?: string[]; word?: string } = {}) {
    const page = ports.page();
    const check: EggCheck = { page, target, action, conditions: conditions(root, endOf === page) };
    const trail = extra.trail ?? [];
    ports.send({ ...check, ...(trail.length > 0 ? { trail } : {}), ...(extra.word ? { word: extra.word } : {}) });
  }

  function onSelectionSettled() {
    const selected = selectedWord(root);
    const key = selected ? `${selected.id} ${selected.word}` : "";
    // The browser fires many changes for one selection, so one selection sends one check.
    if (selected && key !== lastSelection) send(selected.id, "select", { word: selected.word });
    lastSelection = key;
  }

  function onSelectionChange() {
    clearTimeout(settle);
    settle = setTimeout(onSelectionSettled, SELECT_SETTLE_MS);
  }

  function flush() {
    const done = run;
    run = null;
    if (!done) return;
    if (done.count === 1) {
      singles = [...singles, { id: done.id, at: done.at }].slice(-2);
      return;
    }
    // A double-tap carries the single taps before it within the time of a combo, so a tap combo sends one check.
    const trail = done.count === 2 ? singles.filter((single) => done.at - single.at <= COMBO_MS).map((single) => single.id) : [];
    singles = [];
    send(done.id, `tap${done.count}`, { trail });
  }

  function onTap(id: string) {
    clearTimeout(timer);
    // The count follows the stable id and not the node, so a render of the same data keeps the count.
    const at = Date.now();
    if (run && run.id === id) {
      run = { id, count: run.count + 1, at };
    } else {
      // A tap on another element ends the run before it.
      flush();
      run = { id, count: 1, at };
    }
    timer = setTimeout(flush, TAP_GAP_MS);
  }

  function onDown(event: PointerEvent) {
    if (!event.isPrimary) return;
    const id = idOf(event);
    down = id ? { id, at: Date.now() } : null;
  }

  function onUp(event: PointerEvent) {
    if (!event.isPrimary) return;
    const pressed = down;
    down = null;
    // A long press is a hold and not a tap. It names the element where it went down, because a frame of the sim can
    // put another node under the pointer before the release.
    const hold = pressed ? holdOf(Date.now() - pressed.at) : null;
    if (pressed && hold !== null) {
      clearTimeout(timer);
      flush();
      singles = [];
      send(pressed.id, `hold${hold}`);
      return;
    }
    const id = idOf(event) ?? pressed?.id;
    if (id) onTap(id);
  }

  // A scroll or a gesture of the browser cancels the press, so it sends no hold.
  function onCancel() {
    down = null;
  }

  function onScroll() {
    const view = root.defaultView;
    if (!view) return;
    if (view.scrollY + view.innerHeight >= root.documentElement.scrollHeight - END_SLACK_PX) endOf = ports.page();
  }

  root.addEventListener("pointerdown", onDown);
  root.addEventListener("pointerup", onUp);
  root.addEventListener("pointercancel", onCancel);
  root.addEventListener("selectionchange", onSelectionChange);
  root.defaultView?.addEventListener("scroll", onScroll, { passive: true });
  return () => {
    clearTimeout(timer);
    clearTimeout(settle);
    run = null;
    singles = [];
    down = null;
    root.removeEventListener("pointerdown", onDown);
    root.removeEventListener("pointerup", onUp);
    root.removeEventListener("pointercancel", onCancel);
    root.removeEventListener("selectionchange", onSelectionChange);
    root.defaultView?.removeEventListener("scroll", onScroll);
  };
}
