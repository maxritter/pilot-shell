import { renderToReadableStream } from "react-dom/server.browser";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";

import Index from "./Index";

vi.mock("@/components/SEO", () => ({ default: () => null }));
vi.mock("@/components/NavBar", () => ({
  default: () => <nav aria-label="Primary" />,
}));
vi.mock("@/components/home/Hero", () => ({
  default: () => <section>Hero</section>,
}));
vi.mock("@/components/home/Sections", () => ({
  default: () => <section>Sections</section>,
}));
vi.mock("@/components/Footer", () => ({
  default: () => <footer>Footer</footer>,
}));

async function renderIndexPage(): Promise<string> {
  const stream = await renderToReadableStream(
    <MemoryRouter>
      <Index />
    </MemoryRouter>,
  );

  await stream.allReady;
  return new Response(stream).text();
}

describe("homepage landmarks", () => {
  it("renders the global footer outside the main landmark", async () => {
    const markup = await renderIndexPage();
    const mainStart = markup.indexOf("<main");
    const mainEnd = markup.indexOf("</main>");
    const footerStart = markup.indexOf("<footer");

    expect(mainStart).toBeGreaterThanOrEqual(0);
    expect(mainEnd).toBeGreaterThan(mainStart);
    expect(footerStart).toBeGreaterThan(mainEnd);
    expect(markup.slice(mainStart, mainEnd)).not.toContain("<footer");
  });

  it("offers a way past the navigation to the content", async () => {
    const markup = await renderIndexPage();
    expect(markup).toContain('href="#main"');
    expect(markup).toContain('id="main"');
  });
});
