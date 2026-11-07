/**
 * Holds globals.css to the callout rule of the egg hunt: the iOS callout is off on every element with a stable id,
 * and on for each link and image, so a long press on a target opens no menu and a link keeps its menu (AT-31).
 */
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";

const GLOBALS = readFileSync(join(process.cwd(), "src/app/globals.css"), "utf8");

/* The declarations of the rule whose selector list is exactly `selector`, with no comment and no space change. */
function declarationsOf(selector: string): string {
  const body = GLOBALS.replace(/\/\*[\s\S]*?\*\//g, "");
  for (const match of body.matchAll(/([^{}]+)\{([^{}]*)\}/g)) {
    const selectors = match[1].split(",").map((part) => part.trim().replace(/\s+/g, " "));
    if (selectors.join(", ") === selector) return match[2];
  }
  return "";
}

describe("the callout rule of globals.css", () => {
  it("turns the iOS callout off on each element with a stable id", () => {
    expect(declarationsOf("[data-eggs] [data-stable-id]")).toMatch(/-webkit-touch-callout:\s*none/);
  });

  it("keeps the callout on for each link and image, inside a target or not", () => {
    expect(declarationsOf(
        "[data-eggs] [data-stable-id] a, [data-eggs] [data-stable-id] img, [data-eggs] a[data-stable-id], [data-eggs] img[data-stable-id]",
      )).toMatch(
      /-webkit-touch-callout:\s*default/,
    );
  });

  it("scopes the callout rule to a client that takes eggs, so another client keeps the callout", () => {
    expect(declarationsOf("[data-stable-id]")).toBe("");
  });

  it("never turns text selection off on a target, so a manager can select a word", () => {
    expect(declarationsOf("[data-eggs] [data-stable-id]")).not.toMatch(/user-select/);
  });
});
