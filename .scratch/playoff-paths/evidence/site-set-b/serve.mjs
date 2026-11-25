/**
 * A static server of one site export for the site evidence of playoff-paths, round b. A folder gives its index.html,
 * and a missing path gives 404.html with the status 404, as the Worker does. Run: node serve.mjs <dir> <port>.
 */
import { createServer } from "node:http";
import { readFile, stat } from "node:fs/promises";
import { join, extname, normalize } from "node:path";

const [dir, port] = process.argv.slice(2);
const TYPES = { ".html": "text/html; charset=utf-8", ".js": "text/javascript", ".css": "text/css", ".json": "application/json",
  ".txt": "text/plain; charset=utf-8", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".svg": "image/svg+xml",
  ".webp": "image/webp", ".woff2": "font/woff2", ".ico": "image/x-icon", ".webmanifest": "application/manifest+json" };

async function find(path) {
  const full = join(dir, normalize(decodeURIComponent(path)));
  for (const candidate of [full, join(full, "index.html"), full + ".html"]) {
    try {
      if ((await stat(candidate)).isFile()) return candidate;
    } catch {}
  }
  return null;
}

createServer(async (req, res) => {
  const path = new URL(req.url, "http://x").pathname;
  const hit = await find(path);
  const file = hit ?? join(dir, "404.html");
  res.writeHead(hit ? 200 : 404, { "content-type": TYPES[extname(file)] ?? "application/octet-stream" });
  res.end(await readFile(file));
}).listen(Number(port), "127.0.0.1", () => console.log(`serve ${dir} on http://127.0.0.1:${port}`));
