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
  it("labels the marketing site's fictional tasks and people", async () => {
    expect(await html("/")).toContain("The tasks, people and numbers on this site are an illustration.");
  });

  it("does not call a customer's shared task an illustration", async () => {
    const rendered = await html(`/s/${"A".repeat(22)}`);
    expect(rendered).not.toContain("are an illustration");
    expect(rendered).toContain("Prices in US dollars, billed monthly through Polar.");
  });
});
