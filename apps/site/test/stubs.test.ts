/**
 * Tests for the stub helper of `bun test`: a stub of a global or an env value lasts for one test only.
 * The two tests run in order. The first sets the stubs, and the second reads the real values back.
 */
import { describe, expect, it } from "bun:test";
import { stubEnv, stubGlobal } from "./stubs";

// The preload gives each test a fresh guard as its `fetch`, so the second test checks that the stub of the first test is gone.
const fakeFetch = (() => Promise.resolve(new Response("stub"))) as unknown as typeof fetch;
const realHome = process.env.HOME;
// No shell sets this name, so the stub adds it and the restore must delete it.
const UNSET = "CPC_STUB_HELPER_UNSET";

describe("stubGlobal and stubEnv", () => {
  it("replace the global and the env value inside one test", () => {
    stubGlobal("fetch", fakeFetch);
    stubEnv("HOME", "/stub/home");
    stubEnv(UNSET, "set");

    expect(globalThis.fetch).toBe(fakeFetch);
    expect(process.env.HOME).toBe("/stub/home");
    expect(process.env[UNSET]).toBe("set");
  });

  it("give the next test the real global and the real env value", () => {
    expect(realHome).toBeDefined();
    expect(globalThis.fetch).not.toBe(fakeFetch);
    expect(process.env.HOME).toBe(realHome);
    expect(UNSET in process.env).toBe(false);
  });
});

describe("the fetch of each test", () => {
  it("rejects a call to the live API with no request", async () => {
    await expect(fetch("https://api.4thandgoal.app/clients/cpc/eggs/board")).rejects.toThrow(
      "the tests reach no other host",
    );
  });
});
