/**
 * Tests for the API client. fetch is a test stub that returns real Response objects.
 */
import { afterEach, describe, expect, it, vi } from "vitest";
import { ApiError, fetchTeams, postAnalyze, retryText, streamFind, toApiError, toErrorLine, type ApiTarget } from "./api";
import { findResponse } from "./fixtures/api";

// The API of the test. The client slug is not cpc, so a path that drops the slug or fixes it to cpc fails.
const TARGET: ApiTarget = { url: "https://api.example.test", client: "norcal", season: 2026 };

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("fetchTeams", () => {
  it("fills a missing avatar with null", async () => {
    const body = { teams: [{ roster_id: 1, team: "A", manager: "Ana", players: [] }] };
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify(body))));
    expect((await fetchTeams(TARGET, "pw"))[0].avatar).toBeNull();
  });

  it("throws an ApiError with the status and the Retry-After seconds", async () => {
    const response = new Response(JSON.stringify({ detail: { message: "slow down" } }), {
      status: 429,
      headers: { "Retry-After": "12" },
    });
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(response));
    await expect(fetchTeams(TARGET, "pw")).rejects.toMatchObject({ status: 429, message: "slow down", retryAfter: 12 });
    await expect(fetchTeams(TARGET, "pw")).rejects.toBeInstanceOf(ApiError);
  });
});

describe("the client in the path", () => {
  it("calls the teams, analyze, and find stream routes of the client of the target", async () => {
    const teams = { teams: [] };
    const stub = vi.fn().mockImplementation(async () => new Response(JSON.stringify(teams)));
    vi.stubGlobal("fetch", stub);
    await fetchTeams(TARGET, "pw");
    const signal = new AbortController().signal;
    await postAnalyze(TARGET, "pw", { season: 2026, asker: 1, sides: [] }, signal).catch(() => undefined);
    const events = { onStep: () => {}, onTeam: () => {} };
    await streamFind(TARGET, "pw", { season: 2026, asker: 1, partner: 2 }, events, signal).catch(() => undefined);
    expect(stub.mock.calls.map(([url]) => url)).toEqual([
      "https://api.example.test/clients/norcal/teams?season=2026",
      "https://api.example.test/clients/norcal/analyze",
      "https://api.example.test/clients/norcal/find-stream",
    ]);
  });
});

describe("toApiError", () => {
  it("reads Retry-After from a 429", async () => {
    const response = new Response("{}", { status: 429, headers: { "Retry-After": "7" } });
    expect(await toApiError(response)).toMatchObject({ status: 429, retryAfter: 7 });
  });

  it("reads the message from a 422 object detail", async () => {
    const response = new Response(JSON.stringify({ detail: { message: "bad trade" } }), { status: 422 });
    const error = await toApiError(response);
    expect(error).toMatchObject({ status: 422, message: "bad trade" });
    expect(error.retryAfter).toBeUndefined();
  });
});

describe("retryText", () => {
  it("reads seconds for a wait of an hour or less", () => {
    expect(retryText(30)).toBe("Too many requests. Try again in 30 seconds.");
    expect(retryText(3600)).toBe("Too many requests. Try again in 3600 seconds.");
  });

  it("reads hours, rounded up, for a wait over an hour", () => {
    expect(retryText(50000)).toBe("Too many requests. Try again in 14 hours.");
    expect(retryText(3601)).toBe("Too many requests. Try again in 2 hours.");
  });

  it("reads soon when the wait is missing", () => {
    expect(retryText()).toBe("Too many requests. Try again soon.");
  });
});

describe("response parse", () => {
  it("throws an ApiError that names the path of the bad field", async () => {
    const body = { teams: [{ roster_id: "one", team: "A", manager: "Ana", players: [] }] };
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify(body))));
    const error = await fetchTeams(TARGET, "pw").catch((e) => e);
    expect(error).toBeInstanceOf(ApiError);
    expect(error.message).toContain("teams.0.roster_id");
  });

  it("throws the same error for a wrong analyze body", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("{}")));
    const call = postAnalyze(TARGET, "pw", { season: 2026, asker: 1, sides: [] }, new AbortController().signal);
    await expect(call).rejects.toBeInstanceOf(ApiError);
  });
});

describe("toErrorLine for a wrong body", () => {
  it("gives the plain line for a 502", () => {
    const line = toErrorLine(new ApiError(502, "wrong body"), false, "timed out");
    expect(line).toEqual({ message: "The API sent an answer the site cannot read." });
  });
});

