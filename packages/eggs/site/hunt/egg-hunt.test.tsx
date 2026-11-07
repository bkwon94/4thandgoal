/**
 * Tests for the egg hunt: the find and its crack, the claim sheet, and the hero card at the end of each path.
 * Each test fires real pointer events on the page and reads what the hunt sent through the one fake of the port.
 */
import { act, cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { TAP_GAP_MS } from "../listener/listener";
import { EggsError, type Board } from "../lib/api";
import { board, boardWith, fakeEggsApi, PASSPHRASE } from "../lib/fixtures/eggs-api";
import { EggHunt } from "./egg-hunt";
import { CRACK_MS } from "./find-card";

const MATCH = { match: true as const, claimed: false as const, letter: "C", token: "t1" };

beforeEach(() => {
  localStorage.clear();
  document.documentElement.classList.remove("dark");
});

afterEach(cleanup);

const wait = (ms: number) => act(() => new Promise((done) => setTimeout(done, ms)));

/* Three fast taps on the Luck cell of Lil Fridge, then the end of the run. The board loads first, because the
   listener starts only when the board names a drop. */
async function doubleTap() {
  await act(async () => {});
  const cell = screen.getByText("+1.20");
  for (const _ of [1, 2]) fireEvent.pointerUp(cell, { isPrimary: true });
  await wait(TAP_GAP_MS + 50);
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

/* The find, the crack, and the open claim sheet. */
async function openSheet(api: ReturnType<typeof fakeEggsApi>, letter = "C") {
  page(api);
  await doubleTap();
  fireEvent.click(await screen.findByRole("button", { name: "Crack the egg" }));
  await wait(CRACK_MS + 50);
  fireEvent.click(screen.getByRole("button", { name: `Claim ${letter}` }));
  // The group shows at once, and its pills show when the board loads.
  await screen.findByRole("button", { name: "Lil Fridge" });
}

const wordCard = (word: string) => screen.getByRole("button", { name: word }) as HTMLButtonElement;

describe("EggHunt", () => {
  it("sends one check for a double-tap, shows the egg, and cracks it to the red letter tile", async () => {
    const api = fakeEggsApi(MATCH);
    page(api);
    await doubleTap();
    expect(api.checks).toEqual([
      { page: "/", target: "luck-3", action: "tap2", conditions: { theme: "light" } },
    ]);
    expect(await screen.findByRole("heading", { name: "You found an egg" })).toBeTruthy();
    // The ring ripples out from the spot of the find while the egg waits.
    expect(document.querySelectorAll(".egg-ripple")).toHaveLength(2);
    expect(screen.queryByTestId("egg-letter")).toBeNull();
    fireEvent.click(screen.getByRole("button", { name: "Crack the egg" }));
    const tile = screen.getByTestId("egg-letter");
    expect(tile.textContent).toBe("C");
    expect(tile.className).toContain("egg-tile-rise");
    expect(document.querySelector(".egg-crack")).toBeTruthy();
    await wait(CRACK_MS + 50);
    expect(screen.getByRole("heading", { name: "The letter C is yours to claim." })).toBeTruthy();
    expect(screen.getByRole("button", { name: "Claim C" })).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Crack the egg" })).toBeNull();
  });

  it("sends no check and opens no card before the first drop", async () => {
    const api = fakeEggsApi(MATCH, {}, { ...board, last_drop: null });
    page(api);
    await doubleTap();
    expect(api.checks).toEqual([]);
    expect(screen.queryByRole("dialog")).toBeNull();
  });

  it("sends no check when the board call fails", async () => {
    const api = fakeEggsApi(MATCH, { board: new EggsError(500, "Server error") });
    page(api);
    await doubleTap();
    expect(api.checks).toEqual([]);
    expect(screen.queryByRole("dialog")).toBeNull();
  });

  it("shows nothing on no match", async () => {
    const api = fakeEggsApi({ match: false });
    page(api);
    await doubleTap();
    expect(api.checks).toHaveLength(1);
    expect(screen.queryByRole("dialog")).toBeNull();
  });

  it("shows the hero card of another manager first on a claimed egg", async () => {
    page(fakeEggsApi({ match: true, claimed: true, letter: "C" }));
    await doubleTap();
    const card = await screen.findByRole("dialog", { name: "Another manager claimed first." });
    expect(within(card).getByText("Too late")).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Claim C" })).toBeNull();
  });

  it("shows the limit hero card with the minutes to wait on a 429 of the check", async () => {
    page(fakeEggsApi(MATCH, { check: new EggsError(429, "Too many requests", 690) }));
    await doubleTap();
    const card = await screen.findByRole("dialog", { name: "The eggs need a rest." });
    expect(card.textContent).toContain("Try again in 12 minutes.");
  });

  it("shows nothing on any other failure of the check", async () => {
    page(fakeEggsApi(MATCH, { check: new EggsError(500, "Server error") }));
    await doubleTap();
    expect(screen.queryByRole("dialog")).toBeNull();
  });

  it("shows 11 team pills without the commissioner, then a card for each egg word", async () => {
    await openSheet(fakeEggsApi(MATCH));
    const pills = within(screen.getByRole("group", { name: "Your team" })).getAllByRole("button");
    expect(pills).toHaveLength(11);
    expect(pills.map((pill) => pill.textContent)).not.toContain("Bo Girds");
    expect(screen.getByRole("button", { name: "Pick your team" })).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "All You Need Is Love" }));
    expect(screen.queryByRole("group", { name: "Your team" })).toBeNull();
    expect(screen.getByRole("button", { name: "Change" })).toBeTruthy();
    const cornerstone = wordCard("CORNERSTONE");
    expect(cornerstone.disabled).toBe(false);
    expect(cornerstone.textContent).toContain("$50");
    expect(cornerstone.textContent).toContain("0/11");
    expect(cornerstone.textContent).toContain("Lil Fridge leads with 1 of 11");
    // The ghost tile pulses in the C slot of CORNERSTONE.
    expect(cornerstone.querySelector(".egg-ghost")?.textContent).toBe("C");
    // LANSDALE and EAGLES hold no C, so each is faded and disabled, with no ghost tile.
    for (const word of ["LANSDALE", "EAGLES"]) {
      expect(wordCard(word).disabled).toBe(true);
      expect(wordCard(word).textContent).toContain("No open C in this word.");
      expect(wordCard(word).querySelector(".egg-ghost")).toBeNull();
    }
    expect(screen.getByRole("button", { name: "Pick an egg word" })).toBeTruthy();
    fireEvent.click(cornerstone);
    expect(cornerstone.getAttribute("aria-pressed")).toBe("true");
    expect(cornerstone.textContent).toContain("1/11");
  });

  it("fades a disabled egg word card with the muted tokens, and leaves an enabled card plain", async () => {
    await openSheet(fakeEggsApi(MATCH));
    fireEvent.click(screen.getByRole("button", { name: "All You Need Is Love" }));
    const faded = ["border-dashed", "bg-raised", "text-mute"];
    const enabled = wordCard("CORNERSTONE");
    for (const name of faded) expect(enabled.classList.contains(name)).toBe(false);
    for (const word of ["LANSDALE", "EAGLES"]) {
      const card = wordCard(word);
      for (const name of faded) expect(card.classList.contains(name)).toBe(true);
      // The entry motion of a card ends at opacity 1 and holds it, so an opacity class gives no fade.
      expect(card.classList.contains("egg-up")).toBe(true);
      expect([...card.classList].filter((name) => name.startsWith("opacity-"))).toEqual([]);
    }
  });

  it("fades and disables an egg word where the manager holds the letter already", async () => {
    await openSheet(fakeEggsApi(MATCH, {}, boardWith({ CORNERSTONE: { 2: ["C"] }, LANSDALE: { 2: [] } })));
    fireEvent.click(screen.getByRole("button", { name: "All You Need Is Love" }));
    expect(wordCard("CORNERSTONE").disabled).toBe(true);
    expect(wordCard("CORNERSTONE").textContent).toContain("1/11");
  });

  it("fades and disables an egg word with a winner", async () => {
    const won: Board = boardWith({});
    won.words = won.words.map((word) =>
      word.word === "CORNERSTONE" ? { ...word, winner: { roster_id: 5, team: "London Cooking" } } : word,
    );
    await openSheet(fakeEggsApi(MATCH, {}, won));
    fireEvent.click(screen.getByRole("button", { name: "All You Need Is Love" }));
    expect(wordCard("CORNERSTONE").disabled).toBe(true);
    expect(wordCard("CORNERSTONE").textContent).toContain("London Cooking won CORNERSTONE.");
  });

  it("claims the letter for the picked team into the picked egg word, then shows the claim hero card", async () => {
    const api = fakeEggsApi(MATCH);
    await openSheet(api);
    fireEvent.click(screen.getByRole("button", { name: "All You Need Is Love" }));
    fireEvent.click(wordCard("CORNERSTONE"));
    expect(screen.getByRole("button", { name: "Enter the passphrase" })).toBeTruthy();
    fireEvent.change(screen.getByLabelText(/passphrase/i), { target: { value: PASSPHRASE } });
    fireEvent.click(screen.getByRole("button", { name: "Claim C for CORNERSTONE" }));
    const card = await screen.findByRole("dialog", { name: "C goes to CORNERSTONE." });
    expect(api.claims).toEqual([{ token: "t1", roster_id: 2, word: "CORNERSTONE" }]);
    expect(card.textContent).toContain("1/11");
    expect(card.textContent).toContain("10 letters to go for the $50.");
    expect(card.textContent).toContain("All You Need Is Love");
    // The red C tile drops into its slot.
    expect(card.querySelector(".egg-land")?.textContent).toBe("C");
    expect(screen.getByRole("link", { name: "See the egg board" }).getAttribute("href")).toBe("/eggs/");
  });

  it("says the gift card is the manager's when the claim fills the egg word", async () => {
    const api = fakeEggsApi({ ...MATCH, letter: "S" }, {}, boardWith({ EAGLES: { 3: ["E", "A", "G", "L", "E"] } }));
    localStorage.setItem("cpc.passphrase", PASSPHRASE);
    await openSheet(api, "S");
    fireEvent.click(screen.getByRole("button", { name: "Lil Fridge" }));
    fireEvent.click(wordCard("EAGLES"));
    fireEvent.click(screen.getByRole("button", { name: "Claim S for EAGLES" }));
    const card = await screen.findByRole("dialog", { name: "EAGLES is complete." });
    expect(card.textContent).toContain("6/6");
    expect(card.textContent).toContain("The $20 gift card is yours.");
  });

  it("shows the dashed block notice when the letter fits no egg word, and claims a block", async () => {
    const api = fakeEggsApi(MATCH);
    localStorage.setItem("cpc.passphrase", PASSPHRASE);
    await openSheet(api);
    // Lil Fridge holds the one C of CORNERSTONE, and the other egg words hold no C.
    fireEvent.click(screen.getByRole("button", { name: "Lil Fridge" }));
    expect(screen.getByText("C fits none of your egg words.").closest(".border-dashed")).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "Claim C as a block" }));
    const card = await screen.findByRole("dialog", { name: "You hold C as a block." });
    expect(api.claims).toEqual([{ token: "t1", roster_id: 3, word: null }]);
    expect(within(card).getByText("BLOCKED")).toBeTruthy();
  });

  it("shows no block notice when the letter fits an egg word", async () => {
    await openSheet(fakeEggsApi(MATCH));
    fireEvent.click(screen.getByRole("button", { name: "All You Need Is Love" }));
    expect(screen.queryByText("C fits none of your egg words.")).toBeNull();
  });

  it("shows no passphrase field when the browser holds the passphrase", async () => {
    localStorage.setItem("cpc.passphrase", PASSPHRASE);
    await openSheet(fakeEggsApi(MATCH));
    fireEvent.click(screen.getByRole("button", { name: "All You Need Is Love" }));
    fireEvent.click(wordCard("CORNERSTONE"));
    expect(screen.queryByLabelText(/passphrase/i)).toBeNull();
    fireEvent.click(screen.getByRole("button", { name: "Claim C for CORNERSTONE" }));
    expect(await screen.findByRole("dialog", { name: "C goes to CORNERSTONE." })).toBeTruthy();
  });

  it("asks for the passphrase again after a wrong one", async () => {
    localStorage.setItem("cpc.passphrase", "wrong");
    await openSheet(fakeEggsApi(MATCH));
    fireEvent.click(screen.getByRole("button", { name: "All You Need Is Love" }));
    fireEvent.click(wordCard("CORNERSTONE"));
    fireEvent.click(screen.getByRole("button", { name: "Claim C for CORNERSTONE" }));
    expect(await screen.findByText("The passphrase is wrong. Ask a league member for it.")).toBeTruthy();
    expect(screen.getByLabelText(/passphrase/i)).toBeTruthy();
  });

  it("shows the hero card of another manager first on a 409 of the claim", async () => {
    localStorage.setItem("cpc.passphrase", PASSPHRASE);
    await openSheet(fakeEggsApi(MATCH, { claim: new EggsError(409, "Another manager claimed first.") }));
    fireEvent.click(screen.getByRole("button", { name: "All You Need Is Love" }));
    fireEvent.click(wordCard("CORNERSTONE"));
    fireEvent.click(screen.getByRole("button", { name: "Claim C for CORNERSTONE" }));
    expect(await screen.findByRole("dialog", { name: "Another manager claimed first." })).toBeTruthy();
  });

  it("shows the reason of a refusal on the sheet", async () => {
    localStorage.setItem("cpc.passphrase", PASSPHRASE);
    await openSheet(fakeEggsApi(MATCH, { claim: new EggsError(422, "CORNERSTONE has a winner.") }));
    fireEvent.click(screen.getByRole("button", { name: "All You Need Is Love" }));
    fireEvent.click(wordCard("CORNERSTONE"));
    fireEvent.click(screen.getByRole("button", { name: "Claim C for CORNERSTONE" }));
    expect((await screen.findByRole("alert")).textContent).toBe("CORNERSTONE has a winner.");
  });
});
