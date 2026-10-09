import { existsSync, readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

const html = readFileSync(new URL("./index.html", import.meta.url), "utf8");
const schemas = Array.from(
  html.matchAll(/<script type="application\/ld\+json">\s*([\s\S]*?)<\/script>/g),
  (match) => JSON.parse(match[1]) as Record<string, unknown>,
);

const schema = (type: string) => {
  const value = schemas.find((item) => item["@type"] === type);
  expect(value, `missing ${type} JSON-LD`).toBeDefined();
  return value!;
};

const meta = (attribute: "name" | "property", key: string) =>
  html.match(new RegExp(`<meta ${attribute}="${key}"\\s+content="([^"]*)"`))?.[1];

const staticText = Array.from(html.matchAll(/<noscript>([\s\S]*?)<\/noscript>/g), (match) => match[1])
  .join(" ")
  .replace(/<[^>]+>/g, " ")
  .replaceAll("&amp;", "&")
  .replace(/\s+/g, " ")
  .trim();

describe("static marketing shell", () => {
  it("names the product and points at its own domain", () => {
    expect(html).toContain("<title>QualityLayer");
    expect(html).toContain('<link rel="canonical" href="https://qualitylayer.dev/" />');
    expect(meta("property", "og:url")).toBe("https://qualitylayer.dev/");
    expect(meta("property", "og:site_name")).toBe("QualityLayer");
    expect(meta("property", "og:image")).toBe("https://qualitylayer.dev/og.png");
    expect(meta("name", "twitter:image")).toBe("https://qualitylayer.dev/og.png");
  });

  it("describes the product in structured data", () => {
    const website = schema("WebSite");
    expect(website.url).toBe("https://qualitylayer.dev/");
    const software = schema("SoftwareApplication");
    expect(software.name).toBe("QualityLayer");
    expect(String(software.description)).toContain("your coding agents");
  });

  it("gives crawlers without JavaScript the promise, the seven steps and the install line", () => {
    expect(staticText).toContain("The software factory for your coding agents");
    for (const step of ["Discuss:", "Research:", "Plan:", "Outline:", "Implement:", "Verify:", "Review:"]) expect(staticText).toContain(step);
    expect(staticText).toContain("qualitylayer.dev/download");
    expect(staticText).toContain("curl -fsSL https://qualitylayer.dev/install.sh | bash");
    expect(staticText).toContain("type /ql and the problem");
  });

  it("carries no leftover from the previous products", () => {
    expect(html).not.toMatch(/pilot-shell\.com|Pilot Shell|Superharness|analytics\.ahrefs/i);
  });

  it("loads only what it hosts itself: no inline script, no third-party fonts", () => {
    expect(html).not.toMatch(/<script>/);
    expect(html).not.toContain("fonts.googleapis.com");
    expect(html).toContain("/fonts/geist-latin.woff2");
  });

  it("ships the IndexNow key file its meta tag names", () => {
    const key = meta("name", "indexnow");
    expect(key).toMatch(/^[0-9a-f]{32}$/);
    const file = new URL(`./public/${key}.txt`, import.meta.url);
    expect(existsSync(file)).toBe(true);
    expect(readFileSync(file, "utf8").trim()).toBe(key);
  });
});
