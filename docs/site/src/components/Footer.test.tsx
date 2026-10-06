import { renderToReadableStream } from "react-dom/server.browser";
import { MemoryRouter } from "react-router-dom";
import { expect, it } from "vitest";
import Footer from "./Footer";

it("scopes fictional tasks and numbers to the tour, including when a real shared plan uses the footer", async () => {
  for (const route of ["/", "/s/AAAAAAAAAAAAAAAAAAAAAA"]) {
    const stream = await renderToReadableStream(<MemoryRouter initialEntries={[route]}><Footer /></MemoryRouter>);
    await stream.allReady;
    const html = await new Response(stream).text();
    expect(html).toContain("in the tour are fictional");
    expect(html).not.toContain("on this site are an illustration");
    expect(html).toContain("Prices in US dollars, billed monthly through Polar");
  }
});
