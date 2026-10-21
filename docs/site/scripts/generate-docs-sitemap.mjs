import { readdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { parse } from "parse5";

const ORIGIN = "https://qualitylayer.dev";
const escapeXml = (text) => text.replaceAll("&", "&amp;").replaceAll('"', "&quot;").replaceAll("<", "&lt;").replaceAll(">", "&gt;");

function metadata(html) {
  const found = { canonical: null, noindex: false };
  function visit(node) {
    const attrs = Object.fromEntries((node.attrs ?? []).map(({ name, value }) => [name, value]));
    if (node.tagName === "link" && attrs.rel === "canonical") found.canonical = attrs.href;
    if (node.tagName === "meta" && /^(robots|googlebot)$/i.test(attrs.name ?? "") && /noindex/i.test(attrs.content ?? "")) found.noindex = true;
    for (const child of node.childNodes ?? []) visit(child);
  }
  visit(parse(html));
  return found;
}

/** Read final HTML, so frontmatter slugs, generated pages and pagination stay in sync. */
export async function generateDocsSitemap(dist) {
  const urls = new Set();
  for (const name of await readdir(dist, { recursive: true })) {
    if (!name.endsWith(".html") || !/^(docs|blog)(\.html|\/)/.test(name)) continue;
    const { canonical, noindex } = metadata(await readFile(path.join(dist, name), "utf8"));
    if (noindex || !canonical) continue;
    const url = new URL(canonical);
    if (url.origin !== ORIGIN || url.hash || url.search) throw new Error(`Invalid canonical in ${name}: ${canonical}`);
    const route = url.pathname.replace(/\/$/, "") || "/";
    const actual = `/${name.replace(/(?:\/index)?\.html$/, "")}`;
    if (route !== actual) throw new Error(`Canonical does not match output: ${name} → ${canonical}`);
    urls.add(`${ORIGIN}${route}`);
  }
  if (!urls.has(`${ORIGIN}/docs`) || !urls.has(`${ORIGIN}/docs/install`)) throw new Error("Documentation output is incomplete");
  const xml = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${[...urls].sort().map((url) => `  <url><loc>${escapeXml(url)}</loc></url>`).join("\n")}\n</urlset>\n`;
  await writeFile(path.join(dist, "docs/sitemap.xml"), xml);
  return [...urls].sort();
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const urls = await generateDocsSitemap(path.resolve(process.argv[2] ?? "dist"));
  console.log(`Documentation and blog sitemap: ${urls.length} canonical pages`);
}
