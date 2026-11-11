/**
 * Tests for the hidden route /ask/ of the front door, which the client build writes while the flag front_door is off.
 * The page is the front door, with noindex, and no menu item marks it as the current page (ticket 43 of front-door).
 */
import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { readFixtureSite } from "@/fixtures/sites";
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

  it("marks no menu item as the current page, and no menu item links to /ask/", () => {
    render(<AskPage />);
    const menu = screen.getByRole("navigation", { name: "Bottom menu" });
    expect(within(menu).queryByRole("link", { current: "page" })).toBeNull();
    for (const link of screen.getAllByRole("link")) expect(link.getAttribute("href")).not.toContain("/ask");
  });
});
