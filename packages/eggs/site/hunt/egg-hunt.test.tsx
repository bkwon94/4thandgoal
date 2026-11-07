/**
 * Tests for the egg hunt: the find card after a match, the claim sheet, and the end of each path.
 * Each test fires real pointer events on the page and reads what the hunt sent through the one fake of the port.
 */
import { act, cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { TAP_GAP_MS } from "../listener/listener";
import { board, fakeEggsApi, PASSPHRASE } from "../lib/fixtures/eggs-api";
import { EggHunt } from "./egg-hunt";

const MATCH = { match: true as const, claimed: false as const, letter: "C", token: "t1" };

beforeEach(() => {
  localStorage.clear();
  document.documentElement.classList.remove("dark");
});

afterEach(cleanup);

/* Three fast taps on the Luck cell of Lil Fridge, then the end of the run. */
async function tripleTap() {
  const cell = screen.getByText("+1.20");
  for (const _ of [1, 2, 3]) fireEvent.pointerUp(cell, { isPrimary: true });
  await act(() => new Promise((done) => setTimeout(done, TAP_GAP_MS + 50)));
}

function page(api: ReturnType<typeof fakeEggsApi>) {
  return render(
    <>
      <table>
        <tbody>
          <tr>
            <td data-stable-id="luck-3">+1.20</td>
          </tr>
        </tbody>
      </table>
      <EggHunt api={api} />
    </>,
  );
}

describe("EggHunt", () => {
  it("sends one check for a 3-tap and shows the find card with the letter on a match", async () => {
    const api = fakeEggsApi(MATCH);
    page(api);
    await tripleTap();
    expect(api.checks).toEqual([
      { page: "/", target: "luck-3", action: "tap3", conditions: { theme: "light" } },
    ]);
    expect(await screen.findByRole("heading", { name: "You found an egg" })).toBeTruthy();
    expect(screen.getByTestId("egg-letter").textContent).toBe("C");
    expect(screen.getByRole("button", { name: "Claim C" })).toBeTruthy();
  });

  it("shows nothing on no match", async () => {
    const api = fakeEggsApi({ match: false });
    page(api);
    await tripleTap();
    expect(api.checks).toHaveLength(1);
    expect(screen.queryByRole("heading", { name: "You found an egg" })).toBeNull();
  });

  it("says that another manager claimed first on a claimed egg", async () => {
    page(fakeEggsApi({ match: true, claimed: true, letter: "C" }));
    await tripleTap();
    expect(await screen.findByText("Another manager claimed first.")).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Claim C" })).toBeNull();
  });

  it("claims the letter for the picked team into the picked egg word with the typed passphrase", async () => {
    const api = fakeEggsApi(MATCH);
    page(api);
    await tripleTap();
    fireEvent.click(await screen.findByRole("button", { name: "Claim C" }));
    // The sheet lists each manager who hunts, so the commissioner has no pill.
    const pills = within(await screen.findByRole("group", { name: "Your team" })).getAllByRole("button");
    expect(pills).toHaveLength(board.managers.length);
    expect(pills.map((pill) => pill.textContent)).not.toContain("Bo Girds");
    expect(screen.getByRole("button", { name: "Pick your team" })).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "Lil Fridge" }));
    expect(screen.getByRole("button", { name: "Pick an egg word" })).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "CORNERSTONE" }));
    expect(screen.getByRole("button", { name: "Enter the passphrase" })).toBeTruthy();
    fireEvent.change(screen.getByLabelText("Passphrase"), { target: { value: PASSPHRASE } });
    fireEvent.click(screen.getByRole("button", { name: "Claim C" }));
    expect(await screen.findByText("C is yours in CORNERSTONE.")).toBeTruthy();
    expect(api.claims).toEqual([{ token: "t1", roster_id: 3, word: "CORNERSTONE" }]);
    expect(screen.getByRole("link", { name: "See the egg board" }).getAttribute("href")).toBe("/eggs/");
  });

  it("shows no passphrase field when the browser holds the passphrase", async () => {
    localStorage.setItem("cpc.passphrase", PASSPHRASE);
    page(fakeEggsApi(MATCH));
    await tripleTap();
    fireEvent.click(await screen.findByRole("button", { name: "Claim C" }));
    fireEvent.click(await screen.findByRole("button", { name: "Lil Fridge" }));
    fireEvent.click(screen.getByRole("button", { name: "CORNERSTONE" }));
    expect(screen.queryByLabelText("Passphrase")).toBeNull();
    fireEvent.click(screen.getByRole("button", { name: "Claim C" }));
    expect(await screen.findByText("C is yours in CORNERSTONE.")).toBeTruthy();
  });

  it("asks for the passphrase again after a wrong one", async () => {
    localStorage.setItem("cpc.passphrase", "wrong");
    page(fakeEggsApi(MATCH));
    await tripleTap();
    fireEvent.click(await screen.findByRole("button", { name: "Claim C" }));
    fireEvent.click(await screen.findByRole("button", { name: "Lil Fridge" }));
    fireEvent.click(screen.getByRole("button", { name: "CORNERSTONE" }));
    fireEvent.click(screen.getByRole("button", { name: "Claim C" }));
    expect(await screen.findByText("The passphrase is wrong. Ask a league member for it.")).toBeTruthy();
    expect(screen.getByLabelText("Passphrase")).toBeTruthy();
  });
});
