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
import HomePage from "./front-door/door-page";

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

/* Whether `text` ever shows on the page with no "Checked" mark, as a MutationObserver sees each change. */
function watchEarly(text: string) {
  const seen = { early: false };
  const observer = new MutationObserver(() => {
    const page = document.body.textContent ?? "";
    if (page.includes(text) && !page.includes("Checked")) seen.early = true;
  });
  observer.observe(document.body, { childList: true, subtree: true, characterData: true });
  onTestFinished(() => observer.disconnect());
  return seen;
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

  it("waits on the one first line as a live step inside the card before the first tool call", async () => {
    routes.push({ route: "free", topic: null, team: null, closest: [], suggestion: null, jev: { model: "jev-1.14.0", nouls: {}, choices: {} } });
    streams.push(() => sse(new ReadableStream<Uint8Array>({ start() {} })));
    render(<HomePage />);
    await ask("highest scoring team this season");
    await waitFor(() => expect(freeCalls()).toHaveLength(1));
    const answer = await articleWith("highest scoring team this season", "Reading the league…");
    const [step] = within(within(answer).getByRole("list", { name: "Steps" })).getAllByRole("listitem");
    expect(step.getAttribute("data-state")).toBe("live");
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

  it("never shows a failed first text, and shows no text before Checked (H10)", async () => {
    const failed = watchFor("Through the weeks I could check");
    const rewrite = watchEarly("In weeks 2 through 5");
    freeWith("fix");
    render(<HomePage />);
    await ask("who spent the most FAAB on a waiver wire pickup");
    await articleWith("who spent the most FAAB on a waiver wire pickup", "In weeks 2 through 5");
    expect(failed.at).toBeNull();
    expect(rewrite.early).toBe(false);
  });

  it("shows the text of a checked answer only with Checked, after the hold of Checking (H10)", async () => {
    const text = watchEarly("you beat NFC Least");
    const checking = watchFor("Checking");
    freeWith("week-1");
    render(<HomePage />);
    await ask("week 1 results");
    await articleWith("week 1 results", "you beat NFC Least");
    expect(checking.at).not.toBeNull();
    expect(text.early).toBe(false);
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

  it("holds the words until Checked, then sharpens each word from a blur, with no stop control (H10, AT-44, AT-55)", async () => {
    const lines = recorded("week-1").split("\n\n");
    const cut = lines.findIndex((line) => line.includes('"state":"checked"'));
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
    // Each part up to the check is in, so the steps and "Checking" show, and no word of the text shows yet.
    const held = await articleWith("week 1 results", "Checking");
    expect(within(held).getByRole("list", { name: "Steps" })).toBeTruthy();
    expect(held.querySelectorAll(".stream-word")).toHaveLength(0);
    expect(held.textContent).not.toContain("you beat NFC Least");
    expect(screen.queryByRole("button", { name: /stop|cancel/i })).toBeNull();
    finish();
    const answer = await articleWith("week 1 results", "you beat NFC Least");
    expect(answer.textContent).toContain("Checked");
    expect(answer.querySelectorAll(".stream-word").length).toBeGreaterThan(10);
    // The whole text shows in one read, and its words sweep in one after another, so each word plays its own blur
    // and not one block. The sweep takes no more than --duration-very-slow.
    const delays = [...answer.querySelectorAll<HTMLElement>(".stream-word")].map((word) => parseFloat(word.style.animationDelay || "0"));
    expect(delays.at(-1)!).toBeGreaterThan(delays[0]);
    expect([...delays].sort((a, b) => a - b)).toEqual(delays);
    expect(delays.at(-1)! - delays[0]).toBeLessThanOrEqual(500);
    expect(screen.queryByRole("button", { name: /stop|cancel/i })).toBeNull();
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

describe("the block of a free answer (H27)", () => {
  it("shows a lead line and a ranked list of the players of Bo Girds, after Checked", async () => {
    const early = watchEarly("Kenneth Walker III");
    freeWith("block-list");
    render(<HomePage />);
    await ask("order my players by performance");
    const answer = await articleWith("order my players by performance", "Checked");
    expect(answer.textContent).toContain("Here are your players ranked by season fantasy points");
    const list = await within(answer).findByRole("list", { name: "Bo Girds by season points" });
    const rows = within(list).getAllByRole("listitem");
    expect(rows).toHaveLength(12);
    expect(rows[0].textContent).toContain("1");
    expect(rows[0].textContent).toContain("Kenneth Walker III");
    expect(rows[0].textContent).toContain("RB");
    expect(rows[0].textContent).toContain("183.4");
    expect(rows[8].textContent).toContain("On IR, can't play");
    // The block waits for the check with the text, so no row shows early (H10).
    expect(early.early).toBe(false);
    // The display tool never shows as a step.
    expect(within(within(answer).getByRole("list", { name: "Steps" })).getAllByRole("listitem")).toHaveLength(1);
  });

  it("shows a comparison of Bo Girds and Teehee as a table with its column names", async () => {
    freeWith("block-table", { team: 6 });
    render(<HomePage />);
    await ask("compare Bo Girds and Teehee");
    const answer = await articleWith("compare Bo Girds and Teehee", "Checked");
    const table = await within(answer).findByRole("table", { name: "Bo Girds vs Teehee" });
    expect(within(table).getAllByRole("columnheader").map((cell) => cell.textContent)).toEqual(["Stat", "Bo Girds", "Teehee"]);
    const [, first] = within(table).getAllByRole("row");
    expect(within(first).getAllByRole("cell").map((cell) => cell.textContent)).toEqual(["Rank", "2", "8"]);
  });

  it("shows a player card that says Lamar Jackson cannot play now, and only the block of the checked rewrite", async () => {
    freeWith("block-player");
    render(<HomePage />);
    await ask("how is Lamar Jackson doing");
    const answer = await articleWith("how is Lamar Jackson doing", "Checked");
    const card = await within(answer).findByRole("group", { name: "Lamar Jackson" });
    expect(card.textContent).toContain("QB");
    expect(card.textContent).toContain("BAL");
    expect(card.textContent).toContain("Bo Girds");
    expect(card.textContent).toContain("Can't play now");
    expect(card.textContent).toContain("on IR");
    expect(card.textContent).toContain("80.08");
    expect(answer.querySelectorAll('[role="group"]')).toHaveLength(1);
  });

  it("keeps the block with the answer, so a reload shows it with no new stream", async () => {
    freeWith("block-list");
    const { unmount } = render(<HomePage />);
    await ask("order my players by performance");
    await articleWith("order my players by performance", "Checked");
    await waitFor(() => expect(localStorage.getItem("cpc.thread")).toContain("Kenneth Walker III"));
    unmount();
    render(<HomePage />);
    const kept = await articleWith("order my players by performance", "Kenneth Walker III");
    expect(within(kept).getByRole("list", { name: "Bo Girds by season points" })).toBeTruthy();
    expect(freeCalls()).toHaveLength(1);
  });

  it("shows a week 1 answer with no block as text alone", async () => {
    freeWith("week-1");
    render(<HomePage />);
    await ask("week 1 results");
    const answer = await articleWith("week 1 results", "Checked");
    expect(answer.querySelector("[data-block]")).toBeNull();
  });
});


describe("the transaction feed of a free answer (AT-35)", () => {
  it("shows the moves of this week: a strip of the moves per day, one row per move with a dot for its kind", async () => {
    const early = watchEarly("Tutu Atwell");
    freeWith("moves-feed");
    render(<HomePage />);
    await ask("What moves happened this week?");
    const answer = await articleWith("What moves happened this week?", "Checked");
    expect(within(within(answer).getByRole("list", { name: "Steps" })).getAllByRole("listitem")[0].textContent).toContain("Reading the moves of this week");
    expect(within(answer).getByRole("img", { name: "Moves per day. Wed Nov 11: 5." })).toBeTruthy();
    const feed = within(answer).getByRole("list", { name: "Week 10 moves" });
    const rows = within(feed).getAllByRole("listitem");
    expect(rows).toHaveLength(5);
    // Newest first, each row names its kind, its team, and what it added and dropped.
    expect(rows[0].textContent).toContain("Free agent");
    expect(rows[0].textContent).toContain("Puka Deez");
    expect(rows[0].textContent).toContain("Tutu Atwell");
    expect(rows[0].textContent).toContain("Matthew Stafford");
    expect(rows[1].textContent).toContain("Bo Girds");
    expect(within(answer).getByRole("list", { name: "Kinds of move" }).textContent).toBe("Free agent");
    expect(early.early).toBe(false);
  });

  it("shows a trade row with what each side got, a waiver row with its bid, and the count past the rows", async () => {
    freeWith("moves-feed-week-6");
    render(<HomePage />);
    await ask("What moves happened in week 6?");
    const answer = await articleWith("What moves happened in week 6?", "Checked");
    const strip = within(answer).getByRole("img", { name: /^Moves per day\. Wed Oct 14: 17, Thu Oct 15: 2, / });
    expect(strip.getAttribute("aria-label")).toContain("Mon Oct 19: 0");
    const rows = within(within(answer).getByRole("list", { name: "Week 6 moves" })).getAllByRole("listitem");
    expect(rows).toHaveLength(20);
    const trade = rows.find((row) => row.textContent?.startsWith("Trade"))!;
    expect(trade.textContent).toContain("To Infinity and Bijan got");
    expect(trade.textContent).toContain("Malik Nabers, Jared Goff");
    expect(trade.textContent).toContain("Return of T Mac got");
    expect(trade.textContent).toContain("Bijan Robinson");
    expect(rows[0].textContent).toContain("Waiver claim");
    expect(rows[0].textContent).toContain("Terrance Ferguson");
    expect(rows[0].textContent).toContain("$0");
    expect(answer.textContent).toContain("36 more moves this week");
    expect(within(answer).getByRole("list", { name: "Kinds of move" }).textContent).toBe("TradeWaiver claimFree agent");
  });

  it("keeps the feed with the answer, so a reload shows it with no new stream", async () => {
    freeWith("moves-feed");
    const { unmount } = render(<HomePage />);
    await ask("What moves happened this week?");
    await articleWith("What moves happened this week?", "Checked");
    await waitFor(() => expect(localStorage.getItem("cpc.thread")).toContain("Tutu Atwell"));
    unmount();
    render(<HomePage />);
    const kept = await articleWith("What moves happened this week?", "Tutu Atwell");
    expect(within(kept).getByRole("list", { name: "Week 10 moves" })).toBeTruthy();
    expect(freeCalls()).toHaveLength(1);
  });
});


/* A free answer whose checked text is `text`, in the parts that the API streams for a live run: one step, the text,
   then the check. */
function textWith(text: string) {
  routes.push({ route: "free", topic: null, team: null, closest: [], suggestion: null, jev: { model: "jev-1.14.0", nouls: {}, choices: {} } });
  const parts = [
    { type: "start" },
    { type: "start-step" },
    { type: "finish-step" },
    { type: "data-check", id: "check", data: { state: "checking" } },
    { type: "text-start", id: "t" },
    { type: "text-delta", id: "t", delta: text },
    { type: "text-end", id: "t" },
    { type: "data-check", id: "check", data: { state: "checked" } },
    { type: "finish", finishReason: "stop" },
  ];
  streams.push(() => sse(`${parts.map((part) => `data: ${JSON.stringify(part)}\n\n`).join("")}data: [DONE]\n\n`));
}

/* The text block of the Answer: the one element that holds the text marks. */
function textBlockOf(answer: HTMLElement) {
  const block = answer.querySelector<HTMLElement>("[data-text-block]");
  expect(block).not.toBeNull();
  return block!;
}

describe("the text block of an Answer", () => {
  const MARKED = [
    "Lil Fridge is **3rd** of 12, and the gap is *small*.",
    "",
    "- Bo Girds won by 14.2",
    "- Teehee lost by 3.1",
    "",
    "1. Start Kenneth Walker III",
    "2. Sit Blake Corum",
  ].join("\n");

  it("renders bold, italic, a bullet list, and a numbered list as marks, live and kept (AT-36)", async () => {
    textWith(MARKED);
    render(<HomePage />);
    await ask("how is my team");
    const expectMarks = (answer: HTMLElement) => {
      const block = textBlockOf(answer);
      expect(within(block).getByText("3rd").closest("strong")).not.toBeNull();
      expect(within(block).getByText("small").closest("em")).not.toBeNull();
      expect([...block.querySelectorAll("ul li")].map((item) => item.textContent?.trim())).toEqual(["Bo Girds won by 14.2", "Teehee lost by 3.1"]);
      expect([...block.querySelectorAll("ol li")].map((item) => item.textContent?.trim())).toEqual(["Start Kenneth Walker III", "Sit Blake Corum"]);
      expect(block.textContent).not.toContain("*");
    };
    // The live card sweeps each word in, inside its marks.
    const live = await articleWith("how is my team", "Checked");
    await waitFor(() => expectMarks(live));
    expect(textBlockOf(live).querySelector("strong .stream-word")?.textContent).toBe("3rd");
    // The kept card takes the place of the live card, and a reload shows the same marks with no stream.
    await waitFor(() => expect(localStorage.getItem("cpc.thread")).toContain("Kenneth Walker III"), { timeout: 3000 });
    cleanup();
    render(<HomePage />);
    expectMarks(await articleWith("how is my team", "Sit Blake Corum"));
    expect(freeCalls()).toHaveLength(1);
  });

  it("shows a link, an image, a heading, and raw HTML as plain text, with no such element (AT-37)", async () => {
    const lines = [
      "## Week 9 recap",
      "",
      "Read [the recap](https://example.com/recap) first.",
      "",
      "![a chart](https://example.com/chart.png)",
      "",
      'Bo Girds won. <b>Bold</b> <a href="https://example.com">here</a> <script>alert(1)</script>',
      "",
      "| Team | Points |",
      "| --- | --- |",
      "| Bo Girds | 114.07 |",
    ];
    textWith(lines.join("\n"));
    render(<HomePage />);
    await ask("what happened");
    const answer = await articleWith("what happened", "Checked");
    const block = await waitFor(() => textBlockOf(answer));
    for (const line of ["## Week 9 recap", "Read [the recap](https://example.com/recap) first.", "![a chart](https://example.com/chart.png)", "<b>Bold</b>", '<a href="https://example.com">here</a>', "<script>alert(1)</script>", "| Bo Girds | 114.07 |"]) {
      expect(block.textContent).toContain(line);
    }
    expect(block.querySelectorAll("a, img, h1, h2, h3, h4, h5, h6, b, script, table")).toHaveLength(0);
    // Only the elements of the allowlist reach the page.
    const tags = new Set([...block.querySelectorAll("*")].map((element) => element.tagName.toLowerCase()));
    expect([...tags].every((tag) => ["p", "ul", "ol", "li", "strong", "em", "span"].includes(tag))).toBe(true);
  });
});
