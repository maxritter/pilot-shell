import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { PUBLIC_PAGES } from "./src/lib/seo";
import { render } from "./src/prerender";
import { renderedHtml } from "./vite-plugin-prerender";

const template = readFileSync(new URL("./index.html", import.meta.url), "utf8");

describe("HTML available before JavaScript runs", () => {
  it.each(Object.entries(PUBLIC_PAGES))("renders %s with its own content and one set of metadata", async (route, expected) => {
    const { head, body } = await render(route);
    const html = renderedHtml(template, head, body);
    expect(html.match(/<title[ >]/g)).toHaveLength(1);
    expect(html).toContain(`>${expected.title}</title>`);
    expect(head).toContain("data-prerendered-head");
    for (const key of ["description", "og:description", "twitter:description"]) {
      expect(html.match(new RegExp(`(?:name|property)="${key}"`, "g"))).toHaveLength(1);
      expect(html).toContain(`content="${expected.description}"`);
    }
    for (const key of ["og:title", "twitter:title"]) expect(head).toContain(`${key}" content="${expected.title}"`);
    for (const key of ["og:url", "twitter:url"]) expect(head).toContain(`${key}" content="https://qualitylayer.dev${route}"`);
    expect(head).toContain(`rel="canonical" href="https://qualitylayer.dev${route}"`);
    expect(body).toMatch(/<h1[ >]/);
    expect(body).toContain('<main id="main">');
    expect(body).not.toMatch(/<script[\s>]/);
    expect(body).not.toContain('id="S:');
    expect(html).not.toContain("<noscript>");
    expect(html).not.toContain("noindex");
    if (route !== "/") expect(body).not.toContain("hero-h");
    else for (const term of ["Spec-driven development", "AI code review", "human in the loop", "Claude Code", "Codex"]) expect(body).toContain(term);
  });

  it("renders a complete, non-indexable 404 instead of the home page", async () => {
    const { head, body } = await render("/404");
    expect(head).toContain("noindex, follow");
    expect(body).toContain("Page not found");
    expect(body).not.toContain("hero-h");
  });

  it.each(["/billing", "/checkout/success", "/shared", "/open"])("keeps the %s shell out of search results", async (route) => {
    const { head, body } = await render(route);
    expect(head).toContain("noindex, follow");
    expect(body).not.toContain("hero-h");
  });
});
