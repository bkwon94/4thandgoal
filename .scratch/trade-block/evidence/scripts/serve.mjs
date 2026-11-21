/**
 * Serves apps/site/out on 127.0.0.1:<port> for the evidence scripts of trade-block.
 * A missing path gets 404.html with the status 404, as the Worker does, the same as apps/site/e2e/serve.ts.
 */
import { createReadStream, existsSync, statSync } from "node:fs";
import { createServer } from "node:http";
import { extname, join, normalize } from "node:path";

const [dir, port] = [process.argv[2], Number(process.argv[3])];
const TYPES = { ".html": "text/html; charset=utf-8", ".js": "text/javascript", ".css": "text/css", ".json": "application/json", ".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg", ".webp": "image/webp", ".woff2": "font/woff2", ".ico": "image/x-icon", ".txt": "text/plain; charset=utf-8" };
function fileFor(path) {
  const file = normalize(join(dir, decodeURIComponent(path)));
  if (!file.startsWith(normalize(dir))) return null;
  if (existsSync(file) && statSync(file).isFile()) return file;
  const index = join(file, "index.html");
  return existsSync(index) ? index : null;
}
createServer((request, response) => {
  const file = fileFor(new URL(request.url ?? "/", "http://localhost").pathname);
  const missing = join(dir, "404.html");
  const body = file ?? (existsSync(missing) ? missing : null);
  response.statusCode = file ? 200 : 404;
  if (!body) return response.end();
  response.setHeader("content-type", TYPES[extname(body)] ?? "application/octet-stream");
  createReadStream(body).pipe(response);
}).listen(port, "127.0.0.1", () => console.log(`serving ${dir} on http://127.0.0.1:${port}`));
