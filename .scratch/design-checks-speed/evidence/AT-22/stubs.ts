/**
 * The stub helper of `bun test`. `bun:test` has no `vi.stubGlobal` or `vi.stubEnv`, so these two give them.
 * The preload calls `restoreStubs` after each test, so a stub never leaks into the next test or file. Package tests use
 * `spyOn` of `bun:test` instead, because a package imports nothing from an app and reads no env (ADR 0012).
 */

// The first value of each name, kept from the first stub of that name in a test. A later stub of the same name keeps
// it, so the restore always goes back to the real value.
const globals = new Map<string, { had: boolean; value: unknown }>();
const envs = new Map<string, string | undefined>();

/** Set `globalThis[name]` to `value` until the end of the test. */
export function stubGlobal(name: string, value: unknown): void {
  const scope = globalThis as Record<string, unknown>;
  if (!globals.has(name)) globals.set(name, { had: name in scope, value: scope[name] });
  scope[name] = value;
}

/** Set `process.env[name]` to `value` until the end of the test. `undefined` removes the name. */
export function stubEnv(name: string, value: string | undefined): void {
  if (!envs.has(name)) envs.set(name, process.env[name]);
  if (value === undefined) delete process.env[name];
  else process.env[name] = value;
}

/** Put back each global and each env value that a stub changed. The preload calls it after each test. */
export function restoreStubs(): void {
  const scope = globalThis as Record<string, unknown>;
  for (const [name, real] of globals) {
    if (real.had) scope[name] = real.value;
    else delete scope[name];
  }
  globals.clear();
  for (const [name, real] of envs) {
    if (real === undefined) delete process.env[name];
    else process.env[name] = real;
  }
  envs.clear();
}
