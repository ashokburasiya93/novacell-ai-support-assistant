// Local dev server: serves public/ and the same api/ handlers Vercel runs. No dependencies.
// Usage: node server.js   (reads ../.env style KEY=VALUE files from .env in this folder or its parents)
import http from "node:http";
import { readFileSync, existsSync } from "node:fs";
import { join, extname, dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
for (let d = here, i = 0; i < 4; i++, d = resolve(d, "..")) {
  const f = join(d, ".env");
  if (existsSync(f)) {
    for (const line of readFileSync(f, "utf8").split(/\r?\n/)) {
      const m = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$/);
      if (m && !process.env[m[1]]) process.env[m[1]] = m[2].replace(/^["']|["']$/g, "");
    }
    break;
  }
}

const { default: chat } = await import("./api/chat.js");
const { default: health } = await import("./api/health.js");
const TYPES = { ".html": "text/html", ".js": "text/javascript", ".css": "text/css", ".svg": "image/svg+xml", ".json": "application/json" };

function wrap(res) {
  res.status = (c) => ((res.statusCode = c), res);
  res.json = (o) => (res.setHeader("Content-Type", "application/json"), res.end(JSON.stringify(o)));
  return res;
}

http
  .createServer(async (req, res) => {
    wrap(res);
    if (req.url.startsWith("/api/")) {
      let raw = "";
      for await (const c of req) raw += c;
      req.body = raw ? JSON.parse(raw) : {};
      return req.url.startsWith("/api/chat") ? chat(req, res) : health(req, res);
    }
    const p = join(here, "public", req.url === "/" ? "index.html" : req.url.split("?")[0]);
    if (!p.startsWith(join(here, "public")) || !existsSync(p)) return res.status(404).end("Not found");
    res.setHeader("Content-Type", TYPES[extname(p)] || "application/octet-stream");
    res.end(readFileSync(p));
  })
  .listen(process.env.PORT || 3000, () => console.log(`NovaCell assistant on http://localhost:${process.env.PORT || 3000}`));
