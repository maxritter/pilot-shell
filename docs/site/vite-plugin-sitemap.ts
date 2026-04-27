/**
 * Vite plugin that generates two sitemap files at build time:
 *
 *   - /sitemap-pages.xml — landing-page URLs and on-page anchors
 *   - /sitemap.xml       — sitemap index referencing /sitemap-pages.xml
 *                          and the Docusaurus-generated /docs/sitemap.xml
 *
 * Docusaurus emits its own sitemap into the docs build directory; build-all.sh
 * copies it to /docs/sitemap.xml in the final output. The sitemap index points
 * search engines and IndexNow consumers at both files.
 */

import { type Plugin } from "vite";
import fs from "fs";
import path from "path";

const SITE_URL = "https://pilot-shell.com";

interface PageEntry {
  loc: string;
  changefreq: "daily" | "weekly" | "monthly";
  priority: string;
}

const PAGES: PageEntry[] = [
  { loc: "/", changefreq: "weekly", priority: "1.0" },
  { loc: "/#installation", changefreq: "weekly", priority: "0.9" },
  { loc: "/#features", changefreq: "weekly", priority: "0.8" },
  { loc: "/#workflow", changefreq: "weekly", priority: "0.8" },
  { loc: "/#console", changefreq: "weekly", priority: "0.7" },
  { loc: "/#pricing", changefreq: "weekly", priority: "0.8" },
  { loc: "/#faq", changefreq: "weekly", priority: "0.7" },
  { loc: "/shared", changefreq: "monthly", priority: "0.5" },
];

export default function sitemapPlugin(): Plugin {
  let outDir: string;

  return {
    name: "generate-sitemap",
    apply: "build",

    configResolved(config) {
      outDir = config.build.outDir;
    },

    closeBundle() {
      const today = new Date().toISOString().split("T")[0];

      const pagesXml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${PAGES.map(
  (p) => `  <url>
    <loc>${SITE_URL}${p.loc}</loc>
    <lastmod>${today}</lastmod>
    <changefreq>${p.changefreq}</changefreq>
    <priority>${p.priority}</priority>
  </url>`
).join("\n")}
</urlset>
`;

      const indexXml = `<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap>
    <loc>${SITE_URL}/sitemap-pages.xml</loc>
    <lastmod>${today}</lastmod>
  </sitemap>
  <sitemap>
    <loc>${SITE_URL}/docs/sitemap.xml</loc>
    <lastmod>${today}</lastmod>
  </sitemap>
</sitemapindex>
`;

      fs.writeFileSync(path.resolve(outDir, "sitemap-pages.xml"), pagesXml);
      fs.writeFileSync(path.resolve(outDir, "sitemap.xml"), indexXml);

      console.log(
        `\x1b[32m✓\x1b[0m sitemap.xml (index) and sitemap-pages.xml (${PAGES.length} URLs) generated`
      );
    },
  };
}
