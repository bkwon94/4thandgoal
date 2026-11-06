/**
 * Tests for the boot script. They run the same string the root layout inlines, against jsdom.
 * The export ships the dark class on the root, so each test starts dark and reads the class after the script runs.
 */
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { BOOT_SCRIPT, DARK_CLASS, paintOf, THEME_KEY } from "./theme";

const root = document.documentElement;

function runBootScript() {
  new Function(BOOT_SCRIPT)();
}

/* The static export puts the dark class on <html>, so the script always starts from dark. */
beforeEach(() => {
  root.classList.add(DARK_CLASS);
});

afterEach(() => {
  root.classList.remove(DARK_CLASS);
  localStorage.clear();
  vi.restoreAllMocks();
});

describe("boot script", () => {
  it("keeps the dark class when nothing is stored (AT-1)", () => {
    runBootScript();
    expect(root.classList.contains(DARK_CLASS)).toBe(true);
  });

  it("removes the dark class when the stored choice is light (AT-3)", () => {
    localStorage.setItem(THEME_KEY, "light");
    runBootScript();
    expect(root.classList.contains(DARK_CLASS)).toBe(false);
  });

  it("keeps the dark class when the stored choice is dark", () => {
    localStorage.setItem(THEME_KEY, "dark");
    runBootScript();
    expect(root.classList.contains(DARK_CLASS)).toBe(true);
  });

  it("keeps the dark class for a stored value that is not a theme", () => {
    localStorage.setItem(THEME_KEY, "system");
    runBootScript();
    expect(root.classList.contains(DARK_CLASS)).toBe(true);
  });

  it("keeps the dark class and throws nothing when storage is blocked", () => {
    vi.spyOn(Storage.prototype, "getItem").mockImplementation(() => {
      throw new Error("blocked");
    });
    expect(runBootScript).not.toThrow();
    expect(root.classList.contains(DARK_CLASS)).toBe(true);
  });

  it("reads no system setting, so a light system setting still opens dark (AT-39)", () => {
    expect(BOOT_SCRIPT).not.toContain("matchMedia");
    expect(BOOT_SCRIPT).not.toContain("prefers-color-scheme");
  });
});

describe("the first paint of a brand", () => {
  it("paints every brand dark from the build, with the boot script and the theme button (AT-1, AT-4)", () => {
    expect(paintOf()).toEqual({ rootClass: DARK_CLASS, bootScript: BOOT_SCRIPT, themeButton: true });
  });
});
