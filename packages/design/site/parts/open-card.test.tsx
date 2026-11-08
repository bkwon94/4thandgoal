/**
 * Tests for the Open card, the one part that opens and closes a card in place.
 * They check the toggle states, the closed panel that find-in-page can still find, and the open on a find match.
 */
import { act, cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { OpenCard } from "./open-card";

afterEach(() => {
  cleanup();
});

function renderCard() {
  render(
    <OpenCard
      panelId="recap-9"
      head={<span>Team A 101.5</span>}
      chips={["Best A. Player 30", "Records 5-3 · 3-5"]}
      text="Team A won the game late."
      action={{ href: "/2026/managers/9/", label: "Manager page", hiddenLabel: " of Team A" }}
    />,
  );
  const head = screen.getByRole("button", { name: /Team A/ });
  const panel = document.getElementById("recap-9")!;
  return { head, panel, chevron: screen.getByRole("button", { name: "Show the details" }) };
}

describe("OpenCard", () => {
  it("starts closed, with the toggle bound to a panel that find-in-page can still find", () => {
    const { head, panel, chevron } = renderCard();
    for (const toggle of [head, chevron]) {
      expect(toggle.getAttribute("aria-expanded")).toBe("false");
      expect(toggle.getAttribute("aria-controls")).toBe("recap-9");
    }
    // hidden="until-found" keeps the text out of sight and out of the tab order, and find-in-page still finds it.
    // inert would hide it from find-in-page in Chromium, so the closed panel has no inert.
    expect(panel.getAttribute("hidden")).toBe("until-found");
    expect(panel.hasAttribute("inert")).toBe(false);
    expect(panel.textContent).toContain("Team A won the game late.");
  });

  it("opens on a tap of the head, with the chips, the text, and the action pill", () => {
    const { head, panel, chevron } = renderCard();
    fireEvent.click(head);
    expect(head.getAttribute("aria-expanded")).toBe("true");
    expect(chevron.getAttribute("aria-expanded")).toBe("true");
    expect(chevron.getAttribute("aria-label")).toBe("Hide the details");
    expect(panel.hasAttribute("hidden")).toBe(false);
    expect(head.closest("[data-open]")?.getAttribute("data-open")).toBe("true");
    expect(within(panel).getAllByRole("listitem").map((chip) => chip.textContent)).toEqual(["Best A. Player 30", "Records 5-3 · 3-5"]);
    const link = screen.getByRole("link");
    expect(link.textContent).toBe("Manager page of Team A");
    expect(link.getAttribute("href")).toBe("/2026/managers/9/");
  });

  it("closes on a tap of the chevron, and hides the panel when the close ends", async () => {
    const { head, panel, chevron } = renderCard();
    fireEvent.click(head);
    fireEvent.click(chevron);
    expect(head.getAttribute("aria-expanded")).toBe("false");
    expect(head.closest("[data-open]")?.getAttribute("data-open")).toBe("false");
    await waitFor(() => expect(panel.getAttribute("hidden")).toBe("until-found"));
  });

  it("opens when find-in-page finds a word of the closed panel", () => {
    const { head, panel } = renderCard();
    // The browser fires beforematch on a hidden="until-found" element before it shows a match inside it.
    act(() => {
      panel.dispatchEvent(new Event("beforematch", { bubbles: true }));
    });
    expect(head.getAttribute("aria-expanded")).toBe("true");
    expect(panel.hasAttribute("hidden")).toBe(false);
  });

  it("draws a row with no frame and no chevron, with the head as the one toggle and the extra panel content", () => {
    render(
      <OpenCard panelId="row-1" look="row" head={<span>1 The Blue Tent</span>} text="Strong at QB.">
        <p>Grade A</p>
      </OpenCard>,
    );
    // A row of a ledger stays short, so the head is the only toggle and the chevron row goes.
    const toggles = screen.getAllByRole("button");
    expect(toggles).toHaveLength(1);
    const card = toggles[0].closest<HTMLElement>(".open-card")!;
    expect(card.querySelector(".rounded-card")).toBeNull();
    fireEvent.click(toggles[0]);
    const panel = document.getElementById("row-1")!;
    expect(panel.hasAttribute("hidden")).toBe(false);
    expect(within(panel).getByText("Grade A")).toBeTruthy();
    expect(within(panel).getByText("Strong at QB.")).toBeTruthy();
  });
});
