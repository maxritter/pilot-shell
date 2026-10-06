import { renderToReadableStream } from "react-dom/server.browser";
import { expect, it } from "vitest";
import SearchMain from "../../../docusaurus/src/components/SearchMain";

it("gives search results a main landmark that a keyboard user can focus", async () => {
  const stream = await renderToReadableStream(<SearchMain><h1>Search the documentation</h1><p>No results found.</p></SearchMain>);
  await stream.allReady;
  const html = await new Response(stream).text();
  expect(html).toContain('<main id="main-content" tabindex="-1">');
  expect(html).toContain("No results found.");
  expect(html).not.toContain("<nav");
  expect(html).not.toContain("<footer");
});
