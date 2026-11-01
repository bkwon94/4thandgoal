/**
 * Tests for the API client. fetch is a test stub that returns real Response objects.
 */
import { afterEach, describe, expect, it, vi } from "vitest";
import { ApiError, fetchTeams, postAnalyze, retryText, toApiError, toErrorLine } from "./api";

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("fetchTeams", () => {
  it("fills a missing avatar with null", async () => {
    const body = { teams: [{ roster_id: 1, team: "A", manager: "Ana", players: [] }] };
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify(body))));
    expect((await fetchTeams("pw"))[0].avatar).toBeNull();
  });

  it("throws an ApiError with the status and the Retry-After seconds", async () => {
    const response = new Response(JSON.stringify({ detail: { message: "slow down" } }), {
      status: 429,
      headers: { "Retry-After": "12" },
    });
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(response));
    await expect(fetchTeams("pw")).rejects.toMatchObject({ status: 429, message: "slow down", retryAfter: 12 });
    await expect(fetchTeams("pw")).rejects.toBeInstanceOf(ApiError);
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
    const error = await fetchTeams("pw").catch((e) => e);
    expect(error).toBeInstanceOf(ApiError);
    expect(error.message).toContain("teams.0.roster_id");
  });

  it("throws the same error for a wrong analyze body", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("{}")));
    const call = postAnalyze("pw", { season: 2026, asker: 1, sides: [] }, new AbortController().signal);
    await expect(call).rejects.toBeInstanceOf(ApiError);
  });
});

describe("toErrorLine for a wrong body", () => {
  it("offers no retry for a 502", () => {
    const line = toErrorLine(new ApiError(502, "wrong body"), false, "timed out");
    expect(line).toEqual({ message: "The API sent an answer the site cannot read.", retry: false });
  });
});
