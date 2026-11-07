/**
 * The listener of the egg hunt: it counts fast taps on an element with a stable id and sends one egg check when they stop.
 * It never blocks a tap, so a link, a toggle, or a chip still does what it always does.
 */
import { DARK_CLASS } from "@cpc/design/lib/theme";
import type { Conditions, EggCheck } from "../lib/api";

/* A tap counts toward a multi-tap when it lands within this gap of the tap before, on the same element. */
export const TAP_GAP_MS = 400;

/* The attribute of each element that a check can name. Its value derives from the data that the element renders. */
export const STABLE_ID = "data-stable-id";

export type ListenerPorts = {
  // The path of the page, such as /midseason/2026/.
  page: () => string;
  // Sends one egg check. The hunt sends it to the API.
  send: (check: EggCheck) => void;
};

/* The state of the conditions on the page now. */
function conditions(root: Document): Conditions {
  return { theme: root.documentElement.classList.contains(DARK_CLASS) ? "dark" : "light" };
}

/* Listen on `root` and return the stop. Only a run of 2 or more taps sends a check, so a normal tap sends none. */
export function listenForEggs(root: Document, ports: ListenerPorts): () => void {
  let run: { id: string; count: number } | null = null;
  let timer: ReturnType<typeof setTimeout> | undefined;

  function flush() {
    const done = run;
    run = null;
    if (done && done.count >= 2) {
      ports.send({ page: ports.page(), target: done.id, action: `tap${done.count}`, conditions: conditions(root) });
    }
  }

  function onTap(event: PointerEvent) {
    if (!event.isPrimary) return;
    const element = event.target instanceof Element ? event.target.closest(`[${STABLE_ID}]`) : null;
    const id = element?.getAttribute(STABLE_ID);
    if (!id) return;
    clearTimeout(timer);
    // The count follows the stable id and not the node, so a render of the same data keeps the count.
    if (run && run.id === id) {
      run = { id, count: run.count + 1 };
    } else {
      // A tap on another element ends the run before it.
      flush();
      run = { id, count: 1 };
    }
    timer = setTimeout(flush, TAP_GAP_MS);
  }

  root.addEventListener("pointerup", onTap);
  return () => {
    clearTimeout(timer);
    run = null;
    root.removeEventListener("pointerup", onTap);
  };
}
