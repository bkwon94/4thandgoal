/**
 * Tests for the failed calls of the Suggestions route and of the key check. Each one goes through the shared request
 * of ask-api.ts, so a 429 keeps the wait of its Retry-After header, as a 429 of the ask route does.
 */
import { afterEach, describe, expect, it, mock } from "bun:test";
import { stubGlobal } from "../../../test/stubs";
import { AskError } from "./ask-api";
import { checkCurrent, fetchSuggestions } from "./suggestions-api";

const TARGET = { url: "https://api.test", client: "cpc" };

afterEach(() => {});

describe("the Suggestions route", () => {
  it("gives the seconds of the Retry-After header on a 429", async () => {
    stubGlobal(
      "fetch",
      mock(async () => new Response("", { status: 429, headers: { "Retry-After": "42" } })),
    );
    const failure = await fetchSuggestions(TARGET, "pw", {
      roster_id: 3,
      order: [],
      opened: {},
    }).catch((error: unknown) => error);
    expect(failure).toBeInstanceOf(AskError);
    expect(failure).toMatchObject({ status: 429, retryAfter: 42 });
  });

  it("gives no wait on a 429 with no Retry-After header", async () => {
    stubGlobal(
      "fetch",
      mock(async () => new Response("", { status: 429 })),
    );
    await expect(checkCurrent(TARGET, "pw", [])).rejects.toMatchObject({
      status: 429,
      retryAfter: undefined,
    });
  });

  it("throws a 502 on a body that the schema rejects", async () => {
    stubGlobal(
      "fetch",
      mock(async () => Response.json({ facts: "none" })),
    );
    await expect(
      fetchSuggestions(TARGET, "pw", { roster_id: 3, order: [], opened: {} }),
    ).rejects.toMatchObject({ status: 502 });
  });

  it("throws a status of 0 on a call that never reaches the API", async () => {
    stubGlobal(
      "fetch",
      mock(async () => Promise.reject(new TypeError("offline"))),
    );
    await expect(
      fetchSuggestions(TARGET, "pw", { roster_id: 3, order: [], opened: {} }),
    ).rejects.toMatchObject({ status: 0 });
  });

  it("sends the passphrase to the path of the client", async () => {
    const stub = mock(async () => Response.json({ facts: {}, urgent: [] }));
    stubGlobal("fetch", stub);
    await fetchSuggestions(TARGET, "pw", { roster_id: 3, order: [], opened: {} });
    expect(stub).toHaveBeenCalledWith(
      "https://api.test/clients/cpc/suggestions",
      expect.objectContaining({
        method: "POST",
        headers: expect.objectContaining({ "X-League-Passphrase": "pw" }),
      }),
    );
  });
});
