/**
 * Tests for the boot script. They run the same string the root layout inlines, against jsdom.
 * They read the class on the root element, with a stored dark choice, no choice, and blocked storage.
 */
import { afterEach, describe, expect, it, vi } from "vitest";
import { BOOT_SCRIPT, DARK_CLASS, THEME_KEY } from "./theme";

const root = document.documentElement;

function runBootScript() {
  new Function(BOOT_SCRIPT)();
}

afterEach(() => {
  root.classList.remove(DARK_CLASS);
  localStorage.clear();
  vi.restoreAllMocks();
});

describe("boot script", () => {
  it("adds the dark class when the stored choice is dark", () => {
    localStorage.setItem(THEME_KEY, "dark");
    runBootScript();
    expect(root.classList.contains(DARK_CLASS)).toBe(true);
  });

  it("adds no class when nothing is stored", () => {
    runBootScript();
    expect(root.classList.contains(DARK_CLASS)).toBe(false);
  });

  it("adds no class when the stored choice is light", () => {
    localStorage.setItem(THEME_KEY, "light");
    runBootScript();
    expect(root.classList.contains(DARK_CLASS)).toBe(false);
  });

  it("adds no class and throws nothing when storage is blocked", () => {
    vi.spyOn(Storage.prototype, "getItem").mockImplementation(() => {
      throw new Error("blocked");
    });
    expect(runBootScript).not.toThrow();
    expect(root.classList.contains(DARK_CLASS)).toBe(false);
  });
});
