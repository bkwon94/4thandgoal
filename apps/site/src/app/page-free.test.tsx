/**
 * Tests for the free answer of the front door at /. Each test renders the page with the fixed copy of the published data of cpc,
 * and the free route plays a stream that the API recorded in a live run with the real Jev and the real Claude.
 */
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, onTestFinished, vi } from "vitest";
import { readFixtureSite } from "@/fixtures/sites";
import { MISS_LEAD } from "./front-door/miss-card";
import { FIXING_LINE } from "./front-door/free-answer";
import HomePage from "./page";

/* The readers of public/ read the fixed copy of the cpc data, so a weekly publish never changes these tests. The spy
   runs before the imports, because the week reader takes its folder when it loads. Each test sets it again, because a
   restore of the mocks removes it. */
await vi.hoisted(async () => (await import("@/fixtures/sites")).readFixtureSite("cpc"));
beforeEach(() => readFixtureSite("cpc"));

const PASSPHRASE = "cornerstone-test";
const fetchStub = vi.fn();
const routes: unknown[] = [];
const streams: (() => Response)[] = [];

// The path comes from this file and not from the working folder, because the tests point the working folder at the fixed copy.
const recorded = (name: string) => readFileSync(join(__dirname, "..", "fixtures", "free-answer", `${name}.sse`), "utf8");
const freeCalls = () => fetchStub.mock.calls.filter(([url]) => String(url).endsWith("/ask/free"));

function sse(body: ReadableStream<Uint8Array> | string): Response {
  return new Response(body, { headers: { "Content-Type": "text/event-stream", "x-vercel-ai-ui-message-stream": "v1" } });
}

/* The route of the question, then the recorded stream of its free answer. */
function freeWith(name: string, body: { team?: number | null; suggestion?: string | null } = {}) {
  routes.push({ route: "free", topic: null, team: null, closest: [], suggestion: null, ...body, jev: { model: "jev-1.14.0", nouls: {}, choices: {} } });
  streams.push(() => sse(recorded(name)));
}

async function ask(question: string) {
  const box = await screen.findByRole("form", { name: "Ask" });
  fireEvent.change(within(box).getByRole("textbox", { name: "Ask a question" }), { target: { value: question } });
  fireEvent.submit(box);
}

/* The time that `text` first shows on the page, as a MutationObserver sees each change, so a state that shows for one
   render only is still seen. */
function watchFor(text: string) {
  const seen: { at: number | null } = { at: null };
  const observer = new MutationObserver(() => {
    if (seen.at === null && document.body.textContent?.includes(text)) seen.at = performance.now();
  });
  observer.observe(document.body, { childList: true, subtree: true, characterData: true });
  onTestFinished(() => observer.disconnect());
  return seen;
}

