/**
 * The keyboard signal of the shell: a field that opens the on-screen keyboard marks it here, and the dock tucks away
 * while it is open. The field stays right above the keyboard, through the inset of the visual viewport.
 */
import { useEffect, useState, useSyncExternalStore } from "react";

let open = false;
const listeners = new Set<() => void>();

/* The root carries data-keyboard while the keyboard is open, so the CSS can move what sticks to the foot of the page. */
function setOpen(next: boolean) {
  if (open === next) return;
  open = next;
  document.documentElement.toggleAttribute("data-keyboard", next);
  listeners.forEach((listener) => listener());
}

function subscribe(listener: () => void) {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

/* True while a field that opens the keyboard has the focus. The server render has no keyboard. */
export function useKeyboardOpen(): boolean {
  return useSyncExternalStore(subscribe, () => open, () => false);
}

/*
 * The focus and blur handlers of a field that opens the keyboard. While the field has the focus, the root holds
 * --keyboard-inset: the part of the layout viewport that the keyboard covers. iOS Safari keeps the layout viewport at
 * full height under the keyboard and shrinks only the visual viewport, so a part that sticks to the foot of the layout
 * viewport sits under the keyboard. The inset lifts it to the foot of the visual viewport. Where the layout viewport
 * shrinks with the keyboard, or no keyboard opens, the inset is 0 and nothing moves.
 */
export function useKeyboardField() {
  const [focused, setFocused] = useState(false);
  useEffect(() => {
    if (!focused) return;
    setOpen(true);
    const root = document.documentElement;
    const view = window.visualViewport;
    const place = () => {
      if (!view) return;
      const inset = Math.max(0, root.clientHeight - view.height - view.offsetTop);
      root.style.setProperty("--keyboard-inset", `${Math.round(inset)}px`);
    };
    place();
    // The keyboard opens over about 250 ms, and iOS scrolls the visual viewport to show the field, so each step places it again.
    view?.addEventListener("resize", place);
    view?.addEventListener("scroll", place);
    return () => {
      view?.removeEventListener("resize", place);
      view?.removeEventListener("scroll", place);
      root.style.removeProperty("--keyboard-inset");
      setOpen(false);
    };
  }, [focused]);
  return { onFocus: () => setFocused(true), onBlur: () => setFocused(false) };
}
