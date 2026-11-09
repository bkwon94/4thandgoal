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
import { DRAG_PX, STAMP_MS, TEAR_MS } from "./claim-ticket";
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

// The card of an egg word: its name starts with the word, then the gift card, the count, and the note.
const wordCard = (word: string) => screen.getByRole("button", { name: new RegExp(`^${word} `) }) as HTMLButtonElement;

/* The egg on the screen: 180 by 220 px, the size of the art, with its top left at (100, 200).
   jsdom lays out no page, so the test gives the egg the box that a browser gives it. */
const EGG_BOX = { left: 100, top: 200, width: 180, height: 220 };

async function findEgg() {
  const egg = await screen.findByRole("button", { name: "Crack the egg" });
  egg.getBoundingClientRect = () => DOMRect.fromRect({ x: EGG_BOX.left, y: EGG_BOX.top, width: EGG_BOX.width, height: EGG_BOX.height });
  return egg;
}

/* A pointer tap at a point of the egg, in px from the top left of the egg. */
function tapEgg(egg: HTMLElement, x: number, y: number) {
  const at = { clientX: EGG_BOX.left + x, clientY: EGG_BOX.top + y, isPrimary: true };
  fireEvent.pointerDown(egg, at);
  fireEvent.pointerUp(egg, at);
  fireEvent.click(egg, { ...at, detail: 1 });
}

/* Each crack line on the egg, as its list of points in the units of the egg art. */
function crackLines() {
  return screen.getAllByTestId("egg-crack-line").map((line) =>
    (line.getAttribute("points") ?? "").split(" ").map((pair) => pair.split(",").map(Number)),
  );
}

const ticket = () => screen.getByRole("group", { name: "Claim ticket" });

const stub = (name: string) => within(ticket()).getByRole("button", { name });

/* A tap on the stub, then the time of the tear, so the claim sends. */
async function tap(name: string) {
  fireEvent.click(stub(name));
  await wait(TEAR_MS + 50);
}

/* The stub on the screen: 96 by 144 px, the size of the stub, with its top left at (250, 600).
   jsdom lays out no page, so the test gives the stub the box that a browser gives it. */
const STUB_BOX = { left: 250, top: 600, width: 96, height: 144 };

/* A pointer drag on the stub from its middle, by dx and dy px in ten steps. The drag holds at its end with no release. */
function dragStub(name: string, dx: number, dy = 0) {
  const shown = stub(name);
  shown.getBoundingClientRect = () => DOMRect.fromRect({ x: STUB_BOX.left, y: STUB_BOX.top, width: STUB_BOX.width, height: STUB_BOX.height });
  const x = STUB_BOX.left + STUB_BOX.width / 2;
  const y = STUB_BOX.top + STUB_BOX.height / 2;
  fireEvent.pointerDown(shown, { clientX: x, clientY: y, pointerId: 1, isPrimary: true });
  for (let step = 1; step <= 10; step += 1) {
    fireEvent.pointerMove(shown, { clientX: x + (dx * step) / 10, clientY: y + (dy * step) / 10, pointerId: 1, isPrimary: true });
  }
  return { shown, at: { clientX: x + dx, clientY: y + dy, pointerId: 1, isPrimary: true } };
}

/* The release of a drag: the pointer goes up, and the browser sends the click that follows it. */
function release({ shown, at }: ReturnType<typeof dragStub>) {
  fireEvent.pointerUp(shown, at);
  fireEvent.click(shown, { ...at, detail: 1 });
}

/* The count of popped holes, and whether they run from the top hole down with no gap. */
function poppedHoles() {
  const holes = [...ticket().querySelectorAll("[data-popped]")].map((hole) => hole.getAttribute("data-popped") === "true");
  const count = holes.filter(Boolean).length;
  return { count, fromTop: holes.slice(0, count).every(Boolean) };
}

