/**
 * The theme choice of the reader in local storage, so the choice holds across visits.
 * A try block guards every access, because a private window or blocked site data makes storage throw.
 */

/* The storage key of the choice. The boot script in the root layout reads the same key before the first paint. */
export const THEME_KEY = "cpc.theme";

/* The class on the root element that turns on the dark theme. The export ships it, and the boot script removes it. */
export const DARK_CLASS = "dark";

export type Theme = "light" | "dark";

export function storeTheme(theme: Theme): void {
  try {
    localStorage.setItem(THEME_KEY, theme);
  } catch {
    // The theme still switches for this visit. The next load opens in the default theme, dark.
  }
}

/*
 * The boot script is a string because it runs inline in the head, before React loads.
 * A test runs the same string, so the script that ships is the script that is tested.
 * It is plain ES5 and built from the two constants above, so the key and the class never drift.
 * The export ships the dark class, so the script only removes it for a stored light choice. No choice, a stored dark
 * choice, a value that is not a theme, and blocked storage all keep dark. It reads no system setting (ADR 0024).
 */
export const BOOT_SCRIPT = `try{if(localStorage.getItem(${JSON.stringify(THEME_KEY)})==="light"){document.documentElement.classList.remove(${JSON.stringify(DARK_CLASS)})}}catch(e){}`;

/* The sets of a brand, in paint order, as brand.toml gives them. */
export type BrandSets = readonly Theme[];

/*
 * The first paint of every brand. Each brand gives both sets, so the build puts the dark class on the root, the boot
 * script applies a stored light choice, and the theme button shows. Dark is the default (ADR 0024).
 */
export function paintOf(): { rootClass: string; bootScript: string; themeButton: boolean } {
  return { rootClass: DARK_CLASS, bootScript: BOOT_SCRIPT, themeButton: true };
}
