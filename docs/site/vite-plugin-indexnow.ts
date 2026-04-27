/**
 * Vite plugin: notifies IndexNow (https://www.indexnow.org) of all URLs in the
 * generated sitemap-pages.xml after a production build.
 *
 * IndexNow is supported by Bing, Yandex, Naver, Seznam, and Yep — submitting
 * once distributes the URL set to every participating engine.
 *
 * The key file lives at /public/<KEY>.txt so that it deploys to /<KEY>.txt
 * (Option 1 from the spec). Search engines verify ownership by fetching it.
 *
 * Skipped when:
 *   - INDEXNOW_DISABLE=1 (manual override, e.g. local builds)
 *   - mode !== production
 *   - dist/sitemap-pages.xml does not exist (sitemap plugin disabled)
 */

import { type Plugin } from "vite";
import fs from "fs";
import path from "path";

const SITE_HOST = "pilot-shell.com";
const SITE_URL = `https://${SITE_HOST}`;
const INDEXNOW_KEY = "0bd196f90bbc9ec8113bd78de2507fb2";
const INDEXNOW_ENDPOINT = "https://api.indexnow.org/IndexNow";

interface IndexNowOptions {
  /** Override key for testing. */
  key?: string;
  /** Override endpoint for testing. */
  endpoint?: string;
}

export default function indexNowPlugin(options: IndexNowOptions = {}): Plugin {
  let outDir: string;
  let isProd = false;

  const key = options.key ?? INDEXNOW_KEY;
  const endpoint = options.endpoint ?? INDEXNOW_ENDPOINT;

  return {
    name: "indexnow-submit",
    apply: "build",

    configResolved(config) {
      outDir = config.build.outDir;
      isProd = config.mode === "production";
    },

    async closeBundle() {
      if (process.env.INDEXNOW_DISABLE === "1") {
        console.log("\x1b[33m⚠\x1b[0m IndexNow submission skipped (INDEXNOW_DISABLE=1)");
        return;
      }
      if (!isProd) {
        console.log("\x1b[33m⚠\x1b[0m IndexNow submission skipped (non-production build)");
        return;
      }

      const sitemapPath = path.resolve(outDir, "sitemap-pages.xml");
      if (!fs.existsSync(sitemapPath)) {
        console.log("\x1b[33m⚠\x1b[0m IndexNow: sitemap-pages.xml not found, skipping");
        return;
      }

      // Verify the key file made it into the build output. Without it the
      // search engines reject submissions with 403.
      const keyFile = path.resolve(outDir, `${key}.txt`);
      if (!fs.existsSync(keyFile)) {
        console.log(
          `\x1b[31m✗\x1b[0m IndexNow: key file ${key}.txt missing from output, aborting submit`
        );
        return;
      }

      const xml = fs.readFileSync(sitemapPath, "utf8");
      const urlList = Array.from(xml.matchAll(/<loc>([^<]+)<\/loc>/g))
        .map((m) => m[1])
        // Anchor URLs (#installation, #faq, ...) duplicate / for IndexNow,
        // so dedupe by stripping the fragment.
        .map((u) => u.split("#")[0])
        .filter((u, i, arr) => arr.indexOf(u) === i);

      if (urlList.length === 0) {
        console.log("\x1b[33m⚠\x1b[0m IndexNow: no URLs in sitemap, skipping");
        return;
      }

      const payload = {
        host: SITE_HOST,
        key,
        keyLocation: `${SITE_URL}/${key}.txt`,
        urlList,
      };

      try {
        const res = await fetch(endpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json; charset=utf-8" },
          body: JSON.stringify(payload),
        });

        if (res.status === 200 || res.status === 202) {
          console.log(
            `\x1b[32m✓\x1b[0m IndexNow: submitted ${urlList.length} URL(s) (HTTP ${res.status})`
          );
        } else {
          // 4xx is a real failure (bad key, host mismatch, rate limit). Don't
          // fail the build — search engines see the next deploy regardless.
          const body = await res.text().catch(() => "");
          console.log(
            `\x1b[33m⚠\x1b[0m IndexNow: HTTP ${res.status} — ${body.slice(0, 200)}`
          );
        }
      } catch (err) {
        console.log(
          `\x1b[33m⚠\x1b[0m IndexNow: network error — ${(err as Error).message}`
        );
      }
    },
  };
}
