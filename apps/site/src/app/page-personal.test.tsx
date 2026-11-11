/**
 * Tests for the personal Topics of the front door at /. Each test renders the page with the fixed copy of the published data of cpc,
 * and the personal route plays a stream that the API recorded in a live run with the real Jev and the real Claude.
 */
import { copyFileSync, mkdirSync, mkdtempSync, readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, onTestFinished, vi } from "vitest";
import { fixturePublished, readFixtureSite } from "@/fixtures/sites";
import { FIXING_LINE } from "./front-door/free-answer";
import { MISS_LEAD } from "./front-door/miss-card";
import HomePage from "./front-door/door-page";

/* The readers of public/ read the fixed copy of the cpc data, so a weekly publish never changes these tests. The spy
   runs before the imports, because the week reader takes its folder when it loads. Each test sets it again, because a
   restore of the mocks removes it. */
await vi.hoisted(async () => (await import("@/fixtures/sites")).readFixtureSite("cpc"));
beforeEach(() => readFixtureSite("cpc"));

const PASSPHRASE = "cornerstone-test";
const LIL_FRIDGE = 3;
const fetchStub = vi.fn();
const streams: (() => Response)[] = [];

// The path comes from this file and not from the working folder, because the tests point the working folder at the fixed copy.
const recorded = (name: string) => readFileSync(join(__dirname, "..", "fixtures", "personal-answer", `${name}.sse`), "utf8");
const personalCalls = () => fetchStub.mock.calls.filter(([url]) => String(url).endsWith("/personal"));

function sse(body: ReadableStream<Uint8Array> | string): Response {
  return new Response(body, { headers: { "Content-Type": "text/event-stream", "x-vercel-ai-ui-message-stream": "v1" } });
}

/* A recorded stream that holds back every line from the first text part on, until the test calls `release`. */
function heldStream(name: string) {
  const lines = recorded(name).split("\n\n").filter((line) => line.trim() !== "");
  const at = lines.findIndex((line) => line.includes('"text-start"'));
  const encoder = new TextEncoder();
  let release = () => {};
  const body = new ReadableStream<Uint8Array>({
    start(controller) {
      for (const line of lines.slice(0, at)) controller.enqueue(encoder.encode(`${line}\n\n`));
      release = () => {
        for (const line of lines.slice(at)) controller.enqueue(encoder.encode(`${line}\n\n`));
        controller.close();
      };
    },
  });
  streams.push(() => sse(body));
  return () => release();
}

/* Open "More" and tap one Topic of the list. */
async function tapInMore(name: string) {
  fireEvent.click(await screen.findByRole("button", { name: "More" }));
  const list = await screen.findByRole("list", { name: "All Topics" });
  fireEvent.click(within(list).getByRole("button", { name: new RegExp(`^${name}:`) }));
}

async function articleWith(name: string, text: string) {
  await waitFor(() => expect(screen.getByRole("article", { name }).textContent).toContain(text), { timeout: 3000 });
  return screen.getByRole("article", { name });
}

beforeEach(() => {
  fetchStub.mockImplementation(async (url: string) => {
    if (String(url).endsWith("/personal")) return streams.shift()?.() ?? new Response("", { status: 500 });
    return new Response("", { status: 404 });
  });
  vi.stubGlobal("fetch", fetchStub);
  localStorage.setItem("cpc.your-team", String(LIL_FRIDGE));
  localStorage.setItem("cpc.passphrase", PASSPHRASE);
});

