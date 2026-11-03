/**
 * Smoke test of the config module. It checks the defaults and the env overrides.
 * Later tests copy this setup.
 */
import { afterEach, describe, expect, it, vi } from "vitest";

afterEach(() => {
  vi.unstubAllEnvs();
  vi.resetModules();
});

describe("config", () => {
  it("uses the defaults when the env is empty", async () => {
    const { apiUrl, basePath, season } = await import("./config");
    expect(apiUrl).toBe("https://api.cpcfantasy.com");
    expect(basePath).toBe("");
    expect(season).toBe(2026);
  });

  it("reads the env when it is set", async () => {
    vi.stubEnv("NEXT_PUBLIC_API_URL", "http://localhost:8080");
    vi.stubEnv("NEXT_PUBLIC_BASE_PATH", "/site");
    vi.stubEnv("NEXT_PUBLIC_SEASON", "2027");
    const { apiUrl, basePath, season } = await import("./config");
    expect(apiUrl).toBe("http://localhost:8080");
    expect(basePath).toBe("/site");
    expect(season).toBe(2027);
  });

  it("falls back to 2026 when the season is empty or not a number", async () => {
    vi.stubEnv("NEXT_PUBLIC_SEASON", "");
    expect((await import("./config")).season).toBe(2026);
    vi.resetModules();
    vi.stubEnv("NEXT_PUBLIC_SEASON", "abc");
    expect((await import("./config")).season).toBe(2026);
  });

  it("keeps the finder off by default and turns it on with the value on", async () => {
    expect((await import("./config")).finderOn).toBe(false);
    vi.resetModules();
    vi.stubEnv("NEXT_PUBLIC_FINDER", "on");
    expect((await import("./config")).finderOn).toBe(true);
  });

  it("keeps the waiver page off by default and turns it on with the value on", async () => {
    expect((await import("./config")).waiverOn).toBe(false);
    vi.resetModules();
    vi.stubEnv("NEXT_PUBLIC_WAIVER", "on");
    expect((await import("./config")).waiverOn).toBe(true);
  });

  it("defaults the usage code and lets the env override it, even to empty", async () => {
    expect((await import("./config")).usageCode).toBe("cpcfantasy");
    vi.resetModules();
    vi.stubEnv("NEXT_PUBLIC_USAGE_CODE", "other");
    expect((await import("./config")).usageCode).toBe("other");
    vi.resetModules();
    vi.stubEnv("NEXT_PUBLIC_USAGE_CODE", "");
    expect((await import("./config")).usageCode).toBe("");
  });
});
