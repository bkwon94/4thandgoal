/**
 * The two moves of a tap in the dock while the ask box has the focus: keep the focus through the press, and close the
 * keyboard after the action ran. The press must not blur the field, because the blur moves the dock before the click lands.
 */
import type { MouseEvent } from "react";

/* Cancels the move of the focus at mousedown. The click still fires on the target, and the field keeps the keyboard open. */
export function keepFocus(event: MouseEvent) {
  event.preventDefault();
}

/* Blurs the field that holds the focus, so the keyboard closes and the Answer shows. Call it after the action ran. */
export function closeKeyboard() {
  if (document.activeElement instanceof HTMLElement) document.activeElement.blur();
}
