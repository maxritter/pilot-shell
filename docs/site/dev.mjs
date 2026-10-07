#!/usr/bin/env node
/**
 * Unified dev server: starts both Vite (landing page) and Docusaurus (docs + blog).
 * Vite redirects /docs and /blog to the Docusaurus dev server automatically.
 * Ctrl+C stops both.
 */

import { spawn } from "child_process";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const docusaurusDir = resolve(__dirname, "../docusaurus");

const procs = [];

function start(name, cmd, args, cwd) {
  const proc = spawn(cmd, args, {
    cwd,
    stdio: ["ignore", "pipe", "pipe"],
    env: { ...process.env, FORCE_COLOR: "1" },
  });

  proc.stdout.on("data", (d) => {
    for (const line of d.toString().split("\n").filter(Boolean)) {
      process.stdout.write(`\x1b[36m[${name}]\x1b[0m ${line}\n`);
    }
  });

  proc.stderr.on("data", (d) => {
    for (const line of d.toString().split("\n").filter(Boolean)) {
      process.stderr.write(`\x1b[36m[${name}]\x1b[0m ${line}\n`);
    }
  });

  proc.on("exit", (code) => {
    if (code !== null && code !== 0) {
      console.error(`\x1b[31m[${name}] exited with code ${code}\x1b[0m`);
    }
  });

  procs.push(proc);
  return proc;
}

function shutdown() {
  console.log("\n\x1b[33mShutting down dev servers...\x1b[0m");
  for (const proc of procs) {
    if (!proc.killed) {
      proc.kill("SIGTERM");
    }
  }
  // Force kill after 3s if still alive
  setTimeout(() => {
    for (const proc of procs) {
      if (!proc.killed) {
        proc.kill("SIGKILL");
      }
    }
    process.exit(0);
  }, 3000);
}

process.on("SIGINT", shutdown);
process.on("SIGTERM", shutdown);

console.log("\x1b[32m=== Starting unified dev server ===\x1b[0m");
console.log("  Landing page: http://localhost:8080");
console.log("  Docs + Blog:  http://localhost:3000 (proxied from :8080/docs and :8080/blog)");
console.log("");

start("docusaurus", "npx", ["docusaurus", "start", "--port", "3000", "--no-open"], docusaurusDir);
start("vite", "npx", ["vite", "--port", "8080", "--host"], __dirname);
