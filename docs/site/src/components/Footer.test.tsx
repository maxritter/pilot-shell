import { renderToReadableStream } from "react-dom/server.browser";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";
import Footer from "./Footer";

async function html(path: string): Promise<string> {
  const stream = await renderToReadableStream(<MemoryRouter initialEntries={[path]}><Footer /></MemoryRouter>);
  await stream.allReady;
  return new Response(stream).text();
}

describe("the footer's example disclaimer", () => {
  it("scopes the fictional examples to the tour", async () => {
    const rendered = await html("/");
    expect(rendered).toContain("in the tour are fictional");
    expect(rendered).not.toContain("on this site are an illustration");
  });

  it("does not call a customer's shared task fictional", async () => {
    const rendered = await html(`/s/${"A".repeat(22)}`);
    expect(rendered).not.toContain("are fictional");
    expect(rendered).toContain("Prices in US dollars, billed monthly through Polar.");
  });
});
