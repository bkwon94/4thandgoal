/**
 * Tests for the root layout: the page-end target and the data-eggs mark on the root appear only for a client that
 * takes the eggs package, so another client gets no extra gap and no egg CSS scope.
 */
import { renderToStaticMarkup } from "react-dom/server";
import { beforeEach, describe, expect, it, vi } from "vitest";

let eggs = true;
vi.mock("./shell-props", () => ({ takesEggs: () => eggs }));
// next/font compiles in the Next build only, so the test gives the layout plain font variables.
vi.mock("./fonts/fonts", () => ({ fontVariables: "" }));

import RootLayout from "./layout";

function markup(): string {
  return renderToStaticMarkup(<RootLayout>{null}</RootLayout>);
}

describe("RootLayout", () => {
  beforeEach(() => {
    eggs = true;
  });

  it("adds the page-end target and the data-eggs mark for a client that takes eggs", () => {
    const html = markup();
    expect(html).toContain('data-stable-id="page-end"');
    expect(html).toMatch(/<html[^>]* data-eggs=""/);
  });

  it("adds neither for a client that omits eggs", () => {
    eggs = false;
    const html = markup();
    expect(html).not.toContain("page-end");
    expect(html).not.toContain("data-eggs");
  });
});
