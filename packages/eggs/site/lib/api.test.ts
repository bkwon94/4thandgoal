/**
 * Tests for the client of the eggs routes against a real local HTTP server: the wait of a 429 and the reason of a refusal.
 * The server answers as the API does, so the test reads the real parse of each answer.
 */
// @vitest-environment node
import { createServer, type Server } from "node:http";
import type { AddressInfo } from "node:net";
import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { EggsError, eggsApi, type EggsApi } from "./api";

let server: Server;
let api: EggsApi;

beforeAll(async () => {
  server = createServer((request, response) => {
    response.setHeader("Content-Type", "application/json");
    if (request.url?.endsWith("/check")) {
      response.writeHead(429, { "Retry-After": "690" });
      response.end(JSON.stringify({ detail: "Too many egg checks." }));
      return;
    }
    response.writeHead(422);
    response.end(JSON.stringify({ detail: "EAGLES has a winner." }));
  });
  await new Promise<void>((done) => server.listen(0, "127.0.0.1", done));
  const { port } = server.address() as AddressInfo;
  api = eggsApi({ url: `http://127.0.0.1:${port}`, client: "cpc" });
});

afterAll(() => new Promise<void>((done) => server.close(() => done())));

describe("eggsApi", () => {
  it("gives the seconds of the Retry-After header on a 429 of the check", async () => {
    const failure = await api.check({ page: "/", target: "luck-3", action: "tap2", conditions: {} }).catch((error) => error);
    expect(failure).toBeInstanceOf(EggsError);
    expect(failure.status).toBe(429);
    expect(failure.retryAfter).toBe(690);
  });

  it("gives the reason of a 422 refusal of the claim, with no wait", async () => {
    const failure = await api.claim("pass", { token: "t1", roster_id: 3, word: null }).catch((error) => error);
    expect(failure.status).toBe(422);
    expect(failure.message).toBe("EAGLES has a winner.");
    expect(failure.retryAfter).toBeUndefined();
  });
});
