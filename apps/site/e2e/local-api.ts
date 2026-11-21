/**
 * The local API of one smoke run or one evidence round: it starts make -C apps/api api-evidence on a free port, for one
 * site origin, and stops its whole process group. Two runs in two worktrees then never share a port or an API.
 */
import { spawn } from "node:child_process";
import { closeSync, mkdirSync, openSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { createServer, type Server } from "node:net";
import { join } from "node:path";

export type LocalApi = { url: string; stop: () => Promise<void> };

export type ApiOptions = {
  // The origin of the site server of the run. The API answers only the origins it allows, so it allows this one.
  origin: string;
  // The folder of the run. The API writes api.log here, and the start writes api.pid, the id of its process group. The
  // wrapper of the run reads api.pid, and stops the group after a signal or a test process that died before its stop.
  out: string;
  // The port of the API. The default is a free port.
  port?: number;
  // The command that runs the API on a port for an origin. The default is make -C apps/api api-evidence.
  command?: (port: number, origin: string) => string[];
  // The time in ms that the start waits for the API. The first start of a checkout installs the env of the API first.
  timeoutMs?: number;
};

// pnpm runs each script of the site in apps/site, so the API app sits one folder up.
const API_APP = join(process.cwd(), "..", "api");

const makeTarget = (port: number, origin: string) => [
  "make",
  "-C",
  API_APP,
  "api-evidence",
  `API_PORT=${port}`,
  `API_ORIGIN=${origin}`,
];

/* The time in ms that stop waits after SIGTERM before it sends SIGKILL to the group. */
const STOP_MS = 5000;

/* A free port of 127.0.0.1: the system gives one to a listen on port 0, and the close gives it back. */
export async function freePort(): Promise<number> {
  const server = createServer();
  await new Promise<void>((done) => server.listen(0, "127.0.0.1", done));
  const { port } = server.address() as { port: number };
  await new Promise<void>((done) => server.close(() => done()));
  return port;
}

/*
 * A port with no API, for a run with no API. A server holds the port and ends each connection at once, so a call
 * fails as a call to a stopped API fails, and no other run can take the port while this run uses it.
 */
export async function holdPort(): Promise<LocalApi> {
  const server: Server = createServer((socket) => socket.destroy());
  await new Promise<void>((done) => server.listen(0, "127.0.0.1", done));
  const { port } = server.address() as { port: number };
  return {
    url: `http://127.0.0.1:${port}`,
    stop: () => new Promise<void>((done) => server.close(() => done())),
  };
}

const pause = (ms: number) => new Promise((done) => setTimeout(done, ms));

/* Whether a process group still has a process. A signal of 0 checks the group and sends nothing. */
function groupAlive(pid: number): boolean {
  if (pid <= 0) return false;
  try {
    process.kill(-pid, 0);
    return true;
  } catch {
    return false;
  }
}

function signalGroup(pid: number, signal: NodeJS.Signals): void {
  // A pid of 0 means a command that never started. A kill of -0 would signal the group of this test process.
  if (pid <= 0) return;
  try {
    process.kill(-pid, signal);
  } catch {
    // The group is gone already.
  }
}

/* The last lines of the log of the API, for the error of a failed start. */
function tail(log: string): string {
  return readFileSync(log, "utf8").split("\n").slice(-30).join("\n");
}

/*
 * Starts the API in its own process group, with its output in api.log. The start waits for the ready line of uvicorn
 * for this port and a 200 from /health. The line proves that this API holds the port, and not a server of another run.
 */
export async function startApi(options: ApiOptions): Promise<LocalApi> {
  const port = options.port ?? (await freePort());
  const url = `http://127.0.0.1:${port}`;
  mkdirSync(options.out, { recursive: true });
  const log = join(options.out, "api.log");
  const pidFile = join(options.out, "api.pid");
  const fd = openSync(log, "w");
  const [command, ...args] = (options.command ?? makeTarget)(port, options.origin);
  // detached gives the API its own process group, so one signal stops make, uv, and uvicorn together.
  const child = spawn(command, args, {
    detached: true,
    stdio: ["ignore", fd, fd],
    env: process.env,
  });
  closeSync(fd);
  const pid = child.pid ?? 0;
  writeFileSync(pidFile, String(pid));
  // The exit code of the child, once it exits. An API that exits before it is ready failed its start, even when a
  // server of another run answers on the port.
  let exited: number | string | null = null;
  child.on("exit", (code, signal) => {
    exited = code ?? signal ?? "unknown";
  });
  // A command that cannot start, such as a missing make, gives an error and no exit.
  child.on("error", (error) => {
    exited = error.message;
  });
  // The backstop of a run that ends with no stop: the exit of the test process kills the group.
  const backstop = () => signalGroup(pid, "SIGKILL");
  process.on("exit", backstop);

  const stop = async () => {
    process.off("exit", backstop);
    signalGroup(pid, "SIGTERM");
    for (const start = Date.now(); groupAlive(pid) && Date.now() - start < STOP_MS;)
      await pause(100);
    signalGroup(pid, "SIGKILL");
    for (const start = Date.now(); groupAlive(pid) && Date.now() - start < STOP_MS;)
      await pause(100);
    rmSync(pidFile, { force: true });
  };

  const ready = `Uvicorn running on ${url}`;
  const timeout = options.timeoutMs ?? 180_000;
  for (const start = Date.now(); Date.now() - start < timeout; await pause(250)) {
    if (exited !== null) {
      await stop();
      throw new Error(
        `the API exited with code ${exited} before it was ready on ${url}. The last lines of ${log}:\n${tail(log)}`,
      );
    }
    if (!readFileSync(log, "utf8").includes(ready)) continue;
    const status = await fetch(`${url}/health`).then(
      (response) => response.status,
      () => 0,
    );
    if (status === 200) return { url, stop };
  }
  await stop();
  throw new Error(
    `the API is not ready on ${url} after ${timeout} ms. The last lines of ${log}:\n${tail(log)}`,
  );
}
