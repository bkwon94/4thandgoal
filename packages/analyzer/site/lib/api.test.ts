/**
 * Tests for the API client. fetch is a test stub that returns real Response objects.
 */
import { afterEach, describe, expect, it, vi } from "vitest";
import { ApiError, fetchTeams, postAnalyze, postFind, retryText, toApiError, toErrorLine, type ApiTarget } from "./api";

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
  it("calls the teams, analyze, and find routes of the client of the target", async () => {
    const teams = { teams: [] };
    const stub = vi.fn().mockImplementation(async () => new Response(JSON.stringify(teams)));
    vi.stubGlobal("fetch", stub);
    await fetchTeams(TARGET, "pw");
    const signal = new AbortController().signal;
    await postAnalyze(TARGET, "pw", { season: 2026, asker: 1, sides: [] }, signal).catch(() => undefined);
    await postFind(TARGET, "pw", { season: 2026, asker: 1, partner: 2 }, signal).catch(() => undefined);
    expect(stub.mock.calls.map(([url]) => url)).toEqual([
      "https://api.example.test/clients/norcal/teams?season=2026",
      "https://api.example.test/clients/norcal/analyze",
      "https://api.example.test/clients/norcal/find",
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
