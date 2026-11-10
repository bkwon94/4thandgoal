/**
 * Tests for the front door at /. Each test renders the page with the real published data of a client and reads what
 * a manager sees: the sheet that asks for Your team on the first visit, then the empty Thread with the ask box.
 */
import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { cpSync, mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, describe, expect, it, vi } from "vitest";
import HomePage from "./page";

/* The temp public/ folders that homeOfClient made, so each test removes its own folder. */
const roots: string[] = [];

afterEach(() => {
  cleanup();
  for (const root of roots.splice(0)) rmSync(root, { recursive: true, force: true });
  localStorage.clear();
  vi.restoreAllMocks();
});

describe("the front door of cpc", () => {
  it("asks for Your team in a sheet that lists the 12 teams, with no skip, no close, and no login (AT-1)", async () => {
    render(<HomePage />);
    const sheet = await screen.findByRole("dialog", { name: "Which team is yours?" });
    const teams = within(sheet).getAllByRole("button");
    expect(teams).toHaveLength(12);
    expect(teams[0].textContent).toContain("All You Need Is Love");
    expect(within(sheet).getByRole("button", { name: /Lil Fridge/ })).toBeTruthy();
    expect(within(sheet).queryByRole("button", { name: /skip|close|later|log ?in|sign ?in/i })).toBeNull();
    expect(within(sheet).queryByRole("textbox")).toBeNull();
    expect(sheet.querySelector("input[type=password]")).toBeNull();
  });

  it("keeps Your team after a reload, so no sheet shows and the empty Thread asks about Lil Fridge (AT-2)", async () => {
    render(<HomePage />);
    const sheet = await screen.findByRole("dialog", { name: "Which team is yours?" });
    fireEvent.click(within(sheet).getByRole("button", { name: /Lil Fridge/ }));
    // The check lands, then the sheet leaves.
    await waitFor(() => expect(screen.queryByRole("dialog")).toBeNull(), { timeout: 3000 });
    expect(screen.getByRole("heading", { level: 1 }).textContent).toBe("Ask about Lil Fridge");

    // A reload renders the page again from the static markup, with the store of the browser as it was.
    cleanup();
    render(<HomePage />);
    const heading = await screen.findByRole("heading", { level: 1, name: "Ask about Lil Fridge" });
    expect(heading).toBeTruthy();
    expect(screen.queryByRole("dialog")).toBeNull();
  });

  it("shows the ask box at the center of the empty Thread, with a send button that waits for a question", async () => {
    localStorage.setItem("cpc.your-team", "3");
    render(<HomePage />);
    const thread = await screen.findByRole("region", { name: "Thread" });
    const box = within(thread).getByRole("form", { name: "Ask" });
    const field = within(box).getByRole("textbox", { name: "Ask a question" });
    const send = within(box).getByRole("button", { name: "Send" }) as HTMLButtonElement;
    expect(field.getAttribute("placeholder")).toBe("Ask about your team");
    expect(send.disabled).toBe(true);
    fireEvent.change(field, { target: { value: "who am i playing sunday" } });
    expect(send.disabled).toBe(false);
  });

  it("opens the sheet again from the Thread, so a manager can change Your team", async () => {
    localStorage.setItem("cpc.your-team", "3");
    render(<HomePage />);
    fireEvent.click(await screen.findByRole("button", { name: "Your team: Lil Fridge. Change the team" }));
    const sheet = await screen.findByRole("dialog", { name: "Which team is yours?" });
    expect(within(sheet).getByRole("button", { name: /Lil Fridge/ }).getAttribute("aria-pressed")).toBe("true");
    fireEvent.click(within(sheet).getByRole("button", { name: /Bo Girds/ }));
    await screen.findByRole("heading", { level: 1, name: "Ask about Bo Girds" }, { timeout: 3000 });
    expect(localStorage.getItem("cpc.your-team")).toBe("6");
  });

  it("asks again when the stored team is no team of the league", async () => {
    localStorage.setItem("cpc.your-team", "99");
    render(<HomePage />);
    expect(await screen.findByRole("dialog", { name: "Which team is yours?" })).toBeTruthy();
  });

  it("shows no hero, no four numbers, no midseason takeover, and no tool tiles (AT-50)", async () => {
    localStorage.setItem("cpc.your-team", "3");
    const { container } = render(<HomePage />);
    await screen.findByRole("heading", { level: 1, name: "Ask about Lil Fridge" });
    expect(screen.queryByRole("region", { name: "Matchup of the Week" })).toBeNull();
    expect(screen.queryByRole("region", { name: "The week in numbers" })).toBeNull();
    expect(screen.queryByRole("region", { name: "2026 Midseason Report" })).toBeNull();
    expect(screen.queryByRole("region", { name: "Tools" })).toBeNull();
    expect(container.querySelectorAll("canvas")).toHaveLength(0);
    // The menu keeps its links, but the main holds no link to a tool page.
    expect(within(screen.getByRole("main")).queryAllByRole("link")).toHaveLength(0);
  });
});

describe("the front door of NorCal", () => {
  it("lists the 12 teams of NorCal in the sheet", async () => {
    const Home = await homeOfClient("norcal");
    render(<Home />);
    const sheet = await screen.findByRole("dialog", { name: "Which team is yours?" });
    expect(within(sheet).getAllByRole("button")).toHaveLength(12);
    expect(within(sheet).getByRole("button", { name: /kaiedmonds/ })).toBeTruthy();
  });
});

/* A temp public/ folder with the published files of one client, as its client build copies them. */
async function homeOfClient(slug: string) {
  const root = mkdtempSync(join(tmpdir(), "home-page-"));
  roots.push(root);
  cpSync(join(process.cwd(), "..", "..", "clients", slug, "published"), join(root, "public"), { recursive: true });
  vi.spyOn(process, "cwd").mockReturnValue(root);
  // The readers read the working folder when they load, so reset them to pick up the temp folder.
  vi.resetModules();
  return (await import("./page")).default;
}
