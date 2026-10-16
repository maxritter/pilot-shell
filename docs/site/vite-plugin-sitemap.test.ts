import { mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import type { ResolvedConfig } from "vite";
import { describe, expect, it } from "vitest";
import sitemapPlugin from "./vite-plugin-sitemap";
import { PUBLIC_PAGES } from "./src/lib/seo";

const locations = (xml: string) => [...xml.matchAll(/<loc>([^<]+)<\/loc>/g)].map((match) => match[1]);

describe("crawler discovery", () => {
  it("generates the sitemap index and canonical marketing URLs at build time", () => {
    const outDir = mkdtempSync(join(tmpdir(), "qualitylayer-sitemap-"));
    try {
      const plugin = sitemapPlugin();
      expect(plugin.apply).toBe("build");
      (plugin.configResolved as (config: ResolvedConfig) => void)({ build: { outDir } } as ResolvedConfig);
      (plugin.closeBundle as () => void)();
      const index = readFileSync(join(outDir, "sitemap.xml"), "utf8");
      expect(index).toContain('<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">');
      expect(locations(index)).toEqual([
        "https://qualitylayer.dev/sitemap-pages.xml", "https://qualitylayer.dev/docs/sitemap.xml",
      ]);
      const pages = readFileSync(join(outDir, "sitemap-pages.xml"), "utf8");
      expect(pages).toContain('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">');
      expect(locations(pages)).toEqual(Object.keys(PUBLIC_PAGES).map((route) => `https://qualitylayer.dev${route}`));
    } finally {
      rmSync(outDir, { recursive: true, force: true });
    }
  });

  it("references the sitemap in the HTML and allows crawlers in public robots.txt", () => {
    const html = readFileSync(new URL("./index.html", import.meta.url), "utf8");
    expect(html).toMatch(/<link rel="sitemap"[^>]+href="\/sitemap.xml"/);
    const robots = readFileSync(new URL("./public/robots.txt", import.meta.url), "utf8");
    expect(robots).toMatch(/User-agent: \*\s+Allow: \/(?:\s|$)/);
    expect(robots).not.toMatch(/^Disallow:\s*\S/m);
    expect(robots).toContain("Sitemap: https://qualitylayer.dev/sitemap.xml");
    expect(robots).toContain("Sitemap: https://qualitylayer.dev/docs/sitemap.xml");
  });
});
