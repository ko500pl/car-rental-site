// Local stand-in for the deployed Worker: node worker/test/serve-mock.mjs [port] [siteUrl]
// MOCK model, catalog fetched from siteUrl (default the local dist server).
import http from "node:http";
import worker from "../src/index.js";

const port = Number(process.argv[2] || 8787);
const env = { MOCK: "1", SITE_URL: process.argv[3] || "http://localhost:8874", ALLOWED_ORIGINS: "https://rentup.ge" };

http.createServer(async (req, res) => {
  const chunks = []; for await (const c of req) chunks.push(c);
  const body = Buffer.concat(chunks);
  const r = await worker.fetch(new Request(`http://localhost:${port}${req.url}`, {
    method: req.method, headers: req.headers, body: req.method === "POST" ? body : undefined,
  }), env);
  res.writeHead(r.status, Object.fromEntries(r.headers));
  res.end(Buffer.from(await r.arrayBuffer()));
}).listen(port, () => console.log(`mock worker on :${port}, catalog from ${env.SITE_URL}`));
