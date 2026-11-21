/**
 * Proves the start and the stop of the local API of one run, with a stand-in node server in the place of uvicorn.
 * The real API needs uv, and the CI job of the site has no uv, so the real start is proved by a real smoke run.
 */
import { expect, test } from "@playwright/test";
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { createServer } from "node:http";
import type { AddressInfo } from "node:net";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { startApi } from "./local-api";

/* The temp roots of the running test. The hook below removes them. */
const roots: string[] = [];

test.afterEach(() => {
  for (const root of roots.splice(0)) rmSync(root, { recursive: true });
});

function temp(): string {
  const root = mkdtempSync(join(tmpdir(), "local-api-"));
  roots.push(root);
  return root;
}

/*
 * A stand-in of make -C apps/api api-evidence: a parent process that starts a child, and the child serves /health on
 * the port and prints the ready line of uvicorn. The real target runs make, then uv, then uvicorn, so the server is
 * a grandchild of the start too.
 */
function standIn(root: string) {
  const server = join(root, "server.mjs");
  writeFileSync(
    server,
    `import { createServer } from "node:http";
const port = Number(process.argv[2]);
createServer((request, response) => response.end("ok")).listen(port, "127.0.0.1", () => {
  console.log("INFO:     Uvicorn running on http://127.0.0.1:" + port + " (Press CTRL+C to quit)");
});`,
  );
  const parent = join(root, "parent.mjs");
  writeFileSync(
    parent,
    `import { spawn } from "node:child_process";
spawn(process.execPath, [${JSON.stringify(server)}, process.argv[2]], { stdio: "inherit" });`,
  );
  return (port: number) => [process.execPath, parent, String(port)];
}

/* Whether a process group still has a process. A signal of 0 checks the group and sends nothing. */
function groupAlive(pid: number): boolean {
  try {
    process.kill(-pid, 0);
    return true;
  } catch {
    return false;
  }
}

test("stop ends the whole process group of the API, so no process of it holds its port", async () => {
  const out = temp();
  const api = await startApi({ origin: "http://127.0.0.1:1", out, command: standIn(out) });
  const pid = Number(readFileSync(join(out, "api.pid"), "utf8"));
  expect((await fetch(`${api.url}/health`)).status).toBe(200);
  await api.stop();
  expect(groupAlive(pid)).toBe(false);
  await expect(fetch(`${api.url}/health`)).rejects.toThrow();
});

test("an API that exits fails the start with its log, even when a server of another run answers /health on its port", async () => {
  const out = temp();
  // The server of another run holds the port and answers each path with a 200.
  const other = createServer((request, response) => response.end("ok"));
  await new Promise<void>((done) => other.listen(0, "127.0.0.1", done));
  const { port } = other.address() as AddressInfo;
  try {
    const exits = () => [
      process.execPath,
      "-e",
      'console.log("ERROR: [Errno 48] address already in use"); process.exit(3)',
    ];
    const start = startApi({
      origin: "http://127.0.0.1:1",
      out,
      port,
      command: exits,
      timeoutMs: 10_000,
    });
    await expect(start).rejects.toThrow(
      /the API exited with code 3 before it was ready[\s\S]*address already in use/,
    );
  } finally {
    await new Promise<void>((done) => other.close(() => done()));
  }
});
