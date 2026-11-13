/**
 * The keyboard signal of the shell: a field that opens the on-screen keyboard marks it here, and the dock tucks away
 * while it is open. The field stays right above the keyboard, through the inset of the visual viewport.
 */
import { useEffect, useState, useSyncExternalStore } from "react";

let open = false;
let raised = false;
const listeners = new Set<() => void>();

/* An inset under this height is no keyboard: a toolbar of the browser or a rounding step can shrink the visual viewport
   by a few px, and a part that pins above the keyboard must not jump for it. */
const RAISED_MIN = 80;

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

/* Raised is true while the keyboard covers part of the layout viewport, so a part can pin itself right above it. */
function setRaised(next: boolean) {
  if (raised === next) return;
  raised = next;
  listeners.forEach((listener) => listener());
}

/* True while a field that opens the keyboard has the focus. The server render has no keyboard. */
export function useKeyboardOpen(): boolean {
  return useSyncExternalStore(subscribe, () => open, () => false);
}

/* True while a field has the focus and the keyboard is open, so a part can pin itself right above it. Two cases raise it.
   iOS Safari keeps the layout viewport at full height, so the keyboard covers its foot, and --keyboard-inset holds the
   height that it covers. Chrome on iOS and Android shrink the layout viewport, so its foot is already the top of the
   keyboard, and --keyboard-inset is 0. */
export function useKeyboardRaised(): boolean {
  return useSyncExternalStore(subscribe, () => raised, () => false);
}

/*
 * The focus and blur handlers of a field that opens the keyboard. While the field has the focus, the root holds
 * --keyboard-inset: the part of the layout viewport that the keyboard covers. iOS Safari keeps the layout viewport at
 * full height under the keyboard and shrinks only the visual viewport, so a part that sticks to the foot of the layout
 * viewport sits under the keyboard. The inset lifts it to the foot of the visual viewport. Chrome on iOS and Android
 * shrink the layout viewport instead, so the inset is 0 and the part already sits at the top of the keyboard. The
 * shrink of the layout viewport since the focus marks the keyboard open there. With no keyboard, nothing moves.
 */
export function useKeyboardField() {
  const [focused, setFocused] = useState(false);
  useEffect(() => {
    if (!focused) return;
    setOpen(true);
    const root = document.documentElement;
    const view = window.visualViewport;
    // The keyboard is not open yet, so this is the full height of the layout viewport.
    const full = root.clientHeight;
    const place = () => {
      const inset = view ? Math.max(0, root.clientHeight - view.height - view.offsetTop) : 0;
      const shrink = Math.max(0, full - root.clientHeight);
      root.style.setProperty("--keyboard-inset", `${Math.round(inset)}px`);
      setRaised(inset >= RAISED_MIN || shrink >= RAISED_MIN);
    };
    place();
    // The keyboard opens over about 250 ms, and iOS scrolls the visual viewport to show the field, so each step places it again.
    view?.addEventListener("resize", place);
    view?.addEventListener("scroll", place);
    // A layout viewport that shrinks with the keyboard fires a resize of the window, not of the visual viewport.
    window.addEventListener("resize", place);
    return () => {
      view?.removeEventListener("resize", place);
      view?.removeEventListener("scroll", place);
      window.removeEventListener("resize", place);
      root.style.removeProperty("--keyboard-inset");
      setRaised(false);
      setOpen(false);
    };
  }, [focused]);
  return { onFocus: () => setFocused(true), onBlur: () => setFocused(false) };
}
