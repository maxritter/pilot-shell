import { spawn } from "node:child_process";
import { once } from "node:events";
import { createServer } from "node:net";
import { fileURLToPath } from "node:url";

const cwd = fileURLToPath(new URL("..", import.meta.url));
const children = [];
async function freePort() {
  const server = createServer();
  server.listen(0, "127.0.0.1");
  await once(server, "listening");
  const port = server.address().port;
  await new Promise((resolve) => server.close(resolve));
  return port;
}
function start(command, args, env) {
  const child = spawn(command, args, { cwd, env: { ...process.env, ...env }, stdio: ["ignore", "pipe", "pipe"] });
  child.output = "";
  for (const stream of [child.stdout, child.stderr]) stream.on("data", (data) => { child.output = (child.output + data).slice(-16000); });
  child.on("error", (error) => { child.startError = error; });
  children.push(child);
  return child;
}
async function ready(child, url) {
  const deadline = Date.now() + 15000;
  while (Date.now() < deadline) {
    if (child.startError) throw child.startError;
    if (child.exitCode !== null) throw new Error(child.output);
    try { if ((await fetch(url, { signal: AbortSignal.timeout(1000) })).ok) return; } catch { /* The server is still starting. */ }
    await new Promise((resolve) => setTimeout(resolve, 100));
  }
  throw new Error(`Local billing server did not start: ${child.output}`);
}
try {
  const fixturePort = await freePort();
  let sitePort = await freePort();
  while (sitePort === fixturePort) sitePort = await freePort();
  const origin = `http://127.0.0.1:${sitePort}`;
  const fixture = start("bun", ["scripts/billing-dev.mjs"], { QUALITYLAYER_BILLING_FIXTURE_PORT: String(fixturePort), QUALITYLAYER_BILLING_DEV_ORIGIN: origin });
  const site = start(process.execPath, ["node_modules/vite/bin/vite.js", "--host", "127.0.0.1", "--port", String(sitePort), "--strictPort"], { QUALITYLAYER_BILLING_DEV_PROXY: `http://127.0.0.1:${fixturePort}` });
  await Promise.all([ready(fixture, `http://127.0.0.1:${fixturePort}/__billing-fixture__/mail`), ready(site, origin)]);
  const checks = spawn(process.execPath, ["scripts/check-billing.mjs", origin], { cwd, stdio: "inherit" });
  children.push(checks);
  const [code] = await once(checks, "exit");
  if (code !== 0) throw new Error(`Billing browser checks failed (${code})`);
} finally {
  await Promise.all(children.map(async (child) => {
    if (child.exitCode !== null || child.signalCode !== null) return;
    const exited = once(child, "exit");
    child.kill("SIGTERM");
    const timer = setTimeout(() => child.kill("SIGKILL"), 2000);
    try { await exited; } finally { clearTimeout(timer); }
  }));
}
