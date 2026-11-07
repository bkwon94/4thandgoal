/**
 * Tests for the egg button of the top band, rendered from the board fixture that the API tests hold to the real answer.
 * Its badge is the count of eggs left to find, and a tap opens the egg board.
 */
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { board, fakeEggsApi } from "../lib/fixtures/eggs-api";
import { EggButton, EggButtonScreen } from "./egg-button";

afterEach(cleanup);

describe("EggButton", () => {
  it("opens the egg board and names the count left in its badge", () => {
    render(<EggButton left={6} href="/eggs/" />);
    const link = screen.getByRole("link", { name: "Egg board, 6 eggs left to find" });
    expect(link.getAttribute("href")).toBe("/eggs/");
    expect(link.textContent).toBe("6");
  });

  it("shows no badge before the board loads, and still opens the egg board", () => {
    render(<EggButton left={null} href="/eggs/" />);
    const link = screen.getByRole("link", { name: "Egg board" });
    expect(link.getAttribute("href")).toBe("/eggs/");
    expect(link.textContent).toBe("");
  });

  it("names one egg left in the singular", () => {
    render(<EggButton left={1} href="/eggs/" />);
    expect(screen.getByRole("link", { name: "Egg board, 1 egg left to find" })).toBeTruthy();
  });
});

describe("EggButtonScreen", () => {
  it("reads the count left from the board of the API", async () => {
    render(<EggButtonScreen api={fakeEggsApi({ match: false })} href="/eggs/" />);
    const name = `Egg board, ${board.counts.left} egg left to find`;
    expect((await screen.findByRole("link", { name })).textContent).toBe(String(board.counts.left));
  });
});
