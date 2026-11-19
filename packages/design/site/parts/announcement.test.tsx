/**
 * Tests for the Announcement, the general sheet that introduces a feature once. They render it with a test art slot and
 * test copy (AT-60), and close it each way: "Not now", Escape, a tap on the dim, a drag down, and a press of the link.
 */
import { act, cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { useState } from "react";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import "../ui/sheet-jsdom";
import { standInForAnimate } from "../ui/sheet-drag-jsdom";
import { Announcement } from "./announcement";

let putBack = () => {};
beforeEach(() => {
  putBack = standInForAnimate();
});
afterEach(() => {
  cleanup();
  putBack();
});

const COPY = {
  eyebrow: "New: Test feature",
  title: "A test title",
  line: "One test line.",
  follow: "Open the test",
  dismiss: "Not now",
};

/* The host keeps the open state, as a use of the Announcement does, and logs each close and each follow. */
function Host({ log, startOpen = true }: { log: string[]; startOpen?: boolean }) {
  const [open, setOpen] = useState(startOpen);
  return (
    <Announcement
      open={open}
      siteName="Test League"
      href="/test/"
      copy={COPY}
      art={<p>Test art</p>}
      onDismiss={() => {
        log.push("dismiss");
        setOpen(false);
      }}
      onFollow={() => log.push("follow")}
      onSettled={() => log.push("settled")}
    />
  );
}

const dialog = () => screen.queryByRole("dialog", { name: "A test title" });

/* A mouse drag down the sheet: press on it, move the pointer down in steps, then let go. A browser then fires a click,
   which the Drawer swallows after a drag, so the helper fires it too and the next test starts clean. */
function dragDown(element: Element) {
  const pointer = { pointerId: 1, pointerType: "mouse", button: 0 };
  fireEvent.pointerDown(element, { ...pointer, clientX: 100, clientY: 100 });
  for (const y of [140, 200, 280, 380]) fireEvent.pointerMove(document, { ...pointer, clientX: 100, clientY: y });
  fireEvent.pointerUp(document, { ...pointer, clientX: 100, clientY: 380 });
  fireEvent.click(document.body);
}

describe("the Announcement (AT-60)", () => {
  it("shows the art slot, the eyebrow, the title, the line, the link, and Not now, in that order", () => {
    render(<Host log={[]} />);
    const sheet = dialog()!;
    expect(sheet).toBeTruthy();
    const text = sheet.textContent ?? "";
    const order = ["Test art", "New: Test feature", "A test title", "One test line.", "Open the test", "Not now"].map((part) => text.indexOf(part));
    expect(order.every((at) => at >= 0)).toBe(true);
    expect([...order].sort((a, b) => a - b)).toEqual(order);
    expect(within(sheet).getByRole("link", { name: "Open the test" }).getAttribute("href")).toBe("/test/");
  });

  it("names the site for a screen reader, with no site name on the screen", () => {
    render(<Host log={[]} />);
    const name = within(dialog()!).getByText("Test League", { exact: false });
    expect(name.className).toContain("sr-only");
  });

  it("closes on Not now", async () => {
    const log: string[] = [];
    render(<Host log={log} />);
    fireEvent.click(within(dialog()!).getByRole("button", { name: "Not now" }));
    await waitFor(() => expect(dialog()).toBeNull());
    expect(log).toEqual(["dismiss"]);
  });

  it("closes on Escape", async () => {
    const log: string[] = [];
    render(<Host log={log} />);
    fireEvent.keyDown(dialog()!, { key: "Escape" });
    await waitFor(() => expect(dialog()).toBeNull());
    expect(log).toEqual(["dismiss"]);
  });

  it("closes on a tap on the dim", async () => {
    const log: string[] = [];
    render(<Host log={log} />);
    const dim = document.querySelector<HTMLElement>('[data-slot="drawer-backdrop"]')!;
    const mouse = { pointerId: 1, pointerType: "mouse", button: 0 };
    fireEvent.pointerDown(dim, mouse);
    fireEvent.pointerUp(dim, mouse);
    fireEvent.click(document.body);
    await waitFor(() => expect(dialog()).toBeNull());
    expect(log).toEqual(["dismiss"]);
  });

  it("closes on a drag down", async () => {
    const log: string[] = [];
    render(<Host log={log} />);
    await act(async () => dragDown(dialog()!));
    await waitFor(() => expect(dialog()).toBeNull());
    expect(log).toEqual(["dismiss"]);
  });

  it("reports once that the sheet stopped on open, so the art can start its move", async () => {
    const log: string[] = [];
    render(<Host log={log} />);
    await waitFor(() => expect(log).toEqual(["settled"]));
  });

  it("reports a press of the link as a follow", () => {
    const log: string[] = [];
    render(<Host log={log} />);
    const link = within(dialog()!).getByRole("link", { name: "Open the test" });
    // jsdom does not follow a link, so the test only reads the report.
    fireEvent.click(link);
    expect(log[0]).toBe("follow");
  });
});
