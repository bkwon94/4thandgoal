/**
 * Tests for the client of the What-if route against a real local HTTP server that sends a recorded answer of the API.
 * They check the path and the body of the call, the parse of the answer, a refusal, a cancel, and an API that is down.
 */
// @vitest-environment node
import { createServer, type IncomingMessage, type Server } from "node:http";
import type { AddressInfo } from "node:net";
import { afterAll, beforeAll, describe, expect, it } from "vitest";
import winAbove from "../fixtures/what-if-win-above.json";
import { WhatIfError, whatIfApi, type WhatIfApi } from "./what-if-api";

let server: Server;
let api: WhatIfApi;
let port: number;
const seen: { url?: string; method?: string; body?: unknown }[] = [];

function bodyOf(request: IncomingMessage): Promise<string> {
  return new Promise((done) => {
    let text = "";
    request.on("data", (chunk) => (text += chunk));
    request.on("end", () => done(text));
  });
}

beforeAll(async () => {
  server = createServer(async (request, response) => {
    const body = JSON.parse(await bodyOf(request));
    seen.push({ url: request.url, method: request.method, body });
    response.setHeader("Content-Type", "application/json");
    if (body.you === 99) {
      response.writeHead(422);
      response.end(JSON.stringify({ detail: "Roster 99 is not a team of the league." }));
      return;
    }
    if (body.you === 1) {
      // The slow answer of a cancel test. The client goes away before it.
      setTimeout(() => response.end(JSON.stringify(winAbove)), 500);
      return;
    }
    response.end(JSON.stringify(winAbove));
  });
  await new Promise<void>((done) => server.listen(0, "127.0.0.1", done));
  port = (server.address() as AddressInfo).port;
  api = whatIfApi({ url: `http://127.0.0.1:${port}`, client: "cpc" });
});

afterAll(() => new Promise<void>((done) => server.close(() => done())));

const SET = [{ week: 11, game: "win", median: "above" }] as const;

describe("whatIfApi", () => {
  it("posts Your team and the set results to the What-if route of the client, and parses the page of the answer", async () => {
    const answer = await api({ you: 6, set: [...SET] }, new AbortController().signal);
    expect(seen.at(-1)).toEqual({ url: "/clients/cpc/sim/what-if", method: "POST", body: { you: 6, set: [...SET] } });
    expect(answer.page.playoff).toBe(86);
    expect(answer.page.sentence).toBe("Win 3 of the 6 left and you're in.");
    expect(answer.set).toEqual([...SET]);
  });

  it("gives the detail of a 422 refusal", async () => {
    const failure = await api({ you: 99, set: [...SET] }, new AbortController().signal).catch((error) => error);
    expect(failure).toBeInstanceOf(WhatIfError);
    expect(failure.status).toBe(422);
    expect(failure.message).toBe("Roster 99 is not a team of the league.");
  });

  it("stops the call on a cancel, with an abort and no WhatIfError", async () => {
    const cancel = new AbortController();
    const call = api({ you: 1, set: [...SET] }, cancel.signal).catch((error) => error);
    cancel.abort();
    const failure = await call;
    expect(failure).not.toBeInstanceOf(WhatIfError);
    expect(failure.name).toBe("AbortError");
  });

  it("gives a WhatIfError with no status when the API is down", async () => {
    // Port 9 is the discard port, which nothing on the machine serves, so the connection is refused.
    const down = whatIfApi({ url: "http://127.0.0.1:9", client: "cpc" });
    const failure = await down({ you: 6, set: [...SET] }, new AbortController().signal).catch((error) => error);
    expect(failure).toBeInstanceOf(WhatIfError);
    expect(failure.status).toBe(0);
  });
});