/* No box from the element down fades from 0 or blurs, so the card shows as it ended. */
function expectShown(element: HTMLElement) {
  for (const box of [element, ...element.querySelectorAll<HTMLElement>("*")]) {
    expect(box.style.opacity).not.toBe("0");
    expect(box.style.filter).not.toMatch(/blur\((?!0)/);
  }
}

async function articleWith(question: string, text: string) {
  await waitFor(() => expect(screen.getByRole("article", { name: question }).textContent).toContain(text), { timeout: 3000 });
  return screen.getByRole("article", { name: question });
}

beforeEach(() => {
  fetchStub.mockImplementation(async (url: string) => {
    if (String(url).endsWith("/ask")) return new Response(JSON.stringify(routes.shift()), { status: 200 });
    if (String(url).endsWith("/ask/free")) return streams.shift()?.() ?? new Response("", { status: 500 });
    return new Response("", { status: 404 });
  });
  vi.stubGlobal("fetch", fetchStub);
  localStorage.setItem("cpc.your-team", "3");
  localStorage.setItem("cpc.passphrase", PASSPHRASE);
});

afterEach(() => {
  cleanup();
  localStorage.clear();
  fetchStub.mockReset();
  routes.length = 0;
  streams.length = 0;
  vi.unstubAllGlobals();
});

describe("the free answer of Lil Fridge", () => {
  it("sends the question, Your team, and the week with the passphrase to the free route of the client", async () => {
    freeWith("highest-scoring", { suggestion: "your_season" });
    render(<HomePage />);
    await ask("highest scoring team this season");
    await waitFor(() => expect(freeCalls()).toHaveLength(1));
    const [url, init] = freeCalls()[0];
    expect(url).toMatch(/\/clients\/cpc\/ask\/free$/);
    expect(new Headers(init.headers).get("X-League-Passphrase")).toBe(PASSPHRASE);
    expect(JSON.parse(init.body)).toMatchObject({ question: "highest scoring team this season", roster_id: 3, week: 8 });
  });

  it("names the team with the most points for, after the step of the standings, checked (AT-11, AT-20)", async () => {
    freeWith("highest-scoring", { suggestion: "your_season" });
    render(<HomePage />);
    await ask("highest scoring team this season");
    const answer = await articleWith("highest scoring team this season", "Checked");
    // Bo Girds has 921.62 points for in weeks 1 to 8 of the standings data, the most of the 12 teams.
    expect(answer.textContent).toContain("Bo Girds has scored the most points this season, with 921.62");
    expect(within(within(answer).getByRole("list", { name: "Steps" })).getByText("Reading the standings")).toBeTruthy();
  });

  it("shows the top Topic of a half fit as one chip under the answer, and the chip opens it (AT-12)", async () => {
    freeWith("highest-scoring", { suggestion: "your_season" });
    render(<HomePage />);
    await ask("highest scoring team this season");
    const answer = await articleWith("highest scoring team this season", "Checked");
    const [chip] = within(answer).getAllByRole("button");
    expect(chip.textContent).toBe("Your season");
    fireEvent.click(chip);
    expect(await screen.findByRole("article", { name: "Your season" })).toBeTruthy();
  });

  it("answers a question about Bo Girds with the 9-7 record of Bo Girds (AT-10)", async () => {
    freeWith("bo-girds", { team: 6, suggestion: "your_season" });
    render(<HomePage />);
    await ask("how's Bo Girds doing");
    const answer = await articleWith("how's Bo Girds doing", "Checked");
    expect(answer.textContent).toContain("Bo Girds is 9-7");
    // The chip opens the season of Bo Girds, not of Lil Fridge.
    fireEvent.click(within(answer).getByRole("button", { name: /Your season.*Bo Girds/ }));
    const season = await screen.findByRole("article", { name: "Your season" });
    expect(season.textContent).toContain("9-7");
  });

  it("shows each tool call of week 1 results as a plain step, and names no internal tool (AT-19)", async () => {
    freeWith("week-1");
    render(<HomePage />);
    await ask("week 1 results");
    const answer = await articleWith("week 1 results", "Checked");
    expect(within(within(answer).getByRole("list", { name: "Steps" })).getByText("Reading week 1")).toBeTruthy();
    expect(answer.textContent).toContain("you beat NFC Least 117.71 to 82.07");
    expect(document.body.textContent).not.toMatch(/Jev|Advisor|Finder|rival|Brian|week_results|standings\(/);
  });

  it("drops the first text after a failed check, and keeps the checked rewrite (AT-21)", async () => {
    freeWith("fix");
    render(<HomePage />);
    await ask("who spent the most FAAB on a waiver wire pickup");
    const answer = await articleWith("who spent the most FAAB on a waiver wire pickup", "Checked");
    expect(answer.textContent).toContain("In weeks 2 through 5, the most FAAB spent on one waiver pickup was 41");
    expect(answer.textContent).not.toContain("Through the weeks I could check");
    expect(answer.textContent).not.toContain(FIXING_LINE);
  });

  it("holds Checking on screen, then turns it to Checked, and the card never fades out on the hand-off (AT-20)", async () => {
    const checking = watchFor("Checking");
    const checked = watchFor("Checked");
    freeWith("week-1");
    render(<HomePage />);
    await ask("week 1 results");
    await articleWith("week 1 results", "Checked");
    // The recorded stream sends "checking" and "checked" in one read, so only the hold shows "Checking".
    expect(checking.at).not.toBeNull();
    expect(checked.at! - checking.at!).toBeGreaterThanOrEqual(500);
    // The kept card takes the place of the live card in the commit that saves the Thread. It shows as the live card
    // ended, with no fade from 0 and no blur.
    await waitFor(
      () => {
        expect(localStorage.getItem("cpc.thread")).toContain("you beat NFC Least");
        expectShown(screen.getByRole("article", { name: "week 1 results" }));
      },
      { timeout: 3000 },
    );
  });

  it("shows the fixing line after a failed check, before the rewrite (AT-21)", async () => {
    const fixing = watchFor(FIXING_LINE);
    freeWith("fix");
    render(<HomePage />);
    await ask("who spent the most FAAB on a waiver wire pickup");
    await articleWith("who spent the most FAAB on a waiver wire pickup", "Checked");
    expect(fixing.at).not.toBeNull();
  });

  it("gives a second failed check the honest miss, with neither text (AT-22)", async () => {
    freeWith("miss");
    render(<HomePage />);
    await ask("highest scoring team this season");
    const miss = await articleWith("highest scoring team this season", MISS_LEAD);
    expect(miss.textContent).not.toContain("921.62");
    const topics = within(within(miss).getByRole("group", { name: "Closest Topics" })).getAllByRole("button");
    expect(topics.map((topic) => topic.textContent)).toEqual(["Your season", "Playoff race", "Power rankings"]);
  });

  it("sharpens each new word from a blur and shows no stop control while it streams (AT-44, AT-55)", async () => {
    const lines = recorded("week-1").split("\n\n");
    const cut = lines.findIndex((line) => line.includes('"text-end"'));
    let finish: () => void = () => {};
    routes.push({ route: "free", topic: null, team: null, closest: [], suggestion: null, jev: { model: "jev-1.14.0", nouls: {}, choices: {} } });
    streams.push(() =>
      sse(
        new ReadableStream({
          start(controller) {
            const encoder = new TextEncoder();
            controller.enqueue(encoder.encode(lines.slice(0, cut).join("\n\n") + "\n\n"));
            finish = () => {
              controller.enqueue(encoder.encode(lines.slice(cut).join("\n\n")));
              controller.close();
            };
          },
        }),
      ),
    );
    render(<HomePage />);
    await ask("week 1 results");
    const answer = await articleWith("week 1 results", "you beat NFC Least");
    expect(answer.querySelectorAll(".stream-word").length).toBeGreaterThan(10);
    // The words of one read sweep in one after another, so each new word plays its own blur and not one block.
    const delays = [...answer.querySelectorAll<HTMLElement>(".stream-word")].map((word) => parseFloat(word.style.animationDelay || "0"));
    expect(delays.at(-1)!).toBeGreaterThan(delays[0]);
    expect([...delays].sort((a, b) => a - b)).toEqual(delays);
    expect(screen.queryByRole("button", { name: /stop|cancel/i })).toBeNull();
    expect(answer.textContent).not.toContain("Checked");
    finish();
    await articleWith("week 1 results", "Checked");
  });

  it("keeps the checked answer for the week, so a reload shows it with no new stream", async () => {
    freeWith("week-1");
    const { unmount } = render(<HomePage />);
    await ask("week 1 results");
    await articleWith("week 1 results", "Checked");
    // The Thread keeps the answer once the stream ends, a moment after the mark shows.
    await waitFor(() => expect(localStorage.getItem("cpc.thread")).toContain("you beat NFC Least"));
    unmount();
    render(<HomePage />);
    const kept = await articleWith("week 1 results", "you beat NFC Least");
    expect(kept.textContent).toContain("Checked");
    expect(kept.querySelectorAll(".stream-word")).toHaveLength(0);
    expect(freeCalls()).toHaveLength(1);
  });

  it("shows the retry line when the stream fails, never a pass", async () => {
    routes.push({ route: "free", topic: null, team: null, closest: [], suggestion: null, jev: { model: "jev-1.14.0", nouls: {}, choices: {} } });
    streams.push(() => new Response("", { status: 503 }));
    render(<HomePage />);
    await ask("week 1 results");
    const note = await articleWith("week 1 results", "The question did not go through. Ask again.");
    expect(within(note).getByRole("button", { name: "Ask again" })).toBeTruthy();
  });
});
