/**
 * Tests that the launcher, the page card, and the none rows of the Site answer only fade with the reduced-motion media query on (AT-16).
 * The pages come from the real Menu of the cpc build, and the fold opens with no height move and only a fade.
 */
import { fireEvent, render, waitFor, within } from "@testing-library/react";
import "@/fixtures/cpc-site";
import { afterEach, beforeEach, describe, expect, it } from "bun:test";
import { stubGlobal } from "../test/stubs";
import { readFixtureSite, restoreFixtureSite } from "@/fixtures/sites";
import { SiteAnswer } from "@/app/front-door/site-answer";
import { clientSitePages } from "@/app/site-pages";
// The jsdom stand-ins that a ui-sdk part needs, such as the running animations of the fold.
import "@cpc/design/ui/sheet-jsdom";

beforeEach(() => readFixtureSite("cpc"));
afterEach(restoreFixtureSite);

/* matchMedia is a stub that matches the reduced-motion query. Framer Motion reads it when the first part mounts. */
beforeEach(() =>
  stubGlobal(
    "matchMedia",
    (query: string) =>
      ({
        matches: query.includes("prefers-reduced-motion"),
        media: query,
        onchange: null,
        addListener: () => {},
        removeListener: () => {},
        addEventListener: () => {},
        removeEventListener: () => {},
        dispatchEvent: () => false,
      }) as MediaQueryList,
  ),
);

/* No part rises, scales, or blurs. */
function expectNoMove(root: HTMLElement) {
  for (const part of [root, ...root.querySelectorAll<HTMLElement>("*")]) {
    expect(part.style.filter).not.toMatch(/blur/);
    expect(part.style.transform).not.toMatch(/translate|scale/);
  }
}

/* Every part ends at full view: no part stays at opacity 0. */
async function expectShown(root: HTMLElement) {
  await waitFor(() => {
    for (const part of [root, ...root.querySelectorAll<HTMLElement>("*")])
      expect(part.style.opacity).not.toBe("0");
  });
}

describe("Reduced motion on the Site answer (AT-16)", () => {
  it("fades the page card and the rows of its open fold in, with no rise and no blur", async () => {
    const { container } = render(
      <SiteAnswer
        question="where is the trade analyzer"
        page="analyzer"
        pages={clientSitePages()}
      />,
    );
    expectNoMove(container);
    fireEvent.click(within(container).getByRole("button", { name: "All pages · 5" }));
    const rows = within(container).getByRole("list", { name: "Pages" });
    // The panel of the fold never moves its height. Its rise sits behind motion-safe, so reduced motion keeps only the fade.
    const panel = rows.closest<HTMLElement>("[data-slot='collapsible-panel']")!.className;
    expect(panel).not.toMatch(/height/);
    expect(panel).toContain("data-starting-style:opacity-0");
    expect(panel.split(/\s+/).filter((name) => name.includes("translate"))).toEqual(
      expect.arrayContaining([expect.stringMatching(/^motion-safe:/)]),
    );
    expect(
      panel
        .split(/\s+/)
        .filter((name) => name.includes("translate") && !name.startsWith("motion-safe:")),
    ).toEqual([]);
    expectNoMove(container);
    await expectShown(container);
    expectNoMove(container);
  });

  it("fades the tiles of the launcher in, with no pop from 0.96 and no blur", async () => {
    const { container } = render(
      <SiteAnswer question="what tools are there" page="all" pages={clientSitePages()} />,
    );
    expect(within(container).getAllByRole("link")).toHaveLength(6);
    expectNoMove(container);
    await expectShown(container);
    expectNoMove(container);
  });

  it("fades the none rows in, with no rise and no blur", async () => {
    const { container } = render(
      <SiteAnswer question="is there a waiver page" page="missing" pages={clientSitePages()} />,
    );
    expectNoMove(container);
    await expectShown(container);
    expectNoMove(container);
  });
});