/* The three steps done: the team, CORNERSTONE, and the passphrase in the browser. */
async function readyTicket(api: ReturnType<typeof fakeEggsApi>) {
  localStorage.setItem("cpc.passphrase", PASSPHRASE);
  await openSheet(api);
  fireEvent.click(screen.getByRole("button", { name: "All You Need Is Love" }));
  fireEvent.click(wordCard("CORNERSTONE"));
}

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
    expect(screen.getAllByTestId("egg-crack-line")).toHaveLength(6);
    await wait(CRACK_MS + 50);
    expect(screen.getByRole("heading", { name: "The letter C is yours to claim." })).toBeTruthy();
    expect(screen.getByRole("button", { name: "Claim C" })).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Crack the egg" })).toBeNull();
  });

  it("starts each crack line at the point of the tap", async () => {
    page(fakeEggsApi(MATCH));
    await doubleTap();
    // A tap near the upper left of the egg: one quarter in from the left, one third down.
    tapEgg(await findEgg(), 45, 75);
    const lines = crackLines();
    expect(lines).toHaveLength(6);
    for (const [start, ...rest] of lines) {
      expect(start[0]).toBeCloseTo(45, 0);
      expect(start[1]).toBeCloseTo(75, 0);
      // Each line runs out from the point, so it ends away from it.
      const end = rest[rest.length - 1];
      expect(Math.hypot(end[0] - 45, end[1] - 75)).toBeGreaterThan(20);
    }
  });

  it("cracks two finds at one tap point along different lines, from a fresh seed on each tap", async () => {
    const finds = [];
    for (const _ of [1, 2]) {
      page(fakeEggsApi(MATCH));
      await doubleTap();
      tapEgg(await findEgg(), 120, 160);
      finds.push(crackLines());
      cleanup();
    }
    const [first, second] = finds;
    // Both start at the one tap point, and the paths of the lines differ.
    expect(first.map((line) => line[0])).toEqual(second.map((line) => line[0]));
    expect(first).not.toEqual(second);
  });

  it("cracks the egg from its middle on Enter, then shows the letter at 1.3 s", async () => {
    page(fakeEggsApi(MATCH));
    await doubleTap();
    const egg = await findEgg();
    egg.focus();
    // Enter on a focused button makes the browser send a click with a detail of 0 and no pointer. jsdom sends no
    // click for a key, so the test sends the events of the browser in their order.
    fireEvent.keyDown(egg, { key: "Enter" });
    fireEvent.click(egg, { detail: 0 });
    fireEvent.keyUp(egg, { key: "Enter" });
    for (const [start] of crackLines()) {
      expect(start).toEqual([90, 130]);
    }
    expect(CRACK_MS).toBe(1300);
    await wait(CRACK_MS - 150);
    expect(screen.queryByRole("heading", { name: "The letter C is yours to claim." })).toBeNull();
    await wait(200);
    expect(screen.getByTestId("egg-letter").textContent).toBe("C");
    expect(screen.getByRole("heading", { name: "The letter C is yours to claim." })).toBeTruthy();
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
    expect(stub("Pick your team")).toBeTruthy();
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
    expect(stub("Pick an egg word")).toBeTruthy();
    fireEvent.click(cornerstone);
    expect(cornerstone.getAttribute("aria-pressed")).toBe("true");
    expect(cornerstone.textContent).toContain("1/11");
  });

  it("names each egg word card by the text it shows, so the name a voice user reads out matches the card", async () => {
    await openSheet(fakeEggsApi(MATCH));
    fireEvent.click(screen.getByRole("button", { name: "All You Need Is Love" }));
    expect(screen.getByRole("button", { name: "CORNERSTONE $50 0/11 Lil Fridge leads with 1 of 11" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "EAGLES $20 0/6 No open C in this word." })).toBeTruthy();
  });

  it("sets the title of the sheet as one element per line, so axe reads each line over one part of the page", async () => {
    await openSheet(fakeEggsApi(MATCH));
    const title = screen.getByRole("heading", { name: "Put C in an egg word." });
    const lines = [...title.children] as HTMLElement[];
    expect(lines.map((line) => line.textContent)).toEqual(["Put C in", "an egg word."]);
    for (const line of lines) expect(line.classList.contains("block")).toBe(true);
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
    expect(stub("Enter the passphrase")).toBeTruthy();
    fireEvent.change(screen.getByLabelText(/league passphrase/i), { target: { value: PASSPHRASE } });
    await tap("Tear to claim C for CORNERSTONE");
    await wait(STAMP_MS);
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
    await tap("Tear to claim S for EAGLES");
    await wait(STAMP_MS);
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
    await tap("Tear to claim C as a block");
    await wait(STAMP_MS);
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
    expect(screen.queryByLabelText(/league passphrase/i)).toBeNull();
    await tap("Tear to claim C for CORNERSTONE");
    await wait(STAMP_MS);
    expect(await screen.findByRole("dialog", { name: "C goes to CORNERSTONE." })).toBeTruthy();
  });

  it("asks for the passphrase again after a wrong one", async () => {
    localStorage.setItem("cpc.passphrase", "wrong");
    await openSheet(fakeEggsApi(MATCH));
    fireEvent.click(screen.getByRole("button", { name: "All You Need Is Love" }));
    fireEvent.click(wordCard("CORNERSTONE"));
    await tap("Tear to claim C for CORNERSTONE");
    expect(await screen.findByText("The passphrase is wrong. Ask a league member for it.")).toBeTruthy();
    expect(screen.getByLabelText(/league passphrase/i)).toBeTruthy();
  });

  it("shows the hero card of another manager first on a 409 of the claim", async () => {
    localStorage.setItem("cpc.passphrase", PASSPHRASE);
    await openSheet(fakeEggsApi(MATCH, { claim: new EggsError(409, "Another manager claimed first.") }));
    fireEvent.click(screen.getByRole("button", { name: "All You Need Is Love" }));
    fireEvent.click(wordCard("CORNERSTONE"));
    await tap("Tear to claim C for CORNERSTONE");
    await wait(STAMP_MS);
    expect(await screen.findByRole("dialog", { name: "Another manager claimed first." })).toBeTruthy();
  });

  it("shows the reason of a refusal on the sheet", async () => {
    localStorage.setItem("cpc.passphrase", PASSPHRASE);
    await openSheet(fakeEggsApi(MATCH, { claim: new EggsError(422, "CORNERSTONE has a winner.") }));
    fireEvent.click(screen.getByRole("button", { name: "All You Need Is Love" }));
    fireEvent.click(wordCard("CORNERSTONE"));
    await tap("Tear to claim C for CORNERSTONE");
    expect((await screen.findByRole("alert")).textContent).toBe("CORNERSTONE has a winner.");
  });

  it("shows the claim ticket with the letter, the egg word, and the team after the three steps", async () => {
    await readyTicket(fakeEggsApi(MATCH));
    const shown = ticket();
    expect(within(shown).getByText("C")).toBeTruthy();
    expect(within(shown).getByText("CORNERSTONE")).toBeTruthy();
    expect(within(shown).getByText("All You Need Is Love")).toBeTruthy();
    const stub = within(shown).getByRole("button", { name: "Tear to claim C for CORNERSTONE" });
    expect(stub.textContent).toContain("Tear to claim");
  });

  it("keeps a locked stub that names the next missing step, and sends no claim on a tap", async () => {
    const api = fakeEggsApi(MATCH);
    localStorage.setItem("cpc.passphrase", PASSPHRASE);
    await openSheet(api);
    fireEvent.click(screen.getByRole("button", { name: "All You Need Is Love" }));
    await tap("Pick an egg word");
    expect(stub("Pick an egg word").textContent).toContain("Pick an egg word");
    expect(stub("Pick an egg word").getAttribute("aria-disabled")).toBe("true");
    expect(api.claims).toEqual([]);
    expect(screen.queryByText("CLAIMED")).toBeNull();
  });

  it("tears the stub on a tap, sends one claim, stamps CLAIMED, then shows the end card", async () => {
    const api = fakeEggsApi(MATCH);
    await readyTicket(api);
    await tap("Tear to claim C for CORNERSTONE");
    expect(api.claims).toEqual([{ token: "t1", roster_id: 2, word: "CORNERSTONE" }]);
    expect(within(ticket()).getByText("CLAIMED")).toBeTruthy();
    expect(screen.queryByRole("dialog", { name: "C goes to CORNERSTONE." })).toBeNull();
    await wait(STAMP_MS + 50);
    expect(screen.getByRole("dialog", { name: "C goes to CORNERSTONE." })).toBeTruthy();
    expect(api.claims).toHaveLength(1);
  });

  for (const key of ["Enter", " "]) {
    it(`tears the stub on the key ${JSON.stringify(key)} and sends one claim`, async () => {
      const api = fakeEggsApi(MATCH);
      await readyTicket(api);
      const named = stub("Tear to claim C for CORNERSTONE");
      named.focus();
      fireEvent.keyDown(named, { key });
      // A second press in the tear sends no second claim.
      fireEvent.keyDown(named, { key });
      await wait(TEAR_MS + 50);
      expect(api.claims).toEqual([{ token: "t1", roster_id: 2, word: "CORNERSTONE" }]);
      expect(within(ticket()).getByText("CLAIMED")).toBeTruthy();
    });
  }

  it("stamps TAKEN and brings the stub back when another manager was first, then shows that end card", async () => {
    const api = fakeEggsApi(MATCH, { claim: new EggsError(409, "Another manager claimed first.") });
    await readyTicket(api);
    await tap("Tear to claim C for CORNERSTONE");
    expect(within(ticket()).getByText("TAKEN")).toBeTruthy();
    expect(stub("Tear to claim C for CORNERSTONE").getAttribute("aria-hidden")).toBeNull();
    await wait(STAMP_MS + 50);
    expect(screen.getByRole("dialog", { name: "Another manager claimed first." })).toBeTruthy();
  });

  it("shows the error of a wrong passphrase and brings the stub back, then a second tear claims", async () => {
    localStorage.setItem("cpc.passphrase", "wrong");
    const api = fakeEggsApi(MATCH);
    await openSheet(api);
    fireEvent.click(screen.getByRole("button", { name: "All You Need Is Love" }));
    fireEvent.click(wordCard("CORNERSTONE"));
    await tap("Tear to claim C for CORNERSTONE");
    expect(screen.getByRole("alert").textContent).toBe("The passphrase is wrong. Ask a league member for it.");
    expect(stub("Enter the passphrase").getAttribute("aria-hidden")).toBeNull();
    fireEvent.change(screen.getByLabelText(/league passphrase/i), { target: { value: PASSPHRASE } });
    await tap("Tear to claim C for CORNERSTONE");
    expect(within(ticket()).getByText("CLAIMED")).toBeTruthy();
    expect(api.claims).toHaveLength(1);
  });

  it("shows the block on the ticket when the letter fits no egg word of the manager", async () => {
    localStorage.setItem("cpc.passphrase", PASSPHRASE);
    await openSheet(fakeEggsApi(MATCH));
    fireEvent.click(screen.getByRole("button", { name: "Lil Fridge" }));
    expect(within(ticket()).getByText("BLOCK")).toBeTruthy();
    expect(within(ticket()).getByText("Lil Fridge")).toBeTruthy();
    expect(stub("Tear to claim C as a block").textContent).toContain("Tear to claim");
  });

  it("tears the stub on a drag to the right to its full length and sends one claim", async () => {
    const api = fakeEggsApi(MATCH);
    await readyTicket(api);
    release(dragStub("Tear to claim C for CORNERSTONE", DRAG_PX + 10));
    await wait(50);
    expect(api.claims).toEqual([{ token: "t1", roster_id: 2, word: "CORNERSTONE" }]);
    expect(within(ticket()).getByText("CLAIMED")).toBeTruthy();
  });

  it("springs the stub back and sends nothing on a release at half the length of the drag", async () => {
    const api = fakeEggsApi(MATCH);
    await readyTicket(api);
    const held = dragStub("Tear to claim C for CORNERSTONE", DRAG_PX / 2);
    // In the drag, the stub tilts and pulls to the right with the pointer, with no spring.
    expect(held.shown.style.transform).toContain("rotate(8.0deg)");
    expect(held.shown.className).not.toContain("egg-stub-spring");
    release(held);
    await wait(TEAR_MS + 50);
    expect(api.claims).toEqual([]);
    const back = stub("Tear to claim C for CORNERSTONE");
    expect(back.style.transform).toBe("");
    expect(back.className).toContain("egg-stub-spring");
    expect(back.getAttribute("aria-hidden")).toBeNull();
    expect(poppedHoles().count).toBe(0);
    expect(within(ticket()).queryByText("CLAIMED")).toBeNull();
  });

  it("pops more holes of the perforation at a longer drag, from the top hole down", async () => {
    const api = fakeEggsApi(MATCH);
    await readyTicket(api);
    const short = dragStub("Tear to claim C for CORNERSTONE", DRAG_PX * 0.3);
    const atShort = poppedHoles();
    release(short);
    const long = dragStub("Tear to claim C for CORNERSTONE", DRAG_PX * 0.8);
    const atLong = poppedHoles();
    release(long);
    expect(atShort).toEqual({ count: 3, fromTop: true });
    expect(atLong).toEqual({ count: 8, fromTop: true });
    expect(api.claims).toEqual([]);
  });

  it("springs the stub back and sends nothing on a pointer cancel in the drag", async () => {
    const api = fakeEggsApi(MATCH);
    await readyTicket(api);
    const held = dragStub("Tear to claim C for CORNERSTONE", DRAG_PX * 0.7);
    // The browser takes the pointer, for example to scroll the sheet, and sends no click.
    fireEvent.pointerCancel(held.shown, held.at);
    // A move after the cancel belongs to no drag.
    fireEvent.pointerMove(held.shown, { ...held.at, clientX: held.at.clientX + DRAG_PX });
    await wait(TEAR_MS + 50);
    expect(api.claims).toEqual([]);
    expect(stub("Tear to claim C for CORNERSTONE").style.transform).toBe("");
    expect(poppedHoles().count).toBe(0);
  });

  it("does not tear the stub on a vertical move, so the sheet can scroll", async () => {
    const api = fakeEggsApi(MATCH);
    await readyTicket(api);
    const held = dragStub("Tear to claim C for CORNERSTONE", 0, -200);
    expect(poppedHoles().count).toBe(0);
    release(held);
    await wait(TEAR_MS + 50);
    expect(api.claims).toEqual([]);
    expect(within(ticket()).queryByText("CLAIMED")).toBeNull();
  });

  it("tears the stub by itself on a pointer tap with a move under 6 px", async () => {
    const api = fakeEggsApi(MATCH);
    await readyTicket(api);
    release(dragStub("Tear to claim C for CORNERSTONE", 4));
    await wait(TEAR_MS + 50);
    expect(api.claims).toEqual([{ token: "t1", roster_id: 2, word: "CORNERSTONE" }]);
  });

  it("starts no drag on a locked stub", async () => {
    const api = fakeEggsApi(MATCH);
    localStorage.setItem("cpc.passphrase", PASSPHRASE);
    await openSheet(api);
    fireEvent.click(screen.getByRole("button", { name: "All You Need Is Love" }));
    release(dragStub("Pick an egg word", DRAG_PX + 10));
    await wait(TEAR_MS + 50);
    expect(api.claims).toEqual([]);
    expect(poppedHoles().count).toBe(0);
  });
});
