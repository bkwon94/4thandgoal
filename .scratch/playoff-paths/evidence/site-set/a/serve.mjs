/**
 * Static server of one site export for the evidence of playoff-paths, site agent A.
 * A missing path gets 404.html with the status 404, as the Worker does.
 */
import { createReadStream, existsSync, statSync } from "node:fs";
import { createServer } from "node:http";
import { extname, join, normalize } from "node:path";
const [dir, port] = process.argv.slice(2);
const TYPES = {".html":"text/html; charset=utf-8",".js":"text/javascript",".css":"text/css",".json":"application/json",".svg":"image/svg+xml",".png":"image/png",".jpg":"image/jpeg",".webp":"image/webp",".woff2":"font/woff2",".ico":"image/x-icon",".txt":"text/plain; charset=utf-8"};
function fileFor(path) {
  const file = normalize(join(dir, decodeURIComponent(path)));
  if (!file.startsWith(normalize(dir))) return null;
  if (existsSync(file) && statSync(file).isFile()) return file;
  const index = join(file, "index.html");
  if (existsSync(index)) return index;
  if (existsSync(file + ".html")) return file + ".html";
  return null;
}
createServer((req, res) => {
  const path = new URL(req.url ?? "/", "http://localhost").pathname;
  const file = fileFor(path);
  const missing = join(dir, "404.html");
  const body = file ?? (existsSync(missing) ? missing : null);
  res.statusCode = file ? 200 : 404;
  if (!body) return res.end();
  res.setHeader("content-type", TYPES[extname(body)] ?? "application/octet-stream");
  createReadStream(body).pipe(res);
}).listen(Number(port), "127.0.0.1", () => console.log("serving " + dir + " on " + port));
