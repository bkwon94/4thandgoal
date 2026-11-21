/**
 * Runs one Playwright project whose test starts its own local API, and stops the process group of that API at the end.
 * The test stops its API itself. This wrapper covers a signal, and a test process that dies before its stop.
 */
import { spawn } from "node:child_process";
import { existsSync, readFileSync, rmSync } from "node:fs";
import { join } from "node:path";

/* Kills the process group that apiOut/api.pid names, if the file is still there. The test removes it after a clean stop. */
function stopApi(apiOut) {
  const file = join(apiOut, "api.pid");
  if (!existsSync(file)) return;
  const pid = Number(readFileSync(file, "utf8"));
  try {
    // A pid of 0 means a command that never started. A kill of -0 would signal the group of this wrapper.
    if (pid > 0) process.kill(-pid, "SIGKILL");
  } catch {
    // The group is gone already.
  }
  rmSync(file, { force: true });
}

/* Runs the project with the env, and exits with its status. The test of the project writes api.pid into apiOut. */
export function runProject(project, env, apiOut) {
  const run = spawn("pnpm", ["exec", "playwright", "test", `--project=${project}`], {
    env,
    stdio: "inherit",
  });
  for (const signal of ["SIGINT", "SIGTERM"]) {
    process.on(signal, () => {
      run.kill(signal);
      stopApi(apiOut);
    });
  }
  run.on("exit", (code) => {
    stopApi(apiOut);
    process.exit(code ?? 1);
  });
}
