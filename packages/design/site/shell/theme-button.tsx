/**
 * The theme button: a 44px icon button that switches the light and the dark theme, and stores the choice.
 * The top band renders it on every page. Every copy on a page shows the same theme.
 */
"use client";

import { MoonIcon, SunIcon } from "lucide-react";
import { useSyncExternalStore } from "react";
import { DARK_CLASS, storeTheme } from "../lib/theme";
import { countEvent } from "../lib/usage";
import { cn } from "../lib/utils";

/* The copies of the button on the page. A press tells each copy, so two copies never disagree. */
const listeners = new Set<() => void>();

function subscribe(listener: () => void) {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

/* The class on the root element is the one source of the theme. The boot script can set it before React runs. */
function rootIsDark() {
  return document.documentElement.classList.contains(DARK_CLASS);
}

/* The server renders the dark theme, the default that the export ships (ADR 0024). It cannot know a stored choice,
   so React reads the root class right after hydration. */
function serverIsDark() {
  return true;
}

function switchTheme() {
  const dark = document.documentElement.classList.toggle(DARK_CLASS);
  storeTheme(dark ? "dark" : "light");
  // The event names the theme the press gives, so the count reads as "presses to dark" and "presses to light".
  countEvent(dark ? "theme-dark" : "theme-light");
  for (const listener of listeners) listener();
}

/* The theme button. The name says what a press does, so a screen reader user knows the result before the press.
   It is a plain button and not a switch, because the name already says the action.
   A switch adds an on or off state to it.
   It has no transition, so the theme switches at once. */
export function ThemeButton({ className }: { className: string }) {
  const dark = useSyncExternalStore(subscribe, rootIsDark, serverIsDark);
  // The icon shows the theme a press gives: the moon in the light theme, the sun in the dark theme.
  const Icon = dark ? SunIcon : MoonIcon;
  return (
    <button
      type="button"
      aria-label={dark ? "Switch to light theme" : "Switch to dark theme"}
      onClick={switchTheme}
      className={cn("press flex size-touch flex-none items-center justify-center text-ink hover-fine:text-accent-ink", className)}
    >
      <Icon aria-hidden className="size-sp-5" />
    </button>
  );
}
