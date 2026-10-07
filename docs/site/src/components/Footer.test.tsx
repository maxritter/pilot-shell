import { renderToReadableStream } from "react-dom/server.browser";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";
import Footer from "./Footer";

async function html(path: string): Promise<string> {
  const stream = await renderToReadableStream(<MemoryRouter initialEntries={[path]}><Footer /></MemoryRouter>);
  await stream.allReady;
  return new Response(stream).text();
}

describe("the footer", () => {
  it("carries the links and the copyright, no fine print", async () => {
    for (const path of ["/", "/pricing", `/s/${"A".repeat(22)}`]) {
      const rendered = await html(path);
      expect(rendered).toContain("© 2026 QualityLayer");
      expect(rendered).not.toMatch(/fictional|illustration|billed monthly/);
    }
  });
});
