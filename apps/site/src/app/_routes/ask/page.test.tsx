/**
 * Tests for the hidden route /ask/ of the front door, which the client build writes while the flag front_door is off.
 * The page is the front door, with noindex, and the Home row of the menu is the current page, because the front door is Home.
 */
import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { readFixtureSite } from "@/fixtures/sites";
import { homeHref } from "@/lib/routes";
import { pageTitle } from "@/app/shell-props";
import AskPage, { metadata } from "./page";

beforeEach(() => readFixtureSite("cpc"));

afterEach(() => {
  cleanup();
  localStorage.clear();
});

describe("the hidden route /ask/", () => {
  it("asks no search engine to index the page, and keeps the title of the site", () => {
    expect(metadata.robots).toEqual({ index: false });
    expect(metadata.title).toBe(pageTitle());
  });

  it("is the front door: the sheet of Your team on a first visit, then the ask box", async () => {
    render(<AskPage />);
    expect(await screen.findByRole("dialog", { name: "Which team is yours?" })).toBeTruthy();
  });

  it("marks the Home row as the current page with a check, and no menu item links to /ask/", () => {
    render(<AskPage />);
    fireEvent.click(screen.getByRole("button", { name: "Open the menu" }));
    const menu = screen.getByRole("navigation", { name: "Pages" });
    const current = within(menu).getByRole("link", { current: "page" });
    expect(current.getAttribute("href")).toBe(homeHref());
    expect(current.querySelector("[data-check]")).toBeTruthy();
    for (const link of screen.getAllByRole("link")) expect(link.getAttribute("href")).not.toContain("/ask");
  });
});
