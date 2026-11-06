/**
 * A small static file server for the readability floor. It serves one folder, such as the static export in out/.
 * next start cannot serve an output: "export" build, and node:http needs no extra package.
 */
import { createReadStream, existsSync, statSync } from "node:fs";
import { createServer } from "node:http";
import type { AddressInfo } from "node:net";
import { extname, join, normalize } from "node:path";

const TYPES: Record<string, string> = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript",
  ".css": "text/css",
  ".json": "application/json",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".webp": "image/webp",
  ".woff2": "font/woff2",
  ".ico": "image/x-icon",
  ".txt": "text/plain; charset=utf-8",
};

/* The file for a path: the file itself, or the index.html of a folder. A path outside the folder gets no file. */
function fileFor(dir: string, path: string): string | null {
  const file = normalize(join(dir, decodeURIComponent(path)));
  if (!file.startsWith(normalize(dir))) return null;
  if (existsSync(file) && statSync(file).isFile()) return file;
  const index = join(file, "index.html");
  return existsSync(index) ? index : null;
}

/* Serves dir on a free port of 127.0.0.1. A missing path gets 404.html with the status 404, as the Worker does. */
export async function serveDir(dir: string): Promise<{ url: string; close: () => Promise<void> }> {
  const server = createServer((request, response) => {
    const path = new URL(request.url ?? "/", "http://localhost").pathname;
    const file = fileFor(dir, path);
    const missing = join(dir, "404.html");
    const body = file ?? (existsSync(missing) ? missing : null);
    response.statusCode = file ? 200 : 404;
    if (!body) return response.end();
    response.setHeader("content-type", TYPES[extname(body)] ?? "application/octet-stream");
    createReadStream(body).pipe(response);
  });
  await new Promise<void>((done) => server.listen(0, "127.0.0.1", done));
  const { port } = server.address() as AddressInfo;
  return {
    url: `http://127.0.0.1:${port}`,
    close: () => new Promise<void>((done) => server.close(() => done())),
  };
}
