import fs from "node:fs";
import os from "node:os";
import path from "node:path";

import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { type ResolvedConfig } from "vite";

import indexNowPlugin from "./vite-plugin-indexnow";

const TEST_KEY = "test-indexnow-key";

function prepareOutput(): string {
  const outDir = fs.mkdtempSync(path.join(os.tmpdir(), "pilot-indexnow-"));
  fs.writeFileSync(
    path.join(outDir, "sitemap-pages.xml"),
    "<urlset><url><loc>https://pilot-shell.com/</loc></url></urlset>",
  );
  fs.writeFileSync(path.join(outDir, `${TEST_KEY}.txt`), TEST_KEY);
  return outDir;
}

async function runPlugin(outDir: string): Promise<void> {
  const plugin = indexNowPlugin({ key: TEST_KEY, endpoint: "https://indexnow.test/submit" });
  (plugin.configResolved as (config: ResolvedConfig) => void)({
    build: { outDir },
    mode: "production",
  } as ResolvedConfig);
  await (plugin.closeBundle as () => Promise<void>)();
}

describe("IndexNow build gating", () => {
  beforeEach(() => {
    vi.stubEnv("INDEXNOW_DISABLE", "");
    vi.stubEnv("INDEXNOW_SUBMIT", "");
    vi.stubEnv("VERCEL_ENV", "");
    vi.stubEnv("NETLIFY", "");
    vi.stubEnv("CONTEXT", "");
    vi.spyOn(console, "log").mockImplementation(() => undefined);
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllEnvs();
    vi.unstubAllGlobals();
  });

  it("does not submit during a local production build", async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);

    await runPlugin(prepareOutput());

    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("submits when explicitly enabled", async () => {
    vi.stubEnv("INDEXNOW_SUBMIT", "1");
    const fetchMock = vi.fn().mockResolvedValue(new Response("", { status: 202 }));
    vi.stubGlobal("fetch", fetchMock);

    await runPlugin(prepareOutput());

    expect(fetchMock).toHaveBeenCalledOnce();
  });

  it("submits in production deploy contexts", async () => {
    vi.stubEnv("VERCEL_ENV", "production");
    const fetchMock = vi.fn().mockResolvedValue(new Response("", { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);

    await runPlugin(prepareOutput());

    expect(fetchMock).toHaveBeenCalledOnce();
  });

  it("recognizes a Netlify production deploy", async () => {
    vi.stubEnv("NETLIFY", "true");
    vi.stubEnv("CONTEXT", "production");
    const fetchMock = vi.fn().mockResolvedValue(new Response("", { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);

    await runPlugin(prepareOutput());

    expect(fetchMock).toHaveBeenCalledOnce();
  });

  it("keeps the disable override authoritative", async () => {
    vi.stubEnv("INDEXNOW_DISABLE", "1");
    vi.stubEnv("INDEXNOW_SUBMIT", "1");
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);

    await runPlugin(prepareOutput());

    expect(fetchMock).not.toHaveBeenCalled();
  });
});
