/* Serves one export folder on 127.0.0.1:<port>. A missing path gets 404.html with the status 404, as the Worker does. */
import { createReadStream, existsSync, statSync } from "node:fs";
import { createServer } from "node:http";
import { extname, join, normalize } from "node:path";
const [dir, port] = process.argv.slice(2);
const TYPES = { ".html": "text/html; charset=utf-8", ".js": "text/javascript", ".css": "text/css", ".json": "application/json", ".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg", ".webp": "image/webp", ".woff2": "font/woff2", ".ico": "image/x-icon", ".txt": "text/plain; charset=utf-8" };
createServer((req, res) => {
  const path = decodeURIComponent(new URL(req.url ?? "/", "http://x").pathname);
  let file = normalize(join(dir, path));
  if (existsSync(file) && statSync(file).isDirectory()) file = join(file, "index.html");
  const ok = file.startsWith(normalize(dir)) && existsSync(file) && statSync(file).isFile();
  const body = ok ? file : join(dir, "404.html");
  res.statusCode = ok ? 200 : 404;
  res.setHeader("content-type", TYPES[extname(body)] ?? "application/octet-stream");
  createReadStream(body).pipe(res);
}).listen(Number(port), "127.0.0.1");