/* A find stream as the API sends it: each part as one `data:` line of an event stream. */
function streamOf(parts: unknown[]): Response {
  const text = [...parts.map((part) => `data: ${JSON.stringify(part)}\n\n`), "data: [DONE]\n\n"].join("");
  return new Response(text, { headers: { "content-type": "text/event-stream" } });
}

describe("streamFind", () => {
  const body = { season: 2026, asker: 6 };

  it("posts the find body to the find stream of the client, and gives each step, each team read, and the document", async () => {
    const stub = vi.fn().mockResolvedValue(
      streamOf([
        { type: "start" },
        { type: "data-step", data: { line: "Reading every team", live: true } },
        { type: "data-team", data: { roster_id: 3 } },
        { type: "data-team", data: { roster_id: 1 } },
        { type: "data-step", data: { line: "Read 11 teams", live: false } },
        { type: "data-answer", data: { kind: "find", document: findResponse } },
        { type: "finish" },
      ]),
    );
    vi.stubGlobal("fetch", stub);
    const steps: [string, boolean][] = [];
    const teams: number[] = [];
    const doc = await streamFind(TARGET, "pw", body, { onStep: (line, live) => steps.push([line, live]), onTeam: (id) => teams.push(id) }, new AbortController().signal);
    const [url, init] = stub.mock.calls[0];
    expect(url).toBe("https://api.example.test/clients/norcal/find-stream");
    expect(init.headers["X-League-Passphrase"]).toBe("pw");
    expect(JSON.parse(init.body)).toEqual(body);
    expect(steps).toEqual([
      ["Reading every team", true],
      ["Read 11 teams", false],
    ]);
    expect(teams).toEqual([3, 1]);
    expect(doc.trades).toHaveLength(findResponse.trades.length);
  });

  it("throws an ApiError with the status and the line of an error part", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(streamOf([{ type: "data-error", data: { status: 503, line: "Try again in a minute." } }])));
    await expect(streamFind(TARGET, "pw", body, { onStep: () => {}, onTeam: () => {} }, new AbortController().signal)).rejects.toMatchObject({
      status: 503,
      detail: "Try again in a minute.",
    });
  });

  it("throws the ApiError of a failed response, such as a 500", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("{}", { status: 500 })));
    await expect(streamFind(TARGET, "pw", body, { onStep: () => {}, onTeam: () => {} }, new AbortController().signal)).rejects.toMatchObject({ status: 500 });
  });

  it("drains the stream to its end after the document, so it leaves no open stream for an abort to cut", async () => {
    const encoder = new TextEncoder();
    const chunks = [
      { type: "data-answer", data: { kind: "find", document: findResponse } },
      { type: "data-error", data: { status: 500, line: "late" } },
      { type: "finish" },
    ].map((part) => encoder.encode(`data: ${JSON.stringify(part)}\n\n`));
    chunks.push(encoder.encode("data: [DONE]\n\n"));
    const cancel = vi.fn();
    let reads = 0;
    const body = new ReadableStream<Uint8Array>({
      pull(controller) {
        reads += 1;
        const chunk = chunks.shift();
        if (chunk) controller.enqueue(chunk);
        else controller.close();
      },
      cancel,
    });
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(body, { headers: { "content-type": "text/event-stream" } })));
    const controller = new AbortController();
    const doc = await streamFind(TARGET, "pw", { season: 2026, asker: 6 }, { onStep: () => {}, onTeam: () => {} }, controller.signal);
    expect(doc.trades).toHaveLength(findResponse.trades.length);
    await vi.waitFor(() => expect(reads).toBeGreaterThanOrEqual(5));
    expect(chunks).toHaveLength(0);
    controller.abort();
    expect(cancel).not.toHaveBeenCalled();
  });

  it("tells the finder when the pick has no more trades, before the document", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        streamOf([
          { type: "data-trades-done", data: {} },
          { type: "data-answer", data: { kind: "find", document: findResponse } },
        ]),
      ),
    );
    const seen: string[] = [];
    await streamFind(TARGET, "pw", body, { onStep: () => {}, onTeam: () => {}, onTradesDone: () => seen.push("done") }, new AbortController().signal);
    expect(seen).toEqual(["done"]);
  });

  it("throws a 502 for a stream that ends with no document", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(streamOf([{ type: "data-step", data: { line: "Reading every team", live: true } }])));
    await expect(streamFind(TARGET, "pw", body, { onStep: () => {}, onTeam: () => {} }, new AbortController().signal)).rejects.toMatchObject({ status: 502 });
  });
});
