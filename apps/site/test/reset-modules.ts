/**
 * The module reset of `bun test`. `bun:test` has no `vi.resetModules`, so this gives it.
 * A test that sets the env or the working folder calls it, then imports the module again, so the module reads the new value.
 */

// A package under node_modules has no state that a test sets, and a reload of React would split its hooks state.
// The helpers of this folder keep their module, so the preload and the test share one set of stubs.
const KEPT = ["/node_modules/", "/apps/site/test/"];

/** Forget each loaded module of the repo, so the next `import` runs it again. */
export function resetModules(): void {
  for (const path of Object.keys(require.cache)) {
    if (!KEPT.some((part) => path.includes(part))) delete require.cache[path];
  }
}
