/**
 * Tests for all matchups. They render the week 6 JSON, read the teams and scores, and open a recap.
 * They check what a reader sees and the button state, not the class names.
 */
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { AllMatchups } from "./all-matchups";
import { firstSentence, week6 } from "@/fixtures/week-page";

afterEach(() => {
  cleanup();
});

const recapText = firstSentence(week6.matchups[0].recap);

function renderMatchups() {
  return render(<AllMatchups matchups={week6.matchups} avatars={week6.avatars} />);
}

describe("AllMatchups", () => {
  it("shows the winner's name and score, then the other score and name", () => {
    renderMatchups();
    expect(screen.getByText("Lil Fridge")).toBeTruthy();
    expect(screen.getByText("126.79")).toBeTruthy();
    expect(screen.getByText("88.31 Brock ‘N’ Roll")).toBeTruthy();
    expect(screen.getByText("46.08 To Infinity and Bijan")).toBeTruthy();
  });

  it("shows one closed recap button per matchup", () => {
    renderMatchups();
    const buttons = screen.getAllByRole("button", { name: "Read Recap" });
    expect(buttons.length).toBe(6);
    expect(buttons[0].getAttribute("aria-expanded")).toBe("false");
    expect(buttons[0].getAttribute("aria-controls")).toBeTruthy();
  });

  it("keeps the recap text in the document, so find-in-page finds it", () => {
    renderMatchups();
    expect(screen.getByText(recapText, { exact: false })).toBeTruthy();
  });

  it("opens the recap with the top scorers, then closes it", () => {
    renderMatchups();
    const button = screen.getAllByRole("button", { name: "Read Recap" })[0];
    const panel = document.getElementById(button.getAttribute("aria-controls") ?? "");
    expect(screen.getByText(recapText, { exact: false })).toBeTruthy();
    expect(button.getAttribute("aria-expanded")).toBe("false");
    expect(panel?.getAttribute("aria-hidden")).toBe("true");
    fireEvent.click(button);
    expect(panel?.getAttribute("aria-hidden")).toBe("false");
    expect(button.textContent).toBe("Hide Recap");
    expect(button.getAttribute("aria-expanded")).toBe("true");
    expect(screen.getByText("Top · Lil Fridge")).toBeTruthy();
    expect(screen.getByText("C. McCaffrey 26.2")).toBeTruthy();
    expect(screen.getByText("B. Purdy 17.36")).toBeTruthy();
    expect(screen.getByText(recapText, { exact: false })).toBeTruthy();
    fireEvent.click(button);
    expect(button.textContent).toBe("Read Recap");
    expect(button.getAttribute("aria-expanded")).toBe("false");
    expect(panel?.getAttribute("aria-hidden")).toBe("true");
  });

  it("points the matchup of the week to the top story", () => {
    renderMatchups();
    fireEvent.click(screen.getAllByRole("button", { name: "Read Recap" })[3]);
    expect(screen.getByText(/This is the Matchup of the Week. Read the full story at the top./)).toBeTruthy();
    expect(screen.getByRole("link", { name: "Go to the top story" }).getAttribute("href")).toBe("#motw");
  });

  it("shows a dash for a side with no top scorer", () => {
    const [winner, loser] = week6.matchups[0].sides;
    const matchup = { ...week6.matchups[0], sides: [winner, { ...loser, top: null }] as typeof week6.matchups[0]["sides"] };
    render(<AllMatchups matchups={[matchup]} avatars={week6.avatars} />);
    fireEvent.click(screen.getByRole("button", { name: "Read Recap" }));
    expect(screen.getByText("—")).toBeTruthy();
  });

  it("links the winner and the loser names to their manager pages only when the season has the managers file", () => {
    const { rerender } = render(
      <AllMatchups matchups={week6.matchups} avatars={week6.avatars} managersHref="/2026/managers/" />,
    );
    expect(
      ["Lil Fridge", "Brock ‘N’ Roll"].map((name) => screen.getByRole("link", { name }).getAttribute("href")),
    ).toEqual(["/2026/managers/3/", "/2026/managers/1/"]);
    rerender(<AllMatchups matchups={week6.matchups} avatars={week6.avatars} />);
    expect(screen.queryByRole("link", { name: "Lil Fridge" })).toBeNull();
  });
});
