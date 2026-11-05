/**
 * Holds the font files of the look to their budget: exactly two woff2 files, each under its own cap and 56,000 bytes
 * in total, and an OFL.txt beside each one (AT-36). The export check holds the built files and the preloads.
 */
import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { FONT_CAPS as CAPS, FONT_TOTAL as TOTAL } from "./budget";

const FONTS = join(process.cwd(), "src", "app", "fonts");

/* Each woff2 file under the fonts folder, by its path from the folder. */
function woff2Files(dir: string, prefix = ""): string[] {
  return readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const path = join(prefix, entry.name);
    if (entry.isDirectory()) return woff2Files(join(dir, entry.name), path);
    return entry.name.endsWith(".woff2") ? [path] : [];
  });
}

describe("the font files of the look (AT-36)", () => {
  const files = woff2Files(FONTS);

  it("are exactly two woff2 files, one for each font", () => {
    expect(files.map((file) => file.split("/")[0]).sort()).toEqual(Object.keys(CAPS).sort());
  });

  it.each(files)("%s is a real woff2 file under the cap of its font", (file) => {
    const bytes = readFileSync(join(FONTS, file));
    expect(bytes.subarray(0, 4).toString("latin1")).toBe("wOF2");
    expect(bytes.length).toBeLessThanOrEqual(CAPS[file.split("/")[0]]);
  });

  it(`cost ${TOTAL} bytes or less in total`, () => {
    const total = files.reduce((sum, file) => sum + statSync(join(FONTS, file)).size, 0);
    expect(total).toBeLessThanOrEqual(TOTAL);
  });

  it.each(files)("%s has the OFL.txt of its font beside it", (file) => {
    const license = join(FONTS, file.split("/")[0], "OFL.txt");
    expect(existsSync(license)).toBe(true);
    expect(readFileSync(license, "utf8")).toContain("SIL OPEN FONT LICENSE Version 1.1");
  });
});
