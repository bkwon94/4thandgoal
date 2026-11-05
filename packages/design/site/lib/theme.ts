/**
 * The theme choice of the reader in local storage, so the choice holds across visits.
 * A try block guards every access, because a private window or blocked site data makes storage throw.
 */

/* The storage key of the choice. The boot script in the root layout reads the same key before the first paint. */
export const THEME_KEY = "cpc.theme";

/* The class on the root element that turns on the dark theme. The boot script adds the same class. */
export const DARK_CLASS = "dark";

export type Theme = "light" | "dark";

export function storeTheme(theme: Theme): void {
  try {
    localStorage.setItem(THEME_KEY, theme);
  } catch {
    // The theme still switches for this visit. The next load opens in the default theme.
  }
}

/*
 * The boot script is a string because it runs inline in the head, before React loads.
 * A test runs the same string, so the script that ships is the script that is tested.
 * It is plain ES5 and built from the two constants above, so the key and the class never drift.
 */
export const BOOT_SCRIPT = `try{if(localStorage.getItem(${JSON.stringify(THEME_KEY)})==="dark"){document.documentElement.classList.add(${JSON.stringify(DARK_CLASS)})}}catch(e){}`;

/* The sets of a brand, in paint order, as brand.toml gives them. */
export type BrandSets = readonly Theme[];

/*
 * The first paint of a brand. A two-set brand paints light first, and the boot script applies a stored dark choice (ADR 0007).
 * A one-set brand has no choice to apply, so it has no boot script and no theme button. A dark brand puts the dark class on
 * the root at build time, so each dark: style applies from the first paint.
 */
export function paintOf(sets: BrandSets): { rootClass: string | undefined; bootScript: string | null; themeButton: boolean } {
  const both = sets.length > 1;
  return {
    rootClass: !both && sets[0] === "dark" ? DARK_CLASS : undefined,
    bootScript: both ? BOOT_SCRIPT : null,
    themeButton: both,
  };
}
