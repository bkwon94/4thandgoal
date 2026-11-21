/**
 * The types of scripts/playwright-shard.mjs, so the TypeScript config of Playwright can import it.
 * The shard is { current, total }, or null when PLAYWRIGHT_SHARD is not set.
 */
export function shardOfEnv(value: string | undefined): { current: number; total: number } | null;