afterEach(() => {
  cleanup();
  localStorage.clear();
  fetchStub.mockReset();
  streams.length = 0;
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe("the personal Topics of Lil Fridge", () => {
  it("sends the Topic and Your team with the passphrase to the personal route of the client", async () => {
    streams.push(() => sse(recorded("weak-spots")));
    render(<HomePage />);
    await tapInMore("Weak spots");
    await waitFor(() => expect(personalCalls()).toHaveLength(1));
    const [url, init] = personalCalls()[0];
    expect(url).toMatch(/\/clients\/cpc\/personal$/);
    expect(new Headers(init.headers).get("X-League-Passphrase")).toBe(PASSPHRASE);
    expect(JSON.parse(init.body)).toMatchObject({ topic: "weak_spots", roster_id: LIL_FRIDGE, team: null });
    // A tap sends no typed question, so the API may serve its kept Answer.
    expect(JSON.parse(init.body)).not.toHaveProperty("question");
  });

  it("shows the data block alone first, then the text under it, then checked (AT-18, AT-20)", async () => {
    const release = heldStream("weak-spots");
    render(<HomePage />);
    await tapInMore("Weak spots");
    // The block of the recorded run: QB and RB both rank 7th of 12, with no hole.
    const answer = await articleWith("Weak spots", "Weakest spot");
    expect(answer.textContent).toContain("7th of 12");
    expect(answer.textContent).not.toContain("Your team has no true holes");
    expect(answer.textContent).not.toContain("Checked");
    expect(within(answer).queryByRole("link", { name: /Read the full report/ })).toBeNull();
    release();
    await articleWith("Weak spots", "Checked");
    expect(answer.textContent).toContain("Your team has no true holes.");
    // The text sits under the data block in the card.
    const text = answer.textContent ?? "";
    expect(text.indexOf("Weakest spot")).toBeLessThan(text.indexOf("Your team has no true holes"));
    expect(within(answer).getByRole("link", { name: /Read the full report/ }).getAttribute("href")).toBe(`/2026/managers/${LIL_FRIDGE}/`);
  });

  it("shows the first line as a live step before the data block lands", async () => {
    streams.push(() => sse(new ReadableStream<Uint8Array>({ start() {} })));
    render(<HomePage />);
    await tapInMore("Weak spots");
    const answer = await articleWith("Weak spots", "Reading the league…");
    const [step] = within(within(answer).getByRole("list", { name: "Steps" })).getAllByRole("listitem");
    expect(step.getAttribute("data-state")).toBe("live");
  });

  it("shows a live Writing step between the data block and the text, and drops it with the check", async () => {
    const release = heldStream("weak-spots");
    render(<HomePage />);
    await tapInMore("Weak spots");
    const answer = await articleWith("Weak spots", "Weakest spot");
    const steps = () => within(answer).queryByRole("list", { name: "Steps" });
    await waitFor(() => expect(steps()?.textContent).toContain("Writing…"));
    // The step sits under the data block, where the text lands.
    const text = answer.textContent ?? "";
    expect(text.indexOf("Weakest spot")).toBeLessThan(text.indexOf("Writing…"));
    release();
    await articleWith("Weak spots", "Checked");
    expect(answer.textContent).not.toContain("Writing");
  });

  it("keeps a checked Answer, so a reload shows it with no new stream (AT-29, story 36)", async () => {
    streams.push(() => sse(recorded("weak-spots")));
    const first = render(<HomePage />);
    await tapInMore("Weak spots");
    await articleWith("Weak spots", "Checked");
    // The Thread keeps the Answer once the stream ends, a render after the mark shows "Checked".
    await waitFor(() => expect(localStorage.getItem("cpc.thread")).toContain("no true holes"));
    first.unmount();
    render(<HomePage />);
    const kept = await articleWith("Weak spots", "Your team has no true holes.");
    expect(kept.textContent).toContain("Checked");
    expect(personalCalls()).toHaveLength(1);
  });

  it("plays a kept Answer of the API at once, with its block and checked", async () => {
    // A kept Answer never streams: no word plays its blur, and no "Checking" mark shows (AT-8).
    let streamed = false;
    const observer = new MutationObserver(() => {
      if (document.body.textContent?.includes("Checking") || document.querySelector(".stream-word")) streamed = true;
    });
    observer.observe(document.body, { childList: true, subtree: true, characterData: true });
    onTestFinished(() => observer.disconnect());
    streams.push(() => sse(recorded("weak-spots-kept")));
    render(<HomePage />);
    await tapInMore("Weak spots");
    const answer = await articleWith("Weak spots", "Checked");
    expect(answer.textContent).toContain("Weakest spot");
    expect(answer.textContent).toContain("Your team has no true holes.");
    expect(streamed).toBe(false);
  });

  it("fades a failed first text, shows the fixing line, and keeps only the checked rewrite (AT-21)", async () => {
    streams.push(() => sse(recorded("stack-up-fixed")));
    render(<HomePage />);
    await tapInMore("How you stack up");
    const answer = await articleWith("How you stack up", "Checked");
    expect(answer.textContent).toContain("Your worst part is Season Production");
    expect(answer.textContent).not.toContain("Your weakest part is Season Production");
    expect(answer.textContent).not.toContain(FIXING_LINE);
    expect(answer.textContent).toContain("Projection Ahead");
  });

  it("says on the data block of How you stack up that the grade is as of today (ticket 32)", async () => {
    streams.push(() => sse(recorded("stack-up-fixed")));
    render(<HomePage />);
    await tapInMore("How you stack up");
    const answer = await articleWith("How you stack up", "Checked");
    expect(within(answer).getByText("as of today")).toBeTruthy();
  });

  it("shows no as of label on the data block of Weak spots (ticket 32)", async () => {
    streams.push(() => sse(recorded("weak-spots")));
    render(<HomePage />);
    await tapInMore("Weak spots");
    const answer = await articleWith("Weak spots", "Checked");
    expect(within(answer).queryByText("as of today")).toBeNull();
  });

  it("never shows the failed first text, and shows the rewrite only with Checked (H10)", async () => {
    const seen: { failed: boolean; early: boolean } = { failed: false, early: false };
    const observer = new MutationObserver(() => {
      const text = document.body.textContent ?? "";
      if (text.includes("Your weakest part is Season Production")) seen.failed = true;
      if (text.includes("Your worst part is Season Production") && !text.includes("Checked")) seen.early = true;
    });
    observer.observe(document.body, { childList: true, subtree: true, characterData: true });
    onTestFinished(() => observer.disconnect());
    streams.push(() => sse(recorded("stack-up-fixed")));
    render(<HomePage />);
    await tapInMore("How you stack up");
    await articleWith("How you stack up", "Your worst part is Season Production");
    expect(seen).toEqual({ failed: false, early: false });
  });

  it("turns a second failed check into the honest miss with the closest Topics", async () => {
    streams.push(() => sse(recorded("weak-spots-miss")));
    render(<HomePage />);
    await tapInMore("Weak spots");
    const miss = await articleWith("Weak spots", MISS_LEAD);
    const chips = within(within(miss).getByRole("group", { name: "Closest Topics" })).getAllByRole("button");
    expect(chips.map((chip) => chip.textContent)).toEqual(["How you stack up", "Waiver targets", "Trade ideas"]);
  });

  it("keeps the data block of an honest miss, with the miss line in the place of the text (H17)", async () => {
    streams.push(() => sse(recorded("weak-spots-miss")));
    const first = render(<HomePage />);
    await tapInMore("Weak spots");
    const miss = await articleWith("Weak spots", MISS_LEAD);
    expect(miss.textContent).toContain("Weakest spot");
    expect(miss.textContent).toContain("7th of 12");
    const text = miss.textContent ?? "";
    expect(text.indexOf("Weakest spot")).toBeLessThan(text.indexOf(MISS_LEAD));
    expect(text).not.toContain("Checked");
    // The miss stays in the Thread with its block, so a reload shows both with no new stream.
    await waitFor(() => expect(localStorage.getItem("cpc.thread")).toContain("Weakest spot"));
    first.unmount();
    render(<HomePage />);
    const kept = await articleWith("Weak spots", MISS_LEAD);
    expect(kept.textContent).toContain("7th of 12");
    expect(personalCalls()).toHaveLength(1);
  });

  it("shows the cap line with the closest Topics past the team cap, and hides the chips (AT-37)", async () => {
    // The stream of a live run with 25 Answers of Lil Fridge seeded in the store: no Claude call, and the cap line.
    streams.push(() => sse(recorded("stack-up-cap")));
    render(<HomePage />);
    await tapInMore("How you stack up");
    const cap = await articleWith("How you stack up", "That's 25 questions today.");
    expect(cap.textContent).toContain("Ask again tomorrow.");
    expect(cap.textContent).not.toContain("Checked");
    const chips = within(within(cap).getByRole("group", { name: "Closest Topics" })).getAllByRole("button");
    expect(chips.map((chip) => chip.textContent)).toEqual(["Weak spots", "Power rankings", "Your season"]);
    expect(screen.queryByRole("group", { name: "Suggestions" })).toBeNull();
    // The cap item stays in the Thread, so a reload shows the line again with no new stream.
    await waitFor(() => expect(localStorage.getItem("cpc.thread")).toContain("questions today"));
  });

  it("shows no report link on waiver targets when the client omits the waiver package", async () => {
    streams.push(() => sse(recorded("waiver-targets")));
    render(<HomePage />);
    await tapInMore("Waiver targets");
    const answer = await articleWith("Waiver targets", "Checked");
    expect(answer.textContent).toContain("Sione Vaki");
    // The fixed copy of cpc holds a waiver file, but cpc builds no waiver page, so a link would give a 404.
    expect(within(answer).queryByRole("link", { name: /Read the full report/ })).toBeNull();
  });

  it("never names an inner tool, a rival, or the commissioner by name in the cards", async () => {
    for (const name of ["weak-spots", "stack-up-fixed", "waiver-targets"]) streams.push(() => sse(recorded(name)));
    render(<HomePage />);
    for (const name of ["Weak spots", "How you stack up", "Waiver targets"]) {
      await tapInMore(name);
      await articleWith(name, "Checked");
    }
    const text = (screen.getByRole("region", { name: "Thread" }).textContent ?? "").toLowerCase();
    for (const word of ["jev", "advisor", "finder", "rival", "brian"]) expect(text).not.toContain(word);
    // Three streams play one after another, each with its held "Checking" and fixing line, so the test takes longer.
  }, 15000);
});

describe("the links of the personal Topics", () => {
  /* A temp public/ folder with the latest week of the fixed copy of cpc and its managers file, but no waiver file. */
  async function dataWithoutWaiver() {
    const root = mkdtempSync(join(tmpdir(), "front-door-personal-"));
    const from = fixturePublished("cpc", "2026");
    mkdirSync(join(root, "public", "2026", "week-08"), { recursive: true });
    for (const file of ["page.json", "topics.json"]) copyFileSync(join(from, "week-08", file), join(root, "public", "2026", "week-08", file));
    copyFileSync(join(from, "managers.json"), join(root, "public", "2026", "managers.json"));
    vi.spyOn(process, "cwd").mockReturnValue(root);
    // The readers read the working folder when they load, so reset them.
    vi.resetModules();
    return import("@/lib/data/front-door-data");
  }

  /* The client values of the build, with the package list set by the test. The fixed copy of cpc holds a waiver file,
     so only the package list tells whether the client has the waiver page. */
  async function dataWithPackages(packages: string[]) {
    readFixtureSite("cpc");
    vi.resetModules();
    const values = await import("../generated/client-values");
    vi.doMock("../generated/client-values", () => ({ clientValues: { ...values.clientValues, packages } }));
    onTestFinished(() => vi.doUnmock("../generated/client-values"));
    return import("@/lib/data/front-door-data");
  }

  it("give waiver targets the waiver page when the client takes the waiver package and the week has its file", async () => {
    const { loadFrontDoor } = await dataWithPackages(["week", "managers", "waiver"]);
    expect(loadFrontDoor()?.personalHrefs[LIL_FRIDGE]).toEqual({
      weak_spots: `/2026/managers/${LIL_FRIDGE}/`,
      stack_up: `/2026/managers/${LIL_FRIDGE}/`,
      waiver_targets: "/2026/week-08/waiver/",
    });
  });

  it("give waiver targets no link when the client omits the waiver package, even with a waiver file", async () => {
    const { loadFrontDoor } = await dataWithPackages(["week", "managers"]);
    expect(loadFrontDoor()?.personalHrefs[LIL_FRIDGE].waiver_targets).toBeNull();
    expect(loadFrontDoor()?.personalHrefs[LIL_FRIDGE].weak_spots).toBe(`/2026/managers/${LIL_FRIDGE}/`);
  });

  it("give the manager Topics no link when the client omits the managers package, even with a managers file", async () => {
    const { loadFrontDoor } = await dataWithPackages(["week", "waiver"]);
    const hrefs = loadFrontDoor()?.personalHrefs[LIL_FRIDGE];
    expect(hrefs?.weak_spots).toBeNull();
    expect(hrefs?.stack_up).toBeNull();
    expect(hrefs?.waiver_targets).toBe("/2026/week-08/waiver/");
  });

  it("give waiver targets no link when the client publishes no waiver file", async () => {
    const { loadFrontDoor } = await dataWithoutWaiver();
    expect(loadFrontDoor()?.personalHrefs[LIL_FRIDGE].waiver_targets).toBeNull();
    expect(loadFrontDoor()?.personalHrefs[LIL_FRIDGE].weak_spots).toBe(`/2026/managers/${LIL_FRIDGE}/`);
  });
});
