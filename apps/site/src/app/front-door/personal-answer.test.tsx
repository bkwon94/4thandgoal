/**
 * Tests that the live card of a tapped personal Topic always ends: in a checked Answer or in an error line. The card
 * renders in the strict mode of React, as `next dev` renders it, and the API plays streams that it gave in a live run.
 */
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { StrictMode } from "react";
import { cleanup, render, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { PersonalAnswerLive } from "./personal-answer";

const TARGET = { url: "https://api.test", client: "cpc" };
const BODY = { topic: "weak_spots" as const, roster_id: 3, team: null };
const fetchStub = vi.fn();

// The path comes from this file and not from the working folder, so the run can start in any folder.
const fixture = (name: string) => readFileSync(join(__dirname, "..", "..", "fixtures", "personal-answer", name), "utf8");

function sse(body: string): Response {
  return new Response(body, { headers: { "Content-Type": "text/event-stream", "x-vercel-ai-ui-message-stream": "v1" } });
}

function renderCard() {
  const ends = { onDone: vi.fn(), onMiss: vi.fn(), onCap: vi.fn(), onError: vi.fn() };
  render(
    <StrictMode>
      <PersonalAnswerLive name="Weak spots" href={null} avatars={{}} target={TARGET} passphrase="cornerstone-test" body={BODY} {...ends} />
    </StrictMode>,
  );
  return ends;
}

beforeEach(() => {
  fetchStub.mockReset();
  vi.stubGlobal("fetch", fetchStub);
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe("the live card of a personal Topic", () => {
  // The strict mode mounts the card, unmounts it, and mounts it again. The unmount stops the chat of useChat, and that
  // stop drops a send that has not reached fetch yet. The card must still send its one request and end.
  it("sends one request and ends in the checked Answer in strict mode", async () => {
    fetchStub.mockImplementation(async () => sse(fixture("weak-spots-kept.sse")));
    const ends = renderCard();
    await waitFor(() => expect(ends.onDone).toHaveBeenCalledTimes(1), { timeout: 3000 });
    expect(fetchStub).toHaveBeenCalledTimes(1);
    expect(String(fetchStub.mock.calls[0][0])).toBe("https://api.test/clients/cpc/personal");
    expect(ends.onError).not.toHaveBeenCalled();
  });

  // A stream that closes with no part gives the chat no assistant message. The card must not wait for one forever.
  it("ends in the error line when the stream closes with no Answer", async () => {
    fetchStub.mockImplementation(async () => sse(""));
    const ends = renderCard();
    await waitFor(() => expect(ends.onError).toHaveBeenCalledTimes(1), { timeout: 3000 });
    expect(ends.onDone).not.toHaveBeenCalled();
  });
});
