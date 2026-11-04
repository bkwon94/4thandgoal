/**
 * Smoke test of the config module. It checks the env defaults, the env overrides, and the values of the client build.
 * The fast check builds the cpc client first, so the client values are the values of clients/cpc/client.toml.
 */
import { afterEach, describe, expect, it, vi } from "vitest";

afterEach(() => {
  vi.unstubAllEnvs();
  vi.resetModules();
});

describe("config", () => {
  it("uses the defaults when the env is empty", async () => {
    const { apiUrl, basePath } = await import("./config");
    expect(apiUrl).toBe("https://api.cpcfantasy.com");
    expect(basePath).toBe("");
  });

  it("reads the env when it is set", async () => {
    vi.stubEnv("NEXT_PUBLIC_API_URL", "http://localhost:8080");
    vi.stubEnv("NEXT_PUBLIC_BASE_PATH", "/site");
    const { apiUrl, basePath } = await import("./config");
    expect(apiUrl).toBe("http://localhost:8080");
    expect(basePath).toBe("/site");
  });

  it("takes the season, the finder, and the usage code from the cpc client.toml", async () => {
    const { finderOn, season, usageCode } = await import("./config");
    expect(season).toBe(2026);
    expect(finderOn).toBe(false);
    expect(usageCode).toBe("cpcfantasy");
  });

  it("ignores the old env flags of the season, the finder, the waiver page, and the usage code", async () => {
    vi.stubEnv("NEXT_PUBLIC_SEASON", "2027");
    vi.stubEnv("NEXT_PUBLIC_FINDER", "on");
    vi.stubEnv("NEXT_PUBLIC_USAGE_CODE", "other");
    const config = await import("./config");
    expect(config.season).toBe(2026);
    expect(config.finderOn).toBe(false);
    expect(config.usageCode).toBe("cpcfantasy");
    expect("waiverOn" in config).toBe(false);
  });
});
